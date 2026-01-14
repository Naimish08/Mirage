"""
User management endpoints for Mirage backend.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.api.dependencies import get_current_user, get_user_repository
from app.core.database.repositories import UserRepository
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class UpdateProfileRequest(BaseModel):
    """Request model for updating user profile."""
    full_name: Optional[str] = None
    avatar_url: Optional[str] = None
    preferred_agent_type: Optional[str] = None


class UpdatePreferencesRequest(BaseModel):
    """Request model for updating user preferences."""
    preferred_agent_type: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None


@router.get("/profile")
async def get_user_profile(
    current_user: Dict[str, Any] = Depends(get_current_user)
):
    """Get current user's profile."""
    return {
        "id": current_user.get("id"),
        "email": current_user.get("email"),
        "full_name": current_user.get("full_name"),
        "avatar_url": current_user.get("avatar_url"),
        "preferred_agent_type": current_user.get("preferred_agent_type", "teacher"),
        "preferences": current_user.get("preferences", {}),
        "is_active": current_user.get("is_active", True),
        "created_at": current_user.get("created_at"),
        "last_login_at": current_user.get("last_login_at")
    }


@router.put("/profile")
async def update_user_profile(
    request: UpdateProfileRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Update current user's profile."""
    try:
        update_data = {}
        
        if request.full_name is not None:
            update_data["full_name"] = request.full_name
        if request.avatar_url is not None:
            update_data["avatar_url"] = request.avatar_url
        if request.preferred_agent_type is not None:
            update_data["preferred_agent_type"] = request.preferred_agent_type
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        updated_user = await user_repo.update_user(current_user["id"], update_data)
        
        return {
            "message": "Profile updated successfully",
            "user": updated_user
        }
        
    except Exception as e:
        logger.error(f"Failed to update profile: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update profile"
        )


@router.put("/preferences")
async def update_user_preferences(
    request: UpdatePreferencesRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Update user preferences."""
    try:
        preferences_data = {}
        
        if request.preferred_agent_type is not None:
            preferences_data["preferred_agent_type"] = request.preferred_agent_type
        if request.preferences is not None:
            preferences_data["preferences"] = request.preferences
        
        if not preferences_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No preferences to update"
            )
        
        updated_user = await user_repo.update_preferences(
            current_user["id"], 
            preferences_data
        )
        
        return {
            "message": "Preferences updated successfully",
            "preferences": updated_user.get("preferences", {})
        }
        
    except Exception as e:
        logger.error(f"Failed to update preferences: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update preferences"
        )


@router.delete("/account")
async def delete_user_account(
    current_user: Dict[str, Any] = Depends(get_current_user),
    user_repo: UserRepository = Depends(get_user_repository)
):
    """Delete current user's account."""
    try:
        await user_repo.delete_user(current_user["id"])
        
        return {
            "message": "Account deleted successfully"
        }
        
    except Exception as e:
        logger.error(f"Failed to delete account: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account"
        )
