"""
Mirage Agent Worker

LiveKit agent worker with:
- Gemini 2.0 Flash for real-time conversation
- Simli for avatar animation
- Multi-agent personality support

Usage:
    python worker.py dev     # Development mode with hot reload
    python worker.py start   # Production mode
"""

import os
import logging
from dotenv import load_dotenv

from livekit.agents import (
    Agent,
    AgentSession,
    JobContext,
    WorkerOptions,
    cli,
)
from livekit.plugins import google, simli

try:
    from agent.agents.registry import get_agent_config
    from agent.emotion import EmotionAwareSessionHandler
except ModuleNotFoundError:
    from agents.registry import get_agent_config
    from emotion import EmotionAwareSessionHandler

# Load environment from parent directory
load_dotenv("../.env")
load_dotenv(".env")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("mirage-agent")


class MirageAgent(Agent):
    """
    Mirage AI Agent with configurable personality.
    
    Inherits from LiveKit Agent and configures based on agent type.
    """
    
    def __init__(self, agent_type: str = "teacher"):
        config = get_agent_config(agent_type)
        super().__init__(instructions=config["instructions"])
        self.agent_type = agent_type
        self.config = config
        logger.info(f"Created MirageAgent with type: {agent_type}")


async def entrypoint(ctx: JobContext):
    """
    Main entry point for the LiveKit agent.
    
    This function is called when a user joins a room.
    It sets up the agent session with Gemini, Simli, and emotion detection.
    """
    logger.info(f"Agent job started for room: {ctx.room.name}")
    
    # Get agent type and session info from room metadata
    room_metadata = ctx.room.metadata or "{}"
    try:
        import json
        metadata = json.loads(room_metadata) if room_metadata else {}
        agent_type = metadata.get("agent_type", "teacher")
        session_id = metadata.get("session_id")
        auth_token = metadata.get("auth_token")
    except:
        agent_type = "teacher"
        session_id = None
        auth_token = None
    
    logger.info(f"Using agent type: {agent_type}")
    if session_id:
        logger.info(f"Session ID: {session_id}")
    
    # Get agent config
    agent_config = get_agent_config(agent_type)
    
    # Create agent session with Gemini
    # Using Google's realtime model for low-latency voice
    session = AgentSession(
        llm=google.realtime.RealtimeModel(
            model="gemini-2.0-flash-exp",  # Gemini 2.0 Flash
            voice=agent_config.get("voice", "Puck"),
        ),
    )
    
    # Initialize emotion-aware session handler
    emotion_enabled = os.getenv("ENABLE_EMOTION_MAPPING", "true").lower() == "true"
    emotion_handler = None
    
    if emotion_enabled:
        try:
            emotion_handler = EmotionAwareSessionHandler(
                session=session,
                agent_type=agent_type,
                session_id=session_id,
                auth_token=auth_token
            )
            logger.info("✅ Emotion mapping enabled")
        except Exception as e:
            logger.warning(f"Failed to initialize emotion handler: {e}")
            logger.info("Continuing without emotion mapping")
    else:
        logger.info("Emotion mapping disabled")
    
    # Configure Simli avatar if API key is available
    simli_api_key = os.getenv("SIMLI_API_KEY")
    simli_face_id = os.getenv("SIMLI_FACE_ID", "tmp9i8bbq7c")
    
    if simli_api_key:
        logger.info("Configuring Simli avatar")
        try:
            simli_avatar = simli.AvatarSession(
                simli_config=simli.SimliConfig(
                    api_key=simli_api_key,
                    face_id=simli_face_id,
                ),
            )
            # Start avatar - it will stream to the room
            await simli_avatar.start(session, room=ctx.room)
            logger.info("Simli avatar started successfully")
        except Exception as e:
            logger.warning(f"Failed to start Simli avatar: {e}")
            logger.info("Continuing without avatar")
    else:
        logger.info("SIMLI_API_KEY not set, running without avatar")
    
    # Create the agent instance
    agent = MirageAgent(agent_type)
    
    # Set up emotion-aware message handling
    if emotion_handler:
        # Store original instructions
        base_instructions = agent_config["instructions"]
        
        # Hook into session to detect emotions and adapt personality
        @session.on("user_speech_committed")
        async def on_user_speech(message):
            """Process user speech for emotion detection."""
            try:
                # Extract text from message
                text = message.content if hasattr(message, 'content') else str(message)
                
                if not text or len(text.strip()) < 3:
                    return
                
                # Detect emotion
                emotion_data = await emotion_handler.process_user_message(text)
                
                if emotion_data and emotion_data["emotion"] != "neutral":
                    # Adapt instructions based on emotion
                    adapted_instructions = emotion_handler.get_adapted_instructions(
                        base_instructions,
                        emotion_data
                    )
                    
                    # Update agent instructions for next response
                    agent.instructions = adapted_instructions
                    
                    logger.info(f"📊 Adapted personality for {emotion_data['emotion']} emotion")
            except Exception as e:
                logger.error(f"Error in emotion detection: {e}")
    
    # Start the session
    await session.start(
        agent=agent,
        room=ctx.room,
    )
    
    logger.info("Agent session started")
    
    # Generate initial greeting
    greeting = agent_config.get("greeting", "Hello! How can I help you today?")
    await session.generate_reply(instructions=f"Greet the user: '{greeting}'")
    
    logger.info("Initial greeting sent")


def main():
    """Main entry point for the worker."""
    logger.info("=" * 60)
    logger.info("🎭 Mirage Agent Worker")
    logger.info("=" * 60)
    
    # Log configuration
    logger.info(f"LIVEKIT_URL: {os.getenv('LIVEKIT_URL', 'NOT SET')}")
    logger.info(f"GOOGLE_API_KEY: {'✅ Set' if os.getenv('GOOGLE_API_KEY') else '❌ Not set'}")
    logger.info(f"SIMLI_API_KEY: {'✅ Set' if os.getenv('SIMLI_API_KEY') else '❌ Not set'}")
    
    # Emotion mapping configuration
    emotion_enabled = os.getenv("ENABLE_EMOTION_MAPPING", "true").lower() == "true"
    logger.info(f"EMOTION_MAPPING: {'✅ Enabled' if emotion_enabled else '❌ Disabled'}")
    if emotion_enabled:
        interval = os.getenv("EMOTION_ANALYSIS_INTERVAL", "5")
        threshold = os.getenv("EMOTION_CONFIDENCE_THRESHOLD", "0.6")
        logger.info(f"  - Analysis interval: {interval}s")
        logger.info(f"  - Confidence threshold: {threshold}")
    
    logger.info("=" * 60)
    
    # Run the LiveKit agent CLI
    cli.run_app(
        WorkerOptions(
            entrypoint_fnc=entrypoint,
        ),
    )


if __name__ == "__main__":
    main()
