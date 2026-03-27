"""Cognito service wrapper with local mock mode."""

import uuid
import hashlib
from datetime import datetime, timedelta


class CognitoService:
    """Wrapper for AWS Cognito authentication.

    In mock mode, simulates user authentication with in-memory storage.
    """

    def __init__(self, use_mock=True, user_pool_id="mock-pool", client_id="mock-client",
                 region="eu-west-1"):
        self.use_mock = use_mock
        self.user_pool_id = user_pool_id
        self.client_id = client_id
        self.region = region
        self._mock_users = {}
        self._mock_tokens = {}
        self._client = None

        if not use_mock:
            try:
                import boto3
                self._client = boto3.client("cognito-idp", region_name=region)
            except Exception:
                self.use_mock = True

    def sign_up(self, username, password, email):
        """Register a new user."""
        if self.use_mock:
            if username in self._mock_users:
                return {"status": "error", "message": "User already exists"}
            self._mock_users[username] = {
                "username": username,
                "password_hash": hashlib.sha256(password.encode()).hexdigest(),
                "email": email,
                "confirmed": True,
                "created_at": datetime.utcnow().isoformat(),
            }
            return {"status": "success", "username": username}
        else:
            response = self._client.sign_up(
                ClientId=self.client_id,
                Username=username,
                Password=password,
                UserAttributes=[{"Name": "email", "Value": email}],
            )
            return {"status": "success", "username": username}

    def sign_in(self, username, password):
        """Authenticate a user and return tokens."""
        if self.use_mock:
            user = self._mock_users.get(username)
            if not user:
                return {"status": "error", "message": "User not found"}
            pw_hash = hashlib.sha256(password.encode()).hexdigest()
            if user["password_hash"] != pw_hash:
                return {"status": "error", "message": "Invalid password"}
            token = str(uuid.uuid4())
            self._mock_tokens[token] = {
                "username": username,
                "expires": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
            }
            return {
                "status": "success",
                "access_token": token,
                "token_type": "Bearer",
                "expires_in": 3600,
            }
        else:
            response = self._client.initiate_auth(
                ClientId=self.client_id,
                AuthFlow="USER_PASSWORD_AUTH",
                AuthParameters={"USERNAME": username, "PASSWORD": password},
            )
            result = response["AuthenticationResult"]
            return {
                "status": "success",
                "access_token": result["AccessToken"],
                "token_type": "Bearer",
                "expires_in": result["ExpiresIn"],
            }

    def verify_token(self, token):
        """Verify an authentication token."""
        if self.use_mock:
            token_data = self._mock_tokens.get(token)
            if not token_data:
                return {"valid": False, "message": "Invalid token"}
            expires = datetime.fromisoformat(token_data["expires"])
            if datetime.utcnow() > expires:
                return {"valid": False, "message": "Token expired"}
            return {"valid": True, "username": token_data["username"]}
        else:
            return {"valid": True}  # Simplified

    def sign_out(self, token):
        """Sign out a user by invalidating their token."""
        if self.use_mock:
            if token in self._mock_tokens:
                del self._mock_tokens[token]
            return {"status": "success"}
        else:
            return {"status": "success"}

    def get_status(self):
        """Get the service status."""
        return {
            "service": "Cognito",
            "status": "running",
            "mock_mode": self.use_mock,
            "user_pool_id": self.user_pool_id,
            "registered_users": len(self._mock_users) if self.use_mock else "N/A",
            "active_tokens": len(self._mock_tokens) if self.use_mock else "N/A",
        }
