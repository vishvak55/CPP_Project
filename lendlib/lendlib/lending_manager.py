"""Lending management for the Community Tool Lending Library."""

from typing import List, Optional
from .lending import LendingRecord, LendingStatus


class LendingManager:
    """Manages lending records with full workflow support.

    Handles the lending lifecycle: request -> approve -> lend -> return.
    """

    def __init__(self):
        self._records: dict = {}  # record_id -> LendingRecord

    @property
    def count(self) -> int:
        """Return the total number of lending records."""
        return len(self._records)

    def create_lending(self, record: LendingRecord) -> LendingRecord:
        """Create a new lending record."""
        if record.record_id in self._records:
            raise ValueError(f"Record {record.record_id} already exists")
        self._records[record.record_id] = record
        return record

    def get_lending(self, record_id: str) -> Optional[LendingRecord]:
        """Get a lending record by ID."""
        return self._records.get(record_id)

    def delete_lending(self, record_id: str) -> bool:
        """Delete a lending record."""
        if record_id in self._records:
            del self._records[record_id]
            return True
        return False

    def list_lendings(self) -> List[LendingRecord]:
        """List all lending records."""
        return list(self._records.values())

    def approve_lending(self, record_id: str) -> Optional[LendingRecord]:
        """Approve a lending request."""
        record = self._records.get(record_id)
        if record:
            record.approve()
        return record

    def activate_lending(self, record_id: str) -> Optional[LendingRecord]:
        """Activate a lending (mark tool as handed over)."""
        record = self._records.get(record_id)
        if record:
            record.activate()
        return record

    def return_lending(self, record_id: str) -> Optional[LendingRecord]:
        """Mark a lending as returned."""
        record = self._records.get(record_id)
        if record:
            record.complete_return()
        return record

    def cancel_lending(self, record_id: str) -> Optional[LendingRecord]:
        """Cancel a lending request."""
        record = self._records.get(record_id)
        if record:
            record.cancel()
        return record

    def get_by_status(self, status: LendingStatus) -> List[LendingRecord]:
        """Get all lending records with a specific status."""
        return [r for r in self._records.values() if r.status == status]

    def get_by_borrower(self, borrower_id: str) -> List[LendingRecord]:
        """Get all lending records for a specific borrower."""
        return [r for r in self._records.values() if r.borrower_id == borrower_id]

    def get_by_tool(self, tool_id: str) -> List[LendingRecord]:
        """Get all lending records for a specific tool."""
        return [r for r in self._records.values() if r.tool_id == tool_id]

    def get_active_lendings(self) -> List[LendingRecord]:
        """Get all currently active lendings."""
        return self.get_by_status(LendingStatus.ACTIVE)

    def get_overdue_lendings(self) -> List[LendingRecord]:
        """Get all overdue lendings."""
        overdue = self.get_by_status(LendingStatus.OVERDUE)
        # Also check active ones that have become overdue
        for record in self.get_active_lendings():
            if record.is_overdue():
                record.mark_overdue()
                overdue.append(record)
        return overdue

    def get_statistics(self) -> dict:
        """Get lending statistics."""
        records = list(self._records.values())
        return {
            "total_records": len(records),
            "by_status": {
                status.value: sum(1 for r in records if r.status == status)
                for status in LendingStatus
                if any(r.status == status for r in records)
            },
            "active": sum(1 for r in records if r.status == LendingStatus.ACTIVE),
            "overdue": sum(1 for r in records if r.status == LendingStatus.OVERDUE),
            "completed": sum(1 for r in records if r.status == LendingStatus.RETURNED),
        }
