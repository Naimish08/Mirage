import asyncio
from dotenv import load_dotenv

from livekit import agents, rtc
from livekit.agents import AgentServer, AgentSession, Agent, room_io
from livekit.plugins import google, noise_cancellation
import mss
import numpy as np
from PIL import Image

load_dotenv(".env")

class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(instructions="You are a helpful voice AI assistant.")

server = AgentServer()

# ---------- SCREEN CAPTURE ----------
async def capture_screen(source: rtc.VideoSource, width: int, height: int):
    """Continuously capture screen frames and feed them to the video source."""
    with mss.mss() as sct:
        # Get the primary monitor
        monitor = sct.monitors[1]
        target_size = (width, height)
        
        while True:
            try:
                # Capture screenshot
                screenshot = sct.grab(monitor)
                
                # Convert to numpy array (BGRA format)
                img = np.array(screenshot)
                
                # Resize if needed
                if img.shape[:2] != target_size[::-1]:
                    pil_img = Image.fromarray(img)
                    pil_img = pil_img.resize(target_size, Image.Resampling.LANCZOS)
                    img = np.array(pil_img)
                
                # Convert BGRA to RGBA
                img_rgba = np.zeros_like(img)
                img_rgba[:, :, 0] = img[:, :, 2]  # R
                img_rgba[:, :, 1] = img[:, :, 1]  # G
                img_rgba[:, :, 2] = img[:, :, 0]  # B
                img_rgba[:, :, 3] = img[:, :, 3]  # A
                
                # Create video frame
                frame = rtc.VideoFrame(
                    width, height,
                    rtc.VideoBufferType.RGBA,
                    img_rgba.tobytes()
                )
                
                # Capture frame
                source.capture_frame(frame)
                
                # Target 15 FPS
                await asyncio.sleep(1 / 15)
            except Exception as e:
                print(f"Error capturing screen: {e}")
                await asyncio.sleep(1 / 15)


# ---------- LIVEKIT AGENT ----------
@server.rtc_session()
async def my_agent(ctx: agents.JobContext):
    session = AgentSession(
        llm=google.realtime.RealtimeModel(voice="Puck")
    )

    WIDTH = 1920
    HEIGHT = 1080

    video_source = rtc.VideoSource(WIDTH, HEIGHT)
    video_track = rtc.LocalVideoTrack.create_video_track(
        "screen-share", video_source
    )

    publish_options = rtc.TrackPublishOptions(
        source=rtc.TrackSource.SOURCE_CAMERA,
        simulcast=True,
        video_encoding=rtc.VideoEncoding(
            max_framerate=15,
            max_bitrate=1_500_000,
        ),
        video_codec=rtc.VideoCodec.H264,
    )

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

    # ✅ Publish AFTER connect
    await ctx.room.local_participant.publish_track(
        video_track, publish_options
    )

    # Start screen capture in background
    capture_task = asyncio.create_task(capture_screen(video_source, WIDTH, HEIGHT))

    await session.generate_reply(
        instructions="Greet the user and offer your assistance. You should start by speaking in English."
    )

    # Keep the capture task running
    try:
        await capture_task
    except asyncio.CancelledError:
        pass


if __name__ == "__main__":
    agents.cli.run_app(server)
