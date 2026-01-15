"""
Emotion analysis service using Google Gemini.

Provides sentiment analysis and emotion detection for user messages.
"""

import os
import json
import logging
from typing import Dict, Any, Optional
from datetime import datetime

from google import genai

from app.config import get_settings
from app.utils.logging import get_logger
from app.services.emotion_config import (
    EMOTION_CATEGORIES,
    GEMINI_MODEL_NAME,
    get_valence_arousal,
    is_valid_emotion,
    get_emotion_categories_str,
    EMOTION_ANALYSIS_PROMPT_TEMPLATE
)

logger = get_logger(__name__)
settings = get_settings()




class EmotionService:
    """Service for emotion detection and analysis using Gemini."""
    
    def __init__(self):
        """Initialize the emotion service with Gemini client."""
        self.client = None
        if settings.GOOGLE_API_KEY:
            try:
                self.client = genai.Client(api_key=settings.GOOGLE_API_KEY)
                logger.info("Emotion service initialized with Gemini")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        else:
            logger.warning("GOOGLE_API_KEY not set, emotion analysis disabled")
    
    async def analyze_text_sentiment(
        self, 
        text: str,
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Analyze sentiment from text using Gemini.
        
        Args:
            text: The text to analyze
            context: Optional conversation context
            
        Returns:
            Dictionary with emotion, confidence, and metadata
        """
        if not self.client:
            return self._get_neutral_emotion()
        
        try:
            # Build prompt for emotion analysis
            prompt = self._build_emotion_prompt(text, context)
            
            # Call Gemini for analysis
            response = self.client.models.generate_content(
                model=GEMINI_MODEL_NAME,
                contents=prompt
            )
            
            # Parse response
            emotion_data = self._parse_emotion_response(response.text)
            
            logger.info(f"Analyzed emotion: {emotion_data['emotion']} (confidence: {emotion_data['confidence']})")
            
            return emotion_data
            
        except Exception as e:
            logger.error(f"Error analyzing text sentiment: {e}")
            return self._get_neutral_emotion()
    
    def calculate_valence_arousal(self, emotion: str) -> Dict[str, float]:
        """
        Calculate valence (positive/negative) and arousal (energy) for emotion.
        
        Args:
            emotion: Detected emotion category
            
        Returns:
            Dictionary with valence and arousal values
        """
        return get_valence_arousal(emotion)
    
    def _build_emotion_prompt(
        self, 
        text: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """Build prompt for Gemini emotion analysis."""
        
        emotion_list = get_emotion_categories_str()
        prompt = EMOTION_ANALYSIS_PROMPT_TEMPLATE.format(
            emotion_categories=emotion_list,
            text=text
        )

        if context:
            prompt += f"\n\nConversation context: {json.dumps(context)}"
        
        return prompt
    
    def _parse_emotion_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini's emotion analysis response."""
        try:
            # Try to extract JSON from response
            # Gemini might wrap it in markdown code blocks
            response_text = response_text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])
            
            # Parse JSON
            data = json.loads(response_text)
            
            # Validate emotion category
            emotion = data.get("emotion", "neutral")
            if not is_valid_emotion(emotion):
                logger.warning(f"Invalid emotion category: {emotion}, defaulting to neutral")
                emotion = "neutral"
            
            # Get valence and arousal
            va = self.calculate_valence_arousal(emotion)
            
            return {
                "emotion": emotion,
                "confidence": float(data.get("confidence", 0.5)),
                "intensity": float(data.get("intensity", 0.5)),
                "valence": va["valence"],
                "arousal": va["arousal"],
                "reasoning": data.get("reasoning", ""),
                "detected_at": datetime.utcnow().isoformat()
            }
            
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse emotion response as JSON: {e}")
            logger.debug(f"Response text: {response_text}")
            return self._get_neutral_emotion()
        except Exception as e:
            logger.error(f"Error parsing emotion response: {e}")
            return self._get_neutral_emotion()
    
    def _get_neutral_emotion(self) -> Dict[str, Any]:
        """Return neutral emotion as fallback."""
        return {
            "emotion": "neutral",
            "confidence": 1.0,
            "intensity": 0.5,
            "valence": 0.0,
            "arousal": 0.5,
            "reasoning": "Default neutral emotion",
            "detected_at": datetime.utcnow().isoformat()
        }


# Singleton instance
_emotion_service: Optional[EmotionService] = None


def get_emotion_service() -> EmotionService:
    """Get or create emotion service singleton."""
    global _emotion_service
    if _emotion_service is None:
        _emotion_service = EmotionService()
    return _emotion_service
