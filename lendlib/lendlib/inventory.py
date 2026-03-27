"""Inventory management for the Community Tool Lending Library."""

from typing import List, Optional
from .tool import Tool, ToolCategory, ToolCondition


class InventoryManager:
    """Manages the tool inventory with CRUD operations and search.

    This class provides an in-memory tool inventory with methods for
    adding, updating, removing, and searching tools.
    """

    def __init__(self):
        self._tools: dict = {}  # tool_id -> Tool

    @property
    def count(self) -> int:
        """Return the total number of tools in inventory."""
        return len(self._tools)

    def add_tool(self, tool: Tool) -> Tool:
        """Add a tool to the inventory."""
        if tool.tool_id in self._tools:
            raise ValueError(f"Tool with ID {tool.tool_id} already exists")
        self._tools[tool.tool_id] = tool
        return tool

    def get_tool(self, tool_id: str) -> Optional[Tool]:
        """Get a tool by ID."""
        return self._tools.get(tool_id)

    def update_tool(self, tool_id: str, **kwargs) -> Optional[Tool]:
        """Update a tool's attributes."""
        tool = self._tools.get(tool_id)
        if not tool:
            return None
        for key, value in kwargs.items():
            if hasattr(tool, key):
                setattr(tool, key, value)
        return tool

    def remove_tool(self, tool_id: str) -> bool:
        """Remove a tool from inventory."""
        if tool_id in self._tools:
            del self._tools[tool_id]
            return True
        return False

    def list_tools(self) -> List[Tool]:
        """List all tools in the inventory."""
        return list(self._tools.values())

    def search_by_name(self, query: str) -> List[Tool]:
        """Search tools by name (case-insensitive partial match)."""
        query_lower = query.lower()
        return [t for t in self._tools.values() if query_lower in t.name.lower()]

    def filter_by_category(self, category: ToolCategory) -> List[Tool]:
        """Filter tools by category."""
        return [t for t in self._tools.values() if t.category == category]

    def filter_by_condition(self, condition: ToolCondition) -> List[Tool]:
        """Filter tools by condition."""
        return [t for t in self._tools.values() if t.condition == condition]

    def get_available_tools(self) -> List[Tool]:
        """Get all currently available tools."""
        return [t for t in self._tools.values() if t.is_available]

    def get_unavailable_tools(self) -> List[Tool]:
        """Get all currently unavailable (lent out) tools."""
        return [t for t in self._tools.values() if not t.is_available]

    def get_tools_needing_maintenance(self) -> List[Tool]:
        """Get tools that need maintenance."""
        return [t for t in self._tools.values() if t.needs_maintenance()]

    def get_statistics(self) -> dict:
        """Get inventory statistics."""
        tools = list(self._tools.values())
        available = sum(1 for t in tools if t.is_available)
        return {
            "total_tools": len(tools),
            "available": available,
            "lent_out": len(tools) - available,
            "needs_maintenance": sum(1 for t in tools if t.needs_maintenance()),
            "by_category": {
                cat.value: sum(1 for t in tools if t.category == cat)
                for cat in ToolCategory
                if any(t.category == cat for t in tools)
            },
        }
