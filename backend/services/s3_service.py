"""S3 service wrapper with local mock mode."""

import os
import uuid
import base64
from datetime import datetime


class S3Service:
    """Wrapper for AWS S3 operations.

    In mock mode, stores files in a local dictionary simulating S3.
    """

    def __init__(self, use_mock=True, bucket_name="tool-lending-images", region="eu-west-1"):
        self.use_mock = use_mock
        self.bucket_name = bucket_name
        self.region = region
        self._mock_storage = {}
        self._client = None

        if not use_mock:
            try:
                import boto3
                self._client = boto3.client("s3", region_name=region)
            except Exception:
                self.use_mock = True

    def upload_file(self, file_content, file_name, content_type="image/jpeg"):
        """Upload a file to S3."""
        key = f"tool-images/{uuid.uuid4()}/{file_name}"

        if self.use_mock:
            self._mock_storage[key] = {
                "content": file_content if isinstance(file_content, bytes) else file_content.encode(),
                "content_type": content_type,
                "uploaded_at": datetime.utcnow().isoformat(),
                "size": len(file_content) if isinstance(file_content, (bytes, str)) else 0,
            }
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
            return {"status": "success", "key": key, "url": url}
        else:
            self._client.put_object(
                Bucket=self.bucket_name, Key=key,
                Body=file_content, ContentType=content_type,
            )
            url = f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}"
            return {"status": "success", "key": key, "url": url}

    def get_file(self, key):
        """Get a file from S3."""
        if self.use_mock:
            item = self._mock_storage.get(key)
            if item:
                return {"content": item["content"], "content_type": item["content_type"]}
            return None
        else:
            response = self._client.get_object(Bucket=self.bucket_name, Key=key)
            return {
                "content": response["Body"].read(),
                "content_type": response["ContentType"],
            }

    def delete_file(self, key):
        """Delete a file from S3."""
        if self.use_mock:
            if key in self._mock_storage:
                del self._mock_storage[key]
                return True
            return False
        else:
            self._client.delete_object(Bucket=self.bucket_name, Key=key)
            return True

    def list_files(self, prefix="tool-images/"):
        """List files in S3 bucket with given prefix."""
        if self.use_mock:
            return [
                {"key": k, "size": v["size"], "uploaded_at": v["uploaded_at"]}
                for k, v in self._mock_storage.items()
                if k.startswith(prefix)
            ]
        else:
            response = self._client.list_objects_v2(
                Bucket=self.bucket_name, Prefix=prefix
            )
            return [
                {"key": obj["Key"], "size": obj["Size"]}
                for obj in response.get("Contents", [])
            ]

    def generate_presigned_url(self, key, expiration=3600):
        """Generate a presigned URL for a file."""
        if self.use_mock:
            return f"https://{self.bucket_name}.s3.{self.region}.amazonaws.com/{key}?mock-presigned=true&expires={expiration}"
        else:
            return self._client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=expiration,
            )

    def get_status(self):
        """Get the service status."""
        return {
            "service": "S3",
            "status": "running",
            "mock_mode": self.use_mock,
            "bucket": self.bucket_name,
            "files_count": len(self._mock_storage) if self.use_mock else "N/A",
        }
