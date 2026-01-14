"""
Database package initialization.
"""

from app.core.database.connection import get_database_client

__all__ = ["get_database_client"]
