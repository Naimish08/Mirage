# Mirage - Voice AI Avatar Platform

Real-time voice AI backend with animated avatar responses.

## Architecture

```
User (Browser) ←→ LiveKit ←→ Mirage Backend ←→ Gemini 2.0 Flash
                                    ↓                ↑
                              Simli Avatar ←→ Emotion Mapping
```

## Features

- **Real-time Voice AI**: Low-latency conversation using Gemini 2.0 Flash.
- **Animated Avatars**: High-fidelity video responses powered by Simli.
- **Emotional Mapping**: Detects user emotions and dynamically adapts agent personality.
- **Session Management**: Full conversation history and emotional journey tracking.
- **Multi-Agent Support**: Switch between different personalities (Teacher, Consultant, Coach, etc.).

## Quick Start

### 1. Setup Environment
```bash
cd Mirage
python -m venv venv
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
```

### 2. Configure API Keys
```bash
cp .env.example .env
# Edit .env with your API keys
```

### 3. Run Database Migrations
Run SQL files from `backend/migrations/` in Supabase SQL Editor.

### 4. Start Backend API
```bash
cd backend
uvicorn app.main:app --reload --port 8000
```

### 5. Start Agent Worker
```bash
cd agent
python worker.py dev
```

## Components

- **backend/** - FastAPI REST API (auth, users, sessions)
- **agent/** - LiveKit agent worker (Gemini + Simli)

## API Keys Required

- [Supabase](https://supabase.com) - Database & Auth
- [LiveKit](https://cloud.livekit.io) - Real-time audio/video
- [Google AI Studio](https://aistudio.google.com) - Gemini API
- [Simli](https://app.simli.com) - Avatar animation