"""GET / - service info."""
from app.lambda_utils import json_response


def handler(event, context):
    return json_response({"service": "Penguin Auth API", "docs": "/docs"})
