"""Tool model for the Community Tool Lending Library."""

from enum import Enum
from datetime import datetime
import uuid


class ToolCategory(Enum):
    """Categories for tools in the lending library."""
    HAND_TOOL = "hand_tool"
    POWER_TOOL = "power_tool"
    GARDEN = "garden"
    PLUMBING = "plumbing"
    ELECTRICAL = "electrical"
    PAINTING = "painting"
    MEASUREMENT = "measurement"
    SAFETY = "safety"
    OTHER = "other"


class ToolCondition(Enum):
    """Condition ratings for tools."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    NEEDS_REPAIR = "needs_repair"


class Tool:
    """Represents a tool in the community lending library.

    Attributes:
        tool_id: Unique identifier for the tool.
        name: Name of the tool.
        description: Description of the tool.
        category: Category enum value.
        condition: Current condition of the tool.
        owner_id: ID of the tool owner/donor.
        image_url: URL to the tool image in S3.
        max_lending_days: Maximum number of days tool can be lent.
        is_available: Whether the tool is currently available.
        created_at: Timestamp when the tool was added.
        updated_at: Timestamp of last update.
    """

    def __init__(self, name: str, description: str,
                 category: ToolCategory = ToolCategory.OTHER,
                 condition: ToolCondition = ToolCondition.GOOD,
                 owner_id: str = None, image_url: str = None,
                 max_lending_days: int = 14, tool_id: str = None):
        self.tool_id = tool_id or str(uuid.uuid4())
        self.name = name
        self.description = description
        self.category = category if isinstance(category, ToolCategory) else ToolCategory(category)
        self.condition = condition if isinstance(condition, ToolCondition) else ToolCondition(condition)
        self.owner_id = owner_id
        self.image_url = image_url
        self.max_lending_days = max_lending_days
        self.is_available = True
        self.created_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()

    def to_dict(self) -> dict:
        """Convert tool to dictionary representation."""
        return {
            "tool_id": self.tool_id,
            "name": self.name,
            "description": self.description,
            "category": self.category.value,
            "condition": self.condition.value,
            "owner_id": self.owner_id,
            "image_url": self.image_url,
            "max_lending_days": self.max_lending_days,
            "is_available": self.is_available,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: dict) -> "Tool":
        """Create a Tool instance from a dictionary."""
        tool = cls(
            name=data["name"],
            description=data["description"],
            category=ToolCategory(data.get("category", "other")),
            condition=ToolCondition(data.get("condition", "good")),
            owner_id=data.get("owner_id"),
            image_url=data.get("image_url"),
            max_lending_days=data.get("max_lending_days", 14),
            tool_id=data.get("tool_id"),
        )
        tool.is_available = data.get("is_available", True)
        if "created_at" in data and isinstance(data["created_at"], str):
            tool.created_at = datetime.fromisoformat(data["created_at"])
        if "updated_at" in data and isinstance(data["updated_at"], str):
            tool.updated_at = datetime.fromisoformat(data["updated_at"])
        return tool

    def update_condition(self, new_condition: ToolCondition):
        """Update the tool condition."""
        self.condition = new_condition
        self.updated_at = datetime.utcnow()

    def mark_unavailable(self):
        """Mark the tool as unavailable (lent out)."""
        self.is_available = False
        self.updated_at = datetime.utcnow()

    def mark_available(self):
        """Mark the tool as available (returned)."""
        self.is_available = True
        self.updated_at = datetime.utcnow()

    def needs_maintenance(self) -> bool:
        """Check if tool needs maintenance based on condition."""
        return self.condition in (ToolCondition.POOR, ToolCondition.NEEDS_REPAIR)

    def __repr__(self):
        return f"Tool(name='{self.name}', category={self.category.value}, available={self.is_available})"

    def __eq__(self, other):
        if not isinstance(other, Tool):
            return False
        return self.tool_id == other.tool_id
