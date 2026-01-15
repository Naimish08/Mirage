"""
Emotion analysis and tracking endpoints for Mirage backend.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Dict, Any, Optional, List

from app.api.dependencies import (
    get_current_user,
    get_emotion_repository,
    get_session_repository
)
from app.core.database.repositories import EmotionEventRepository, SessionRepository
from app.services.emotion_service import get_emotion_service
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


class AnalyzeEmotionRequest(BaseModel):
    """Request model for emotion analysis."""
    text: str
    session_id: Optional[str] = None
    context: Optional[Dict[str, Any]] = None


class AnalyzeEmotionResponse(BaseModel):
    """Response model for emotion analysis."""
    emotion: str
    confidence: float
    intensity: float
    valence: float
    arousal: float
    reasoning: str


@router.post("/analyze", response_model=AnalyzeEmotionResponse)
async def analyze_emotion(
    request: AnalyzeEmotionRequest,
    current_user: Dict[str, Any] = Depends(get_current_user),
    emotion_repo: EmotionEventRepository = Depends(get_emotion_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """
    Analyze emotion from text.
    
    Optionally stores the emotion event if session_id is provided.
    """
    try:
        # Get emotion service
        emotion_service = get_emotion_service()
        
        # Analyze sentiment
        emotion_data = await emotion_service.analyze_text_sentiment(
            request.text,
            context=request.context
        )
        
        # If session_id provided, verify ownership and store emotion event
        if request.session_id:
            session = await session_repo.get_session_by_id(request.session_id)
            
            if not session:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="Session not found"
                )
            
            if session.get("user_id") != current_user["id"]:
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Not authorized to access this session"
                )
            
            # Store emotion event
            event_data = {
                "session_id": request.session_id,
                "emotion": emotion_data["emotion"],
                "confidence": emotion_data["confidence"],
                "intensity": emotion_data["intensity"],
                "valence": emotion_data["valence"],
                "arousal": emotion_data["arousal"],
                "context": request.context or {}
            }
            
            await emotion_repo.create_emotion_event(event_data)
            logger.info(f"Stored emotion event for session {request.session_id}")
        
        return AnalyzeEmotionResponse(**emotion_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to analyze emotion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to analyze emotion"
        )


@router.get("/session/{session_id}")
async def get_session_emotions(
    session_id: str,
    limit: int = 100,
    offset: int = 0,
    current_user: Dict[str, Any] = Depends(get_current_user),
    emotion_repo: EmotionEventRepository = Depends(get_emotion_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """
    Get emotion timeline for a session.
    
    Returns all emotion events detected during the conversation.
    """
    try:
        # Verify session ownership
        session = await session_repo.get_session_by_id(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session.get("user_id") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this session"
            )
        
        # Get emotion events
        emotions = await emotion_repo.get_session_emotions(
            session_id,
            limit=limit,
            offset=offset
        )
        
        return {
            "session_id": session_id,
            "emotions": emotions,
            "count": len(emotions)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get session emotions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get session emotions"
        )


@router.get("/session/{session_id}/stats")
async def get_session_emotion_stats(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    emotion_repo: EmotionEventRepository = Depends(get_emotion_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """
    Get emotion statistics for a session.
    
    Returns aggregated emotion data including:
    - Dominant emotion
    - Emotion distribution
    - Average valence and arousal
    - Number of emotion transitions
    """
    try:
        # Verify session ownership
        session = await session_repo.get_session_by_id(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session.get("user_id") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this session"
            )
        
        # Get statistics
        stats = await emotion_repo.get_emotion_statistics(session_id)
        
        return {
            "session_id": session_id,
            **stats
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get emotion statistics: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get emotion statistics"
        )


@router.get("/session/{session_id}/recent")
async def get_recent_emotion(
    session_id: str,
    current_user: Dict[str, Any] = Depends(get_current_user),
    emotion_repo: EmotionEventRepository = Depends(get_emotion_repository),
    session_repo: SessionRepository = Depends(get_session_repository)
):
    """
    Get the most recent emotion detected in a session.
    
    Useful for real-time emotion tracking.
    """
    try:
        # Verify session ownership
        session = await session_repo.get_session_by_id(session_id)
        
        if not session:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Session not found"
            )
        
        if session.get("user_id") != current_user["id"]:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this session"
            )
        
        # Get recent emotion
        recent_emotion = await emotion_repo.get_recent_emotion(session_id)
        
        if not recent_emotion:
            return {
                "session_id": session_id,
                "emotion": None,
                "message": "No emotions detected yet"
            }
        
        return {
            "session_id": session_id,
            **recent_emotion
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get recent emotion: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get recent emotion"
        )
