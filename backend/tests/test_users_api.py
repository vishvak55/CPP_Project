"""Tests for the Users API endpoints."""

import pytest


class TestUsersAPI:
    def test_list_users_empty(self, client):
        resp = client.get("/api/users")
        assert resp.status_code == 200
        assert resp.get_json()["count"] == 0

    def test_create_user(self, client, sample_user):
        resp = client.post("/api/users", json=sample_user)
        assert resp.status_code == 201
        data = resp.get_json()
        assert data["username"] == "testuser"
        assert data["trust_score"] == 100

    def test_create_user_missing_fields(self, client):
        resp = client.post("/api/users", json={"username": "x"})
        assert resp.status_code == 400

    def test_create_duplicate_user(self, client, sample_user):
        client.post("/api/users", json=sample_user)
        resp = client.post("/api/users", json=sample_user)
        assert resp.status_code == 409

    def test_get_user(self, client, sample_user):
        create_resp = client.post("/api/users", json=sample_user)
        user_id = create_resp.get_json()["user_id"]
        resp = client.get(f"/api/users/{user_id}")
        assert resp.status_code == 200

    def test_get_user_not_found(self, client):
        resp = client.get("/api/users/nonexistent")
        assert resp.status_code == 404

    def test_update_user(self, client, sample_user):
        create_resp = client.post("/api/users", json=sample_user)
        user_id = create_resp.get_json()["user_id"]
        resp = client.put(f"/api/users/{user_id}",
                          json={"full_name": "Updated Name"})
        assert resp.status_code == 200
        assert resp.get_json()["full_name"] == "Updated Name"

    def test_delete_user(self, client, sample_user):
        create_resp = client.post("/api/users", json=sample_user)
        user_id = create_resp.get_json()["user_id"]
        resp = client.delete(f"/api/users/{user_id}")
        assert resp.status_code == 200

    def test_delete_user_not_found(self, client):
        resp = client.delete("/api/users/nonexistent")
        assert resp.status_code == 404
