"""
Supabase authentication utilities for validating frontend tokens.
"""

import jwt
from typing import Dict, Any, Optional
from datetime import datetime

# Handle missing supabase gracefully
try:
    from supabase import Client
    SUPABASE_AVAILABLE = True
except ImportError:
    Client = None
    SUPABASE_AVAILABLE = False

from app.config import get_settings
from app.utils.logging import get_logger
from app.utils.errors import AuthenticationError

logger = get_logger(__name__)
settings = get_settings()

# Global Supabase client for auth
_supabase_client: Optional["Client"] = None


class SupabaseAuthError(AuthenticationError):
    """Specific error for Supabase authentication issues."""
    pass


def get_supabase_client() -> Optional[Client]:
    """
    Get Supabase client for token validation.
    
    Returns:
        Supabase client instance or None if not configured
    """
    global _supabase_client
    
    if _supabase_client is not None:
        return _supabase_client
    
    try:
        from app.core.database.connection import get_database_client
        _supabase_client = get_database_client()
        logger.info("Supabase client initialized for token validation")
        return _supabase_client
        
    except Exception as e:
        logger.error(f"Failed to get Supabase client: {e}")
        return None


def validate_supabase_token(token: str) -> Dict[str, Any]:
    """
    Validate a Supabase JWT token and extract user information.
    
    Args:
        token: JWT token from Supabase frontend
        
    Returns:
        Dictionary containing validated user information
        
    Raises:
        SupabaseAuthError: If token is invalid or expired
    """
    try:
        logger.debug("Starting Supabase token validation")
        
        supabase_client = get_supabase_client()
        if not supabase_client:
            raise SupabaseAuthError("Supabase client not available")
        
        # Method 1: Use Supabase client to validate token
        try:
            user_response = supabase_client.auth.get_user(token)
            
            if user_response.user:
                user_data = {
                    "id": user_response.user.id,
                    "email": user_response.user.email,
                    "email_confirmed_at": user_response.user.email_confirmed_at,
                    "created_at": user_response.user.created_at,
                    "updated_at": user_response.user.updated_at,
                    "user_metadata": user_response.user.user_metadata or {},
                    "app_metadata": user_response.user.app_metadata or {}
                }
                
                logger.info(f"Token validated for user: {user_data['email']}")
                return user_data
                
        except Exception as supabase_error:
            logger.warning(f"Supabase client validation failed: {supabase_error}")
        
        # Method 2: Manual JWT validation (backup)
        if settings.SUPABASE_JWT_SECRET:
            try:
                jwt_secret = settings.SUPABASE_JWT_SECRET.strip().strip('"').strip("'")
                
                payload = jwt.decode(
                    token,
                    jwt_secret,
                    algorithms=["HS256"],
                    options={"verify_exp": True}
                )
                
                user_data = {
                    "id": payload.get("sub"),
                    "email": payload.get("email"),
                    "email_confirmed_at": payload.get("email_confirmed_at"),
                    "created_at": payload.get("created_at"),
                    "user_metadata": payload.get("user_metadata", {}),
                    "app_metadata": payload.get("app_metadata", {})
                }
                
                if not user_data["id"] or not user_data["email"]:
                    raise SupabaseAuthError("Invalid user data in token")
                
                logger.info(f"Manual JWT validation successful for: {user_data['email']}")
                return user_data
                
            except jwt.ExpiredSignatureError:
                raise SupabaseAuthError("Token has expired")
            except jwt.InvalidTokenError as e:
                raise SupabaseAuthError(f"Invalid JWT token: {str(e)}")
        
        raise SupabaseAuthError("Unable to validate token")
        
    except SupabaseAuthError:
        raise
    except Exception as e:
        logger.error(f"Unexpected error validating token: {str(e)}")
        raise SupabaseAuthError(f"Token validation failed: {str(e)}")


def extract_user_profile(supabase_user: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extract user profile information from Supabase user data.
    
    Args:
        supabase_user: User data from Supabase validation
        
    Returns:
        Dictionary with profile information matching the users table schema
    """
    user_metadata = supabase_user.get("user_metadata", {})
    
    # Only include fields that exist in the users table
    profile = {
        "id": supabase_user["id"],
        "email": supabase_user["email"],
    }
    
    # Add optional fields if they exist
    full_name = user_metadata.get("full_name") or user_metadata.get("name")
    if full_name:
        profile["full_name"] = full_name
    
    avatar_url = user_metadata.get("avatar_url") or user_metadata.get("picture")
    if avatar_url:
        profile["avatar_url"] = avatar_url
    
    # Note: email_verified and created_at are NOT in the users table schema
    # The users table uses its own created_at, and doesn't track email verification
    
    return profile



def test_supabase_connection() -> bool:
    """Test connection to Supabase."""
    try:
        client = get_supabase_client()
        if not client:
            return False
        
        logger.info("Supabase connection test successful")
        return True
        
    except Exception as e:
        logger.error(f"Supabase connection test failed: {e}")
        return False


__all__ = [
    "validate_supabase_token",
    "extract_user_profile",
    "test_supabase_connection",
    "SupabaseAuthError"
]
