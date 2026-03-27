"""
Tool management for the ToolShare lending library.
Handles tool validation, status flows, categorization, and search.
"""


VALID_CATEGORIES = [
    "power_tools", "hand_tools", "garden", "ladders",
    "cleaning", "kitchen", "other"
]

VALID_CONDITIONS = ["excellent", "good", "fair", "poor"]

VALID_STATUSES = ["ready", "loaned", "under_repair"]


class ToolManager:
    """Manages tool operations for the lending library."""

    @staticmethod
    def validate_tool(data):
        """Validate tool data contains required fields with valid values."""
        errors = []
        required = ["name", "category"]
        for field in required:
            if field not in data or not str(data[field]).strip():
                errors.append(f"Missing required field: {field}")
        if "category" in data and data["category"] not in VALID_CATEGORIES:
            errors.append(f"Invalid category. Must be one of: {', '.join(VALID_CATEGORIES)}")
        if "condition" in data and data["condition"] not in VALID_CONDITIONS:
            errors.append(f"Invalid condition. Must be one of: {', '.join(VALID_CONDITIONS)}")
        if "status" in data and data["status"] not in VALID_STATUSES:
            errors.append(f"Invalid status. Must be one of: {', '.join(VALID_STATUSES)}")
        if "name" in data and len(str(data["name"])) > 200:
            errors.append("Tool name cannot exceed 200 characters")
        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def get_tool_status_flow():
        """Return the valid tool status transition flow."""
        return {
            "ready": ["loaned", "under_repair"],
            "loaned": ["returned"],
            "returned": ["ready"],
            "under_repair": ["ready"],
        }

    @staticmethod
    def validate_status_transition(current, new):
        """Validate whether a status transition is allowed."""
        flow = ToolManager.get_tool_status_flow()
        if current not in flow:
            return {"valid": False, "error": f"Unknown current status: {current}"}
        if new not in flow[current]:
            allowed = ", ".join(flow[current])
            return {
                "valid": False,
                "error": f"Cannot transition from '{current}' to '{new}'. Allowed: {allowed}",
            }
        return {"valid": True, "error": None}

    @staticmethod
    def categorize_tools(tools):
        """Group a list of tools by their category."""
        if not isinstance(tools, list):
            raise ValueError("tools must be a list")
        categories = {}
        for tool in tools:
            cat = tool.get("category", "other")
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(tool)
        return categories

    @staticmethod
    def search_tools(tools, query):
        """Search tools by name or description matching the query string."""
        if not isinstance(tools, list):
            raise ValueError("tools must be a list")
        if not query or not query.strip():
            return tools
        q = query.lower().strip()
        results = []
        for tool in tools:
            name = str(tool.get("name", "")).lower()
            desc = str(tool.get("description", "")).lower()
            cat = str(tool.get("category", "")).lower()
            if q in name or q in desc or q in cat:
                results.append(tool)
        return results
