"""
API Dependencies for Mirage backend.
Provides authentication and repository injection.
"""

from typing import Optional, Dict, Any
from fastapi import Depends, HTTPException, status, Header

from app.config import get_settings, Settings
from app.core.database.connection import get_database_client
from app.core.database.repositories import UserRepository, SessionRepository, MessageRepository
from app.utils.supabase_auth import validate_supabase_token, SupabaseAuthError, extract_user_profile
from app.utils.logging import get_logger

logger = get_logger(__name__)


def get_settings_dependency() -> Settings:
    """FastAPI dependency that provides settings."""
    return get_settings()


def get_user_repository() -> UserRepository:
    """Get user repository instance."""
    db_client = get_database_client()
    return UserRepository(db_client)


def get_session_repository() -> SessionRepository:
    """Get session repository instance."""
    db_client = get_database_client()
    return SessionRepository(db_client)


def get_message_repository() -> MessageRepository:
    """Get message repository instance."""
    db_client = get_database_client()
    return MessageRepository(db_client)


async def get_current_user(
    authorization: Optional[str] = Header(None),
    user_repo: UserRepository = Depends(get_user_repository)
) -> Dict[str, Any]:
    """
    Validate token and get current user.
    
    This dependency:
    1. Extracts JWT token from Authorization header
    2. Validates token with Supabase
    3. Gets or creates user in database
    4. Returns user data
    
    Raises:
        HTTPException: If authentication fails
    """
    if not authorization:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization header required",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract token from "Bearer <token>"
    try:
        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise ValueError("Invalid auth scheme")
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format. Use 'Bearer <token>'",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Validate token with Supabase
    try:
        supabase_user = validate_supabase_token(token)
    except SupabaseAuthError as e:
        logger.warning(f"Token validation failed: {e}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e),
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Get or create user in our database
    user_id = supabase_user["id"]
    user = await user_repo.get_user_by_id(user_id)
    
    if not user:
        # Create user from Supabase data
        profile = extract_user_profile(supabase_user)
        user = await user_repo.create_user(profile)
        logger.info(f"Created new user from Supabase auth: {user['email']}")
    else:
        # Update last login
        await user_repo.update_last_login(user_id)
    
    return user


async def get_optional_current_user(
    authorization: Optional[str] = Header(None),
    user_repo: UserRepository = Depends(get_user_repository)
) -> Optional[Dict[str, Any]]:
    """
    Optionally get current user (doesn't raise if not authenticated).
    
    Useful for endpoints that work with or without authentication.
    """
    if not authorization:
        return None
    
    try:
        return await get_current_user(authorization, user_repo)
    except HTTPException:
        return None
