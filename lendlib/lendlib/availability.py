"""Availability checking for the Community Tool Lending Library."""

from typing import List, Optional
from datetime import datetime, timedelta
from .tool import Tool
from .lending import LendingRecord, LendingStatus


class AvailabilityChecker:
    """Checks tool availability and predicts return dates.

    Works with inventory and lending data to determine
    if tools are available for borrowing.
    """

    def __init__(self, tools: List[Tool] = None, records: List[LendingRecord] = None):
        self._tools = {t.tool_id: t for t in (tools or [])}
        self._records = records or []

    def set_tools(self, tools: List[Tool]):
        """Set the tools to check availability for."""
        self._tools = {t.tool_id: t for t in tools}

    def set_records(self, records: List[LendingRecord]):
        """Set the lending records for availability checking."""
        self._records = records

    def is_tool_available(self, tool_id: str) -> bool:
        """Check if a specific tool is available for borrowing."""
        tool = self._tools.get(tool_id)
        if not tool:
            return False
        if not tool.is_available:
            return False
        # Check if there's an active or approved lending for this tool
        active_statuses = {LendingStatus.ACTIVE, LendingStatus.APPROVED}
        for record in self._records:
            if record.tool_id == tool_id and record.status in active_statuses:
                return False
        return True

    def get_available_tools(self) -> List[Tool]:
        """Get all currently available tools."""
        return [t for t in self._tools.values() if self.is_tool_available(t.tool_id)]

    def get_unavailable_tools(self) -> List[Tool]:
        """Get all currently unavailable tools."""
        return [t for t in self._tools.values() if not self.is_tool_available(t.tool_id)]

    def get_expected_return_date(self, tool_id: str) -> Optional[datetime]:
        """Get the expected return date for a lent-out tool."""
        for record in self._records:
            if (record.tool_id == tool_id and
                    record.status in (LendingStatus.ACTIVE, LendingStatus.OVERDUE)):
                return record.due_date
        return None

    def get_availability_summary(self) -> dict:
        """Get a summary of tool availability."""
        total = len(self._tools)
        available = len(self.get_available_tools())
        return {
            "total_tools": total,
            "available": available,
            "unavailable": total - available,
            "availability_rate": round(available / total * 100, 1) if total > 0 else 0.0,
        }

    def check_can_borrow(self, tool_id: str, borrower_id: str) -> dict:
        """Check if a borrower can borrow a specific tool, with reasons."""
        result = {"can_borrow": True, "reasons": []}

        tool = self._tools.get(tool_id)
        if not tool:
            result["can_borrow"] = False
            result["reasons"].append("Tool not found")
            return result

        if not tool.is_available:
            result["can_borrow"] = False
            result["reasons"].append("Tool is not available")

        if tool.needs_maintenance():
            result["can_borrow"] = False
            result["reasons"].append("Tool needs maintenance")

        # Check if borrower already has this tool
        for record in self._records:
            if (record.tool_id == tool_id and
                    record.borrower_id == borrower_id and
                    record.status in (LendingStatus.ACTIVE, LendingStatus.APPROVED)):
                result["can_borrow"] = False
                result["reasons"].append("Borrower already has an active lending for this tool")

        # Check if borrower has overdue items
        for record in self._records:
            if (record.borrower_id == borrower_id and
                    record.status == LendingStatus.OVERDUE):
                result["can_borrow"] = False
                result["reasons"].append("Borrower has overdue items")
                break

        return result

    def predict_next_available(self, tool_id: str) -> Optional[datetime]:
        """Predict when a tool will next be available."""
        return_date = self.get_expected_return_date(tool_id)
        if return_date:
            return return_date + timedelta(days=1)
        return None
