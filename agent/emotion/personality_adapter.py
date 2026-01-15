"""
Personality adapter for emotion-aware agent responses.

Dynamically adjusts agent instructions based on detected user emotions.
"""

import logging
from typing import Dict, Any, Optional

logger = logging.getLogger("mirage-agent.personality")


# Emotion-specific instruction modifiers for each agent type
EMOTION_ADAPTATIONS = {
    "teacher": {
        "happy": """
The user seems happy and engaged! Match their positive energy:
- Celebrate their enthusiasm
- Build on their momentum
- Use encouraging language
- Keep the pace upbeat
""",
        "excited": """
The user is very excited! Channel that energy:
- Share in their excitement
- Keep explanations dynamic and engaging
- Use vivid examples
- Maintain high energy in your responses
""",
        "confused": """
The user seems confused. Adjust your teaching approach:
- Slow down and break concepts into smaller steps
- Use simpler language and more examples
- Check for understanding frequently
- Be patient and reassuring
- Offer to explain in a different way
""",
        "frustrated": """
The user appears frustrated. Provide extra support:
- Acknowledge that this is challenging
- Break the problem down into manageable pieces
- Offer encouragement and remind them of progress
- Suggest taking a different approach
- Be patient and supportive
""",
        "anxious": """
The user seems anxious. Create a calm, supportive environment:
- Use reassuring language
- Emphasize that mistakes are part of learning
- Go at a comfortable pace
- Provide clear, structured guidance
- Celebrate small wins
""",
        "sad": """
The user seems down. Be empathetic and supportive:
- Show understanding and compassion
- Keep tone gentle and encouraging
- Focus on achievable goals
- Remind them of their capabilities
- Offer positive reinforcement
""",
        "angry": """
The user seems upset. Stay calm and professional:
- Remain patient and understanding
- Acknowledge their feelings
- Focus on problem-solving
- Keep responses clear and helpful
- Don't take it personally
""",
        "neutral": """
The user has a neutral emotional state. Maintain your standard approach:
- Be clear and informative
- Stay engaged and helpful
- Adapt as their emotional state changes
"""
    },
    
    "consultant": {
        "happy": "The client is positive. Leverage this momentum to explore opportunities and make progress.",
        "excited": "The client is enthusiastic. Channel this energy into actionable next steps.",
        "confused": "The client needs clarity. Slow down, simplify your points, and ensure understanding before proceeding.",
        "frustrated": "The client is frustrated. Acknowledge the challenge, break it down, and focus on practical solutions.",
        "anxious": "The client is concerned. Provide reassurance, clear frameworks, and reduce uncertainty.",
        "sad": "The client seems discouraged. Be empathetic, focus on wins, and rebuild confidence.",
        "angry": "The client is upset. Stay professional, listen carefully, and focus on resolving the issue.",
        "neutral": "Maintain professional, strategic guidance."
    },
    
    "coach": {
        "happy": "The person is in a positive state! Amplify this energy and help them set ambitious goals.",
        "excited": "They're fired up! Help them channel this excitement into concrete action plans.",
        "confused": "They're uncertain. Help them gain clarity through powerful questions and reflection.",
        "frustrated": "They're struggling. Acknowledge their effort, reframe the challenge, and find a new angle.",
        "anxious": "They're worried. Create safety, validate their feelings, and help them find their center.",
        "sad": "They're feeling low. Hold space for their emotions, remind them of their strength, and find small steps forward.",
        "angry": "They're upset. Let them express it, validate the emotion, then guide toward constructive action.",
        "neutral": "Meet them where they are and help them explore what's next."
    },
    
    "friend": {
        "happy": "They're happy! Share in their joy and keep the good vibes going.",
        "excited": "They're pumped! Match their energy and have fun with it.",
        "confused": "They're not sure about something. Help them think it through in a relaxed way.",
        "frustrated": "They're annoyed. Be understanding and help them vent or find a solution.",
        "anxious": "They're stressed. Be a calming presence and supportive friend.",
        "sad": "They're down. Be there for them, listen, and offer comfort.",
        "angry": "They're mad. Let them express it and be supportive without judgment.",
        "neutral": "Just have a good, natural conversation."
    }
}


