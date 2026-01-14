-- =============================================================================
-- MIRAGE - Sessions Table Migration
-- Run this in Supabase SQL Editor AFTER 01_users_table.sql
-- =============================================================================

-- Create sessions table
CREATE TABLE IF NOT EXISTS sessions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id) ON DELETE CASCADE,
    agent_type TEXT NOT NULL DEFAULT 'teacher',
    livekit_room_name TEXT,
    title TEXT DEFAULT 'New Chat',
    status TEXT DEFAULT 'active',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    last_activity_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_sessions_user_id ON sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_sessions_status ON sessions(status);
CREATE INDEX IF NOT EXISTS idx_sessions_last_activity ON sessions(last_activity_at DESC);

-- Add comment
COMMENT ON TABLE sessions IS 'Mirage chat sessions with agent type and LiveKit room tracking';
