"""
ToolShare - Community Tool Lending Library
AWS Lambda handler for all API operations.
Single-table design: partition key = id (String), entityType field for filtering.
"""

import json
import os
import uuid
import hashlib
import hmac
import base64
import time
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

# ---------------------------------------------------------------------------
# Environment
# ---------------------------------------------------------------------------
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "toolshare-prod")
S3_BUCKET = os.environ.get("S3_BUCKET", "toolshare-files-prod-vishvak")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
REGION = os.environ.get("REGION", "eu-west-1")
JWT_SECRET = os.environ.get("JWT_SECRET", "toolshare-secret-2026")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(DYNAMODB_TABLE)
sns = boto3.client("sns", region_name=REGION)

CORS_HEADERS = {
    "Content-Type": "application/json",
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def response(status, body):
    return {
        "statusCode": status,
        "headers": CORS_HEADERS,
        "body": json.dumps(body, default=str),
    }


def hash_password(password):
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + key.hex()


def verify_password(password, stored):
    parts = stored.split(":")
    if len(parts) != 2:
        return False
    salt = bytes.fromhex(parts[0])
    stored_key = parts[1]
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return hmac.compare_digest(key.hex(), stored_key)


def create_jwt(user_id, email, role="user"):
    header = json.dumps({"alg": "HS256", "typ": "JWT"})
    payload = json.dumps({
        "userId": user_id,
        "email": email,
        "role": role,
        "exp": int(time.time()) + 86400,
    })
    h = base64.urlsafe_b64encode(header.encode()).rstrip(b"=").decode()
    p = base64.urlsafe_b64encode(payload.encode()).rstrip(b"=").decode()
    sig_input = f"{h}.{p}"
    sig = hmac.new(JWT_SECRET.encode(), sig_input.encode(), hashlib.sha256).digest()
    s = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
    return f"{h}.{p}.{s}"


def verify_jwt(token):
    try:
        parts = token.split(".")
        if len(parts) != 3:
            return None
        sig_input = f"{parts[0]}.{parts[1]}"
        sig = hmac.new(JWT_SECRET.encode(), sig_input.encode(), hashlib.sha256).digest()
        expected = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
        if not hmac.compare_digest(expected, parts[2]):
            return None
        padding = 4 - len(parts[1]) % 4
        payload = json.loads(base64.urlsafe_b64decode(parts[1] + "=" * padding))
        if payload.get("exp", 0) < time.time():
            return None
        return payload
    except Exception:
        return None


def get_user_from_event(event):
    headers = event.get("headers") or {}
    token_header = headers.get("Authorization") or headers.get("authorization") or ""
    token = token_header[7:] if token_header.startswith("Bearer ") else token_header
    if not token:
        return None
    return verify_jwt(token)


def get_body(event):
    body = event.get("body", "{}")
    if isinstance(body, str):
        return json.loads(body) if body else {}
    return body or {}


def extract_tool_id(path):
    """Extract tool id from paths like /tools/{id} or /tools/{id}/borrow."""
    parts = path.split("/tools/")
    if len(parts) < 2:
        return None
    return parts[1].split("/")[0] or None


# ---------------------------------------------------------------------------
# Auth handlers
# ---------------------------------------------------------------------------

def handle_register(event):
    try:
        body = get_body(event)
        username = body.get("username", "").strip()
        email = body.get("email", "").strip().lower()
        password = body.get("password", "")

        if not username or not email or not password:
            return response(400, {"error": "Username, email, and password are required"})
        if len(password) < 8:
            return response(400, {"error": "Password must be at least 8 characters"})

        # Check if email already exists by scanning users
        existing = table.scan(
            FilterExpression="entityType = :et AND email = :email",
            ExpressionAttributeValues={":et": "user", ":email": email},
        )
        if existing.get("Items"):
            return response(400, {"error": "Email already registered"})

        user_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        table.put_item(Item={
            "id": user_id,
            "entityType": "user",
            "username": username,
            "email": email,
            "password": hash_password(password),
            "role": "user",
            "createdAt": now,
        })

        token = create_jwt(user_id, email, "user")
        return response(201, {
            "message": "Registration successful",
            "token": token,
            "user": {"userId": user_id, "username": username, "email": email, "role": "user"},
        })
    except Exception as e:
        return response(500, {"error": f"Registration failed: {str(e)}"})


def handle_login(event):
    try:
        body = get_body(event)
        email = body.get("email", "").strip().lower()
        password = body.get("password", "")

        if not email or not password:
            return response(400, {"error": "Email and password are required"})

        # Scan for user by email
        result = table.scan(
            FilterExpression="entityType = :et AND email = :email",
            ExpressionAttributeValues={":et": "user", ":email": email},
        )
        users = result.get("Items", [])
        if not users:
            return response(401, {"error": "Invalid email or password"})

        user = users[0]
        if not verify_password(password, user["password"]):
            return response(401, {"error": "Invalid email or password"})

        token = create_jwt(user["id"], email, user.get("role", "user"))
        return response(200, {
            "message": "Login successful",
            "token": token,
            "user": {
                "userId": user["id"],
                "username": user.get("username", ""),
                "email": user["email"],
                "role": user.get("role", "user"),
            },
        })
    except Exception as e:
        return response(500, {"error": f"Login failed: {str(e)}"})


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

def handle_get_tools(event):
    try:
        result = table.scan(
            FilterExpression="entityType = :et",
            ExpressionAttributeValues={":et": "tool"},
        )
        tools = result.get("Items", [])
        # Strip password just in case, return clean items
        for t in tools:
            t.pop("password", None)
        return response(200, {"tools": tools})
    except Exception as e:
        return response(500, {"error": f"Failed to fetch tools: {str(e)}"})


def handle_create_tool(event, user):
    try:
        body = get_body(event)
        name = body.get("name", "").strip()
        description = body.get("description", "").strip()
        category = body.get("category", "other")
        condition = body.get("condition", "good")
        status = body.get("status", "ready")

        if not name:
            return response(400, {"error": "Tool name is required"})

        tool_id = str(uuid.uuid4())
        now = datetime.utcnow().isoformat()
        tool = {
            "id": tool_id,
            "entityType": "tool",
            "name": name,
            "description": description,
            "category": category,
            "condition": condition,
            "status": status,
            "ownerId": user["userId"],
            "createdAt": now,
        }
        table.put_item(Item=tool)
        return response(201, {"message": "Tool created", "tool": tool})
    except Exception as e:
        return response(500, {"error": f"Failed to create tool: {str(e)}"})


def handle_get_tool(tool_id):
    try:
        result = table.get_item(Key={"id": tool_id})
        tool = result.get("Item")
        if not tool or tool.get("entityType") != "tool":
            return response(404, {"error": "Tool not found"})
        return response(200, {"tool": tool})
    except Exception as e:
        return response(500, {"error": f"Failed to fetch tool: {str(e)}"})


def handle_update_tool(event, user, tool_id):
    try:
        result = table.get_item(Key={"id": tool_id})
        tool = result.get("Item")
        if not tool or tool.get("entityType") != "tool":
            return response(404, {"error": "Tool not found"})

        body = get_body(event)
        update_parts = []
        expr_values = {}
        expr_names = {}

        allowed = ["name", "description", "category", "condition", "status"]
        for field in allowed:
            if field in body:
                attr_name = f"#{field}"
                attr_val = f":{field}"
                update_parts.append(f"{attr_name} = {attr_val}")
                expr_names[attr_name] = field
                expr_values[attr_val] = body[field]

        if not update_parts:
            return response(400, {"error": "No fields to update"})

        update_parts.append("#updatedAt = :updatedAt")
        expr_names["#updatedAt"] = "updatedAt"
        expr_values[":updatedAt"] = datetime.utcnow().isoformat()

        table.update_item(
            Key={"id": tool_id},
            UpdateExpression="SET " + ", ".join(update_parts),
            ExpressionAttributeNames=expr_names,
            ExpressionAttributeValues=expr_values,
        )
        return response(200, {"message": "Tool updated"})
    except Exception as e:
        return response(500, {"error": f"Failed to update tool: {str(e)}"})


def handle_delete_tool(user, tool_id):
    try:
        result = table.get_item(Key={"id": tool_id})
        tool = result.get("Item")
        if not tool or tool.get("entityType") != "tool":
            return response(404, {"error": "Tool not found"})

        table.delete_item(Key={"id": tool_id})
        return response(200, {"message": "Tool deleted"})
    except Exception as e:
        return response(500, {"error": f"Failed to delete tool: {str(e)}"})


# ---------------------------------------------------------------------------
# Borrow / Return handlers
# ---------------------------------------------------------------------------

def handle_borrow_tool(event, user, tool_id):
    try:
        # Fetch tool
        result = table.get_item(Key={"id": tool_id})
        tool = result.get("Item")
        if not tool or tool.get("entityType") != "tool":
            return response(404, {"error": "Tool not found"})

        if tool.get("status") != "ready":
            return response(400, {"error": "Tool is not available for borrowing"})

        # Check borrower has < 3 active loans
        loans_result = table.scan(
            FilterExpression="entityType = :et AND #s = :active AND borrowerId = :uid",
            ExpressionAttributeValues={
                ":et": "loan",
                ":active": "active",
                ":uid": user["userId"],
            },
            ExpressionAttributeNames={"#s": "status"},
        )
        active_loans = loans_result.get("Items", [])
        if len(active_loans) >= 3:
            return response(400, {"error": "Borrower limit reached. Maximum 3 active loans allowed"})

        # Create loan
        loan_id = str(uuid.uuid4())
        now = datetime.utcnow()
        borrow_date = now.strftime("%Y-%m-%d")
        due_date = (now + timedelta(days=14)).strftime("%Y-%m-%d")

        loan = {
            "id": loan_id,
            "entityType": "loan",
            "toolId": tool_id,
            "toolName": tool.get("name", ""),
            "borrowerId": user["userId"],
            "borrowerEmail": user.get("email", ""),
            "borrowDate": borrow_date,
            "dueDate": due_date,
            "status": "active",
            "lateFee": Decimal("0"),
            "createdAt": now.isoformat(),
        }
        table.put_item(Item=loan)

        # Update tool status to loaned
        table.update_item(
            Key={"id": tool_id},
            UpdateExpression="SET #s = :s, borrowedBy = :uid, activeLoanId = :lid",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":s": "loaned",
                ":uid": user["userId"],
                ":lid": loan_id,
            },
        )

        # Publish SNS notification
        try:
            if SNS_TOPIC_ARN:
                sns.publish(
                    TopicArn=SNS_TOPIC_ARN,
                    Subject="ToolShare - Tool Borrowed",
                    Message=(
                        f"Tool '{tool.get('name', '')}' has been borrowed by "
                        f"{user.get('email', '')}. Due date: {due_date}"
                    ),
                )
        except Exception:
            pass  # Non-critical, don't fail the request

        return response(201, {"message": "Tool borrowed successfully", "loan": loan})
    except Exception as e:
        return response(500, {"error": f"Failed to borrow tool: {str(e)}"})


