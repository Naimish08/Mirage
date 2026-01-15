"""
Emotion detector with rate limiting for Gemini API.

Detects user emotions from text with intelligent caching and rate limiting
to avoid hitting Gemini API quotas.
"""

import os
import time
import asyncio
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
import logging

from google import genai

try:
    from agent.emotion.emotion_config import (
        EMOTION_CATEGORIES,
        GEMINI_MODEL_NAME,
        RATE_LIMIT_CALLS,
        RATE_LIMIT_WINDOW,
        EMOTION_CACHE_TTL,
        MIN_ANALYSIS_INTERVAL,
        get_valence_arousal,
        is_valid_emotion,
        get_emotion_categories_str,
        EMOTION_ANALYSIS_PROMPT_TEMPLATE
    )
except ModuleNotFoundError:
    from emotion.emotion_config import (
        EMOTION_CATEGORIES,
        GEMINI_MODEL_NAME,
        RATE_LIMIT_CALLS,
        RATE_LIMIT_WINDOW,
        EMOTION_CACHE_TTL,
        MIN_ANALYSIS_INTERVAL,
        get_valence_arousal,
        is_valid_emotion,
        get_emotion_categories_str,
        EMOTION_ANALYSIS_PROMPT_TEMPLATE
    )

logger = logging.getLogger("mirage-agent.emotion")


class RateLimiter:
    """Simple rate limiter to prevent API quota exhaustion."""
    
    def __init__(self, max_calls: int = 10, time_window: int = 60):
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum number of calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = []
    
    def can_call(self) -> bool:
        """Check if a call can be made without exceeding rate limit."""
        now = time.time()
        
        # Remove calls outside the time window
        self.calls = [call_time for call_time in self.calls 
                     if now - call_time < self.time_window]
        
        return len(self.calls) < self.max_calls
    
    def record_call(self):
        """Record a successful API call."""
        self.calls.append(time.time())
    
    def time_until_next_call(self) -> float:
        """Get seconds until next call is allowed."""
        if self.can_call():
            return 0.0
        
        # Time until oldest call expires
        oldest_call = min(self.calls)
        return self.time_window - (time.time() - oldest_call)


class EmotionCache:
    """Cache recent emotion detections to reduce API calls."""
    
    def __init__(self, ttl_seconds: int = 30):
        """
        Initialize emotion cache.
        
        Args:
            ttl_seconds: Time-to-live for cached emotions
        """
        self.ttl_seconds = ttl_seconds
        self.cache: Dict[str, Dict[str, Any]] = {}
    
    def get(self, text_hash: str) -> Optional[Dict[str, Any]]:
        """Get cached emotion if still valid."""
        if text_hash not in self.cache:
            return None
        
        cached = self.cache[text_hash]
        age = time.time() - cached["timestamp"]
        
        if age > self.ttl_seconds:
            del self.cache[text_hash]
            return None
        
        return cached["emotion"]
    
    def set(self, text_hash: str, emotion: Dict[str, Any]):
        """Cache an emotion detection result."""
        self.cache[text_hash] = {
            "emotion": emotion,
            "timestamp": time.time()
        }
    
    def clear_old(self):
        """Clear expired cache entries."""
        now = time.time()
        expired = [
            key for key, value in self.cache.items()
            if now - value["timestamp"] > self.ttl_seconds
        ]
        for key in expired:
            del self.cache[key]


