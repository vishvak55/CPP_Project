"""DynamoDB service wrapper with local mock mode."""

import uuid
from datetime import datetime


class DynamoDBService:
    """Wrapper for AWS DynamoDB operations.

    Supports both real AWS DynamoDB and a local mock mode
    that uses in-memory dictionaries for development/testing.
    """

    def __init__(self, use_mock=True, region="eu-west-1"):
        self.use_mock = use_mock
        self.region = region
        self._mock_tables = {}
        self._client = None

        if not use_mock:
            try:
                import boto3
                self._client = boto3.resource("dynamodb", region_name=region)
            except Exception:
                self.use_mock = True

    def _get_table(self, table_name):
        if table_name not in self._mock_tables:
            self._mock_tables[table_name] = {}
        return self._mock_tables[table_name]

    def put_item(self, table_name, item):
        """Put an item into a DynamoDB table."""
        if self.use_mock:
            table = self._get_table(table_name)
            key = item.get("tool_id") or item.get("user_id") or item.get("record_id")
            if not key:
                key = str(uuid.uuid4())
            table[key] = item
            return {"status": "success", "item": item}
        else:
            table = self._client.Table(table_name)
            table.put_item(Item=item)
            return {"status": "success", "item": item}

    def get_item(self, table_name, key_name, key_value):
        """Get an item from a DynamoDB table by key."""
        if self.use_mock:
            table = self._get_table(table_name)
            item = table.get(key_value)
            return item
        else:
            table = self._client.Table(table_name)
            response = table.get_item(Key={key_name: key_value})
            return response.get("Item")

    def update_item(self, table_name, key_name, key_value, updates):
        """Update an item in a DynamoDB table."""
        if self.use_mock:
            table = self._get_table(table_name)
            if key_value in table:
                table[key_value].update(updates)
                return table[key_value]
            return None
        else:
            update_expr = "SET " + ", ".join(f"#{k} = :{k}" for k in updates)
            expr_names = {f"#{k}": k for k in updates}
            expr_values = {f":{k}": v for k, v in updates.items()}
            table = self._client.Table(table_name)
            table.update_item(
                Key={key_name: key_value},
                UpdateExpression=update_expr,
                ExpressionAttributeNames=expr_names,
                ExpressionAttributeValues=expr_values,
            )
            return self.get_item(table_name, key_name, key_value)

    def delete_item(self, table_name, key_name, key_value):
        """Delete an item from a DynamoDB table."""
        if self.use_mock:
            table = self._get_table(table_name)
            if key_value in table:
                del table[key_value]
                return True
            return False
        else:
            table = self._client.Table(table_name)
            table.delete_item(Key={key_name: key_value})
            return True

    def scan_table(self, table_name):
        """Scan all items in a DynamoDB table."""
        if self.use_mock:
            table = self._get_table(table_name)
            return list(table.values())
        else:
            table = self._client.Table(table_name)
            response = table.scan()
            return response.get("Items", [])

    def query_by_index(self, table_name, index_name, key_name, key_value):
        """Query items using a secondary index."""
        if self.use_mock:
            table = self._get_table(table_name)
            return [
                item for item in table.values()
                if item.get(key_name) == key_value
            ]
        else:
            table = self._client.Table(table_name)
            from boto3.dynamodb.conditions import Key
            response = table.query(
                IndexName=index_name,
                KeyConditionExpression=Key(key_name).eq(key_value),
            )
            return response.get("Items", [])

    def get_status(self):
        """Get the service status."""
        return {
            "service": "DynamoDB",
            "status": "running",
            "mock_mode": self.use_mock,
            "region": self.region,
            "tables": list(self._mock_tables.keys()) if self.use_mock else [],
        }