def handle_return_tool(event, user, tool_id):
    try:
        # Fetch tool
        result = table.get_item(Key={"id": tool_id})
        tool = result.get("Item")
        if not tool or tool.get("entityType") != "tool":
            return response(404, {"error": "Tool not found"})

        if tool.get("status") != "loaned":
            return response(400, {"error": "Tool is not currently on loan"})

        # Find active loan for this tool + user
        loans_result = table.scan(
            FilterExpression="entityType = :et AND toolId = :tid AND borrowerId = :uid AND #s = :active",
            ExpressionAttributeValues={
                ":et": "loan",
                ":tid": tool_id,
                ":uid": user["userId"],
                ":active": "active",
            },
            ExpressionAttributeNames={"#s": "status"},
        )
        loans = loans_result.get("Items", [])
        if not loans:
            return response(404, {"error": "No active loan found for this tool"})

        loan = loans[0]
        returned_date = datetime.utcnow().strftime("%Y-%m-%d")
        late_fee = Decimal("0")

        # Calculate late fee if overdue
        if loan.get("dueDate"):
            due = datetime.strptime(loan["dueDate"], "%Y-%m-%d")
            if datetime.utcnow() > due:
                days_late = (datetime.utcnow() - due).days
                late_fee = Decimal(str(round(days_late * 2.0, 2)))

        # Update loan to returned
        table.update_item(
            Key={"id": loan["id"]},
            UpdateExpression="SET #s = :s, returnedDate = :rd, lateFee = :lf",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":s": "returned",
                ":rd": returned_date,
                ":lf": late_fee,
            },
        )

        # Update tool status back to ready
        table.update_item(
            Key={"id": tool_id},
            UpdateExpression="SET #s = :s REMOVE borrowedBy, activeLoanId",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={":s": "ready"},
        )

        resp_body = {"message": "Tool returned successfully", "returnedDate": returned_date}
        if late_fee > 0:
            resp_body["lateFee"] = late_fee
            resp_body["message"] = f"Tool returned with late fee of ${late_fee:.2f}"

        return response(200, resp_body)
    except Exception as e:
        return response(500, {"error": f"Failed to return tool: {str(e)}"})


