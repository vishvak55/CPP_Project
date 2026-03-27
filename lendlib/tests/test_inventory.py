"""Tests for the InventoryManager."""

import pytest
from lendlib.tool import Tool, ToolCategory, ToolCondition
from lendlib.inventory import InventoryManager


class TestInventoryManager:
    def setup_method(self):
        self.mgr = InventoryManager()
        self.hammer = Tool(name="Hammer", description="Claw hammer",
                           category=ToolCategory.HAND_TOOL)
        self.drill = Tool(name="Drill", description="Power drill",
                          category=ToolCategory.POWER_TOOL)
        self.saw = Tool(name="Saw", description="Hand saw",
                        category=ToolCategory.HAND_TOOL,
                        condition=ToolCondition.POOR)

    def test_add_tool(self):
        self.mgr.add_tool(self.hammer)
        assert self.mgr.count == 1

    def test_add_duplicate(self):
        self.mgr.add_tool(self.hammer)
        with pytest.raises(ValueError):
            self.mgr.add_tool(self.hammer)

    def test_get_tool(self):
        self.mgr.add_tool(self.hammer)
        found = self.mgr.get_tool(self.hammer.tool_id)
        assert found.name == "Hammer"

    def test_get_nonexistent(self):
        assert self.mgr.get_tool("nonexistent") is None

    def test_remove_tool(self):
        self.mgr.add_tool(self.hammer)
        assert self.mgr.remove_tool(self.hammer.tool_id) is True
        assert self.mgr.count == 0

    def test_update_tool(self):
        self.mgr.add_tool(self.hammer)
        self.mgr.update_tool(self.hammer.tool_id, name="Big Hammer")
        assert self.mgr.get_tool(self.hammer.tool_id).name == "Big Hammer"

    def test_search_by_name(self):
        self.mgr.add_tool(self.hammer)
        self.mgr.add_tool(self.drill)
        results = self.mgr.search_by_name("ham")
        assert len(results) == 1

    def test_filter_by_category(self):
        self.mgr.add_tool(self.hammer)
        self.mgr.add_tool(self.drill)
        results = self.mgr.filter_by_category(ToolCategory.HAND_TOOL)
        assert len(results) == 1

    def test_get_available_tools(self):
        self.mgr.add_tool(self.hammer)
        self.mgr.add_tool(self.drill)
        self.drill.mark_unavailable()
        assert len(self.mgr.get_available_tools()) == 1

    def test_get_tools_needing_maintenance(self):
        self.mgr.add_tool(self.hammer)
        self.mgr.add_tool(self.saw)
        result = self.mgr.get_tools_needing_maintenance()
        assert len(result) == 1
        assert result[0].name == "Saw"

    def test_statistics(self):
        self.mgr.add_tool(self.hammer)
        self.mgr.add_tool(self.drill)
        self.mgr.add_tool(self.saw)
        self.drill.mark_unavailable()
        stats = self.mgr.get_statistics()
        assert stats["total_tools"] == 3
        assert stats["available"] == 2
        assert stats["lent_out"] == 1
