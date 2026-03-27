"""SQLAlchemy database models for local development."""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()


class ToolModel(db.Model):
    """SQLite model for tools."""
    __tablename__ = "tools"

    tool_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    category = db.Column(db.String(50), default="other")
    condition = db.Column(db.String(50), default="good")
    owner_id = db.Column(db.String(36), nullable=True)
    image_url = db.Column(db.String(500), nullable=True)
    max_lending_days = db.Column(db.Integer, default=14)
    is_available = db.Column(db.Boolean, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "category": self.category,
            "condition": self.condition,
            "owner_id": self.owner_id,
            "image_url": self.image_url,
            "max_lending_days": self.max_lending_days,
            "is_available": self.is_available,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class UserModel(db.Model):
    """SQLite model for users."""
    __tablename__ = "users"

    user_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    full_name = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(20), default="borrower")
    phone = db.Column(db.String(20), nullable=True)
    address = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    trust_score = db.Column(db.Integer, default=100)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role,
            "phone": self.phone,
            "address": self.address,
            "is_active": self.is_active,
            "trust_score": self.trust_score,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class LendingModel(db.Model):
    """SQLite model for lending records."""
    __tablename__ = "lendings"

    record_id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    tool_id = db.Column(db.String(36), db.ForeignKey("tools.tool_id"), nullable=False)
    borrower_id = db.Column(db.String(36), db.ForeignKey("users.user_id"), nullable=False)
    lender_id = db.Column(db.String(36), nullable=True)
    status = db.Column(db.String(20), default="requested")
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    lent_at = db.Column(db.DateTime, nullable=True)
    due_date = db.Column(db.DateTime, nullable=True)
    returned_at = db.Column(db.DateTime, nullable=True)
    lending_days = db.Column(db.Integer, default=7)
    notes = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "record_id": self.record_id,
            "tool_id": self.tool_id,
            "borrower_id": self.borrower_id,
            "lender_id": self.lender_id,
            "status": self.status,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "lent_at": self.lent_at.isoformat() if self.lent_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
            "lending_days": self.lending_days,
            "notes": self.notes,
        }
