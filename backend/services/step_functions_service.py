"""Step Functions service wrapper with local mock mode."""

import uuid
from datetime import datetime


class StepFunctionsService:
    """Wrapper for AWS Step Functions workflow orchestration.

    Manages the lending workflow: request -> approve -> lend -> return.
    In mock mode, simulates state machine execution locally.
    """

    WORKFLOW_STATES = ["REQUESTED", "APPROVED", "ACTIVE", "RETURNED"]

    def __init__(self, use_mock=True, region="eu-west-1"):
        self.use_mock = use_mock
        self.region = region
        self._executions = {}
        self._client = None

        if not use_mock:
            try:
                import boto3
                self._client = boto3.client("stepfunctions", region_name=region)
            except Exception:
                self.use_mock = True

    def start_execution(self, workflow_name, input_data):
        """Start a new workflow execution."""
        execution_id = str(uuid.uuid4())

        if self.use_mock:
            self._executions[execution_id] = {
                "execution_id": execution_id,
                "workflow_name": workflow_name,
                "input": input_data,
                "current_state": "REQUESTED",
                "state_history": [{
                    "state": "REQUESTED",
                    "timestamp": datetime.utcnow().isoformat(),
                }],
                "status": "RUNNING",
                "started_at": datetime.utcnow().isoformat(),
            }
            return {
                "status": "success",
                "execution_id": execution_id,
                "current_state": "REQUESTED",
            }
        else:
            import json
            response = self._client.start_execution(
                stateMachineArn=f"arn:aws:states:{self.region}:123456789:stateMachine:{workflow_name}",
                input=json.dumps(input_data),
            )
            return {"status": "success", "execution_id": response["executionArn"]}

    def advance_state(self, execution_id):
        """Advance the workflow to the next state."""
        if self.use_mock:
            execution = self._executions.get(execution_id)
            if not execution:
                return {"status": "error", "message": "Execution not found"}

            current = execution["current_state"]
            idx = self.WORKFLOW_STATES.index(current)

            if idx >= len(self.WORKFLOW_STATES) - 1:
                execution["status"] = "COMPLETED"
                return {
                    "status": "completed",
                    "execution_id": execution_id,
                    "final_state": current,
                }

            next_state = self.WORKFLOW_STATES[idx + 1]
            execution["current_state"] = next_state
            execution["state_history"].append({
                "state": next_state,
                "timestamp": datetime.utcnow().isoformat(),
            })

            if next_state == "RETURNED":
                execution["status"] = "COMPLETED"

            return {
                "status": "success",
                "execution_id": execution_id,
                "previous_state": current,
                "current_state": next_state,
            }
        return {"status": "error", "message": "Not supported in production mode"}

    def get_execution(self, execution_id):
        """Get execution details."""
        if self.use_mock:
            return self._executions.get(execution_id)
        return None

    def list_executions(self):
        """List all executions."""
        if self.use_mock:
            return list(self._executions.values())
        return []

    def get_workflow_definition(self):
        """Get the state machine definition."""
        return {
            "Comment": "Tool Lending Workflow - Community Tool Lending Library",
            "StartAt": "RequestReceived",
            "States": {
                "RequestReceived": {
                    "Type": "Task",
                    "Comment": "Validate lending request",
                    "Next": "ApprovalDecision",
                },
                "ApprovalDecision": {
                    "Type": "Choice",
                    "Comment": "Check if request should be approved",
                    "Choices": [
                        {"Variable": "$.approved", "BooleanEquals": True, "Next": "ToolHandover"},
                        {"Variable": "$.approved", "BooleanEquals": False, "Next": "RequestDenied"},
                    ],
                },
                "ToolHandover": {
                    "Type": "Task",
                    "Comment": "Mark tool as lent and set due date",
                    "Next": "WaitForReturn",
                },
                "WaitForReturn": {
                    "Type": "Wait",
                    "Comment": "Wait until due date",
                    "Next": "CheckReturn",
                },
                "CheckReturn": {
                    "Type": "Choice",
                    "Comment": "Check if tool was returned",
                    "Choices": [
                        {"Variable": "$.returned", "BooleanEquals": True, "Next": "Completed"},
                        {"Variable": "$.returned", "BooleanEquals": False, "Next": "OverdueNotification"},
                    ],
                },
                "OverdueNotification": {
                    "Type": "Task",
                    "Comment": "Send overdue notification",
                    "Next": "WaitForReturn",
                },
                "RequestDenied": {"Type": "Fail", "Cause": "Request was denied"},
                "Completed": {"Type": "Succeed"},
            },
        }

    def get_status(self):
        """Get the service status."""
        running = sum(1 for e in self._executions.values() if e.get("status") == "RUNNING")
        completed = sum(1 for e in self._executions.values() if e.get("status") == "COMPLETED")
        return {
            "service": "Step Functions",
            "status": "running",
            "mock_mode": self.use_mock,
            "total_executions": len(self._executions),
            "running": running,
            "completed": completed,
        }
