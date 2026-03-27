"""AWS services status API route."""

from flask import Blueprint, jsonify, current_app

aws_bp = Blueprint("aws", __name__)


@aws_bp.route("/api/aws/status", methods=["GET"])
def get_aws_status():
    """Get status of all AWS services."""
    services = current_app.config.get("AWS_SERVICES", {})

    status = {}
    for name, service in services.items():
        try:
            status[name] = service.get_status()
        except Exception as e:
            status[name] = {"service": name, "status": "error", "error": str(e)}

    return jsonify({
        "aws_services": status,
        "mock_mode": current_app.config.get("USE_MOCK_AWS", True),
        "total_services": len(status),
    })


@aws_bp.route("/api/aws/metrics", methods=["GET"])
def get_aws_metrics():
    """Get metrics from CloudWatch."""
    services = current_app.config.get("AWS_SERVICES", {})
    cloudwatch = services.get("cloudwatch")

    if not cloudwatch:
        return jsonify({"error": "CloudWatch service not available"}), 503

    return jsonify(cloudwatch.get_dashboard_data())


@aws_bp.route("/api/aws/workflow", methods=["GET"])
def get_workflow():
    """Get the Step Functions workflow definition."""
    services = current_app.config.get("AWS_SERVICES", {})
    step_functions = services.get("step_functions")

    if not step_functions:
        return jsonify({"error": "Step Functions service not available"}), 503

    return jsonify({
        "workflow": step_functions.get_workflow_definition(),
        "executions": step_functions.list_executions(),
    })
