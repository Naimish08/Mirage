"""
Session repository for managing chat sessions.
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
    handle_supabase_response,
    TableNames
)

logger = structlog.get_logger(__name__)


class SessionRepository:
    """Repository for session data operations."""
    
    def __init__(self, db_client: Client):
        self.db = db_client
        self.table_name = TableNames.SESSIONS
    
    async def create_session(self, session_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new session."""
        try:
            session_data["created_at"] = datetime.utcnow().isoformat()
            session_data["updated_at"] = datetime.utcnow().isoformat()
            session_data["last_activity_at"] = datetime.utcnow().isoformat()
            
            if "status" not in session_data:
                session_data["status"] = "active"
            if "title" not in session_data:
                session_data["title"] = "New Chat"
            if "agent_type" not in session_data:
                session_data["agent_type"] = "teacher"
            
            serialized_data = serialize_for_db(session_data)
            response = self.db.table(self.table_name).insert(serialized_data).execute()
            
            result = handle_supabase_response(response)
            logger.info(f"Created session with ID: {result.get('id')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create session: {e}")
            raise
    
    async def get_session_by_id(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session by ID."""
        try:
            response = self.db.table(self.table_name).select("*").eq("id", session_id).execute()
            
            if not response.data:
                return None
            
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Failed to get session {session_id}: {e}")
            raise
    
    async def get_user_sessions(
        self, 
        user_id: str, 
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """Get all sessions for a user."""
        try:
            query = self.db.table(self.table_name).select("*").eq("user_id", user_id)
            
            if active_only:
                query = query.eq("status", "active")
            else:
                query = query.neq("status", "deleted")
            
            response = query.order("last_activity_at", desc=True).execute()
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Failed to get user sessions {user_id}: {e}")
            raise
    
    async def update_session(self, session_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update session data."""
        try:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            serialized_data = serialize_for_db(update_data)
            
            response = (
                self.db.table(self.table_name)
                .update(serialized_data)
                .eq("id", session_id)
                .execute()
            )
            
            if not response.data:
                raise RecordNotFoundError(f"Session {session_id} not found")
            
            result = handle_supabase_response(response)
            logger.info(f"Updated session {session_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to update session {session_id}: {e}")
            raise
    
    async def update_last_activity(self, session_id: str) -> Dict[str, Any]:
        """Update session last activity timestamp."""
        try:
            update_data = {
                "last_activity_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            serialized_data = serialize_for_db(update_data)
            
            response = (
                self.db.table(self.table_name)
                .update(serialized_data)
                .eq("id", session_id)
                .execute()
            )
            
            if not response.data:
                raise RecordNotFoundError(f"Session {session_id} not found")
            
            return handle_supabase_response(response)
            
        except Exception as e:
            logger.error(f"Failed to update last activity {session_id}: {e}")
            raise
    
    async def update_livekit_room(self, session_id: str, room_name: str) -> Dict[str, Any]:
        """Update session with LiveKit room name."""
        try:
            update_data = {
                "livekit_room_name": room_name,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            serialized_data = serialize_for_db(update_data)
            
            response = (
                self.db.table(self.table_name)
                .update(serialized_data)
                .eq("id", session_id)
                .execute()
            )
            
            if not response.data:
                raise RecordNotFoundError(f"Session {session_id} not found")
            
            result = handle_supabase_response(response)
            logger.info(f"Updated LiveKit room for session {session_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to update LiveKit room {session_id}: {e}")
            raise
    
    async def end_session(self, session_id: str) -> Dict[str, Any]:
        """End a session."""
        try:
            update_data = {
                "status": "ended",
                "updated_at": datetime.utcnow().isoformat()
            }
            
            serialized_data = serialize_for_db(update_data)
            
            response = (
                self.db.table(self.table_name)
                .update(serialized_data)
                .eq("id", session_id)
                .execute()
            )
            
            if not response.data:
                raise RecordNotFoundError(f"Session {session_id} not found")
            
            result = handle_supabase_response(response)
            logger.info(f"Ended session {session_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to end session {session_id}: {e}")
            raise
    
    async def delete_session(self, session_id: str) -> bool:
        """Soft delete a session."""
        try:
            update_data = {
                "status": "deleted",
                "updated_at": datetime.utcnow().isoformat()
            }
            
            serialized_data = serialize_for_db(update_data)
            
            response = (
                self.db.table(self.table_name)
                .update(serialized_data)
                .eq("id", session_id)
                .execute()
            )
            
            if not response.data:
                logger.warning(f"Session {session_id} not found for deletion")
                return False
            
            logger.info(f"Deleted session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session {session_id}: {e}")
            raise
