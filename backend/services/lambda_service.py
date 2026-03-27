"""Lambda service wrapper with local mock mode."""

import json
from datetime import datetime


class LambdaService:
    """Wrapper for AWS Lambda invocations.

    In mock mode, simulates Lambda function execution locally.
    """

    def __init__(self, use_mock=True, region="eu-west-1"):
        self.use_mock = use_mock
        self.region = region
        self._invocation_log = []
        self._client = None

        if not use_mock:
            try:
                import boto3
                self._client = boto3.client("lambda", region_name=region)
            except Exception:
                self.use_mock = True

        # Register mock handlers
        self._handlers = {
            "ToolValidation": self._mock_tool_validation,
            "OverdueCheck": self._mock_overdue_check,
            "NotificationSender": self._mock_notification,
            "ReportGenerator": self._mock_report_generator,
        }

    def invoke(self, function_name, payload):
        """Invoke a Lambda function."""
        self._invocation_log.append({
            "function": function_name,
            "payload": payload,
            "timestamp": datetime.utcnow().isoformat(),
        })

        if self.use_mock:
            handler = self._handlers.get(function_name, self._mock_default)
            result = handler(payload)
            return {"status": "success", "result": result, "mock": True}
        else:
            response = self._client.invoke(
                FunctionName=function_name,
                Payload=json.dumps(payload),
            )
            result = json.loads(response["Payload"].read())
            return {"status": "success", "result": result, "mock": False}

    def _mock_tool_validation(self, payload):
        """Mock tool validation Lambda."""
        tool = payload.get("tool", {})
        errors = []
        if not tool.get("name"):
            errors.append("Tool name is required")
        if not tool.get("description"):
            errors.append("Tool description is required")
        return {"valid": len(errors) == 0, "errors": errors}

    def _mock_overdue_check(self, payload):
        """Mock overdue checking Lambda."""
        return {
            "checked_at": datetime.utcnow().isoformat(),
            "overdue_count": payload.get("overdue_count", 0),
            "notifications_sent": True,
        }

    def _mock_notification(self, payload):
        """Mock notification sending Lambda."""
        return {
            "sent": True,
            "recipient": payload.get("recipient", "unknown"),
            "message_type": payload.get("type", "general"),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _mock_report_generator(self, payload):
        """Mock report generation Lambda."""
        return {
            "report_generated": True,
            "report_type": payload.get("report_type", "summary"),
            "timestamp": datetime.utcnow().isoformat(),
        }

    def _mock_default(self, payload):
        """Default mock handler."""
        return {"executed": True, "payload_received": payload}

    def get_invocation_log(self):
        """Get the invocation history."""
        return self._invocation_log

    def get_status(self):
        """Get the service status."""
        return {
            "service": "Lambda",
            "status": "running",
            "mock_mode": self.use_mock,
            "registered_functions": list(self._handlers.keys()),
            "total_invocations": len(self._invocation_log),
        }
