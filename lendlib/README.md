# lendlib - Community Tool Lending Library

Custom OOP Python library for managing a community tool lending system.

## Features

- **Tool Inventory Management**: CRUD operations, search, filtering by category/condition
- **Lending Period Calculations**: Configurable lending periods, due date computation
- **Availability Checking**: Real-time tool availability, borrower eligibility checks
- **Overdue Detection**: Automatic overdue scanning, penalty calculations
- **Borrower History Tracking**: Usage stats, reliability scoring, pattern analysis

## Installation

```bash
pip install -e .
```

## Usage

```python
from lendlib import Tool, User, LendingRecord, InventoryManager

# Create inventory
inventory = InventoryManager()
tool = Tool(name="Hammer", description="Claw hammer", category=ToolCategory.HAND_TOOL)
inventory.add_tool(tool)

# Check availability
checker = AvailabilityChecker(tools=inventory.list_tools())
print(checker.is_tool_available(tool.tool_id))
```

## Author

Vishvaksen Machana (25173421) - NCI Cloud Platform Programming
