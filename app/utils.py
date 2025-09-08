"""
Utility functions for the API
"""

from datetime import datetime
from typing import Any, Dict, List, Union


def serialize_datetime_objects(obj: Any) -> Any:
    """
    Recursively convert datetime objects to ISO format strings
    """
    if isinstance(obj, datetime):
        return obj.isoformat()
    elif isinstance(obj, dict):
        return {key: serialize_datetime_objects(value) for key, value in obj.items()}
    elif isinstance(obj, list):
        return [serialize_datetime_objects(item) for item in obj]
    elif hasattr(obj, '__dict__'):
        # Handle Pydantic models and other objects with __dict__
        return serialize_datetime_objects(obj.__dict__)
    else:
        return obj


def clean_response_for_json(response: Any) -> Dict[str, Any]:
    """
    Clean a response object to ensure it's JSON serializable
    """
    if hasattr(response, 'dict'):
        # Pydantic model
        return serialize_datetime_objects(response.dict())
    else:
        return serialize_datetime_objects(response)
