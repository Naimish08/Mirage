-- =============================================================================
-- MIRAGE - Messages Table Migration
-- Run this in Supabase SQL Editor AFTER 02_sessions_table.sql
-- =============================================================================

-- Create messages table
CREATE TABLE IF NOT EXISTS messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    role TEXT NOT NULL, -- 'user' or 'assistant'
    content TEXT NOT NULL,
    audio_url TEXT,     -- Optional: URL to stored audio
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_messages_session_id ON messages(session_id);
CREATE INDEX IF NOT EXISTS idx_messages_created_at ON messages(created_at);

-- Add comment
COMMENT ON TABLE messages IS 'Mirage conversation messages with optional audio storage';
