"""Seed demo data for ToolShare — idempotent."""

import os
import uuid
import hashlib
import boto3
from datetime import datetime, timezone

REGION = os.environ.get("REGION", "eu-west-1")
TABLE = os.environ.get("DYNAMODB_TABLE", "toolshare-prod")

dynamodb = boto3.resource("dynamodb", region_name=REGION)
table = dynamodb.Table(TABLE)


def hash_password(password):
    salt = os.urandom(16)
    key = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100000)
    return salt.hex() + ":" + key.hex()


def user_exists(email):
    r = table.scan(
        FilterExpression="entityType = :et AND email = :e",
        ExpressionAttributeValues={":et": "user", ":e": email},
    )
    return len(r.get("Items", [])) > 0


def tool_exists(name):
    r = table.scan(
        FilterExpression="entityType = :et AND #n = :n",
        ExpressionAttributeValues={":et": "tool", ":n": name},
        ExpressionAttributeNames={"#n": "name"},
    )
    return len(r.get("Items", [])) > 0


def seed():
    now = datetime.now(timezone.utc).isoformat()

    # --- Demo users ---
    users = [
        {"email": "admin@toolshare.com", "username": "admin", "role": "admin", "password": "Admin123!"},
        {"email": "user@toolshare.com",  "username": "demo_user", "role": "user", "password": "User1234!"},
    ]
    user_ids = {}
    for u in users:
        if user_exists(u["email"]):
            print(f"  User {u['email']} already exists, skipping")
            r = table.scan(
                FilterExpression="entityType = :et AND email = :e",
                ExpressionAttributeValues={":et": "user", ":e": u["email"]},
            )
            user_ids[u["email"]] = r["Items"][0]["id"]
            continue
        uid = str(uuid.uuid4())
        user_ids[u["email"]] = uid
        table.put_item(Item={
            "id": uid,
            "entityType": "user",
            "username": u["username"],
            "email": u["email"],
            "password": hash_password(u["password"]),
            "role": u["role"],
            "createdAt": now,
        })
        print(f"  Created user: {u['email']}")

    # --- Demo tools ---
    tools = [
        {"name": "DeWalt Power Drill",    "description": "18V cordless drill with lithium-ion battery, variable speed, keyless chuck", "category": "power_tools", "condition": "excellent"},
        {"name": "Bosch Jigsaw",           "description": "500W jigsaw with dust blower and LED light, ideal for curved cuts", "category": "power_tools", "condition": "good"},
        {"name": "Stanley Hammer",         "description": "16oz fibreglass shaft claw hammer, anti-vibration grip", "category": "hand_tools",  "condition": "good"},
        {"name": "Socket Wrench Set",      "description": "72-piece metric and imperial socket set with ratchet handle and extension bars", "category": "hand_tools",  "condition": "excellent"},
        {"name": "Garden Hedge Trimmer",   "description": "Electric hedge trimmer with 50cm blade, lightweight design for easy handling", "category": "garden",      "condition": "fair"},
        {"name": "Extension Ladder 3.8m",  "description": "Aluminium extending ladder, EN131 certified, 150kg max load", "category": "ladders",     "condition": "good"},
        {"name": "Pressure Washer",        "description": "1800W electric pressure washer with 130 bar max pressure, patio cleaner included", "category": "cleaning",    "condition": "excellent"},
        {"name": "Digital Multimeter",     "description": "Auto-ranging digital multimeter for voltage, current, resistance, and continuity testing", "category": "other",       "condition": "good"},
    ]
    admin_id = user_ids.get("admin@toolshare.com", "seed-admin")
    for t in tools:
        if tool_exists(t["name"]):
            print(f"  Tool '{t['name']}' already exists, skipping")
            continue
        table.put_item(Item={
            "id": str(uuid.uuid4()),
            "entityType": "tool",
            "name": t["name"],
            "description": t["description"],
            "category": t["category"],
            "condition": t["condition"],
            "status": "ready",
            "ownerId": admin_id,
            "createdAt": now,
        })
        print(f"  Created tool: {t['name']}")

    print("Seed complete.")


if __name__ == "__main__":
    seed()
