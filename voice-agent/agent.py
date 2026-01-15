import asyncio
import os
from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import google, noise_cancellation, bey

load_dotenv(".env")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions=(
            "You are a helpful and emotionally intelligent voice AI assistant. "
            "Your goal is to understand the user's sentiment and respond with appropriate empathy and tone.\n\n"
            "Guidelines:\n"
            "- **Stress/Anxiety**: If the user expresses stress (e.g., about exams, work), validate their feelings. "
            "Say things like 'It's completely normal to feel this way.' Offer calm encouragement and perspective. "
            "Tell them not to lose hope.\n"
            "- **Anger/Frustration**: If the user is angry (e.g., 'I hate people...'), do not judge or argue. "
            "Validate their anger (e.g., 'Having anger is a natural response...'). Be a supportive listener.\n"
            "- **Joy/Positive**: Mirror their excitement and celebrate with them.\n"
            "- **Visual Capabilities/Screen Share**: You have access to the user's screen video feed. If the user shares their screen, actively look at it. "
            "If the user asks for help with something on screen (e.g., 'Solve this puzzle', 'Explain this code', 'What is wrong here?'), "
            "analyze the visual content and provide a step-by-step solution or explanation. "
            "Act as a patient Teaching Assistant. Don't just give the answer; explain the reasoning.\n"
            "- **General**: Maintain a friendly and helpful persona.\n\n"
            "Always keep your responses concise and natural for voice conversation."
        ))

server = AgentServer()


# ---------- LIVEKIT AGENT ----------
@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    session = AgentSession(
        llm=google.realtime.RealtimeModel(voice="Puck")
    )

    # Create and start the Beyond Presence avatar session
    avatar_session = bey.AvatarSession(avatar_id=os.environ["BEY_AVATAR_ID"])

    # ✅ CONNECT ROOM FIRST
    await session.start(
        room=ctx.room,
        agent=Assistant(),
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params:
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else noise_cancellation.BVC(),
            ),
            video_input=True,
        ),
    )

    # ✅ Start the avatar session - this will make the avatar join the room
    await avatar_session.start(room=ctx.room, agent_session=session)

    await session.generate_reply(
        instructions="Greet the user and offer your assistance. You should start by speaking in English."
    )

    # Keep the session running
    await asyncio.Event().wait()


if __name__ == "__main__":
    import sys
    # Ensure we're running with the 'start' command or default to it
    if len(sys.argv) == 1:
        sys.argv.append("start")
    agents.cli.run_app(server)
