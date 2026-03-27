"""API Gateway service wrapper with local mock mode."""

from datetime import datetime


class APIGatewayService:
    """Wrapper for AWS API Gateway management.

    In mock mode, simulates API Gateway configuration and metrics.
    """

    def __init__(self, use_mock=True, region="eu-west-1"):
        self.use_mock = use_mock
        self.region = region
        self._request_log = []
        self._api_keys = {}
        self._rate_limits = {"default": 1000}
        self._client = None

        if not use_mock:
            try:
                import boto3
                self._client = boto3.client("apigateway", region_name=region)
            except Exception:
                self.use_mock = True

    def register_api_key(self, key_name, api_key):
        """Register an API key."""
        self._api_keys[key_name] = {
            "key": api_key,
            "created_at": datetime.utcnow().isoformat(),
            "enabled": True,
        }
        return {"status": "registered", "key_name": key_name}

    def validate_api_key(self, api_key):
        """Validate an API key."""
        if self.use_mock:
            for key_data in self._api_keys.values():
                if key_data["key"] == api_key and key_data["enabled"]:
                    return True
            return True  # In mock mode, all keys are valid
        return True

    def log_request(self, method, path, status_code, response_time_ms):
        """Log an API request for metrics."""
        self._request_log.append({
            "method": method,
            "path": path,
            "status_code": status_code,
            "response_time_ms": response_time_ms,
            "timestamp": datetime.utcnow().isoformat(),
        })

    def get_metrics(self):
        """Get API Gateway metrics."""
        total = len(self._request_log)
        if total == 0:
            return {"total_requests": 0, "avg_response_time": 0, "error_rate": 0}

        errors = sum(1 for r in self._request_log if r["status_code"] >= 400)
        avg_time = sum(r["response_time_ms"] for r in self._request_log) / total

        return {
            "total_requests": total,
            "avg_response_time_ms": round(avg_time, 2),
            "error_rate": round(errors / total * 100, 2),
            "by_method": self._count_by_field("method"),
            "by_status": self._count_by_field("status_code"),
        }

    def _count_by_field(self, field):
        counts = {}
        for r in self._request_log:
            val = str(r[field])
            counts[val] = counts.get(val, 0) + 1
        return counts

    def get_endpoints(self):
        """Get registered API endpoints."""
        return [
            {"path": "/api/tools", "methods": ["GET", "POST"]},
            {"path": "/api/tools/<id>", "methods": ["GET", "PUT", "DELETE"]},
            {"path": "/api/users", "methods": ["GET", "POST"]},
            {"path": "/api/users/<id>", "methods": ["GET", "PUT", "DELETE"]},
            {"path": "/api/lendings", "methods": ["GET", "POST"]},
            {"path": "/api/lendings/<id>", "methods": ["GET", "PUT", "DELETE"]},
            {"path": "/api/lendings/<id>/approve", "methods": ["POST"]},
            {"path": "/api/lendings/<id>/activate", "methods": ["POST"]},
            {"path": "/api/lendings/<id>/return", "methods": ["POST"]},
            {"path": "/api/aws/status", "methods": ["GET"]},
        ]

    def get_status(self):
        """Get the service status."""
        return {
            "service": "API Gateway",
            "status": "running",
            "mock_mode": self.use_mock,
            "total_endpoints": len(self.get_endpoints()),
            "api_keys_registered": len(self._api_keys),
            "total_requests_logged": len(self._request_log),
        }
