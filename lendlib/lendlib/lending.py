"""Lending record model for the Community Tool Lending Library."""

from enum import Enum
from datetime import datetime, timedelta
import uuid


class LendingStatus(Enum):
    """Status of a lending record."""
    REQUESTED = "requested"
    APPROVED = "approved"
    ACTIVE = "active"
    RETURNED = "returned"
    OVERDUE = "overdue"
    CANCELLED = "cancelled"


class LendingRecord:
    """Represents a lending transaction in the community tool library.

    Attributes:
        record_id: Unique identifier for the lending record.
        tool_id: ID of the tool being lent.
        borrower_id: ID of the borrower.
        lender_id: ID of the tool owner/lender.
        status: Current lending status.
        requested_at: When the lending was requested.
        approved_at: When the lending was approved.
        lent_at: When the tool was physically handed over.
        due_date: When the tool is due to be returned.
        returned_at: When the tool was actually returned.
        lending_days: Number of days for the lending period.
        notes: Additional notes about the lending.
    """

    def __init__(self, tool_id: str, borrower_id: str, lender_id: str = None,
                 lending_days: int = 7, notes: str = None, record_id: str = None):
        self.record_id = record_id or str(uuid.uuid4())
        self.tool_id = tool_id
        self.borrower_id = borrower_id
        self.lender_id = lender_id
        self.status = LendingStatus.REQUESTED
        self.requested_at = datetime.utcnow()
        self.approved_at = None
        self.lent_at = None
        self.due_date = None
        self.returned_at = None
        self.lending_days = lending_days
        self.notes = notes

    def to_dict(self) -> dict:
        """Convert lending record to dictionary representation."""
        return {
            "record_id": self.record_id,
            "tool_id": self.tool_id,
            "borrower_id": self.borrower_id,
            "lender_id": self.lender_id,
            "status": self.status.value,
            "requested_at": self.requested_at.isoformat() if self.requested_at else None,
            "approved_at": self.approved_at.isoformat() if self.approved_at else None,
            "lent_at": self.lent_at.isoformat() if self.lent_at else None,
            "due_date": self.due_date.isoformat() if self.due_date else None,
            "returned_at": self.returned_at.isoformat() if self.returned_at else None,
            "lending_days": self.lending_days,
            "notes": self.notes,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "LendingRecord":
        """Create a LendingRecord from a dictionary."""
        record = cls(
            tool_id=data["tool_id"],
            borrower_id=data["borrower_id"],
            lender_id=data.get("lender_id"),
            lending_days=data.get("lending_days", 7),
            notes=data.get("notes"),
            record_id=data.get("record_id"),
        )
        record.status = LendingStatus(data.get("status", "requested"))
        for field in ("requested_at", "approved_at", "lent_at", "due_date", "returned_at"):
            val = data.get(field)
            if val and isinstance(val, str):
                setattr(record, field, datetime.fromisoformat(val))
        return record

    def approve(self):
        """Approve the lending request."""
        if self.status != LendingStatus.REQUESTED:
            raise ValueError(f"Cannot approve lending in status {self.status.value}")
        self.status = LendingStatus.APPROVED
        self.approved_at = datetime.utcnow()

    def activate(self):
        """Mark the tool as handed over (active lending)."""
        if self.status != LendingStatus.APPROVED:
            raise ValueError(f"Cannot activate lending in status {self.status.value}")
        self.status = LendingStatus.ACTIVE
        self.lent_at = datetime.utcnow()
        self.due_date = self.lent_at + timedelta(days=self.lending_days)

    def complete_return(self):
        """Mark the tool as returned."""
        if self.status not in (LendingStatus.ACTIVE, LendingStatus.OVERDUE):
            raise ValueError(f"Cannot return lending in status {self.status.value}")
        self.status = LendingStatus.RETURNED
        self.returned_at = datetime.utcnow()

    def mark_overdue(self):
        """Mark the lending as overdue."""
        if self.status != LendingStatus.ACTIVE:
            raise ValueError(f"Cannot mark overdue for status {self.status.value}")
        self.status = LendingStatus.OVERDUE

    def cancel(self):
        """Cancel the lending request."""
        if self.status in (LendingStatus.RETURNED, LendingStatus.CANCELLED):
            raise ValueError(f"Cannot cancel lending in status {self.status.value}")
        self.status = LendingStatus.CANCELLED

    def is_overdue(self) -> bool:
        """Check if the lending is past the due date."""
        if self.status == LendingStatus.OVERDUE:
            return True
        if self.status == LendingStatus.ACTIVE and self.due_date:
            return datetime.utcnow() > self.due_date
        return False

    def days_remaining(self) -> int:
        """Calculate days remaining until due date. Negative if overdue."""
        if not self.due_date:
            return self.lending_days
        delta = self.due_date - datetime.utcnow()
        return delta.days

    def days_overdue(self) -> int:
        """Calculate how many days the tool is overdue. 0 if not overdue."""
        if not self.due_date:
            return 0
        delta = datetime.utcnow() - self.due_date
        return max(0, delta.days)

    def calculate_lending_period(self) -> timedelta:
        """Calculate the total lending period."""
        return timedelta(days=self.lending_days)

    def __repr__(self):
        return (f"LendingRecord(tool={self.tool_id[:8]}, "
                f"borrower={self.borrower_id[:8]}, status={self.status.value})")

    def __eq__(self, other):
        if not isinstance(other, LendingRecord):
            return False
        return self.record_id == other.record_id
