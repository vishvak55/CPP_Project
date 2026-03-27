"""Configuration for the Community Tool Lending Library backend."""

import os


class Config:
    """Base configuration."""
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-key-vishvaksen-25173421")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///tool_lending.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # AWS Configuration
    AWS_REGION = os.environ.get("AWS_REGION", "eu-west-1")
    AWS_ACCESS_KEY_ID = os.environ.get("AWS_ACCESS_KEY_ID", "mock-key")
    AWS_SECRET_ACCESS_KEY = os.environ.get("AWS_SECRET_ACCESS_KEY", "mock-secret")

    # Mock mode: when True, all AWS services use local mocks
    USE_MOCK_AWS = os.environ.get("USE_MOCK_AWS", "true").lower() == "true"

    # DynamoDB
    DYNAMODB_TABLE_TOOLS = "ToolLendingLibrary-Tools"
    DYNAMODB_TABLE_USERS = "ToolLendingLibrary-Users"
    DYNAMODB_TABLE_LENDINGS = "ToolLendingLibrary-Lendings"

    # S3
    S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME", "tool-lending-images")
    S3_UPLOAD_FOLDER = "tool-images"

    # Cognito
    COGNITO_USER_POOL_ID = os.environ.get("COGNITO_USER_POOL_ID", "eu-west-1_mockPool")
    COGNITO_CLIENT_ID = os.environ.get("COGNITO_CLIENT_ID", "mock-client-id")

    # Step Functions
    STEP_FUNCTION_ARN = os.environ.get(
        "STEP_FUNCTION_ARN",
        "arn:aws:states:eu-west-1:123456789:stateMachine:LendingWorkflow"
    )

    # CloudWatch
    CLOUDWATCH_LOG_GROUP = "/tool-lending-library/app"
    CLOUDWATCH_NAMESPACE = "ToolLendingLibrary"


class DevelopmentConfig(Config):
    """Development configuration."""
    DEBUG = True
    USE_MOCK_AWS = True


class ProductionConfig(Config):
    """Production configuration."""
    DEBUG = False
    USE_MOCK_AWS = False


class TestingConfig(Config):
    """Testing configuration."""
    TESTING = True
    USE_MOCK_AWS = True
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"


config_by_name = {
    "development": DevelopmentConfig,
    "production": ProductionConfig,
    "testing": TestingConfig,
}
