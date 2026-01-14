"""
Agent types endpoints for Mirage backend.
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List

from app.api.dependencies import get_optional_current_user
from app.utils.logging import get_logger

router = APIRouter()
logger = get_logger(__name__)


# Define available agent types
AGENT_TYPES = {
    "teacher": {
        "id": "teacher",
        "name": "Teacher",
        "description": "Patient and educational, explains concepts clearly with encouragement",
        "personality": "Educational, patient, encouraging, uses examples",
        "icon": "👩‍🏫"
    },
    "consultant": {
        "id": "consultant",
        "name": "Consultant",
        "description": "Professional and analytical, provides strategic advice",
        "personality": "Professional, analytical, strategic, problem-solving",
        "icon": "💼"
    },
    "coach": {
        "id": "coach",
        "name": "Life Coach",
        "description": "Motivational and supportive, helps with personal growth",
        "personality": "Motivational, supportive, empathetic, goal-oriented",
        "icon": "🌟"
    },
    "friend": {
        "id": "friend",
        "name": "Friendly Chat",
        "description": "Casual and friendly, great for general conversation",
        "personality": "Casual, friendly, humorous, relatable",
        "icon": "😊"
    }
}


@router.get("/")
async def list_agent_types():
    """List all available agent types."""
    return {
        "agents": list(AGENT_TYPES.values()),
        "default": "teacher"
    }


@router.get("/{agent_id}")
async def get_agent_type(agent_id: str):
    """Get details for a specific agent type."""
    agent = AGENT_TYPES.get(agent_id)
    
    if not agent:
        return {
            "error": "Agent type not found",
            "available": list(AGENT_TYPES.keys())
        }
    
    return agent


def get_agent_config(agent_type: str) -> Dict[str, Any]:
    """
    Get agent configuration for LiveKit worker.
    
    Used by the agent worker to configure personality.
    """
    agent = AGENT_TYPES.get(agent_type, AGENT_TYPES["teacher"])
    
    # Build instructions based on agent type
    base_instructions = """You are a helpful AI assistant with voice interaction capabilities. 
Respond naturally and conversationally. Keep responses concise for voice delivery.
Do not use markdown formatting, emojis, or special characters in your responses."""
    
    personality_instructions = {
        "teacher": """
You are a patient and educational teacher. You:
- Explain concepts clearly and thoroughly
- Use examples and analogies to aid understanding
- Encourage questions and curiosity
- Celebrate learning progress
- Break down complex topics into simpler parts""",
        
        "consultant": """
You are a professional business consultant. You:
- Provide strategic and analytical insights
- Focus on practical, actionable advice
- Ask clarifying questions to understand the problem
- Consider multiple perspectives and options
- Speak with authority and confidence""",
        
        "coach": """
You are a motivational life coach. You:
- Are supportive and encouraging
- Help identify goals and create action plans
- Celebrate wins and reframe setbacks
- Listen actively and show empathy
- Ask powerful questions to promote self-reflection""",
        
        "friend": """
You are a friendly and casual chat companion. You:
- Are warm, approachable, and relatable
- Use casual language and light humor
- Share in conversations naturally
- Are genuinely interested in what the user says
- Keep things light and enjoyable"""
    }
    
    instructions = base_instructions + personality_instructions.get(
        agent_type, 
        personality_instructions["teacher"]
    )
    
    return {
        "id": agent["id"],
        "name": agent["name"],
        "instructions": instructions,
        "personality": agent["personality"]
    }
