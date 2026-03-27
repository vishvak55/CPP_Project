"""Tests for the AvailabilityChecker."""

import pytest
from datetime import datetime, timedelta
from lendlib.tool import Tool, ToolCategory, ToolCondition
from lendlib.lending import LendingRecord, LendingStatus
from lendlib.availability import AvailabilityChecker


class TestAvailabilityChecker:
    def setup_method(self):
        self.tool1 = Tool(name="Hammer", description="Hammer")
        self.tool2 = Tool(name="Drill", description="Drill")
        self.checker = AvailabilityChecker(
            tools=[self.tool1, self.tool2], records=[]
        )

    def test_tool_available(self):
        assert self.checker.is_tool_available(self.tool1.tool_id) is True

    def test_tool_not_found(self):
        assert self.checker.is_tool_available("nonexistent") is False

    def test_tool_unavailable_when_lent(self):
        record = LendingRecord(
            tool_id=self.tool1.tool_id, borrower_id="b1"
        )
        record.approve()
        record.activate()
        self.checker.set_records([record])
        assert self.checker.is_tool_available(self.tool1.tool_id) is False

    def test_get_available_tools(self):
        record = LendingRecord(
            tool_id=self.tool1.tool_id, borrower_id="b1"
        )
        record.approve()
        record.activate()
        self.checker.set_records([record])
        available = self.checker.get_available_tools()
        assert len(available) == 1
        assert available[0].tool_id == self.tool2.tool_id

    def test_availability_summary(self):
        summary = self.checker.get_availability_summary()
        assert summary["total_tools"] == 2
        assert summary["available"] == 2
        assert summary["availability_rate"] == 100.0

    def test_check_can_borrow_success(self):
        result = self.checker.check_can_borrow(self.tool1.tool_id, "b1")
        assert result["can_borrow"] is True

    def test_check_can_borrow_maintenance(self):
        self.tool1.update_condition(ToolCondition.NEEDS_REPAIR)
        result = self.checker.check_can_borrow(self.tool1.tool_id, "b1")
        assert result["can_borrow"] is False
        assert "maintenance" in result["reasons"][0].lower()

    def test_expected_return_date(self):
        record = LendingRecord(tool_id=self.tool1.tool_id, borrower_id="b1")
        record.approve()
        record.activate()
        self.checker.set_records([record])
        ret_date = self.checker.get_expected_return_date(self.tool1.tool_id)
        assert ret_date is not None
