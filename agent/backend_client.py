"""
Backend API client for agent worker.

Handles saving messages and other backend interactions.
"""

import os
import logging
from typing import Optional, Dict, Any
import httpx

logger = logging.getLogger("mirage-agent.backend-client")


class BackendClient:
    """Client for interacting with Mirage backend API."""
    
    def __init__(
        self,
        backend_url: Optional[str] = None,
        auth_token: Optional[str] = None,
        timeout: float = 5.0
    ):
        """
        Initialize backend client.
        
        Args:
            backend_url: Backend API URL (defaults to env BACKEND_URL)
            auth_token: Authentication token for API requests
            timeout: Request timeout in seconds
        """
        self.backend_url = backend_url or os.getenv("BACKEND_URL", "http://localhost:8000")
        self.auth_token = auth_token
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    @property
    async def client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def close(self):
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    def _get_headers(self) -> Dict[str, str]:
        """Get request headers with auth token."""
        headers = {"Content-Type": "application/json"}
        if self.auth_token:
            headers["Authorization"] = f"Bearer {self.auth_token}"
        return headers
    
    async def save_message(
        self,
        session_id: str,
        role: str,
        content: str,
        audio_url: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save a message to the backend.
        
        Args:
            session_id: Session ID
            role: Message role ('user' or 'assistant')
            content: Message content
            audio_url: Optional audio URL
            metadata: Optional metadata
            
        Returns:
            True if successful, False otherwise
        """
        if not self.auth_token:
            logger.warning("No auth token, cannot save message")
            return False
        
        try:
            client = await self.client
            response = await client.post(
                f"{self.backend_url}/api/v1/messages/save",
                json={
                    "session_id": session_id,
                    "role": role,
                    "content": content,
                    "audio_url": audio_url,
                    "metadata": metadata or {}
                },
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                logger.info(f"✅ Saved {role} message to session {session_id}")
                return True
            else:
                logger.warning(
                    f"Failed to save message: {response.status_code} - {response.text}"
                )
                return False
                
        except Exception as e:
            logger.error(f"Error saving message: {e}")
            return False
    
    async def store_emotion(
        self,
        session_id: str,
        emotion_data: Dict[str, Any],
        message_text: str
    ) -> bool:
        """
        Store emotion analysis in backend.
        
        Args:
            session_id: Session ID
            emotion_data: Detected emotion data
            message_text: Message that was analyzed
            
        Returns:
            True if successful, False otherwise
        """
        if not self.auth_token:
            logger.debug("No auth token, skipping emotion storage")
            return False
        
        try:
            client = await self.client
            response = await client.post(
                f"{self.backend_url}/api/v1/emotions/analyze",
                json={
                    "text": message_text,
                    "session_id": session_id,
                    "context": emotion_data
                },
                headers=self._get_headers()
            )
            
            if response.status_code == 200:
                logger.debug("Stored emotion event in backend")
                return True
            else:
                logger.warning(f"Failed to store emotion: {response.status_code}")
                return False
                
        except Exception as e:
            logger.error(f"Error storing emotion: {e}")
            return False
