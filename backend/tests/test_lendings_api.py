"""Tests for the Lendings API endpoints."""

import pytest


class TestLendingsAPI:
    def test_list_lendings_empty(self, client):
        resp = client.get("/api/lendings")
        assert resp.status_code == 200
        assert resp.get_json()["count"] == 0

    def test_create_lending(self, client, sample_tool_id, sample_user_id):
        resp = client.post("/api/lendings", json={
            "tool_id": sample_tool_id,
            "borrower_id": sample_user_id,
            "lending_days": 7,
        })
        assert resp.status_code == 201
        assert resp.get_json()["status"] == "requested"

    def test_create_lending_missing_fields(self, client):
        resp = client.post("/api/lendings", json={"tool_id": "x"})
        assert resp.status_code == 400

    def test_get_lending(self, client, sample_tool_id, sample_user_id):
        create_resp = client.post("/api/lendings", json={
            "tool_id": sample_tool_id,
            "borrower_id": sample_user_id,
        })
        record_id = create_resp.get_json()["record_id"]
        resp = client.get(f"/api/lendings/{record_id}")
        assert resp.status_code == 200

    def test_get_lending_not_found(self, client):
        resp = client.get("/api/lendings/nonexistent")
        assert resp.status_code == 404

    def test_approve_lending(self, client, sample_tool_id, sample_user_id):
        create_resp = client.post("/api/lendings", json={
            "tool_id": sample_tool_id,
            "borrower_id": sample_user_id,
        })
        record_id = create_resp.get_json()["record_id"]
        resp = client.post(f"/api/lendings/{record_id}/approve")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "approved"

    def test_activate_lending(self, client, sample_tool_id, sample_user_id):
        create_resp = client.post("/api/lendings", json={
            "tool_id": sample_tool_id,
            "borrower_id": sample_user_id,
        })
        record_id = create_resp.get_json()["record_id"]
        client.post(f"/api/lendings/{record_id}/approve")
        resp = client.post(f"/api/lendings/{record_id}/activate")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "active"
        assert resp.get_json()["due_date"] is not None

    def test_return_lending(self, client, sample_tool_id, sample_user_id):
        create_resp = client.post("/api/lendings", json={
            "tool_id": sample_tool_id,
            "borrower_id": sample_user_id,
        })
        record_id = create_resp.get_json()["record_id"]
        client.post(f"/api/lendings/{record_id}/approve")
        client.post(f"/api/lendings/{record_id}/activate")
        resp = client.post(f"/api/lendings/{record_id}/return")
        assert resp.status_code == 200
        assert resp.get_json()["status"] == "returned"

    def test_delete_lending(self, client, sample_tool_id, sample_user_id):
        create_resp = client.post("/api/lendings", json={
            "tool_id": sample_tool_id,
            "borrower_id": sample_user_id,
        })
        record_id = create_resp.get_json()["record_id"]
        resp = client.delete(f"/api/lendings/{record_id}")
        assert resp.status_code == 200

    def test_update_lending(self, client, sample_tool_id, sample_user_id):
        create_resp = client.post("/api/lendings", json={
            "tool_id": sample_tool_id,
            "borrower_id": sample_user_id,
        })
        record_id = create_resp.get_json()["record_id"]
        resp = client.put(f"/api/lendings/{record_id}",
                          json={"notes": "Updated notes"})
        assert resp.status_code == 200
        assert resp.get_json()["notes"] == "Updated notes"

    def test_approve_wrong_status(self, client, sample_tool_id, sample_user_id):
        create_resp = client.post("/api/lendings", json={
            "tool_id": sample_tool_id,
            "borrower_id": sample_user_id,
        })
        record_id = create_resp.get_json()["record_id"]
        client.post(f"/api/lendings/{record_id}/approve")
        # Try approving again
        resp = client.post(f"/api/lendings/{record_id}/approve")
        assert resp.status_code == 400
