"""
Tests for the toollibrary package.
30+ tests covering LoanManager, ToolManager, LendingFormatter, and InputValidator.
"""

import unittest
from datetime import datetime, timedelta
from toollibrary.loan import LoanManager
from toollibrary.tool import ToolManager
from toollibrary.formatter import LendingFormatter
from toollibrary.validator import InputValidator


class TestLoanManager(unittest.TestCase):
    """Tests for LoanManager."""

    def test_calculate_due_date_default(self):
        due = LoanManager.calculate_due_date()
        expected = (datetime.utcnow() + timedelta(days=14)).strftime("%Y-%m-%d")
        self.assertEqual(due, expected)

    def test_calculate_due_date_custom(self):
        due = LoanManager.calculate_due_date(days=7)
        expected = (datetime.utcnow() + timedelta(days=7)).strftime("%Y-%m-%d")
        self.assertEqual(due, expected)

    def test_calculate_due_date_invalid(self):
        with self.assertRaises(ValueError):
            LoanManager.calculate_due_date(days=-1)

    def test_check_overdue_true(self):
        loan = {"dueDate": "2020-01-01"}
        self.assertTrue(LoanManager.check_overdue(loan))

    def test_check_overdue_false(self):
        future = (datetime.utcnow() + timedelta(days=30)).strftime("%Y-%m-%d")
        loan = {"dueDate": future}
        self.assertFalse(LoanManager.check_overdue(loan))

    def test_check_overdue_missing_field(self):
        with self.assertRaises(ValueError):
            LoanManager.check_overdue({})

    def test_calculate_late_fee_not_late(self):
        future = (datetime.utcnow() + timedelta(days=10)).strftime("%Y-%m-%d")
        loan = {"dueDate": future}
        self.assertEqual(LoanManager.calculate_late_fee(loan), 0.0)

    def test_calculate_late_fee_overdue(self):
        past = (datetime.utcnow() - timedelta(days=5)).strftime("%Y-%m-%d")
        loan = {"dueDate": past}
        fee = LoanManager.calculate_late_fee(loan, fee_per_day=2.0)
        self.assertEqual(fee, 10.0)

    def test_validate_loan_valid(self):
        result = LoanManager.validate_loan({"toolId": "t1", "userId": "u1"})
        self.assertTrue(result["valid"])

    def test_validate_loan_missing_fields(self):
        result = LoanManager.validate_loan({})
        self.assertFalse(result["valid"])
        self.assertEqual(len(result["errors"]), 2)

    def test_validate_loan_excessive_days(self):
        result = LoanManager.validate_loan({"toolId": "t1", "userId": "u1", "days": 100})
        self.assertFalse(result["valid"])

    def test_check_borrower_limit_allowed(self):
        loans = [{"status": "active"}, {"status": "active"}]
        result = LoanManager.check_borrower_limit(loans, max_tools=3)
        self.assertTrue(result["allowed"])
        self.assertEqual(result["remaining"], 1)

    def test_check_borrower_limit_exceeded(self):
        loans = [{"status": "active"}] * 3
        result = LoanManager.check_borrower_limit(loans, max_tools=3)
        self.assertFalse(result["allowed"])

    def test_get_loan_status_active(self):
        future = (datetime.utcnow() + timedelta(days=5)).strftime("%Y-%m-%d")
        loan = {"dueDate": future}
        self.assertEqual(LoanManager.get_loan_status(loan), "active")

    def test_get_loan_status_overdue(self):
        loan = {"dueDate": "2020-01-01"}
        self.assertEqual(LoanManager.get_loan_status(loan), "overdue")

    def test_get_loan_status_returned(self):
        loan = {"dueDate": "2025-12-01", "returnedDate": "2025-11-30"}
        self.assertEqual(LoanManager.get_loan_status(loan), "returned")

    def test_get_loan_status_returned_late(self):
        loan = {"dueDate": "2025-01-01", "returnedDate": "2025-01-10"}
        self.assertEqual(LoanManager.get_loan_status(loan), "returned_late")


