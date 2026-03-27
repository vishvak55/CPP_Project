"""Tests for the User model."""

import pytest
from lendlib.user import User, UserRole


class TestUser:
    def test_create_user(self):
        user = User(username="john", email="john@example.com", full_name="John Doe")
        assert user.username == "john"
        assert user.role == UserRole.BORROWER
        assert user.is_active is True
        assert user.trust_score == 100

    def test_user_to_dict(self):
        user = User(username="jane", email="jane@example.com", full_name="Jane Smith")
        d = user.to_dict()
        assert d["username"] == "jane"
        assert d["role"] == "borrower"

    def test_user_from_dict(self):
        data = {"username": "bob", "email": "bob@example.com",
                "full_name": "Bob Jones", "role": "admin"}
        user = User.from_dict(data)
        assert user.role == UserRole.ADMIN

    def test_deactivate_user(self):
        user = User(username="test", email="t@t.com", full_name="Test")
        user.deactivate()
        assert user.is_active is False

    def test_activate_user(self):
        user = User(username="test", email="t@t.com", full_name="Test")
        user.deactivate()
        user.activate()
        assert user.is_active is True

    def test_adjust_trust_score(self):
        user = User(username="test", email="t@t.com", full_name="Test")
        user.adjust_trust_score(-30)
        assert user.trust_score == 70

    def test_trust_score_clamped(self):
        user = User(username="test", email="t@t.com", full_name="Test")
        user.adjust_trust_score(-200)
        assert user.trust_score == 0
        user.adjust_trust_score(300)
        assert user.trust_score == 100

    def test_can_borrow(self):
        user = User(username="test", email="t@t.com", full_name="Test")
        assert user.can_borrow() is True

    def test_cannot_borrow_low_trust(self):
        user = User(username="test", email="t@t.com", full_name="Test")
        user.adjust_trust_score(-85)
        assert user.can_borrow() is False

    def test_cannot_borrow_inactive(self):
        user = User(username="test", email="t@t.com", full_name="Test")
        user.deactivate()
        assert user.can_borrow() is False

    def test_is_admin(self):
        user = User(username="admin", email="a@a.com", full_name="Admin",
                    role=UserRole.ADMIN)
        assert user.is_admin() is True
