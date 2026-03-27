"""
Input validation for the ToolShare lending library.
Validates users, tools, loan requests, and sanitizes input.
"""

import re


class InputValidator:
    """Validates and sanitizes input data for the lending library."""

    @staticmethod
    def validate_user(data):
        """Validate user registration/profile data."""
        errors = []
        if not data:
            return {"valid": False, "errors": ["No data provided"]}
        if "name" not in data or not str(data["name"]).strip():
            errors.append("Name is required")
        elif len(str(data["name"])) > 100:
            errors.append("Name cannot exceed 100 characters")
        if "email" not in data or not str(data["email"]).strip():
            errors.append("Email is required")
        else:
            email = str(data["email"]).strip()
            pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
            if not re.match(pattern, email):
                errors.append("Invalid email format")
        if "password" in data:
            pwd = str(data["password"])
            if len(pwd) < 8:
                errors.append("Password must be at least 8 characters")
            if not re.search(r"[A-Z]", pwd):
                errors.append("Password must contain an uppercase letter")
            if not re.search(r"[0-9]", pwd):
                errors.append("Password must contain a number")
        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_tool_data(data):
        """Validate tool creation/update data."""
        errors = []
        if not data:
            return {"valid": False, "errors": ["No data provided"]}
        if "name" not in data or not str(data["name"]).strip():
            errors.append("Tool name is required")
        elif len(str(data["name"])) > 200:
            errors.append("Tool name cannot exceed 200 characters")
        valid_categories = [
            "power_tools", "hand_tools", "garden", "ladders",
            "cleaning", "kitchen", "other"
        ]
        if "category" not in data or not str(data["category"]).strip():
            errors.append("Category is required")
        elif data["category"] not in valid_categories:
            errors.append(f"Invalid category. Must be one of: {', '.join(valid_categories)}")
        if "description" in data and len(str(data["description"])) > 1000:
            errors.append("Description cannot exceed 1000 characters")
        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def validate_loan_request(data):
        """Validate a loan/borrow request."""
        errors = []
        if not data:
            return {"valid": False, "errors": ["No data provided"]}
        if "toolId" not in data or not str(data["toolId"]).strip():
            errors.append("Tool ID is required")
        if "userId" not in data or not str(data["userId"]).strip():
            errors.append("User ID is required")
        if "days" in data:
            try:
                days = int(data["days"])
                if days <= 0:
                    errors.append("Loan days must be positive")
                elif days > 90:
                    errors.append("Maximum loan period is 90 days")
            except (ValueError, TypeError):
                errors.append("Loan days must be a valid number")
        return {"valid": len(errors) == 0, "errors": errors}

    @staticmethod
    def sanitize_input(text):
        """Sanitize user input by removing dangerous characters."""
        if text is None:
            return ""
        text = str(text).strip()
        text = text.replace("<", "&lt;").replace(">", "&gt;")
        text = text.replace("'", "&#39;").replace('"', "&quot;")
        text = re.sub(r"[;\-]{2,}", "", text)
        return text
