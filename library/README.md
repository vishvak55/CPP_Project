# toollibrary-nci

A Python library for managing community tool lending operations.

## Features

- **LoanManager** - Calculate due dates, check overdue status, late fees, borrower limits
- **ToolManager** - Validate tools, manage status flows, categorize and search tools
- **LendingFormatter** - Format loan summaries, tool cards, CSV export, overdue alerts, reports
- **InputValidator** - Validate users, tools, loan requests, sanitize input

## Installation

```bash
pip install toollibrary-nci
```

## Usage

```python
from toollibrary import LoanManager, ToolManager, LendingFormatter, InputValidator

# Calculate a due date (14 days default)
due = LoanManager.calculate_due_date(days=14)

# Check borrower limit
result = LoanManager.check_borrower_limit(user_loans, max_tools=3)

# Validate a tool
result = ToolManager.validate_tool({"name": "Drill", "category": "power_tools"})

# Search tools
matches = ToolManager.search_tools(tools, "drill")

# Format a lending report
report = LendingFormatter.format_lending_report(tools, loans)
```

## Testing

```bash
cd library
python -m pytest tests/ -v
```
