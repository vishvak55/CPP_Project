"""CloudWatch service wrapper with local mock mode."""

from datetime import datetime
from collections import defaultdict


class CloudWatchService:
    """Wrapper for AWS CloudWatch monitoring and scheduling.

    In mock mode, simulates CloudWatch metrics, logs, and alarms locally.
    """

    def __init__(self, use_mock=True, region="eu-west-1",
                 namespace="ToolLendingLibrary"):
        self.use_mock = use_mock
        self.region = region
        self.namespace = namespace
        self._metrics = defaultdict(list)
        self._logs = []
        self._alarms = {}
        self._scheduled_rules = {}
        self._client = None

        if not use_mock:
            try:
                import boto3
                self._client = boto3.client("cloudwatch", region_name=region)
            except Exception:
                self.use_mock = True

    def put_metric(self, metric_name, value, unit="Count"):
        """Put a metric data point."""
        data_point = {
            "metric_name": metric_name,
            "value": value,
            "unit": unit,
            "timestamp": datetime.utcnow().isoformat(),
        }

        if self.use_mock:
            self._metrics[metric_name].append(data_point)
        else:
            self._client.put_metric_data(
                Namespace=self.namespace,
                MetricData=[{
                    "MetricName": metric_name,
                    "Value": value,
                    "Unit": unit,
                }],
            )
        return data_point

    def get_metric(self, metric_name, limit=100):
        """Get metric data points."""
        if self.use_mock:
            return self._metrics.get(metric_name, [])[-limit:]
        return []

    def log_event(self, log_group, message, level="INFO"):
        """Log an event to CloudWatch Logs."""
        event = {
            "log_group": log_group,
            "message": message,
            "level": level,
            "timestamp": datetime.utcnow().isoformat(),
        }
        self._logs.append(event)
        return event

    def get_logs(self, log_group=None, limit=100):
        """Get log events."""
        logs = self._logs
        if log_group:
            logs = [l for l in logs if l["log_group"] == log_group]
        return logs[-limit:]

    def create_alarm(self, alarm_name, metric_name, threshold,
                     comparison="GreaterThanThreshold"):
        """Create a CloudWatch alarm."""
        alarm = {
            "alarm_name": alarm_name,
            "metric_name": metric_name,
            "threshold": threshold,
            "comparison": comparison,
            "state": "OK",
            "created_at": datetime.utcnow().isoformat(),
        }
        self._alarms[alarm_name] = alarm
        return alarm

    def check_alarms(self):
        """Check all alarms against current metrics."""
        triggered = []
        for name, alarm in self._alarms.items():
            metrics = self.get_metric(alarm["metric_name"], limit=1)
            if metrics:
                latest_value = metrics[-1]["value"]
                if alarm["comparison"] == "GreaterThanThreshold":
                    if latest_value > alarm["threshold"]:
                        alarm["state"] = "ALARM"
                        triggered.append(alarm)
                    else:
                        alarm["state"] = "OK"
        return triggered

    def create_scheduled_rule(self, rule_name, schedule_expression, target):
        """Create a scheduled rule (e.g., for overdue checking)."""
        rule = {
            "rule_name": rule_name,
            "schedule_expression": schedule_expression,
            "target": target,
            "enabled": True,
            "created_at": datetime.utcnow().isoformat(),
        }
        self._scheduled_rules[rule_name] = rule
        return rule

    def get_scheduled_rules(self):
        """Get all scheduled rules."""
        return list(self._scheduled_rules.values())

    def get_dashboard_data(self):
        """Get data for CloudWatch dashboard."""
        return {
            "metrics_summary": {
                name: {
                    "count": len(points),
                    "latest": points[-1]["value"] if points else None,
                }
                for name, points in self._metrics.items()
            },
            "recent_logs": self.get_logs(limit=10),
            "alarms": list(self._alarms.values()),
            "scheduled_rules": self.get_scheduled_rules(),
        }

    def get_status(self):
        """Get the service status."""
        return {
            "service": "CloudWatch",
            "status": "running",
            "mock_mode": self.use_mock,
            "namespace": self.namespace,
            "metrics_tracked": len(self._metrics),
            "total_log_events": len(self._logs),
            "alarms_configured": len(self._alarms),
            "scheduled_rules": len(self._scheduled_rules),
        }
