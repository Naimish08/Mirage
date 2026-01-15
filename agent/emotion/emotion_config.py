"""
Configuration constants for Emotion Mapping feature.

This module centralizes all emotion mapping configuration to avoid hardcoding.
Values can be customized here or overridden via environment variables.
"""

import os
from typing import List, Dict, Any


# =============================================================================
# Emotion Categories
# =============================================================================
EMOTION_CATEGORIES: List[str] = [
    "happy",
    "sad",
    "angry",
    "anxious",
    "neutral",
    "excited",
    "confused",
    "frustrated"
]


# =============================================================================
# Valence-Arousal Mapping
# =============================================================================
# Based on Circumplex Model of Affect
# Valence: -1.0 (negative) to 1.0 (positive)
# Arousal: 0.0 (low energy) to 1.0 (high energy)
EMOTION_VALENCE_AROUSAL: Dict[str, Dict[str, float]] = {
    "happy": {"valence": 0.8, "arousal": 0.6},
    "excited": {"valence": 0.9, "arousal": 0.9},
    "sad": {"valence": -0.7, "arousal": 0.3},
    "anxious": {"valence": -0.5, "arousal": 0.8},
    "angry": {"valence": -0.8, "arousal": 0.9},
    "frustrated": {"valence": -0.6, "arousal": 0.7},
    "confused": {"valence": -0.3, "arousal": 0.5},
    "neutral": {"valence": 0.0, "arousal": 0.5}
}


# =============================================================================
# Gemini API Configuration
# =============================================================================
GEMINI_MODEL_NAME: str = os.getenv(
    "GEMINI_MODEL_NAME",
    "gemini-2.0-flash-exp"
)


# =============================================================================
# Rate Limiting Configuration
# =============================================================================
# These can be customized based on your Gemini API tier
RATE_LIMIT_CALLS: int = int(os.getenv("EMOTION_RATE_LIMIT_CALLS", "10"))
RATE_LIMIT_WINDOW: int = int(os.getenv("EMOTION_RATE_LIMIT_WINDOW", "60"))
EMOTION_CACHE_TTL: int = int(os.getenv("EMOTION_CACHE_TTL", "30"))


# =============================================================================
# Analysis Configuration
# =============================================================================
MIN_ANALYSIS_INTERVAL: int = int(os.getenv("EMOTION_ANALYSIS_INTERVAL", "5"))
CONFIDENCE_THRESHOLD: float = float(os.getenv("EMOTION_CONFIDENCE_THRESHOLD", "0.6"))
ENABLE_EMOTION_MAPPING: bool = os.getenv("ENABLE_EMOTION_MAPPING", "true").lower() == "true"


# =============================================================================
# Backend API Configuration
# =============================================================================
BACKEND_URL: str = os.getenv("BACKEND_URL", "http://localhost:8000")
BACKEND_API_TIMEOUT: int = int(os.getenv("BACKEND_API_TIMEOUT", "5"))


# =============================================================================
# Prompt Templates
# =============================================================================
EMOTION_ANALYSIS_PROMPT_TEMPLATE: str = """Analyze the emotional tone of the following text and classify it into one of these categories: {emotion_categories}.

Text to analyze: "{text}"

Respond ONLY with a JSON object in this exact format:
{{
    "emotion": "category_name",
    "confidence": 0.0-1.0,
    "intensity": 0.0-1.0,
    "reasoning": "brief explanation"
}}

Consider:
- The words used and their emotional connotations
- The overall tone and sentiment
- Any indicators of frustration, confusion, excitement, etc.
- Context clues about the speaker's state of mind

Be precise and choose the most appropriate single emotion category."""


# =============================================================================
# Helper Functions
# =============================================================================
def get_valence_arousal(emotion: str) -> Dict[str, float]:
    """
    Get valence and arousal values for an emotion.
    
    Args:
        emotion: Emotion category
        
    Returns:
        Dictionary with valence and arousal values
    """
    return EMOTION_VALENCE_AROUSAL.get(
        emotion,
        {"valence": 0.0, "arousal": 0.5}  # Default to neutral
    )


def is_valid_emotion(emotion: str) -> bool:
    """
    Check if an emotion is valid.
    
    Args:
        emotion: Emotion category to validate
        
    Returns:
        True if valid, False otherwise
    """
    return emotion in EMOTION_CATEGORIES


def get_emotion_categories_str() -> str:
    """
    Get emotion categories as a comma-separated string.
    
    Returns:
        Comma-separated string of emotion categories
    """
    return ", ".join(EMOTION_CATEGORIES)