class EmotionDetector:
    """
    Emotion detector with rate limiting and caching.
    
    Features:
    - Rate limiting to prevent API quota exhaustion
    - Caching to reduce redundant API calls
    - Fallback to neutral emotion when limits are hit
    - Configurable analysis interval
    """
    
    def __init__(
        self,
        api_key: Optional[str] = None,
        rate_limit_calls: int = RATE_LIMIT_CALLS,
        rate_limit_window: int = RATE_LIMIT_WINDOW,
        cache_ttl: int = EMOTION_CACHE_TTL,
        min_analysis_interval: int = MIN_ANALYSIS_INTERVAL
    ):
        """
        Initialize emotion detector.
        
        Args:
            api_key: Google API key (defaults to env var)
            rate_limit_calls: Max API calls per time window
            rate_limit_window: Time window in seconds
            cache_ttl: Cache time-to-live in seconds
            min_analysis_interval: Minimum seconds between analyses
        """
        self.api_key = api_key or os.getenv("GOOGLE_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                self.client = genai.Client(api_key=self.api_key)
                logger.info("Emotion detector initialized with Gemini")
            except Exception as e:
                logger.error(f"Failed to initialize Gemini client: {e}")
        else:
            logger.warning("GOOGLE_API_KEY not set, emotion detection disabled")
        
        # Rate limiting and caching
        self.rate_limiter = RateLimiter(rate_limit_calls, rate_limit_window)
        self.cache = EmotionCache(cache_ttl)
        self.min_analysis_interval = min_analysis_interval
        self.last_analysis_time = 0
        self.last_emotion = self._get_neutral_emotion()
    
    async def detect_emotion(
        self, 
        text: str,
        force: bool = False
    ) -> Dict[str, Any]:
        """
        Detect emotion from text with rate limiting.
        
        Args:
            text: Text to analyze
            force: Force analysis even if interval hasn't elapsed
            
        Returns:
            Dictionary with emotion data
        """
        # Check if enough time has passed since last analysis
        if not force:
            time_since_last = time.time() - self.last_analysis_time
            if time_since_last < self.min_analysis_interval:
                logger.debug(f"Skipping analysis, only {time_since_last:.1f}s since last")
                return self.last_emotion
        
        # Check cache
        text_hash = str(hash(text.lower().strip()))
        cached_emotion = self.cache.get(text_hash)
        if cached_emotion:
            logger.debug("Using cached emotion")
            return cached_emotion
        
        # Check rate limit
        if not self.rate_limiter.can_call():
            wait_time = self.rate_limiter.time_until_next_call()
            logger.warning(f"Rate limit hit, next call available in {wait_time:.1f}s")
            return self.last_emotion
        
        # Perform analysis
        if not self.client:
            return self._get_neutral_emotion()
        
        try:
            emotion_data = await self._analyze_with_gemini(text)
            
            # Record successful call
            self.rate_limiter.record_call()
            self.last_analysis_time = time.time()
            self.last_emotion = emotion_data
            
            # Cache result
            self.cache.set(text_hash, emotion_data)
            
            logger.info(f"Detected emotion: {emotion_data['emotion']} (confidence: {emotion_data['confidence']:.2f})")
            
            return emotion_data
            
        except Exception as e:
            logger.error(f"Error detecting emotion: {e}")
            return self.last_emotion
    
    async def _analyze_with_gemini(self, text: str) -> Dict[str, Any]:
        """Analyze text with Gemini API."""
        prompt = self._build_prompt(text)
        
        response = self.client.models.generate_content(
            model=GEMINI_MODEL_NAME,
            contents=prompt
        )
        
        return self._parse_response(response.text)
    
    def _build_prompt(self, text: str) -> str:
        """Build emotion analysis prompt."""
        emotion_list = get_emotion_categories_str()
        
        return f"""Analyze the emotional tone of this text and classify it into ONE category: {emotion_list}.

Text: "{text}"

Respond with ONLY a JSON object:
{{
    "emotion": "category",
    "confidence": 0.0-1.0,
    "intensity": 0.0-1.0
}}

Be concise and accurate."""
    
    def _parse_response(self, response_text: str) -> Dict[str, Any]:
        """Parse Gemini response."""
        import json
        
        try:
            # Remove markdown code blocks
            response_text = response_text.strip()
            if response_text.startswith("```"):
                lines = response_text.split("\n")
                response_text = "\n".join(lines[1:-1])
            
            data = json.loads(response_text)
            
            emotion = data.get("emotion", "neutral")
            if not is_valid_emotion(emotion):
                emotion = "neutral"
            
            # Calculate valence and arousal
            va = get_valence_arousal(emotion)
            
            return {
                "emotion": emotion,
                "confidence": float(data.get("confidence", 0.5)),
                "intensity": float(data.get("intensity", 0.5)),
                "valence": va["valence"],
                "arousal": va["arousal"],
                "detected_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to parse emotion response: {e}")
            return self._get_neutral_emotion()

    
    def _get_neutral_emotion(self) -> Dict[str, Any]:
        """Return neutral emotion as fallback."""
        return {
            "emotion": "neutral",
            "confidence": 1.0,
            "intensity": 0.5,
            "valence": 0.0,
            "arousal": 0.5,
            "detected_at": datetime.utcnow().isoformat()
        }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get detector statistics."""
        return {
            "rate_limit": {
                "calls_made": len(self.rate_limiter.calls),
                "max_calls": self.rate_limiter.max_calls,
                "time_window": self.rate_limiter.time_window,
                "can_call": self.rate_limiter.can_call(),
                "wait_time": self.rate_limiter.time_until_next_call()
            },
            "cache": {
                "size": len(self.cache.cache),
                "ttl": self.cache.ttl_seconds
            },
            "last_emotion": self.last_emotion["emotion"],
            "last_analysis": self.last_analysis_time
        }
