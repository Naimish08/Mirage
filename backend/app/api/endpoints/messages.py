"""
Message storage endpoints for Mirage backend.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional

from app.api.dependencies import (
    get_current_user,
    get_message_repository,
    get_session_repository
)
from app.core.database.repositories import MessageRepository, SessionRepository
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class SaveMessageRequest(BaseModel):
    """Request model for saving a message."""
    session_id: str
    role: str  # 'user' or 'assistant'
    content: str
    audio_url: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None


@router.post("/save")
async def save_message(
    request: SaveMessageRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    message_repo: MessageRepository = Depends(get_message_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """
    Save a message to a session.
    
    Used by the agent worker to persist conversation messages.
    """
    try:
        # Verify session exists and belongs to user
        session = await session_repo.get_session_by_id(request.session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session.get("user_id") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to add messages to this session"
            )
        
        # Create message
        message_data = {
            "session_id": request.session_id,
            "role": request.role,
            "content": request.content,
            "audio_url": request.audio_url,
            "metadata": request.metadata or {}
        }
        
        message = await message_repo.create_message(message_data)
        
        # Update session last_activity_at
        await session_repo.update_session(
            request.session_id,
            {"last_activity_at": message["created_at"]}
        )
        
        logger.info(f"Saved {request.role} message to session {request.session_id}")
        
        return {
            "message": "Message saved successfully",
            "data": message
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to save message: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to save message"
        )
