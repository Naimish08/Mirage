"""
Emotion detection and analysis module for Mirage agent worker.
"""

from .detector import EmotionDetector
from .personality_adapter import PersonalityAdapter
from .session_handler import EmotionAwareSessionHandler

__all__ = ["EmotionDetector", "PersonalityAdapter", "EmotionAwareSessionHandler"]
