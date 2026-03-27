"""
ToolShare - Community Tool Lending Library
AWS Lambda handler for all API operations.
"""

import json
import os
import uuid
import hashlib
import hmac
import time
import boto3
from datetime import datetime, timedelta
from decimal import Decimal

# Environment variables
DYNAMODB_TABLE = os.environ.get("DYNAMODB_TABLE", "toolshare-prod")
S3_BUCKET = os.environ.get("S3_BUCKET", "toolshare-files-prod-vishvak")
SNS_TOPIC_ARN = os.environ.get("SNS_TOPIC_ARN", "")
REGION = os.environ.get("REGION", "eu-west-1")
JWT_SECRET = os.environ.get("JWT_SECRET", "toolshare-secret-2026")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(DYNAMODB_TABLE)
sns = boto3.client("sns", region_name=REGION)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def decimal_default(obj):
    if isinstance(obj, Decimal):
        return int(obj) if obj % 1 == 0 else float(obj)
    raise TypeError(f"Object of type {type(obj)} is not JSON serializable")


def response(status, body):
    return {
        "statusCode": status,
        "headers": {
            "Content-Type": "application/json",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Content-Type,Authorization",
            "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
        },
        "body": json.dumps(body, default=decimal_default),
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
    import base64
    h = base64.urlsafe_b64encode(header.encode()).rstrip(b"=").decode()
    p = base64.urlsafe_b64encode(payload.encode()).rstrip(b"=").decode()
    sig_input = f"{h}.{p}"
    sig = hmac.new(JWT_SECRET.encode(), sig_input.encode(), hashlib.sha256).digest()
    s = base64.urlsafe_b64encode(sig).rstrip(b"=").decode()
    return f"{h}.{p}.{s}"


def verify_jwt(token):
    import base64
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
    auth = event.get("headers", {})
    token_header = auth.get("Authorization") or auth.get("authorization") or ""
    if token_header.startswith("Bearer "):
        token = token_header[7:]
    else:
        token = token_header
    if not token:
        return None
    return verify_jwt(token)


def get_body(event):
    body = event.get("body", "{}")
    if isinstance(body, str):
        return json.loads(body) if body else {}
    return body or {}


def get_path_param(event, param):
    params = event.get("pathParameters") or {}
    return params.get(param)


# ---------------------------------------------------------------------------
# Auth handlers
# ---------------------------------------------------------------------------

def handle_register(event):
    body = get_body(event)
    name = body.get("name", "").strip()
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not name or not email or not password:
        return response(400, {"error": "Name, email, and password are required"})
    if len(password) < 8:
        return response(400, {"error": "Password must be at least 8 characters"})

    existing = table.get_item(Key={"PK": f"USER#{email}", "SK": "PROFILE"})
    if "Item" in existing:
        return response(409, {"error": "Email already registered"})

    user_id = str(uuid.uuid4())
    table.put_item(Item={
        "PK": f"USER#{email}",
        "SK": "PROFILE",
        "userId": user_id,
        "name": name,
        "email": email,
        "password": hash_password(password),
        "role": "user",
        "createdAt": datetime.utcnow().isoformat(),
    })

    token = create_jwt(user_id, email, "user")
    return response(201, {
        "message": "Registration successful",
        "token": token,
        "user": {"userId": user_id, "name": name, "email": email, "role": "user"},
    })


def handle_login(event):
    body = get_body(event)
    email = body.get("email", "").strip().lower()
    password = body.get("password", "")

    if not email or not password:
        return response(400, {"error": "Email and password are required"})

    result = table.get_item(Key={"PK": f"USER#{email}", "SK": "PROFILE"})
    user = result.get("Item")
    if not user or not verify_password(password, user["password"]):
        return response(401, {"error": "Invalid email or password"})

    token = create_jwt(user["userId"], email, user.get("role", "user"))
    return response(200, {
        "message": "Login successful",
        "token": token,
        "user": {
            "userId": user["userId"],
            "name": user["name"],
            "email": user["email"],
            "role": user.get("role", "user"),
        },
    })


# ---------------------------------------------------------------------------
# Tool handlers
# ---------------------------------------------------------------------------

def handle_get_tools(event):
    result = table.scan(
        FilterExpression="begins_with(PK, :pk)",
        ExpressionAttributeValues={":pk": "TOOL#"},
    )
    tools = []
    for item in result.get("Items", []):
        if item.get("SK") == "METADATA":
            item.pop("PK", None)
            item.pop("SK", None)
            item.pop("password", None)
            tools.append(item)
    return response(200, {"tools": tools})


def handle_create_tool(event):
    user = get_user_from_event(event)
    if not user:
        return response(401, {"error": "Authentication required"})

    body = get_body(event)
    name = body.get("name", "").strip()
    category = body.get("category", "other")

    if not name:
        return response(400, {"error": "Tool name is required"})

    valid_categories = ["power_tools", "hand_tools", "garden", "ladders", "cleaning", "kitchen", "other"]
    if category not in valid_categories:
        return response(400, {"error": f"Invalid category. Must be one of: {', '.join(valid_categories)}"})

    tool_id = str(uuid.uuid4())
    tool = {
        "PK": f"TOOL#{tool_id}",
        "SK": "METADATA",
        "toolId": tool_id,
        "name": name,
        "description": body.get("description", ""),
        "category": category,
        "condition": body.get("condition", "good"),
        "status": "ready",
        "imageUrl": body.get("imageUrl", ""),
        "ownerId": user["userId"],
        "createdAt": datetime.utcnow().isoformat(),
    }
    table.put_item(Item=tool)
    tool.pop("PK", None)
    tool.pop("SK", None)
    return response(201, {"message": "Tool created", "tool": tool})


def handle_get_tool(event):
    tool_id = get_path_param(event, "id")
    if not tool_id:
        return response(400, {"error": "Tool ID is required"})

    result = table.get_item(Key={"PK": f"TOOL#{tool_id}", "SK": "METADATA"})
    tool = result.get("Item")
    if not tool:
        return response(404, {"error": "Tool not found"})

    tool.pop("PK", None)
    tool.pop("SK", None)
    return response(200, {"tool": tool})


def handle_update_tool(event):
    user = get_user_from_event(event)
    if not user:
        return response(401, {"error": "Authentication required"})

    tool_id = get_path_param(event, "id")
    if not tool_id:
        return response(400, {"error": "Tool ID is required"})

    result = table.get_item(Key={"PK": f"TOOL#{tool_id}", "SK": "METADATA"})
    tool = result.get("Item")
    if not tool:
        return response(404, {"error": "Tool not found"})

    body = get_body(event)
    update_expr_parts = []
    expr_values = {}
    expr_names = {}

    allowed_fields = ["name", "description", "category", "condition", "status", "imageUrl"]
    for field in allowed_fields:
        if field in body:
            safe_name = f"#{field}"
            safe_val = f":{field}"
            update_expr_parts.append(f"{safe_name} = {safe_val}")
            expr_names[safe_name] = field
            expr_values[safe_val] = body[field]

    if not update_expr_parts:
        return response(400, {"error": "No fields to update"})

    update_expr_parts.append("#updatedAt = :updatedAt")
    expr_names["#updatedAt"] = "updatedAt"
    expr_values[":updatedAt"] = datetime.utcnow().isoformat()

    table.update_item(
        Key={"PK": f"TOOL#{tool_id}", "SK": "METADATA"},
        UpdateExpression="SET " + ", ".join(update_expr_parts),
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
    )
    return response(200, {"message": "Tool updated"})


def handle_delete_tool(event):
    user = get_user_from_event(event)
    if not user:
        return response(401, {"error": "Authentication required"})

    tool_id = get_path_param(event, "id")
    if not tool_id:
        return response(400, {"error": "Tool ID is required"})

    result = table.get_item(Key={"PK": f"TOOL#{tool_id}", "SK": "METADATA"})
    if "Item" not in result:
        return response(404, {"error": "Tool not found"})

    table.delete_item(Key={"PK": f"TOOL#{tool_id}", "SK": "METADATA"})
    return response(200, {"message": "Tool deleted"})


# ---------------------------------------------------------------------------
# Loan handlers
# ---------------------------------------------------------------------------

def handle_borrow_tool(event):
    user = get_user_from_event(event)
    if not user:
        return response(401, {"error": "Authentication required"})

    tool_id = get_path_param(event, "id")
    if not tool_id:
        return response(400, {"error": "Tool ID is required"})

    result = table.get_item(Key={"PK": f"TOOL#{tool_id}", "SK": "METADATA"})
    tool = result.get("Item")
    if not tool:
        return response(404, {"error": "Tool not found"})

    if tool.get("status") != "ready":
        return response(400, {"error": "Tool is not available for borrowing"})

    # Check borrower limit (max 3)
    loans_result = table.scan(
        FilterExpression="begins_with(PK, :pk) AND userId = :uid AND #s = :active",
        ExpressionAttributeValues={
            ":pk": "LOAN#",
            ":uid": user["userId"],
            ":active": "active",
        },
        ExpressionAttributeNames={"#s": "status"},
    )
    active_loans = loans_result.get("Items", [])
    if len(active_loans) >= 3:
        return response(400, {"error": "Borrower limit reached. Maximum 3 active loans allowed"})

    body = get_body(event)
    days = int(body.get("days", 14))
    if days <= 0 or days > 90:
        days = 14

    loan_id = str(uuid.uuid4())
    borrow_date = datetime.utcnow().strftime("%Y-%m-%d")
    due_date = (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")

    loan = {
        "PK": f"LOAN#{loan_id}",
        "SK": "METADATA",
        "loanId": loan_id,
        "toolId": tool_id,
        "toolName": tool.get("name", ""),
        "userId": user["userId"],
        "userName": user.get("email", ""),
        "borrowDate": borrow_date,
        "dueDate": due_date,
        "status": "active",
        "createdAt": datetime.utcnow().isoformat(),
    }
    table.put_item(Item=loan)

    # Update tool status to loaned
    table.update_item(
        Key={"PK": f"TOOL#{tool_id}", "SK": "METADATA"},
        UpdateExpression="SET #s = :s, borrowedBy = :uid, loanId = :lid",
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
                Message=f"Tool '{tool.get('name', '')}' has been borrowed by {user.get('email', '')}. Due date: {due_date}",
            )
    except Exception:
        pass

    loan.pop("PK", None)
    loan.pop("SK", None)
    return response(201, {"message": "Tool borrowed successfully", "loan": loan})


def handle_return_tool(event):
    user = get_user_from_event(event)
    if not user:
        return response(401, {"error": "Authentication required"})

    tool_id = get_path_param(event, "id")
    if not tool_id:
        return response(400, {"error": "Tool ID is required"})

    result = table.get_item(Key={"PK": f"TOOL#{tool_id}", "SK": "METADATA"})
    tool = result.get("Item")
    if not tool:
        return response(404, {"error": "Tool not found"})

    if tool.get("status") != "loaned":
        return response(400, {"error": "Tool is not currently on loan"})

    loan_id = tool.get("loanId")
    if not loan_id:
        return response(400, {"error": "No active loan found for this tool"})

    loan_result = table.get_item(Key={"PK": f"LOAN#{loan_id}", "SK": "METADATA"})
    loan = loan_result.get("Item")

    returned_date = datetime.utcnow().strftime("%Y-%m-%d")
    late_fee = 0

    if loan and loan.get("dueDate"):
        due = datetime.strptime(loan["dueDate"], "%Y-%m-%d")
        if datetime.utcnow() > due:
            days_late = (datetime.utcnow() - due).days
            late_fee = round(days_late * 2.0, 2)

    # Update loan
    if loan:
        table.update_item(
            Key={"PK": f"LOAN#{loan_id}", "SK": "METADATA"},
            UpdateExpression="SET #s = :s, returnedDate = :rd, lateFee = :lf",
            ExpressionAttributeNames={"#s": "status"},
            ExpressionAttributeValues={
                ":s": "returned",
                ":rd": returned_date,
                ":lf": Decimal(str(late_fee)),
            },
        )

    # Update tool status back to ready
    table.update_item(
        Key={"PK": f"TOOL#{tool_id}", "SK": "METADATA"},
        UpdateExpression="SET #s = :s REMOVE borrowedBy, loanId",
        ExpressionAttributeNames={"#s": "status"},
        ExpressionAttributeValues={":s": "ready"},
    )

    resp_body = {"message": "Tool returned successfully", "returnedDate": returned_date}
    if late_fee > 0:
        resp_body["lateFee"] = late_fee
        resp_body["message"] = f"Tool returned with late fee of ${late_fee:.2f}"

    return response(200, resp_body)


def handle_get_loans(event):
    user = get_user_from_event(event)
    if not user:
        return response(401, {"error": "Authentication required"})

    if user.get("role") == "admin":
        result = table.scan(
            FilterExpression="begins_with(PK, :pk)",
            ExpressionAttributeValues={":pk": "LOAN#"},
        )
    else:
        result = table.scan(
            FilterExpression="begins_with(PK, :pk) AND userId = :uid",
            ExpressionAttributeValues={
                ":pk": "LOAN#",
                ":uid": user["userId"],
            },
        )

    loans = []
    for item in result.get("Items", []):
        if item.get("SK") == "METADATA":
            item.pop("PK", None)
            item.pop("SK", None)
            loans.append(item)

    loans.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    return response(200, {"loans": loans})


def handle_get_overdue_loans(event):
    user = get_user_from_event(event)
    if not user:
        return response(401, {"error": "Authentication required"})

    result = table.scan(
        FilterExpression="begins_with(PK, :pk) AND #s = :active",
        ExpressionAttributeValues={
            ":pk": "LOAN#",
            ":active": "active",
        },
        ExpressionAttributeNames={"#s": "status"},
    )

    today = datetime.utcnow().strftime("%Y-%m-%d")
    overdue = []
    for item in result.get("Items", []):
        if item.get("SK") == "METADATA" and item.get("dueDate", "9999") < today:
            item.pop("PK", None)
            item.pop("SK", None)
            overdue.append(item)

    return response(200, {"loans": overdue})


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

def handle_dashboard(event):
    user = get_user_from_event(event)
    if not user:
        return response(401, {"error": "Authentication required"})

    tools_result = table.scan(
        FilterExpression="begins_with(PK, :pk)",
        ExpressionAttributeValues={":pk": "TOOL#"},
    )
    tools = [i for i in tools_result.get("Items", []) if i.get("SK") == "METADATA"]

    total = len(tools)
    available = len([t for t in tools if t.get("status") == "ready"])
    loaned = len([t for t in tools if t.get("status") == "loaned"])

    loans_result = table.scan(
        FilterExpression="begins_with(PK, :pk) AND #s = :active",
        ExpressionAttributeValues={":pk": "LOAN#", ":active": "active"},
        ExpressionAttributeNames={"#s": "status"},
    )
    active_loans = [i for i in loans_result.get("Items", []) if i.get("SK") == "METADATA"]

    today = datetime.utcnow().strftime("%Y-%m-%d")
    overdue = len([l for l in active_loans if l.get("dueDate", "9999") < today])

    recent_result = table.scan(
        FilterExpression="begins_with(PK, :pk)",
        ExpressionAttributeValues={":pk": "LOAN#"},
    )
    recent = [i for i in recent_result.get("Items", []) if i.get("SK") == "METADATA"]
    recent.sort(key=lambda x: x.get("createdAt", ""), reverse=True)
    recent_loans = []
    for loan in recent[:5]:
        loan.pop("PK", None)
        loan.pop("SK", None)
        recent_loans.append(loan)

    return response(200, {
        "totalTools": total,
        "availableCount": available,
        "loanedCount": loaned,
        "overdueCount": overdue,
        "recentLoans": recent_loans,
    })


# ---------------------------------------------------------------------------
# Notifications
# ---------------------------------------------------------------------------

def handle_subscribe(event):
    body = get_body(event)
    email = body.get("email", "").strip()
    if not email:
        return response(400, {"error": "Email is required"})
    try:
        if SNS_TOPIC_ARN:
            sns.subscribe(
                TopicArn=SNS_TOPIC_ARN,
                Protocol="email",
                Endpoint=email,
            )
        return response(200, {"message": f"Subscription request sent to {email}"})
    except Exception as e:
        return response(500, {"error": str(e)})


def handle_get_subscribers(event):
    try:
        if not SNS_TOPIC_ARN:
            return response(200, {"subscribers": []})
        result = sns.list_subscriptions_by_topic(TopicArn=SNS_TOPIC_ARN)
        subs = [
            {"email": s["Endpoint"], "status": s["SubscriptionArn"]}
            for s in result.get("Subscriptions", [])
            if s.get("Protocol") == "email"
        ]
        return response(200, {"subscribers": subs})
    except Exception as e:
        return response(500, {"error": str(e)})


# ---------------------------------------------------------------------------
# Router
# ---------------------------------------------------------------------------

def lambda_handler(event, context):
    method = event.get("httpMethod", "GET")
    path = event.get("path", "")

    # Handle CORS preflight
    if method == "OPTIONS":
        return response(200, {"message": "OK"})

    # --- Public routes (before auth) ---
    if path == "/subscribe" and method == "POST":
        return handle_subscribe(event)
    if path == "/subscribers" and method == "GET":
        return handle_get_subscribers(event)

    # --- Auth routes ---
    if path == "/auth/register" and method == "POST":
        return handle_register(event)
    if path == "/auth/login" and method == "POST":
        return handle_login(event)

    # --- Dashboard ---
    if path == "/dashboard" and method == "GET":
        return handle_dashboard(event)

    # --- Tool routes ---
    if path == "/tools" and method == "GET":
        return handle_get_tools(event)
    if path == "/tools" and method == "POST":
        return handle_create_tool(event)

    # Tool-specific routes with ID
    if path.startswith("/tools/") and "/borrow" not in path and "/return" not in path:
        tool_id = path.split("/tools/")[1].split("/")[0]
        if not event.get("pathParameters"):
            event["pathParameters"] = {}
        event["pathParameters"]["id"] = tool_id

        if method == "GET":
            return handle_get_tool(event)
        if method == "PUT":
            return handle_update_tool(event)
        if method == "DELETE":
            return handle_delete_tool(event)

    # Borrow and return
    if "/borrow" in path and method == "POST":
        tool_id = path.split("/tools/")[1].split("/borrow")[0]
        if not event.get("pathParameters"):
            event["pathParameters"] = {}
        event["pathParameters"]["id"] = tool_id
        return handle_borrow_tool(event)

    if "/return" in path and method == "POST":
        tool_id = path.split("/tools/")[1].split("/return")[0]
        if not event.get("pathParameters"):
            event["pathParameters"] = {}
        event["pathParameters"]["id"] = tool_id
        return handle_return_tool(event)

    # --- Loan routes ---
    if path == "/loans" and method == "GET":
        return handle_get_loans(event)
    if path == "/loans/overdue" and method == "GET":
        return handle_get_overdue_loans(event)

    return response(404, {"error": f"Route not found: {method} {path}"})
