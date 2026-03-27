"""Tests for the BorrowerHistory."""

import pytest
from datetime import datetime, timedelta
from lendlib.lending import LendingRecord, LendingStatus
from lendlib.history import BorrowerHistory


class TestBorrowerHistory:
    def setup_method(self):
        self.records = []
        for i in range(3):
            r = LendingRecord(tool_id=f"t{i}", borrower_id="b1")
            r.approve()
            r.activate()
            r.complete_return()
            self.records.append(r)
        # Add one for a different borrower
        r2 = LendingRecord(tool_id="t0", borrower_id="b2")
        r2.approve()
        r2.activate()
        self.records.append(r2)
        self.history = BorrowerHistory(records=self.records)

    def test_get_borrower_records(self):
        assert len(self.history.get_borrower_records("b1")) == 3

    def test_get_borrow_count(self):
        assert self.history.get_borrow_count("b1") == 3

    def test_get_active_borrows(self):
        assert len(self.history.get_active_borrows("b2")) == 1

    def test_get_return_rate(self):
        rate = self.history.get_return_rate("b1")
        assert rate == 100.0

    def test_get_all_borrowers(self):
        borrowers = self.history.get_all_borrowers()
        assert set(borrowers) == {"b1", "b2"}

    def test_get_top_borrowers(self):
        top = self.history.get_top_borrowers(limit=1)
        assert top[0]["borrower_id"] == "b1"

    def test_borrower_summary(self):
        summary = self.history.get_borrower_summary("b1")
        assert summary["total_borrows"] == 3
        assert summary["return_rate"] == 100.0

    def test_reliability_score(self):
        score = self.history.calculate_reliability_score("b1")
        assert score == 100

    def test_reliability_score_new_borrower(self):
        score = self.history.calculate_reliability_score("unknown")
        assert score == 100
