"""Tests for the Tools API endpoints."""

import pytest


class TestToolsAPI:
    def test_list_tools_empty(self, client):
        resp = client.get("/api/tools")
        assert resp.status_code == 200
        data = resp.get_json()
        assert data["count"] == 0

    def test_create_tool(self, client, sample_tool):
        resp = client.post("/api/tools", json=sample_tool)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["name"] == "Test Hammer"
        assert data["is_available"] is True

    def test_create_tool_missing_name(self, client):
        resp = client.post("/api/tools", json={"description": "No name"})
        assert resp.status_code == 400

    def test_get_tool(self, client, sample_tool):
        create_resp = client.post("/api/tools", json=sample_tool)
        tool_id = create_resp.get_json()["tool_id"]
        resp = client.get(f"/api/tools/{tool_id}")
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Test Hammer"

    def test_get_tool_not_found(self, client):
        resp = client.get("/api/tools/nonexistent-id")
        assert resp.status_code == 404

    def test_update_tool(self, client, sample_tool):
        create_resp = client.post("/api/tools", json=sample_tool)
        tool_id = create_resp.get_json()["tool_id"]
        resp = client.put(f"/api/tools/{tool_id}",
                          json={"name": "Updated Hammer"})
        assert resp.status_code == 200
        assert resp.get_json()["name"] == "Updated Hammer"

    def test_update_tool_not_found(self, client):
        resp = client.put("/api/tools/nonexistent", json={"name": "X"})
        assert resp.status_code == 404

    def test_delete_tool(self, client, sample_tool):
        create_resp = client.post("/api/tools", json=sample_tool)
        tool_id = create_resp.get_json()["tool_id"]
        resp = client.delete(f"/api/tools/{tool_id}")
        assert resp.status_code == 200
        # Verify deletion
        get_resp = client.get(f"/api/tools/{tool_id}")
        assert get_resp.status_code == 404

    def test_delete_tool_not_found(self, client):
        resp = client.delete("/api/tools/nonexistent")
        assert resp.status_code == 404

    def test_list_tools_with_data(self, client, sample_tool):
        client.post("/api/tools", json=sample_tool)
        client.post("/api/tools", json={**sample_tool, "name": "Drill"})
        resp = client.get("/api/tools")
        assert resp.status_code == 200
        assert resp.get_json()["count"] == 2

    def test_filter_tools_by_category(self, client, sample_tool):
        client.post("/api/tools", json=sample_tool)
        client.post("/api/tools", json={**sample_tool, "name": "Drill",
                                         "category": "power_tool"})
        resp = client.get("/api/tools?category=hand_tool")
        assert resp.get_json()["count"] == 1
