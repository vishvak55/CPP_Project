"""User CRUD API routes."""

from flask import Blueprint, request, jsonify
from models.database import db, UserModel
import uuid
from datetime import datetime

users_bp = Blueprint("users", __name__)


@users_bp.route("/api/users", methods=["GET"])
def list_users():
    """List all users with optional filtering."""
    role = request.args.get("role")
    active = request.args.get("active")

    query = UserModel.query

    if role:
        query = query.filter_by(role=role)
    if active is not None:
        query = query.filter_by(is_active=active.lower() == "true")

    users = query.all()
    return jsonify({"users": [u.to_dict() for u in users], "count": len(users)})


@users_bp.route("/api/users/<user_id>", methods=["GET"])
def get_user(user_id):
    """Get a specific user by ID."""
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404
    return jsonify(user.to_dict())


@users_bp.route("/api/users", methods=["POST"])
def create_user():
    """Create a new user."""
    data = request.get_json()
    if not data or not data.get("username") or not data.get("email"):
        return jsonify({"error": "Username and email are required"}), 400

    # Check for duplicate username/email
    existing = UserModel.query.filter(
        (UserModel.username == data["username"]) | (UserModel.email == data["email"])
    ).first()
    if existing:
        return jsonify({"error": "Username or email already exists"}), 409

    user = UserModel(
        user_id=str(uuid.uuid4()),
        username=data["username"],
        email=data["email"],
        full_name=data.get("full_name", data["username"]),
        role=data.get("role", "borrower"),
        phone=data.get("phone"),
        address=data.get("address"),
        is_active=True,
        trust_score=100,
        created_at=datetime.utcnow(),
    )
    db.session.add(user)
    db.session.commit()
    return jsonify(user.to_dict()), 201


@users_bp.route("/api/users/<user_id>", methods=["PUT"])
def update_user(user_id):
    """Update an existing user."""
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "No data provided"}), 400

    for field in ("username", "email", "full_name", "role", "phone",
                  "address", "is_active", "trust_score"):
        if field in data:
            setattr(user, field, data[field])

    db.session.commit()
    return jsonify(user.to_dict())


@users_bp.route("/api/users/<user_id>", methods=["DELETE"])
def delete_user(user_id):
    """Delete a user."""
    user = UserModel.query.get(user_id)
    if not user:
        return jsonify({"error": "User not found"}), 404

    db.session.delete(user)
    db.session.commit()
    return jsonify({"message": "User deleted", "user_id": user_id})
