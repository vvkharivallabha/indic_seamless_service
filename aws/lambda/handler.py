#!/usr/bin/env python3
"""
AWS Lambda handler for Indic-Seamless Speech-to-Text Service
This handler adapts the FastAPI application for serverless deployment.
"""

import json
import logging
from typing import Any, Dict

from mangum import Mangum

# Import the FastAPI app
from src.api.app import create_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global variable to hold the app instance
app = None


def get_app():
    """Get or create the FastAPI app instance."""
    global app
    if app is None:
        logger.info("Creating FastAPI app for Lambda...")
        app = create_app()
        logger.info("FastAPI app created successfully")
    return app


# Create the Lambda handler using Mangum
handler = Mangum(get_app(), lifespan="off")


def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """
    Main Lambda handler function.

    Args:
        event: Lambda event dictionary
        context: Lambda context object

    Returns:
        Lambda response dictionary
    """
    try:
        # Log the event for debugging (remove in production)
        logger.info(f"Received event: {json.dumps(event, default=str)}")

        # Handle the request using Mangum
        response = handler(event, context)

        # Log the response for debugging (remove in production)
        logger.info(f"Response: {json.dumps(response, default=str)}")

        return response

    except Exception as e:
        logger.error(f"Error in Lambda handler: {str(e)}")
        logger.error(f"Event: {json.dumps(event, default=str)}")

        # Return a proper error response
        return {
            "statusCode": 500,
            "headers": {
                "Content-Type": "application/json",
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": (
                    "Content-Type,X-Amz-Date,Authorization,"
                    "X-Api-Key,X-Amz-Security-Token"
                ),
                "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
            },
            "body": json.dumps({"error": "Internal server error", "message": str(e)}),
        }


# For local testing
if __name__ == "__main__":
    # Test event structure
    test_event = {
        "httpMethod": "GET",
        "path": "/health",
        "headers": {},
        "queryStringParameters": None,
        "body": None,
        "isBase64Encoded": False,
    }

    class MockContext:
        def __init__(self):
            self.function_name = "test-function"
            self.memory_limit_in_mb = 10240
            self.invoked_function_arn = (
                "arn:aws:lambda:us-east-1:123456789012:function:test-function"
            )
            self.aws_request_id = "test-request-id"

    context = MockContext()

    # Test the handler
    response = lambda_handler(test_event, context)
    print(f"Response: {json.dumps(response, indent=2)}")
