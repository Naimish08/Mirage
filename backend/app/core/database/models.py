"""
Database models and utilities.
"""

from typing import Dict, Any, Optional
from datetime import datetime
import json


class RecordNotFoundError(Exception):
    """Raised when a database record is not found."""
    pass


class DatabaseError(Exception):
    """General database error."""
    pass


def serialize_for_db(data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Serialize data for database insertion.
    
    Handles datetime objects and nested dicts/lists.
    
    Args:
        data: Dictionary to serialize
        
    Returns:
        Serialized dictionary safe for database
    """
    serialized = {}
    
    for key, value in data.items():
        if value is None:
            serialized[key] = None
        elif isinstance(value, datetime):
            serialized[key] = value.isoformat()
        elif isinstance(value, (dict, list)):
            # JSON fields - keep as is for Supabase JSONB
            serialized[key] = value
        else:
            serialized[key] = value
    
    return serialized


def handle_supabase_response(response) -> Dict[str, Any]:
    """
    Handle Supabase response and extract data.
    
    Args:
        response: Supabase response object
        
    Returns:
        First record from response data
        
    Raises:
        DatabaseError: If response has no data
    """
    if not response.data:
        raise DatabaseError("No data returned from database operation")
    
    return response.data[0] if isinstance(response.data, list) else response.data


class TableNames:
    """Database table name constants."""
    USERS = "users"
    SESSIONS = "sessions"
    MESSAGES = "messages"
