"""Test fixtures for backend API tests."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from app import create_app
from models.database import db as _db


@pytest.fixture
def app():
    """Create a test application."""
    app = create_app("testing")
    with app.app_context():
        _db.create_all()
        yield app
        _db.session.remove()
        _db.drop_all()


@pytest.fixture
def client(app):
    """Create a test client."""
    return app.test_client()


@pytest.fixture
def sample_tool():
    """Sample tool data."""
    return {
        "name": "Test Hammer",
        "description": "A test hammer for unit tests",
        "category": "hand_tool",
        "condition": "good",
        "max_lending_days": 14,
    }


@pytest.fixture
def sample_user():
    """Sample user data."""
    return {
        "username": "testuser",
        "email": "test@example.com",
        "full_name": "Test User",
        "role": "borrower",
    }


@pytest.fixture
def sample_tool_id(client, sample_tool):
    """Create a tool and return its ID."""
    resp = client.post("/api/tools", json=sample_tool)
    return resp.get_json()["tool_id"]


@pytest.fixture
def sample_user_id(client, sample_user):
    """Create a user and return its ID."""
    resp = client.post("/api/users", json=sample_user)
    return resp.get_json()["user_id"]
