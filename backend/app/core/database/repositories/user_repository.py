"""
User repository for managing user data.
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


class UserRepository:
    """Repository for user data operations."""
    
    def __init__(self, db_client: Client):
        self.db = db_client
        self.table_name = TableNames.USERS
    
    async def create_user(self, user_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new user."""
        try:
            # Set defaults and timestamps
            user_data["created_at"] = datetime.utcnow().isoformat()
            user_data["updated_at"] = datetime.utcnow().isoformat()
            
            if "is_active" not in user_data:
                user_data["is_active"] = True
            if "preferences" not in user_data:
                user_data["preferences"] = {}
            if "preferred_agent_type" not in user_data:
                user_data["preferred_agent_type"] = "teacher"
            
            serialized_data = serialize_for_db(user_data)
            response = self.db.table(self.table_name).insert(serialized_data).execute()
            
            result = handle_supabase_response(response)
            logger.info(f"Created user with ID: {result.get('id')}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to create user: {e}")
            raise

    async def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get user by ID."""
        try:
            response = self.db.table(self.table_name).select("*").eq("id", user_id).execute()
            
            if not response.data:
                return None
            
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Failed to get user {user_id}: {e}")
            raise
    
    async def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        """Get user by email."""
        try:
            response = self.db.table(self.table_name).select("*").eq("email", email).execute()
            
            if not response.data:
                return None
            
            return response.data[0]
            
        except Exception as e:
            logger.error(f"Failed to get user by email {email}: {e}")
            raise
    
    async def update_user(self, user_id: str, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update user data."""
        try:
            update_data["updated_at"] = datetime.utcnow().isoformat()
            serialized_data = serialize_for_db(update_data)
            
            response = (
                self.db.table(self.table_name)
                .update(serialized_data)
                .eq("id", user_id)
                .execute()
            )
            
            if not response.data:
                raise RecordNotFoundError(f"User {user_id} not found")
            
            result = handle_supabase_response(response)
            logger.info(f"Updated user {user_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to update user {user_id}: {e}")
            raise
        
    async def delete_user(self, user_id: str) -> bool:
        """Delete user."""
        try:
            response = self.db.table(self.table_name).delete().eq("id", user_id).execute()
            
            if not response.data:
                raise RecordNotFoundError(f"User {user_id} not found")
            
            logger.info(f"Deleted user {user_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete user {user_id}: {e}")
            raise
    
    async def update_last_login(self, user_id: str) -> Dict[str, Any]:
        """Update user's last login timestamp."""
        try:
            update_data = {
                "last_login_at": datetime.utcnow().isoformat(),
                "updated_at": datetime.utcnow().isoformat()
            }
            
            serialized_data = serialize_for_db(update_data)
            
            response = (
                self.db.table(self.table_name)
                .update(serialized_data)
                .eq("id", user_id)
                .execute()
            )
            
            if not response.data:
                raise RecordNotFoundError(f"User {user_id} not found")
            
            result = handle_supabase_response(response)
            logger.info(f"Updated last login for user {user_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to update last login for user {user_id}: {e}")
            raise

    async def update_preferences(self, user_id: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """Update user preferences."""
        try:
            update_data = {
                "preferences": preferences,
                "updated_at": datetime.utcnow().isoformat()
            }
            
            if "preferred_agent_type" in preferences:
                update_data["preferred_agent_type"] = preferences["preferred_agent_type"]
            
            serialized_data = serialize_for_db(update_data)
            
            response = (
                self.db.table(self.table_name)
                .update(serialized_data)
                .eq("id", user_id)
                .execute()
            )
            
            if not response.data:
                raise RecordNotFoundError(f"User {user_id} not found")
            
            result = handle_supabase_response(response)
            logger.info(f"Updated preferences for user {user_id}")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to update preferences for user {user_id}: {e}")
            raise
