"""
Loan management for the ToolShare lending library.
Handles due dates, overdue checks, late fees, borrower limits, and loan validation.
"""

from datetime import datetime, timedelta


class LoanManager:
    """Manages tool lending loan operations."""

    @staticmethod
    def calculate_due_date(days=14):
        """Calculate the due date from today plus the given number of days."""
        if not isinstance(days, (int, float)) or days <= 0:
            raise ValueError("Loan period must be a positive number")
        due = datetime.utcnow() + timedelta(days=int(days))
        return due.strftime("%Y-%m-%d")

    @staticmethod
    def check_overdue(loan):
        """Check whether a loan is overdue. Returns True if past due date."""
        if not loan or "dueDate" not in loan:
            raise ValueError("Loan must contain a dueDate field")
        due_date = datetime.strptime(loan["dueDate"], "%Y-%m-%d")
        return datetime.utcnow() > due_date

    @staticmethod
    def calculate_late_fee(loan, fee_per_day=2.0):
        """Calculate the late fee for an overdue loan."""
        if not loan or "dueDate" not in loan:
            raise ValueError("Loan must contain a dueDate field")
        if fee_per_day < 0:
            raise ValueError("Fee per day cannot be negative")
        due_date = datetime.strptime(loan["dueDate"], "%Y-%m-%d")
        now = datetime.utcnow()
        if now <= due_date:
            return 0.0
        days_late = (now - due_date).days
        return round(days_late * fee_per_day, 2)

    @staticmethod
    def validate_loan(data):
        """Validate loan data contains all required fields."""
        errors = []
        required = ["toolId", "userId"]
        for field in required:
            if field not in data or not str(data[field]).strip():
                errors.append(f"Missing required field: {field}")
        if "days" in data:
            try:
                days = int(data["days"])
                if days <= 0:
                    errors.append("Loan days must be a positive number")
                if days > 90:
                    errors.append("Loan period cannot exceed 90 days")
            except (ValueError, TypeError):
                errors.append("Loan days must be a valid number")
        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def check_borrower_limit(user_loans, max_tools=3):
        """Check if a borrower has reached their active loan limit."""
        if not isinstance(user_loans, list):
            raise ValueError("user_loans must be a list")
        active = [l for l in user_loans if l.get("status") == "active"]
        return {
            "allowed": len(active) < max_tools,
            "active_count": len(active),
            "max_tools": max_tools,
            "remaining": max(0, max_tools - len(active)),
        }

    @staticmethod
    def get_loan_status(loan):
        """Determine the current status of a loan."""
        if not loan:
            raise ValueError("Loan data is required")
        if loan.get("returnedDate"):
            due = datetime.strptime(loan["dueDate"], "%Y-%m-%d")
            returned = datetime.strptime(loan["returnedDate"], "%Y-%m-%d")
            if returned > due:
                return "returned_late"
            return "returned"
        if "dueDate" in loan:
            due = datetime.strptime(loan["dueDate"], "%Y-%m-%d")
            if datetime.utcnow() > due:
                return "overdue"
        return "active"
