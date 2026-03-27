"""Tests for AWS service wrappers."""

import pytest
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from services import (
    DynamoDBService, S3Service, LambdaService,
    CognitoService, StepFunctionsService, CloudWatchService,
    APIGatewayService,
)


class TestDynamoDBService:
    def test_put_and_get(self):
        svc = DynamoDBService(use_mock=True)
        svc.put_item("tools", {"tool_id": "t1", "name": "Hammer"})
        item = svc.get_item("tools", "tool_id", "t1")
        assert item["name"] == "Hammer"

    def test_delete(self):
        svc = DynamoDBService(use_mock=True)
        svc.put_item("tools", {"tool_id": "t1", "name": "Hammer"})
        assert svc.delete_item("tools", "tool_id", "t1") is True
        assert svc.get_item("tools", "tool_id", "t1") is None

    def test_scan(self):
        svc = DynamoDBService(use_mock=True)
        svc.put_item("tools", {"tool_id": "t1", "name": "Hammer"})
        svc.put_item("tools", {"tool_id": "t2", "name": "Drill"})
        items = svc.scan_table("tools")
        assert len(items) == 2

    def test_status(self):
        svc = DynamoDBService(use_mock=True)
        status = svc.get_status()
        assert status["service"] == "DynamoDB"
        assert status["mock_mode"] is True


class TestS3Service:
    def test_upload_and_get(self):
        svc = S3Service(use_mock=True)
        result = svc.upload_file(b"fake image data", "test.jpg")
        assert result["status"] == "success"
        assert "url" in result

    def test_delete_file(self):
        svc = S3Service(use_mock=True)
        result = svc.upload_file(b"data", "test.jpg")
        key = result["key"]
        assert svc.delete_file(key) is True

    def test_list_files(self):
        svc = S3Service(use_mock=True)
        svc.upload_file(b"data1", "img1.jpg")
        svc.upload_file(b"data2", "img2.jpg")
        files = svc.list_files()
        assert len(files) == 2

    def test_presigned_url(self):
        svc = S3Service(use_mock=True)
        url = svc.generate_presigned_url("some/key")
        assert "mock-presigned" in url


class TestLambdaService:
    def test_invoke_validation(self):
        svc = LambdaService(use_mock=True)
        result = svc.invoke("ToolValidation", {
            "tool": {"name": "Hammer", "description": "Good"}
        })
        assert result["result"]["valid"] is True

    def test_invoke_validation_fail(self):
        svc = LambdaService(use_mock=True)
        result = svc.invoke("ToolValidation", {"tool": {}})
        assert result["result"]["valid"] is False

    def test_invocation_log(self):
        svc = LambdaService(use_mock=True)
        svc.invoke("ToolValidation", {"tool": {"name": "X", "description": "Y"}})
        assert len(svc.get_invocation_log()) == 1


class TestCognitoService:
    def test_signup_and_signin(self):
        svc = CognitoService(use_mock=True)
        svc.sign_up("user1", "password123", "user1@test.com")
        result = svc.sign_in("user1", "password123")
        assert result["status"] == "success"
        assert "access_token" in result

    def test_verify_token(self):
        svc = CognitoService(use_mock=True)
        svc.sign_up("user1", "password123", "user1@test.com")
        signin = svc.sign_in("user1", "password123")
        verify = svc.verify_token(signin["access_token"])
        assert verify["valid"] is True


class TestStepFunctionsService:
    def test_start_execution(self):
        svc = StepFunctionsService(use_mock=True)
        result = svc.start_execution("LendingWorkflow", {"tool_id": "t1"})
        assert result["status"] == "success"
        assert result["current_state"] == "REQUESTED"

    def test_advance_state(self):
        svc = StepFunctionsService(use_mock=True)
        result = svc.start_execution("LendingWorkflow", {"tool_id": "t1"})
        eid = result["execution_id"]
        advance = svc.advance_state(eid)
        assert advance["current_state"] == "APPROVED"

    def test_full_workflow(self):
        svc = StepFunctionsService(use_mock=True)
        result = svc.start_execution("LendingWorkflow", {"tool_id": "t1"})
        eid = result["execution_id"]
        svc.advance_state(eid)  # APPROVED
        svc.advance_state(eid)  # ACTIVE
        final = svc.advance_state(eid)  # RETURNED
        assert final["current_state"] == "RETURNED"
        assert final["status"] == "success"


class TestCloudWatchService:
    def test_put_and_get_metric(self):
        svc = CloudWatchService(use_mock=True)
        svc.put_metric("request_count", 42)
        metrics = svc.get_metric("request_count")
        assert len(metrics) == 1
        assert metrics[0]["value"] == 42

    def test_log_event(self):
        svc = CloudWatchService(use_mock=True)
        svc.log_event("/app/logs", "Test log message")
        logs = svc.get_logs()
        assert len(logs) == 1

    def test_alarm(self):
        svc = CloudWatchService(use_mock=True)
        svc.create_alarm("high_errors", "error_count", threshold=5)
        svc.put_metric("error_count", 10)
        triggered = svc.check_alarms()
        assert len(triggered) == 1

    def test_scheduled_rules(self):
        svc = CloudWatchService(use_mock=True)
        svc.create_scheduled_rule("test_rule", "rate(1 hour)", "target")
        rules = svc.get_scheduled_rules()
        assert len(rules) == 1
