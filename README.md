# Mirage - Voice AI Avatar Platform

Real-time voice AI backend with animated avatar responses.

## Architecture

```
User (Browser) ←→ LiveKit ←→ Mirage Backend ←→ Gemini 2.0 Flash
                                    ↓
                              Simli Avatar
```

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