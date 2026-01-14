"""
LiveKit token generation endpoints for Mirage backend.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional
from datetime import datetime
import time

from livekit.api import AccessToken, VideoGrants

from app.config import get_settings
from app.api.dependencies import get_current_user, get_session_repository
from app.core.database.repositories import SessionRepository
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)
settings = get_settings()


class RoomTokenRequest(BaseModel):
    """Request model for room token generation."""
    session_id: Optional[str] = None
    agent_type: str = "teacher"


class RoomTokenResponse(BaseModel):
    """Response model for room token."""
    token: str
    room_name: str
    session_id: str
    url: str


@router.post("/token", response_model=RoomTokenResponse)
async def get_room_token(
    request: RoomTokenRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """
    Generate a LiveKit room token for the user.
    
    Creates or uses a session and returns a token to join the LiveKit room.
    """
    if not settings.livekit_configured:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="LiveKit is not configured"
        )
    
    try:
        user_id = current_user["id"]
        
        # Create or get session
        if request.session_id:
            session = await session_repo.get_session_by_id(request.session_id)
            if not session or session.get("user_id") != user_id:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )
            session_id = request.session_id
        else:
            # Create new session
            session_data = {
                "user_id": user_id,
                "agent_type": request.agent_type,
                "title": "Voice Chat"
            }
            session = await session_repo.create_session(session_data)
            session_id = session["id"]
        
        # Generate room name
        timestamp = int(time.time())
        room_name = f"mirage_{user_id[:8]}_{timestamp}"
        
        # Update session with room name
        await session_repo.update_livekit_room(session_id, room_name)
        
        # Generate LiveKit token
        token = AccessToken(
            settings.LIVEKIT_API_KEY,
            settings.LIVEKIT_API_SECRET
        )
        token.with_identity(user_id)
        token.with_name(current_user.get("full_name", current_user.get("email", "User")))
        token.with_grants(VideoGrants(
            room=room_name,
            room_join=True,
            can_publish=True,
            can_subscribe=True,
        ))
        
        # Add metadata for agent
        token.with_metadata({
            "agent_type": request.agent_type,
            "session_id": session_id
        })
        
        jwt_token = token.to_jwt()
        
        logger.info(f"Generated LiveKit token for user {user_id}, room {room_name}")
        
        return RoomTokenResponse(
            token=jwt_token,
            room_name=room_name,
            session_id=session_id,
            url=settings.LIVEKIT_URL
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to generate room token: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate room token: {str(e)}"
        )


@router.get("/rooms")
async def list_active_rooms(
    current_user: Dict[str, Any] = Depends(get_current_user),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """List active rooms for current user."""
    try:
        sessions = await session_repo.get_user_sessions(
            current_user["id"], 
            active_only=True
        )
        
        # Filter sessions with room names
        rooms = [
            {
                "session_id": s["id"],
                "room_name": s.get("livekit_room_name"),
                "agent_type": s.get("agent_type"),
                "last_activity": s.get("last_activity_at")
            }
            for s in sessions
            if s.get("livekit_room_name")
        ]
        
        return {
            "rooms": rooms,
            "count": len(rooms)
        }
        
    except Exception as e:
        logger.error(f"Failed to list rooms: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to list rooms"
        )
