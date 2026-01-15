"""
Emotion-aware session handler for Mirage agent.

Handles real-time emotion detection and personality adaptation during conversations.
"""

import os
import asyncio
import logging
from typing import Optional, Dict, Any
import httpx

from livekit.agents import AgentSession
from livekit import rtc

try:
    from agent.emotion.detector import EmotionDetector
    from agent.emotion.personality_adapter import PersonalityAdapter
    from agent.emotion.emotion_config import (
        MIN_ANALYSIS_INTERVAL,
        CONFIDENCE_THRESHOLD,
        BACKEND_URL,
        BACKEND_API_TIMEOUT
    )
except ModuleNotFoundError:
    from emotion.detector import EmotionDetector
    from emotion.personality_adapter import PersonalityAdapter
    from emotion.emotion_config import (
        MIN_ANALYSIS_INTERVAL,
        CONFIDENCE_THRESHOLD,
        BACKEND_URL,
        BACKEND_API_TIMEOUT
    )

logger = logging.getLogger("mirage-agent.emotion-session")


class EmotionAwareSessionHandler:
    """
    Handles emotion detection and adaptation during agent sessions.
    
    Features:
    - Real-time emotion detection from user messages
    - Dynamic personality adaptation
    - Backend API integration for emotion storage
    - Rate limiting to prevent API quota exhaustion
    """
    
    def __init__(
        self,
        session: AgentSession,
        agent_type: str,
        session_id: Optional[str] = None,
        backend_url: Optional[str] = None,
        auth_token: Optional[str] = None
    ):
        """
        Initialize emotion-aware session handler.
        
        Args:
            session: LiveKit agent session
            agent_type: Type of agent (teacher, consultant, etc.)
            session_id: Backend session ID for storing emotions
            backend_url: Backend API URL
            auth_token: Authentication token for backend API
        """
        self.session = session
        self.agent_type = agent_type
        self.session_id = session_id
        self.backend_url = backend_url or BACKEND_URL
        self.auth_token = auth_token
        
        # Initialize emotion modules
        rate_limit = MIN_ANALYSIS_INTERVAL
        self.detector = EmotionDetector(min_analysis_interval=rate_limit)
        self.adapter = PersonalityAdapter(agent_type)
        
        # Track conversation
        self.message_count = 0
        self.last_user_message = ""
        
        logger.info(f"Emotion-aware session handler initialized for {agent_type}")
    
    async def process_user_message(self, message_text: str) -> Optional[Dict[str, Any]]:
        """
        Process user message and detect emotion.
        
        Args:
            message_text: User's message text
            
        Returns:
            Emotion data if detected, None otherwise
        """
        if not message_text or len(message_text.strip()) < 3:
            return None
        
        self.last_user_message = message_text
        self.message_count += 1
        
        try:
            # Detect emotion
            emotion_data = await self.detector.detect_emotion(message_text)
            
            logger.info(
                f"Message {self.message_count}: {emotion_data['emotion']} "
                f"(confidence: {emotion_data['confidence']:.2f})"
            )
            
            # Store emotion in backend if session_id available
            if self.session_id and emotion_data['emotion'] != 'neutral':
                await self._store_emotion(emotion_data, message_text)
            
            return emotion_data
            
        except Exception as e:
            logger.error(f"Error processing user message: {e}")
            return None
    
    def get_adapted_instructions(self, base_instructions: str, emotion_data: Dict[str, Any]) -> str:
        """
        Get personality-adapted instructions based on emotion.
        
        Args:
            base_instructions: Original agent instructions
            emotion_data: Detected emotion data
            
        Returns:
            Adapted instructions
        """
        return self.adapter.adapt_instructions(
            base_instructions,
            emotion_data,
            CONFIDENCE_THRESHOLD
        )
    
    async def _store_emotion(self, emotion_data: Dict[str, Any], message_text: str):
        """Store emotion event in backend."""
        if not self.auth_token:
            logger.debug("No auth token, skipping emotion storage")
            return
        
        try:
            async with httpx.AsyncClient(timeout=BACKEND_API_TIMEOUT) as client:
                response = await client.post(
                    f"{self.backend_url}/api/v1/emotions/analyze",
                    json={
                        "text": message_text,
                        "session_id": self.session_id,
                        "context": {
                            "agent_type": self.agent_type,
                            "message_count": self.message_count
                        }
                    },
                    headers={"Authorization": f"Bearer {self.auth_token}"}
                )
                
                if response.status_code == 200:
                    logger.debug(f"Stored emotion event in backend")
                else:
                    logger.warning(f"Failed to store emotion: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"Error storing emotion in backend: {e}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get session statistics."""
        return {
            "session_id": self.session_id,
            "agent_type": self.agent_type,
            "message_count": self.message_count,
            "detector_stats": self.detector.get_stats(),
            "adapter_stats": self.adapter.get_stats()
        }
