"""
lendlib - Community Tool Lending Library
A custom OOP Python library for tool inventory management,
lending period calculations, availability checking, overdue detection,
and borrower history tracking.

Author: Vishvaksen Machana (25173421)
Module: Cloud Platform Programming - NCI
"""

from .tool import Tool, ToolCategory, ToolCondition
from .user import User, UserRole
from .lending import LendingRecord, LendingStatus
from .inventory import InventoryManager
from .lending_manager import LendingManager
from .availability import AvailabilityChecker
from .overdue import OverdueDetector
from .history import BorrowerHistory

__version__ = "1.0.0"
__author__ = "Vishvaksen Machana"
__all__ = [
    "Tool", "ToolCategory", "ToolCondition",
    "User", "UserRole",
    "LendingRecord", "LendingStatus",
    "InventoryManager",
    "LendingManager",
    "AvailabilityChecker",
    "OverdueDetector",
    "BorrowerHistory",
]
