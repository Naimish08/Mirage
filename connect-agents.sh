#!/bin/bash

# Script to sync LiveKit credentials from voice-agent to agent-frontend
# This connects the two components without modifying voice-agent

VOICE_AGENT_ENV="/home/nash/Desktop/Mirage/voice-agent/.env"
FRONTEND_ENV="/home/nash/Desktop/Mirage/agent-frontend/.env.local"

echo "🔗 Connecting agent-frontend to voice-agent..."
echo ""

# Check if voice-agent .env exists
if [ ! -f "$VOICE_AGENT_ENV" ]; then
    echo "❌ Error: voice-agent .env file not found at $VOICE_AGENT_ENV"
    echo "   Make sure voice-agent is configured first."
    exit 1
fi

# Extract credentials from voice-agent .env
echo "📖 Reading credentials from voice-agent..."
LIVEKIT_URL=$(grep "^LIVEKIT_URL=" "$VOICE_AGENT_ENV" | cut -d '=' -f2-)
LIVEKIT_API_KEY=$(grep "^LIVEKIT_API_KEY=" "$VOICE_AGENT_ENV" | cut -d '=' -f2-)
LIVEKIT_API_SECRET=$(grep "^LIVEKIT_API_SECRET=" "$VOICE_AGENT_ENV" | cut -d '=' -f2-)

# Validate credentials
if [ -z "$LIVEKIT_URL" ] || [ -z "$LIVEKIT_API_KEY" ] || [ -z "$LIVEKIT_API_SECRET" ]; then
    echo "❌ Error: Missing LiveKit credentials in voice-agent .env"
    echo "   Please ensure LIVEKIT_URL, LIVEKIT_API_KEY, and LIVEKIT_API_SECRET are set."
    exit 1
fi

# Create .env.local for frontend
echo "✍️  Writing credentials to agent-frontend/.env.local..."

cat > "$FRONTEND_ENV" << EOF
# Environment variables for agent-frontend
# Auto-generated from voice-agent configuration
# Generated on: $(date)

# LiveKit Configuration (synced from voice-agent)
LIVEKIT_API_KEY=$LIVEKIT_API_KEY
LIVEKIT_API_SECRET=$LIVEKIT_API_SECRET
LIVEKIT_URL=$LIVEKIT_URL

# Agent dispatch (https://docs.livekit.io/agents/server/agent-dispatch)
# Leave AGENT_NAME blank to enable automatic dispatch
# Provide an agent name to enable explicit dispatch
AGENT_NAME=

# Internally used environment variables
NEXT_PUBLIC_APP_CONFIG_ENDPOINT=
SANDBOX_ID=
EOF

echo ""
echo "✅ Success! agent-frontend is now connected to voice-agent"
echo ""
echo "📋 Configuration:"
echo "   LIVEKIT_URL: $LIVEKIT_URL"
echo "   LIVEKIT_API_KEY: ${LIVEKIT_API_KEY:0:10}..."
echo "   LIVEKIT_API_SECRET: ${LIVEKIT_API_SECRET:0:10}..."
echo ""
echo "🚀 Next steps:"
echo "   1. Start voice-agent:"
echo "      cd /home/nash/Desktop/Mirage/voice-agent"
echo "      source .venv/bin/activate"
echo "      python agent.py dev"
echo ""
echo "   2. Start agent-frontend (in another terminal):"
echo "      cd /home/nash/Desktop/Mirage/agent-frontend"
echo "      pnpm dev"
echo ""
echo "   3. Open http://localhost:3000 in your browser"
echo ""
