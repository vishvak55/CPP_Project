"""Overdue detection for the Community Tool Lending Library."""

from typing import List
from datetime import datetime
from .lending import LendingRecord, LendingStatus
from .user import User


class OverdueDetector:
    """Detects and manages overdue lending records.

    Scans active lendings to identify overdue items and
    calculates penalties/trust score adjustments.
    """

    PENALTY_PER_DAY = 2  # Trust score penalty per overdue day

    def __init__(self, records: List[LendingRecord] = None,
                 users: List[User] = None):
        self._records = records or []
        self._users = {u.user_id: u for u in (users or [])}

    def set_records(self, records: List[LendingRecord]):
        """Set the lending records to check."""
        self._records = records

    def set_users(self, users: List[User]):
        """Set the users for trust score adjustments."""
        self._users = {u.user_id: u for u in users}

    def scan_overdue(self) -> List[LendingRecord]:
        """Scan all active records and identify overdue ones."""
        overdue = []
        for record in self._records:
            if record.status == LendingStatus.ACTIVE and record.is_overdue():
                record.mark_overdue()
                overdue.append(record)
            elif record.status == LendingStatus.OVERDUE:
                overdue.append(record)
        return overdue

    def get_overdue_count(self) -> int:
        """Get the number of overdue records."""
        return len(self.scan_overdue())

    def calculate_penalty(self, record: LendingRecord) -> int:
        """Calculate the trust score penalty for an overdue record."""
        days = record.days_overdue()
        return days * self.PENALTY_PER_DAY

    def apply_penalties(self) -> List[dict]:
        """Apply trust score penalties for all overdue records."""
        results = []
        for record in self.scan_overdue():
            penalty = self.calculate_penalty(record)
            user = self._users.get(record.borrower_id)
            if user and penalty > 0:
                user.adjust_trust_score(-penalty)
                results.append({
                    "record_id": record.record_id,
                    "borrower_id": record.borrower_id,
                    "days_overdue": record.days_overdue(),
                    "penalty": penalty,
                    "new_trust_score": user.trust_score,
                })
        return results

    def get_overdue_summary(self) -> dict:
        """Get summary of all overdue items."""
        overdue = self.scan_overdue()
        total_days = sum(r.days_overdue() for r in overdue)
        return {
            "overdue_count": len(overdue),
            "total_overdue_days": total_days,
            "average_overdue_days": round(total_days / len(overdue), 1) if overdue else 0,
            "records": [r.to_dict() for r in overdue],
        }

    def get_worst_offenders(self, limit: int = 5) -> List[dict]:
        """Get borrowers with the most overdue items."""
        overdue = self.scan_overdue()
        borrower_counts = {}
        for r in overdue:
            if r.borrower_id not in borrower_counts:
                borrower_counts[r.borrower_id] = {"count": 0, "total_days": 0}
            borrower_counts[r.borrower_id]["count"] += 1
            borrower_counts[r.borrower_id]["total_days"] += r.days_overdue()

        sorted_offenders = sorted(
            borrower_counts.items(),
            key=lambda x: x[1]["total_days"],
            reverse=True
        )
        return [
            {"borrower_id": bid, **data}
            for bid, data in sorted_offenders[:limit]
        ]
