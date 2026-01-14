"""
Session management endpoints for Mirage backend.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from app.api.dependencies import (
    get_current_user, 
    get_session_repository, 
    get_message_repository
)
from app.core.database.repositories import SessionRepository, MessageRepository
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class CreateSessionRequest(BaseModel):
    """Request model for creating a session."""
    agent_type: Optional[str] = "teacher"
    title: Optional[str] = "New Chat"


class UpdateSessionRequest(BaseModel):
    """Request model for updating a session."""
    title: Optional[str] = None
    agent_type: Optional[str] = None


@router.post("/create")
async def create_session(
    request: CreateSessionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Create a new chat session."""
    try:
        session_data = {
            "user_id": current_user["id"],
            "agent_type": request.agent_type,
            "title": request.title
        }
        
        session = await session_repo.create_session(session_data)
        
        return {
            "message": "Session created successfully",
            "session": session
        }
        
    except Exception as e:
        logger.error(f"Failed to create session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create session"
        )


@router.get("/")
async def list_sessions(
    active_only: bool = True,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """List all sessions for current user."""
    try:
        sessions = await session_repo.get_user_sessions(
            current_user["id"], 
            active_only=active_only
        )
        
        return {
            "sessions": sessions,
            "count": len(sessions)
        }
        
    except Exception as e:
        logger.error(f"Failed to list sessions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list sessions"
        )


@router.get("/{session_id}")
async def get_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Get a specific session."""
    try:
        session = await session_repo.get_session_by_id(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        # Check ownership
        if session.get("user_id") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this session"
            )
        
        return session
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session"
        )


@router.put("/{session_id}")
async def update_session(
    session_id: str,
    request: UpdateSessionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Update a session."""
    try:
        # Check ownership
        session = await session_repo.get_session_by_id(session_id)
        if not session or session.get("user_id") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        update_data = {}
        if request.title is not None:
            update_data["title"] = request.title
        if request.agent_type is not None:
            update_data["agent_type"] = request.agent_type
        
        if not update_data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No fields to update"
            )
        
        updated_session = await session_repo.update_session(session_id, update_data)
        
        return {
            "message": "Session updated successfully",
            "session": updated_session
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update session"
        )


@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """Delete a session (soft delete)."""
    try:
        # Check ownership
        session = await session_repo.get_session_by_id(session_id)
        if not session or session.get("user_id") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        await session_repo.delete_session(session_id)
        
        return {
            "message": "Session deleted successfully"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete session: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete session"
        )


@router.get("/{session_id}/messages")
async def get_session_messages(
    session_id: str,
    limit: int = 50,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session_repo: SessionRepository = Depends(get_session_repository),
    message_repo: MessageRepository = Depends(get_message_repository)
):
    """Get messages for a session."""
    try:
        # Check ownership
        session = await session_repo.get_session_by_id(session_id)
        if not session or session.get("user_id") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        messages = await message_repo.get_session_messages(
            session_id, 
            limit=limit, 
            offset=offset
        )
        
        return {
            "messages": messages,
            "count": len(messages)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get messages: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get messages"
        )