# ---------------------------------------------------------------------------
# Loan handlers
# ---------------------------------------------------------------------------

def handle_get_loans(event, user):
    try:
        if user.get("role") == "admin":
            result = table.scan(
                FilterExpression="entityType = :et",
                ExpressionAttributeValues={":et": "loan"},
            )
        else:
            result = table.scan(
                FilterExpression="entityType = :et AND borrowerId = :uid",
                ExpressionAttributeValues={":et": "loan", ":uid": user["userId"]},
            )

        loans = result.get("Items", [])
        loans.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
        return response(200, {"loans": loans})
    except Exception as e:
        return response(500, {"error": f"Failed to fetch loans: {str(e)}"})


def handle_get_overdue_loans(event, user):
    try:
        result = table.scan(
            FilterExpression="entityType = :et AND #s = :active",
            ExpressionAttributeValues={":et": "loan", ":active": "active"},
            ExpressionAttributeNames={"#s": "status"},
        )

        today = datetime.utcnow().strftime("%Y-%m-%d")
        overdue = [
            item for item in result.get("Items", [])
            if item.get("dueDate", "9999-12-31") < today
        ]
        overdue.sort(key=lambda x: x.get("dueDate", ""), reverse=False)
        return response(200, {"loans": overdue})
    except Exception as e:
        return response(500, {"error": f"Failed to fetch overdue loans: {str(e)}"})


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def handle_dashboard(event, user):
    try:
        # Scan all tools
        tools_result = table.scan(
            FilterExpression="entityType = :et",
            ExpressionAttributeValues={":et": "tool"},
        )
        tools = tools_result.get("Items", [])

        total_tools = len(tools)
        available = len([t for t in tools if t.get("status") == "ready"])
        loaned = len([t for t in tools if t.get("status") == "loaned"])
        repair = len([t for t in tools if t.get("status") == "repair"])

        # Scan active loans for overdue count
        loans_result = table.scan(
            FilterExpression="entityType = :et AND #s = :active",
            ExpressionAttributeValues={":et": "loan", ":active": "active"},
            ExpressionAttributeNames={"#s": "status"},
        )
        active_loans = loans_result.get("Items", [])

        today = datetime.utcnow().strftime("%Y-%m-%d")
        overdue_count = len([
            l for l in active_loans
            if l.get("dueDate", "9999-12-31") < today
        ])

        return response(200, {
            "totalTools": total_tools,
            "available": available,
            "loaned": loaned,
            "repair": repair,
            "overdueCount": overdue_count,
        })
    except Exception as e:
        return response(500, {"error": f"Failed to load dashboard: {str(e)}"})


