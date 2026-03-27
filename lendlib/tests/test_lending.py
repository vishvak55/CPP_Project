"""Tests for the LendingRecord model."""

import pytest
from datetime import datetime, timedelta
from lendlib.lending import LendingRecord, LendingStatus


class TestLendingRecord:
    def test_create_record(self):
        record = LendingRecord(tool_id="t1", borrower_id="b1")
        assert record.tool_id == "t1"
        assert record.status == LendingStatus.REQUESTED

    def test_record_to_dict(self):
        record = LendingRecord(tool_id="t1", borrower_id="b1", lending_days=10)
        d = record.to_dict()
        assert d["tool_id"] == "t1"
        assert d["lending_days"] == 10
        assert d["status"] == "requested"

    def test_record_from_dict(self):
        data = {"tool_id": "t1", "borrower_id": "b1", "status": "approved",
                "lending_days": 14}
        record = LendingRecord.from_dict(data)
        assert record.status == LendingStatus.APPROVED

    def test_approve(self):
        record = LendingRecord(tool_id="t1", borrower_id="b1")
        record.approve()
        assert record.status == LendingStatus.APPROVED
        assert record.approved_at is not None

    def test_activate(self):
        record = LendingRecord(tool_id="t1", borrower_id="b1", lending_days=7)
        record.approve()
        record.activate()
        assert record.status == LendingStatus.ACTIVE
        assert record.due_date is not None

    def test_complete_return(self):
        record = LendingRecord(tool_id="t1", borrower_id="b1")
        record.approve()
        record.activate()
        record.complete_return()
        assert record.status == LendingStatus.RETURNED

    def test_cancel(self):
        record = LendingRecord(tool_id="t1", borrower_id="b1")
        record.cancel()
        assert record.status == LendingStatus.CANCELLED

    def test_cannot_approve_active(self):
        record = LendingRecord(tool_id="t1", borrower_id="b1")
        record.approve()
        record.activate()
        with pytest.raises(ValueError):
            record.approve()

    def test_is_overdue(self):
        record = LendingRecord(tool_id="t1", borrower_id="b1", lending_days=1)
        record.approve()
        record.activate()
        record.due_date = datetime.utcnow() - timedelta(days=2)
        assert record.is_overdue() is True

    def test_is_not_overdue(self):
        record = LendingRecord(tool_id="t1", borrower_id="b1", lending_days=30)
        record.approve()
        record.activate()
        assert record.is_overdue() is False

    def test_days_overdue(self):
        record = LendingRecord(tool_id="t1", borrower_id="b1")
        record.approve()
        record.activate()
        record.due_date = datetime.utcnow() - timedelta(days=5)
        assert record.days_overdue() >= 4

    def test_calculate_lending_period(self):
        record = LendingRecord(tool_id="t1", borrower_id="b1", lending_days=14)
        period = record.calculate_lending_period()
        assert period == timedelta(days=14)
