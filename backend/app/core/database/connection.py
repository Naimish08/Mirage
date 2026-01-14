"""
Supabase database connection.
"""

from typing import Optional

try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None
    create_client = None

from app.config import get_settings

_db_client: Optional[Client] = None
_initialized = False


def get_database_client() -> Client:
    """
    Get Supabase database client.
    
    Uses singleton pattern to reuse connection.
    
    Returns:
        Supabase client instance
        
    Raises:
        RuntimeError: If Supabase is not configured or not available
    """
    global _db_client, _initialized
    
    if not SUPABASE_AVAILABLE:
        raise RuntimeError(
            "Supabase SDK not installed. Run: pip install supabase\n"
            "Note: Requires python3-dev package for compilation."
        )
    
    if not _initialized:
        settings = get_settings()
        
        if not settings.SUPABASE_URL or not settings.SUPABASE_SERVICE_KEY:
            raise RuntimeError(
                "SUPABASE_URL and SUPABASE_SERVICE_KEY must be configured. "
                "Please check your .env file."
            )
        
        _db_client = create_client(
            settings.SUPABASE_URL, 
            settings.SUPABASE_SERVICE_KEY
        )
        _initialized = True
    
    if not _db_client:
        raise RuntimeError("Database client not initialized")
    
    return _db_client


def reset_database_client():
    """Reset database client (useful for testing)."""
    global _db_client, _initialized
    _db_client = None
    _initialized = False


def is_supabase_available() -> bool:
    """Check if supabase package is available."""
    return SUPABASE_AVAILABLE
