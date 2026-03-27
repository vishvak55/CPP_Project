"""
Formatting utilities for the ToolShare lending library.
Handles loan summaries, tool cards, CSV export, alerts, and reports.
"""

from datetime import datetime


class LendingFormatter:
    """Formats lending data for display and export."""

    @staticmethod
    def format_loan_summary(loan):
        """Format a single loan into a human-readable summary."""
        if not loan:
            raise ValueError("Loan data is required")
        tool_name = loan.get("toolName", "Unknown Tool")
        borrower = loan.get("userName", "Unknown User")
        borrow_date = loan.get("borrowDate", "N/A")
        due_date = loan.get("dueDate", "N/A")
        status = loan.get("status", "unknown")
        lines = [
            f"Loan Summary",
            f"{'='*40}",
            f"Tool:       {tool_name}",
            f"Borrower:   {borrower}",
            f"Borrowed:   {borrow_date}",
            f"Due Date:   {due_date}",
            f"Status:     {status.upper()}",
        ]
        if loan.get("returnedDate"):
            lines.append(f"Returned:   {loan['returnedDate']}")
        if loan.get("lateFee"):
            lines.append(f"Late Fee:   ${loan['lateFee']:.2f}")
        return "\n".join(lines)

    @staticmethod
    def format_tool_card(tool):
        """Format a tool into a display card string."""
        if not tool:
            raise ValueError("Tool data is required")
        name = tool.get("name", "Unknown")
        category = tool.get("category", "other").replace("_", " ").title()
        condition = tool.get("condition", "N/A").title()
        status = tool.get("status", "unknown")
        status_icon = {"ready": "[AVAILABLE]", "loaned": "[ON LOAN]", "under_repair": "[REPAIR]"}
        icon = status_icon.get(status, "[UNKNOWN]")
        lines = [
            f"{icon} {name}",
            f"  Category:  {category}",
            f"  Condition: {condition}",
        ]
        if tool.get("description"):
            lines.append(f"  Details:   {tool['description']}")
        return "\n".join(lines)

    @staticmethod
    def to_csv(items, fields):
        """Convert a list of dicts to CSV format string."""
        if not fields:
            raise ValueError("Fields list is required")
        if not isinstance(items, list):
            raise ValueError("Items must be a list")
        lines = [",".join(fields)]
        for item in items:
            row = []
            for f in fields:
                val = str(item.get(f, ""))
                if "," in val or '"' in val:
                    val = f'"{val}"'
                row.append(val)
            lines.append(",".join(row))
        return "\n".join(lines)

    @staticmethod
    def format_overdue_alert(loan):
        """Format an overdue loan alert message."""
        if not loan:
            raise ValueError("Loan data is required")
        tool_name = loan.get("toolName", "Unknown Tool")
        borrower = loan.get("userName", "Unknown User")
        due_date = loan.get("dueDate", "N/A")
        try:
            due = datetime.strptime(due_date, "%Y-%m-%d")
            days_late = (datetime.utcnow() - due).days
        except (ValueError, TypeError):
            days_late = 0
        return (
            f"OVERDUE ALERT: '{tool_name}' borrowed by {borrower} "
            f"was due on {due_date} ({days_late} days late)"
        )

    @staticmethod
    def format_lending_report(tools, loans):
        """Generate a full lending report from tools and loans data."""
        if not isinstance(tools, list) or not isinstance(loans, list):
            raise ValueError("Tools and loans must be lists")
        total_tools = len(tools)
        available = len([t for t in tools if t.get("status") == "ready"])
        on_loan = len([t for t in tools if t.get("status") == "loaned"])
        in_repair = len([t for t in tools if t.get("status") == "under_repair"])
        active_loans = [l for l in loans if l.get("status") == "active"]
        overdue = []
        for loan in active_loans:
            try:
                due = datetime.strptime(loan.get("dueDate", ""), "%Y-%m-%d")
                if datetime.utcnow() > due:
                    overdue.append(loan)
            except (ValueError, TypeError):
                pass
        lines = [
            "ToolShare Lending Report",
            f"Generated: {datetime.utcnow().strftime('%Y-%m-%d %H:%M')} UTC",
            "=" * 50,
            f"Total Tools:     {total_tools}",
            f"Available:       {available}",
            f"On Loan:         {on_loan}",
            f"Under Repair:    {in_repair}",
            f"Active Loans:    {len(active_loans)}",
            f"Overdue Loans:   {len(overdue)}",
            "=" * 50,
        ]
        if overdue:
            lines.append("\nOverdue Items:")
            for loan in overdue:
                lines.append(f"  - {loan.get('toolName', 'Unknown')}: due {loan.get('dueDate', 'N/A')}")
        return "\n".join(lines)
