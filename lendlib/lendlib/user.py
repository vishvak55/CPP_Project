"""User model for the Community Tool Lending Library."""

from enum import Enum
from datetime import datetime
import uuid


class UserRole(Enum):
    """Roles for users in the lending library system."""
    BORROWER = "borrower"
    LENDER = "lender"
    ADMIN = "admin"


class User:
    """Represents a user in the community lending library.

    Attributes:
        user_id: Unique identifier for the user.
        username: Login username.
        email: User email address.
        full_name: Full display name.
        role: User role enum value.
        phone: Contact phone number.
        address: User address.
        is_active: Whether the account is active.
        trust_score: Reliability score (0-100).
        created_at: Timestamp when user registered.
    """

    def __init__(self, username: str, email: str, full_name: str,
                 role: UserRole = UserRole.BORROWER, phone: str = None,
                 address: str = None, user_id: str = None):
        self.user_id = user_id or str(uuid.uuid4())
        self.username = username
        self.email = email
        self.full_name = full_name
        self.role = role if isinstance(role, UserRole) else UserRole(role)
        self.phone = phone
        self.address = address
        self.is_active = True
        self.trust_score = 100
        self.created_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert user to dictionary representation."""
        return {
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "full_name": self.full_name,
            "role": self.role.value,
            "phone": self.phone,
            "address": self.address,
            "is_active": self.is_active,
            "trust_score": self.trust_score,
            "created_at": self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "User":
        """Create a User instance from a dictionary."""
        user = cls(
            username=data["username"],
            email=data["email"],
            full_name=data["full_name"],
            role=UserRole(data.get("role", "borrower")),
            phone=data.get("phone"),
            address=data.get("address"),
            user_id=data.get("user_id"),
        )
        user.is_active = data.get("is_active", True)
        user.trust_score = data.get("trust_score", 100)
        if "created_at" in data and isinstance(data["created_at"], str):
            user.created_at = datetime.fromisoformat(data["created_at"])
        return user

    def deactivate(self):
        """Deactivate the user account."""
        self.is_active = False

    def activate(self):
        """Activate the user account."""
        self.is_active = True

    def adjust_trust_score(self, delta: int):
        """Adjust trust score by delta, clamped to 0-100."""
        self.trust_score = max(0, min(100, self.trust_score + delta))

    def can_borrow(self) -> bool:
        """Check if user is eligible to borrow tools."""
        return self.is_active and self.trust_score >= 20

    def is_admin(self) -> bool:
        """Check if user has admin role."""
        return self.role == UserRole.ADMIN

    def __repr__(self):
        return f"User(username='{self.username}', role={self.role.value})"

    def __eq__(self, other):
        if not isinstance(other, User):
            return False
        return self.user_id == other.user_id
