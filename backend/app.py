"""Flask application for the Community Tool Lending Library.

Author: Vishvaksen Machana (25173421)
Module: Cloud Platform Programming - NCI
"""

import os
import sys

# Add parent directory to path for lendlib imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from flask import Flask
from flask_cors import CORS
from models.database import db
from routes import tools_bp, users_bp, lendings_bp, aws_bp
from services import (
    DynamoDBService, S3Service, LambdaService,
    APIGatewayService, CognitoService,
    StepFunctionsService, CloudWatchService,
)
from config import config_by_name


def create_app(config_name="development"):
    """Application factory."""
    app = Flask(__name__)

    # Load configuration
    config_class = config_by_name.get(config_name, config_by_name["development"])
    app.config.from_object(config_class)

    # Enable CORS
    CORS(app)

    # Initialize database
    db.init_app(app)

    # Initialize AWS services (all in mock mode for local dev)
    use_mock = app.config.get("USE_MOCK_AWS", True)
    aws_services = {
        "dynamodb": DynamoDBService(use_mock=use_mock),
        "s3": S3Service(use_mock=use_mock),
        "lambda": LambdaService(use_mock=use_mock),
        "api_gateway": APIGatewayService(use_mock=use_mock),
        "cognito": CognitoService(use_mock=use_mock),
        "step_functions": StepFunctionsService(use_mock=use_mock),
        "cloudwatch": CloudWatchService(use_mock=use_mock),
    }
    app.config["AWS_SERVICES"] = aws_services

    # Set up CloudWatch scheduled rules
    cw = aws_services["cloudwatch"]
    cw.create_scheduled_rule(
        "OverdueCheck", "rate(1 hour)", "OverdueCheck Lambda"
    )
    cw.create_alarm(
        "HighOverdueCount", "overdue_count", threshold=10
    )

    # Register blueprints
    app.register_blueprint(tools_bp)
    app.register_blueprint(users_bp)
    app.register_blueprint(lendings_bp)
    app.register_blueprint(aws_bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    @app.route("/")
    def index():
        return {
            "name": "Community Tool Lending Library API",
            "version": "1.0.0",
            "author": "Vishvaksen Machana (25173421)",
            "endpoints": {
                "tools": "/api/tools",
                "users": "/api/users",
                "lendings": "/api/lendings",
                "aws_status": "/api/aws/status",
            },
        }

    @app.route("/health")
    def health():
        return {"status": "healthy", "mock_mode": use_mock}

    return app


if __name__ == "__main__":
    app = create_app("development")
    app.run(debug=True, port=5000)