class PersonalityAdapter:
    """
    Adapts agent personality based on detected emotions.
    
    Modifies agent instructions dynamically to provide emotion-appropriate
    responses while maintaining the core personality of each agent type.
    """
    
    def __init__(self, agent_type: str = "teacher"):
        """
        Initialize personality adapter.
        
        Args:
            agent_type: Type of agent (teacher, consultant, coach, friend)
        """
        self.agent_type = agent_type
        self.current_emotion = "neutral"
        self.emotion_history = []
        logger.info(f"Personality adapter initialized for {agent_type}")
    
    def adapt_instructions(
        self,
        base_instructions: str,
        emotion_data: Dict[str, Any],
        confidence_threshold: float = 0.6
    ) -> str:
        """
        Adapt agent instructions based on detected emotion.
        
        Args:
            base_instructions: Original agent instructions
            emotion_data: Emotion detection result
            confidence_threshold: Minimum confidence to apply adaptation
            
        Returns:
            Modified instructions with emotion-aware guidance
        """
        emotion = emotion_data.get("emotion", "neutral")
        confidence = emotion_data.get("confidence", 0.0)
        
        # Only adapt if confidence is high enough
        if confidence < confidence_threshold:
            logger.debug(f"Emotion confidence too low ({confidence:.2f}), using base instructions")
            return base_instructions
        
        # Track emotion
        self.current_emotion = emotion
        self.emotion_history.append({
            "emotion": emotion,
            "confidence": confidence,
            "timestamp": emotion_data.get("detected_at")
        })
        
        # Keep only recent history (last 10)
        if len(self.emotion_history) > 10:
            self.emotion_history = self.emotion_history[-10:]
        
        # Get emotion-specific adaptation
        adaptation = self._get_adaptation(emotion)
        
        if not adaptation:
            return base_instructions
        
        # Combine base instructions with emotion adaptation
        adapted = f"""{base_instructions}

CURRENT USER EMOTIONAL STATE: {emotion.upper()} (confidence: {confidence:.0%})

ADAPT YOUR RESPONSE ACCORDINGLY:
{adaptation}

Remember to maintain your core personality while being sensitive to the user's emotional state.
"""
        
        logger.info(f"Adapted instructions for {emotion} emotion (confidence: {confidence:.2f})")
        
        return adapted
    
    def _get_adaptation(self, emotion: str) -> Optional[str]:
        """Get emotion-specific adaptation for current agent type."""
        agent_adaptations = EMOTION_ADAPTATIONS.get(self.agent_type, {})
        return agent_adaptations.get(emotion)
    
    def get_dominant_emotion(self) -> str:
        """Get the most common recent emotion."""
        if not self.emotion_history:
            return "neutral"
        
        # Count emotions in recent history
        emotion_counts = {}
        for entry in self.emotion_history[-5:]:  # Last 5 emotions
            emotion = entry["emotion"]
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # Return most common
        return max(emotion_counts, key=emotion_counts.get)
    
    def should_check_in(self) -> bool:
        """
        Determine if agent should proactively check in on user.
        
        Returns True if user has been in negative emotional state
        for multiple consecutive detections.
        """
        if len(self.emotion_history) < 3:
            return False
        
        # Check last 3 emotions
        recent = [e["emotion"] for e in self.emotion_history[-3:]]
        negative_emotions = {"sad", "frustrated", "angry", "anxious"}
        
        # If all recent emotions are negative
        return all(e in negative_emotions for e in recent)
    
    def get_stats(self) -> Dict[str, Any]:
        """Get adapter statistics."""
        return {
            "agent_type": self.agent_type,
            "current_emotion": self.current_emotion,
            "dominant_emotion": self.get_dominant_emotion(),
            "should_check_in": self.should_check_in(),
            "emotion_history_length": len(self.emotion_history),
            "recent_emotions": [e["emotion"] for e in self.emotion_history[-5:]]
        }
