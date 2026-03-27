"""Tests for the Tool model."""

import pytest
from lendlib.tool import Tool, ToolCategory, ToolCondition


class TestTool:
    def test_create_tool(self):
        tool = Tool(name="Hammer", description="Claw hammer")
        assert tool.name == "Hammer"
        assert tool.description == "Claw hammer"
        assert tool.is_available is True
        assert tool.category == ToolCategory.OTHER
        assert tool.condition == ToolCondition.GOOD

    def test_create_tool_with_category(self):
        tool = Tool(name="Drill", description="Power drill",
                    category=ToolCategory.POWER_TOOL)
        assert tool.category == ToolCategory.POWER_TOOL

    def test_tool_to_dict(self):
        tool = Tool(name="Saw", description="Hand saw")
        d = tool.to_dict()
        assert d["name"] == "Saw"
        assert d["is_available"] is True
        assert "tool_id" in d

    def test_tool_from_dict(self):
        data = {"name": "Wrench", "description": "Adjustable wrench",
                "category": "hand_tool", "condition": "good"}
        tool = Tool.from_dict(data)
        assert tool.name == "Wrench"
        assert tool.category == ToolCategory.HAND_TOOL

    def test_tool_roundtrip(self):
        tool = Tool(name="Pliers", description="Needle nose pliers",
                    category=ToolCategory.HAND_TOOL, max_lending_days=21)
        restored = Tool.from_dict(tool.to_dict())
        assert restored.name == tool.name
        assert restored.tool_id == tool.tool_id
        assert restored.max_lending_days == 21

    def test_mark_unavailable(self):
        tool = Tool(name="Hammer", description="Ball peen hammer")
        tool.mark_unavailable()
        assert tool.is_available is False

    def test_mark_available(self):
        tool = Tool(name="Hammer", description="Ball peen hammer")
        tool.mark_unavailable()
        tool.mark_available()
        assert tool.is_available is True

    def test_update_condition(self):
        tool = Tool(name="Drill", description="Cordless drill")
        tool.update_condition(ToolCondition.POOR)
        assert tool.condition == ToolCondition.POOR

    def test_needs_maintenance(self):
        tool = Tool(name="Saw", description="Old saw",
                    condition=ToolCondition.NEEDS_REPAIR)
        assert tool.needs_maintenance() is True

    def test_does_not_need_maintenance(self):
        tool = Tool(name="Saw", description="New saw",
                    condition=ToolCondition.EXCELLENT)
        assert tool.needs_maintenance() is False

    def test_tool_equality(self):
        tool1 = Tool(name="Hammer", description="Hammer", tool_id="abc")
        tool2 = Tool(name="Hammer", description="Hammer", tool_id="abc")
        assert tool1 == tool2

    def test_tool_inequality(self):
        tool1 = Tool(name="Hammer", description="Hammer")
        tool2 = Tool(name="Hammer", description="Hammer")
        assert tool1 != tool2
