"""
Emotion event repository for managing emotion tracking data.
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from supabase import Client
import structlog

from app.core.database.models import (
    RecordNotFoundError, 
    serialize_for_db, 
    handle_supabase_response
)

logger = structlog.get_logger(__name__)


class EmotionEventRepository:
    """Repository for emotion event data operations."""
    
    def __init__(self, db_client: 'Client'):
        self.db = db_client
        self.table_name = "emotion_events"
    
    async def create_emotion_event(self, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new emotion event.
        
        Args:
            event_data: Dictionary containing emotion event data
                Required: session_id, emotion, confidence
                Optional: message_id, intensity, valence, arousal, context
        
        Returns:
            Created emotion event record
        """
        try:
            if "detected_at" not in event_data:
                event_data["detected_at"] = datetime.utcnow().isoformat()
            
            if "context" not in event_data:
                event_data["context"] = {}
            
            serialized_data = serialize_for_db(event_data)
            response = self.db.table(self.table_name).insert(serialized_data).execute()
            
            result = handle_supabase_response(response)
            logger.info(f"Created emotion event: {result.get('emotion')} for session {result.get('session_id')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create emotion event: {e}")
            raise
    
    async def get_session_emotions(
        self, 
        session_id: str,
        limit: int = 100,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """
        Get all emotion events for a session.
        
        Args:
            session_id: Session UUID
            limit: Maximum number of events to return
            offset: Number of events to skip
        
        Returns:
            List of emotion event records
        """
        try:
            response = (
                self.db.table(self.table_name)
                .select("*")
                .eq("session_id", session_id)
                .order("detected_at", desc=False)
                .range(offset, offset + limit - 1)
                .execute()
            )
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Failed to get session emotions {session_id}: {e}")
            raise
    
    async def get_emotion_statistics(self, session_id: str) -> Dict[str, Any]:
        """
        Get emotion statistics for a session.
        
        Args:
            session_id: Session UUID
        
        Returns:
            Dictionary with emotion statistics
        """
        try:
            # Get all emotions for the session
            emotions = await self.get_session_emotions(session_id, limit=1000)
            
            if not emotions:
                return {
                    "total_events": 0,
                    "dominant_emotion": "neutral",
                    "emotion_distribution": {},
                    "average_valence": 0.0,
                    "average_arousal": 0.5,
                    "emotion_transitions": 0
                }
            
            # Calculate statistics
            emotion_counts = {}
            total_valence = 0.0
            total_arousal = 0.0
            transitions = 0
            prev_emotion = None
            
            for event in emotions:
                emotion = event.get("emotion", "neutral")
                
                # Count emotions
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
                
                # Sum valence and arousal
                total_valence += event.get("valence", 0.0)
                total_arousal += event.get("arousal", 0.5)
                
                # Count transitions
                if prev_emotion and prev_emotion != emotion:
                    transitions += 1
                prev_emotion = emotion
            
            # Find dominant emotion
            dominant_emotion = max(emotion_counts, key=emotion_counts.get) if emotion_counts else "neutral"
            
            # Calculate averages
            num_events = len(emotions)
            avg_valence = total_valence / num_events if num_events > 0 else 0.0
            avg_arousal = total_arousal / num_events if num_events > 0 else 0.5
            
            # Calculate distribution percentages
            emotion_distribution = {
                emotion: (count / num_events) * 100
                for emotion, count in emotion_counts.items()
            }
            
            return {
                "total_events": num_events,
                "dominant_emotion": dominant_emotion,
                "emotion_distribution": emotion_distribution,
                "average_valence": round(avg_valence, 2),
                "average_arousal": round(avg_arousal, 2),
                "emotion_transitions": transitions
            }
            
        except Exception as e:
            logger.error(f"Failed to get emotion statistics for session {session_id}: {e}")
            raise
    
    async def get_recent_emotion(self, session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get the most recent emotion event for a session.
        
        Args:
            session_id: Session UUID
        
        Returns:
            Most recent emotion event or None
        """
        try:
            response = (
                self.db.table(self.table_name)
                .select("*")
                .eq("session_id", session_id)
                .order("detected_at", desc=True)
                .limit(1)
                .execute()
            )
            
            if not response.data:
                return None
            
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Failed to get recent emotion for session {session_id}: {e}")
            raise
    
    async def delete_session_emotions(self, session_id: str) -> bool:
        """
        Delete all emotion events for a session.
        
        Args:
            session_id: Session UUID
        
        Returns:
            True if successful
        """
        try:
            response = (
                self.db.table(self.table_name)
                .delete()
                .eq("session_id", session_id)
                .execute()
            )
            
            logger.info(f"Deleted emotion events for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session emotions {session_id}: {e}")
            raise
