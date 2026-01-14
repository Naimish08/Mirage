"""
Authentication endpoints for Mirage backend.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import Dict, Any

from app.api.dependencies import get_current_user
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


@router.get("/me")
async def get_current_user_info(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Get current authenticated user info.
    
    Requires valid Supabase JWT token in Authorization header.
    """
    return {
        "id": current_user.get("id"),
        "email": current_user.get("email"),
        "full_name": current_user.get("full_name"),
        "avatar_url": current_user.get("avatar_url"),
        "preferred_agent_type": current_user.get("preferred_agent_type", "teacher"),
        "is_active": current_user.get("is_active", True),
        "created_at": current_user.get("created_at"),
        "last_login_at": current_user.get("last_login_at")
    }


@router.post("/validate")
async def validate_token(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """
    Validate token and return basic info.
    
    Useful for frontend to check if token is still valid.
    """
    return {
        "valid": True,
        "user_id": current_user.get("id"),
        "email": current_user.get("email")
    }
