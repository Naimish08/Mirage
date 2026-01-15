#!/bin/bash

# =============================================================================
# Mirage Database Setup Script
# =============================================================================
# This script helps you set up the Supabase database for Mirage.
# Run this after configuring your .env file with Supabase credentials.
# =============================================================================

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Mirage Database Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}❌ Error: .env file not found${NC}"
    echo -e "${YELLOW}Please copy .env.example to .env and fill in your credentials${NC}"
    exit 1
fi

# Load environment variables
source .env

# Check required variables
if [ -z "$SUPABASE_URL" ] || [ "$SUPABASE_URL" == "https://your-project-id.supabase.co" ]; then
    echo -e "${RED}❌ Error: SUPABASE_URL not configured in .env${NC}"
    exit 1
fi

if [ -z "$SUPABASE_SERVICE_KEY" ] || [ "$SUPABASE_SERVICE_KEY" == "your-supabase-service-role-key" ]; then
    echo -e "${RED}❌ Error: SUPABASE_SERVICE_KEY not configured in .env${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Environment variables loaded${NC}"
echo -e "${YELLOW}Supabase URL: $SUPABASE_URL${NC}"
echo ""

# Extract project ID from URL
PROJECT_ID=$(echo $SUPABASE_URL | sed -n 's/.*\/\/\([^.]*\).*/\1/p')

if [ -z "$PROJECT_ID" ]; then
    echo -e "${RED}❌ Error: Could not extract project ID from SUPABASE_URL${NC}"
    exit 1
fi

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Manual Setup Instructions${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "${YELLOW}Since Supabase migrations require SQL Editor access, please:${NC}"
echo ""
echo -e "1. Open Supabase Dashboard: ${GREEN}https://supabase.com/dashboard/project/${PROJECT_ID}/editor${NC}"
echo ""
echo -e "2. Run the following SQL files in order:"
echo ""
echo -e "   ${BLUE}a)${NC} backend/migrations/01_users_table.sql"
echo -e "   ${BLUE}b)${NC} backend/migrations/02_sessions_table.sql"
echo -e "   ${BLUE}c)${NC} backend/migrations/03_messages_table.sql"
echo -e "   ${BLUE}d)${NC} backend/migrations/04_emotion_tracking.sql"
echo ""
echo -e "3. For each file:"
echo -e "   - Open the SQL Editor in Supabase Dashboard"
echo -e "   - Copy the contents of the migration file"
echo -e "   - Paste into the SQL Editor"
echo -e "   - Click 'Run' to execute"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  Alternative: Run via psql${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "If you have ${GREEN}psql${NC} installed, you can run migrations directly:"
echo ""
echo -e "${GREEN}psql \"postgresql://postgres:[PASSWORD]@db.$PROJECT_ID.supabase.co:5432/postgres\" \\${NC}"
echo -e "${GREEN}  -f backend/migrations/01_users_table.sql \\${NC}"
echo -e "${GREEN}  -f backend/migrations/02_sessions_table.sql \\${NC}"
echo -e "${GREEN}  -f backend/migrations/03_messages_table.sql \\${NC}"
echo -e "${GREEN}  -f backend/migrations/04_emotion_tracking.sql${NC}"
echo ""
echo -e "${YELLOW}Note: Replace [PASSWORD] with your database password${NC}"
echo ""
echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}  After Running Migrations${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""
echo -e "1. Verify tables were created in Supabase → Table Editor"
echo -e "2. Expected tables:"
echo -e "   ${GREEN}✓${NC} users"
echo -e "   ${GREEN}✓${NC} sessions"
echo -e "   ${GREEN}✓${NC} messages"
echo -e "   ${GREEN}✓${NC} emotion_events"
echo ""
echo -e "3. Start the backend server:"
echo -e "   ${GREEN}cd backend && uvicorn app.main:app --reload --port 8000${NC}"
echo ""
echo -e "${GREEN}✅ Setup instructions complete!${NC}"
echo ""
