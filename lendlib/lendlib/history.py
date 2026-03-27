"""Borrower history tracking for the Community Tool Lending Library."""

from typing import List, Optional
from datetime import datetime
from .lending import LendingRecord, LendingStatus


class BorrowerHistory:
    """Tracks and analyzes borrower lending history.

    Provides insights into borrowing patterns, reliability,
    and usage statistics for individual borrowers.
    """

    def __init__(self, records: List[LendingRecord] = None):
        self._records = records or []

    def set_records(self, records: List[LendingRecord]):
        """Set the lending records to analyze."""
        self._records = records

    def get_borrower_records(self, borrower_id: str) -> List[LendingRecord]:
        """Get all lending records for a specific borrower."""
        return [r for r in self._records if r.borrower_id == borrower_id]

    def get_active_borrows(self, borrower_id: str) -> List[LendingRecord]:
        """Get currently active borrows for a borrower."""
        active_statuses = {LendingStatus.ACTIVE, LendingStatus.APPROVED}
        return [
            r for r in self._records
            if r.borrower_id == borrower_id and r.status in active_statuses
        ]

    def get_borrow_count(self, borrower_id: str) -> int:
        """Get total number of borrows for a borrower."""
        return len(self.get_borrower_records(borrower_id))

    def get_return_rate(self, borrower_id: str) -> float:
        """Calculate the on-time return rate for a borrower (0-100%)."""
        records = self.get_borrower_records(borrower_id)
        completed = [r for r in records if r.status == LendingStatus.RETURNED]
        if not completed:
            return 100.0
        on_time = sum(
            1 for r in completed
            if r.returned_at and r.due_date and r.returned_at <= r.due_date
        )
        return round(on_time / len(completed) * 100, 1)

    def get_overdue_count(self, borrower_id: str) -> int:
        """Get number of overdue records for a borrower."""
        return sum(
            1 for r in self.get_borrower_records(borrower_id)
            if r.status == LendingStatus.OVERDUE
        )

    def get_most_borrowed_tools(self, borrower_id: str, limit: int = 5) -> List[dict]:
        """Get the most frequently borrowed tools by a borrower."""
        records = self.get_borrower_records(borrower_id)
        tool_counts = {}
        for r in records:
            tool_counts[r.tool_id] = tool_counts.get(r.tool_id, 0) + 1
        sorted_tools = sorted(tool_counts.items(), key=lambda x: x[1], reverse=True)
        return [
            {"tool_id": tid, "borrow_count": count}
            for tid, count in sorted_tools[:limit]
        ]

    def get_borrower_summary(self, borrower_id: str) -> dict:
        """Get a complete borrowing summary for a borrower."""
        records = self.get_borrower_records(borrower_id)
        return {
            "borrower_id": borrower_id,
            "total_borrows": len(records),
            "active_borrows": len(self.get_active_borrows(borrower_id)),
            "overdue_count": self.get_overdue_count(borrower_id),
            "return_rate": self.get_return_rate(borrower_id),
            "most_borrowed": self.get_most_borrowed_tools(borrower_id),
            "status_breakdown": {
                status.value: sum(1 for r in records if r.status == status)
                for status in LendingStatus
                if any(r.status == status for r in records)
            },
        }

    def get_all_borrowers(self) -> List[str]:
        """Get list of all unique borrower IDs."""
        return list(set(r.borrower_id for r in self._records))

    def get_top_borrowers(self, limit: int = 10) -> List[dict]:
        """Get the most active borrowers."""
        borrower_ids = self.get_all_borrowers()
        summaries = [
            {"borrower_id": bid, "total_borrows": self.get_borrow_count(bid)}
            for bid in borrower_ids
        ]
        return sorted(summaries, key=lambda x: x["total_borrows"], reverse=True)[:limit]

    def calculate_reliability_score(self, borrower_id: str) -> int:
        """Calculate a reliability score (0-100) based on history."""
        records = self.get_borrower_records(borrower_id)
        if not records:
            return 100  # New borrower starts with full score

        score = 100
        completed = [r for r in records if r.status == LendingStatus.RETURNED]

        # Penalty for overdue returns
        for r in completed:
            if r.returned_at and r.due_date and r.returned_at > r.due_date:
                days_late = (r.returned_at - r.due_date).days
                score -= min(days_late * 2, 20)

        # Penalty for currently overdue
        overdue_count = self.get_overdue_count(borrower_id)
        score -= overdue_count * 10

        # Bonus for consistent on-time returns
        if len(completed) >= 5:
            rate = self.get_return_rate(borrower_id)
            if rate >= 95:
                score += 5

        return max(0, min(100, score))
