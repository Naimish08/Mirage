-- =============================================================================
-- MIRAGE - Emotion Tracking Migration
-- Run this in Supabase SQL Editor AFTER 03_messages_table.sql
-- =============================================================================

-- Add emotion columns to messages table
ALTER TABLE messages 
ADD COLUMN IF NOT EXISTS sentiment TEXT,
ADD COLUMN IF NOT EXISTS sentiment_score FLOAT,
ADD COLUMN IF NOT EXISTS emotion_metadata JSONB DEFAULT '{}';

-- Create index for sentiment queries
CREATE INDEX IF NOT EXISTS idx_messages_sentiment ON messages(sentiment);

-- Create emotion_events table for detailed tracking
CREATE TABLE IF NOT EXISTS emotion_events (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    session_id UUID REFERENCES sessions(id) ON DELETE CASCADE,
    message_id UUID REFERENCES messages(id) ON DELETE SET NULL,
    emotion TEXT NOT NULL,
    confidence FLOAT NOT NULL CHECK (confidence >= 0.0 AND confidence <= 1.0),
    intensity FLOAT CHECK (intensity >= 0.0 AND intensity <= 1.0),
    valence FLOAT CHECK (valence >= -1.0 AND valence <= 1.0),  -- positive/negative scale
    arousal FLOAT CHECK (arousal >= 0.0 AND arousal <= 1.0),   -- energy level
    context JSONB DEFAULT '{}',
    detected_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for emotion_events
CREATE INDEX IF NOT EXISTS idx_emotion_events_session ON emotion_events(session_id);
CREATE INDEX IF NOT EXISTS idx_emotion_events_emotion ON emotion_events(emotion);
CREATE INDEX IF NOT EXISTS idx_emotion_events_detected_at ON emotion_events(detected_at DESC);
CREATE INDEX IF NOT EXISTS idx_emotion_events_message ON emotion_events(message_id);

-- Add emotion summary to sessions
ALTER TABLE sessions
ADD COLUMN IF NOT EXISTS emotion_summary JSONB DEFAULT '{}';

-- Add comments
COMMENT ON TABLE emotion_events IS 'Real-time emotion detection events during conversations';
COMMENT ON COLUMN messages.sentiment IS 'Detected emotion category (happy, sad, angry, anxious, neutral, excited, confused, frustrated)';
COMMENT ON COLUMN messages.sentiment_score IS 'Confidence score for emotion detection (0.0 - 1.0)';
COMMENT ON COLUMN messages.emotion_metadata IS 'Additional emotion analysis data (tone, context, etc.)';
COMMENT ON COLUMN sessions.emotion_summary IS 'Aggregated emotion statistics for the session';

-- Create view for emotion timeline
CREATE OR REPLACE VIEW emotion_timeline AS
SELECT 
    e.id,
    e.session_id,
    e.emotion,
    e.confidence,
    e.intensity,
    e.valence,
    e.arousal,
    e.detected_at,
    m.role,
    m.content,
    s.user_id,
    s.agent_type
FROM emotion_events e
LEFT JOIN messages m ON e.message_id = m.id
LEFT JOIN sessions s ON e.session_id = s.id
ORDER BY e.detected_at DESC;

COMMENT ON VIEW emotion_timeline IS 'Comprehensive view of emotion events with message and session context';