class TestToolManager(unittest.TestCase):
    """Tests for ToolManager."""

    def test_validate_tool_valid(self):
        result = ToolManager.validate_tool({"name": "Drill", "category": "power_tools"})
        self.assertTrue(result["valid"])

    def test_validate_tool_missing_name(self):
        result = ToolManager.validate_tool({"category": "power_tools"})
        self.assertFalse(result["valid"])

    def test_validate_tool_invalid_category(self):
        result = ToolManager.validate_tool({"name": "Drill", "category": "weapons"})
        self.assertFalse(result["valid"])

    def test_validate_tool_invalid_status(self):
        result = ToolManager.validate_tool({"name": "X", "category": "other", "status": "lost"})
        self.assertFalse(result["valid"])

    def test_get_tool_status_flow(self):
        flow = ToolManager.get_tool_status_flow()
        self.assertIn("ready", flow)
        self.assertIn("loaned", flow["ready"])
        self.assertIn("under_repair", flow["ready"])

    def test_validate_status_transition_valid(self):
        result = ToolManager.validate_status_transition("ready", "loaned")
        self.assertTrue(result["valid"])

    def test_validate_status_transition_invalid(self):
        result = ToolManager.validate_status_transition("loaned", "under_repair")
        self.assertFalse(result["valid"])

    def test_categorize_tools(self):
        tools = [
            {"name": "Drill", "category": "power_tools"},
            {"name": "Hammer", "category": "hand_tools"},
            {"name": "Saw", "category": "power_tools"},
        ]
        cats = ToolManager.categorize_tools(tools)
        self.assertEqual(len(cats["power_tools"]), 2)
        self.assertEqual(len(cats["hand_tools"]), 1)

    def test_search_tools_by_name(self):
        tools = [{"name": "Drill"}, {"name": "Hammer"}, {"name": "Drill Press"}]
        results = ToolManager.search_tools(tools, "drill")
        self.assertEqual(len(results), 2)

    def test_search_tools_empty_query(self):
        tools = [{"name": "A"}, {"name": "B"}]
        results = ToolManager.search_tools(tools, "")
        self.assertEqual(len(results), 2)


class TestLendingFormatter(unittest.TestCase):
    """Tests for LendingFormatter."""

    def test_format_loan_summary(self):
        loan = {
            "toolName": "Drill", "userName": "Alice",
            "borrowDate": "2025-01-01", "dueDate": "2025-01-15", "status": "active"
        }
        result = LendingFormatter.format_loan_summary(loan)
        self.assertIn("Drill", result)
        self.assertIn("Alice", result)

    def test_format_tool_card(self):
        tool = {"name": "Ladder", "category": "ladders", "condition": "good", "status": "ready"}
        result = LendingFormatter.format_tool_card(tool)
        self.assertIn("[AVAILABLE]", result)
        self.assertIn("Ladder", result)

    def test_to_csv(self):
        items = [{"name": "Drill", "status": "ready"}, {"name": "Saw", "status": "loaned"}]
        csv = LendingFormatter.to_csv(items, ["name", "status"])
        lines = csv.split("\n")
        self.assertEqual(lines[0], "name,status")
        self.assertEqual(len(lines), 3)

    def test_to_csv_empty(self):
        csv = LendingFormatter.to_csv([], ["name"])
        self.assertEqual(csv, "name")

    def test_format_overdue_alert(self):
        loan = {"toolName": "Drill", "userName": "Bob", "dueDate": "2020-01-01"}
        result = LendingFormatter.format_overdue_alert(loan)
        self.assertIn("OVERDUE ALERT", result)
        self.assertIn("Drill", result)

    def test_format_lending_report(self):
        tools = [
            {"status": "ready"}, {"status": "loaned"}, {"status": "under_repair"}
        ]
        loans = [{"status": "active", "dueDate": "2020-01-01"}]
        report = LendingFormatter.format_lending_report(tools, loans)
        self.assertIn("Total Tools:     3", report)
        self.assertIn("Available:       1", report)


class TestInputValidator(unittest.TestCase):
    """Tests for InputValidator."""

    def test_validate_user_valid(self):
        data = {"name": "Alice", "email": "alice@test.com", "password": "Pass1234"}
        result = InputValidator.validate_user(data)
        self.assertTrue(result["valid"])

    def test_validate_user_bad_email(self):
        data = {"name": "Alice", "email": "not-an-email"}
        result = InputValidator.validate_user(data)
        self.assertFalse(result["valid"])

    def test_validate_user_weak_password(self):
        data = {"name": "Alice", "email": "a@b.com", "password": "short"}
        result = InputValidator.validate_user(data)
        self.assertFalse(result["valid"])

    def test_validate_user_no_data(self):
        result = InputValidator.validate_user(None)
        self.assertFalse(result["valid"])

    def test_validate_tool_data_valid(self):
        data = {"name": "Drill", "category": "power_tools"}
        result = InputValidator.validate_tool_data(data)
        self.assertTrue(result["valid"])

    def test_validate_tool_data_missing(self):
        result = InputValidator.validate_tool_data({})
        self.assertFalse(result["valid"])

    def test_validate_loan_request_valid(self):
        data = {"toolId": "t1", "userId": "u1", "days": 7}
        result = InputValidator.validate_loan_request(data)
        self.assertTrue(result["valid"])

    def test_validate_loan_request_invalid_days(self):
        data = {"toolId": "t1", "userId": "u1", "days": -5}
        result = InputValidator.validate_loan_request(data)
        self.assertFalse(result["valid"])

    def test_sanitize_input_html(self):
        result = InputValidator.sanitize_input("<script>alert('xss')</script>")
        self.assertNotIn("<script>", result)

    def test_sanitize_input_none(self):
        result = InputValidator.sanitize_input(None)
        self.assertEqual(result, "")


if __name__ == "__main__":
    unittest.main()
