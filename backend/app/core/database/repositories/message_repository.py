"""
Message repository for managing conversation messages.
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


class MessageRepository:
    """Repository for message data operations."""
    
    def __init__(self, db_client: Client):
        self.db = db_client
        self.table_name = TableNames.MESSAGES
    
    async def create_message(self, message_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new message."""
        try:
            message_data["created_at"] = datetime.utcnow().isoformat()
            
            if "metadata" not in message_data:
                message_data["metadata"] = {}
            
            serialized_data = serialize_for_db(message_data)
            response = self.db.table(self.table_name).insert(serialized_data).execute()
            
            result = handle_supabase_response(response)
            logger.info(f"Created message with ID: {result.get('id')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create message: {e}")
            raise
    
    async def get_session_messages(
        self, 
        session_id: str, 
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        """Get all messages for a session."""
        try:
            response = (
                self.db.table(self.table_name)
                .select("*")
                .eq("session_id", session_id)
                .order("created_at", desc=False)
                .range(offset, offset + limit - 1)
                .execute()
            )
            
            return response.data or []
            
        except Exception as e:
            logger.error(f"Failed to get session messages {session_id}: {e}")
            raise
    
    async def get_message_by_id(self, message_id: str) -> Optional[Dict[str, Any]]:
        """Get message by ID."""
        try:
            response = self.db.table(self.table_name).select("*").eq("id", message_id).execute()
            
            if not response.data:
                return None
            
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Failed to get message {message_id}: {e}")
            raise
    
    async def delete_session_messages(self, session_id: str) -> bool:
        """Delete all messages for a session."""
        try:
            response = (
                self.db.table(self.table_name)
                .delete()
                .eq("session_id", session_id)
                .execute()
            )
            
            logger.info(f"Deleted messages for session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete session messages {session_id}: {e}")
            raise
    
    async def get_message_count(self, session_id: str) -> int:
        """Get count of messages in a session."""
        try:
            response = (
                self.db.table(self.table_name)
                .select("id", count="exact")
                .eq("session_id", session_id)
                .execute()
            )
            
            return response.count or 0
            
        except Exception as e:
            logger.error(f"Failed to get message count for session {session_id}: {e}")
            raise