# ---------------------------------------------------------------------------
# Notifications (PUBLIC)
# ---------------------------------------------------------------------------

def handle_subscribe(event):
    try:
        body = get_body(event)
        email = body.get("email", "").strip()
        if not email:
            return response(400, {"error": "Email is required"})

        if SNS_TOPIC_ARN:
            sns.subscribe(
                TopicArn=SNS_TOPIC_ARN,
                Protocol="email",
                Endpoint=email,
            )
        return response(200, {"message": f"Subscription request sent to {email}"})
    except Exception as e:
        return response(500, {"error": f"Subscribe failed: {str(e)}"})


def handle_get_subscribers(event):
    try:
        if not SNS_TOPIC_ARN:
            return response(200, {"count": 0})

        result = sns.list_subscriptions_by_topic(TopicArn=SNS_TOPIC_ARN)
        count = len([
            s for s in result.get("Subscriptions", [])
            if s.get("Protocol") == "email"
        ])
        return response(200, {"count": count})
    except Exception as e:
        return response(500, {"error": f"Failed to get subscribers: {str(e)}"})


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def lambda_handler(event, context):
    method = event.get("httpMethod", "GET")
    path = event.get("path", "")

    # --- CORS preflight (first) ---
    if method == "OPTIONS":
        return response(200, {"message": "OK"})

    # --- Public routes (BEFORE auth check) ---
    if path == "/subscribe" and method == "POST":
        return handle_subscribe(event)
    if path == "/subscribers" and method == "GET":
        return handle_get_subscribers(event)

    # --- Auth routes (no token needed) ---
    if path == "/auth/register" and method == "POST":
        return handle_register(event)
    if path == "/auth/login" and method == "POST":
        return handle_login(event)

    # --- All remaining routes require authentication ---
    user = get_user_from_event(event)
    if not user:
        return response(401, {"error": "Authentication required"})

    # --- Dashboard ---
    if path == "/dashboard" and method == "GET":
        return handle_dashboard(event, user)

    # --- Tools CRUD ---
    if path == "/tools" and method == "GET":
        return handle_get_tools(event)
    if path == "/tools" and method == "POST":
        return handle_create_tool(event, user)

    # --- Tool-specific routes ---
    if path.startswith("/tools/"):
        tool_id = extract_tool_id(path)
        if not tool_id:
            return response(400, {"error": "Tool ID is required"})

        # Borrow / Return
        if path.endswith("/borrow") and method == "POST":
            return handle_borrow_tool(event, user, tool_id)
        if path.endswith("/return") and method == "POST":
            return handle_return_tool(event, user, tool_id)

        # CRUD on single tool
        if method == "GET":
            return handle_get_tool(tool_id)
        if method == "PUT":
            return handle_update_tool(event, user, tool_id)
        if method == "DELETE":
            return handle_delete_tool(user, tool_id)

    # --- Loans ---
    if path == "/loans" and method == "GET":
        return handle_get_loans(event, user)
    if path == "/loans/overdue" and method == "GET":
        return handle_get_overdue_loans(event, user)

    return response(404, {"error": f"Route not found: {method} {path}"})
