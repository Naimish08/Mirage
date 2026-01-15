/**
 * Backend API Client
 * 
 * Provides typed methods for calling Mirage backend API endpoints.
 */

import { getSessionToken } from './supabase';

const BACKEND_URL = process.env.NEXT_PUBLIC_BACKEND_URL || 'http://localhost:8000';

/**
 * API Error class
 */
export class APIError extends Error {
    constructor(
        message: string,
        public status: number,
        public detail?: any
    ) {
        super(message);
        this.name = 'APIError';
    }
}

/**
 * Make authenticated API request
 */
async function apiRequest<T>(
    endpoint: string,
    options: RequestInit = {}
): Promise<T> {
    const token = await getSessionToken();

    const headers = new Headers(options.headers);
    headers.set('Content-Type', 'application/json');

    if (token) {
        headers.set('Authorization', `Bearer ${token}`);
    }

    const response = await fetch(`${BACKEND_URL}${endpoint}`, {
        ...options,
        headers,
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new APIError(
            error.detail || 'Request failed',
            response.status,
            error
        );
    }

    // Handle empty responses (204 No Content, etc.)
    if (response.status === 204) {
        return {} as T;
    }

    return response.json();
}

// =============================================================================
// Types
// =============================================================================

export interface User {
    id: string;
    email: string;
    full_name?: string;
    avatar_url?: string;
    preferred_agent_type?: string;
    is_active: boolean;
    created_at: string;
    last_login_at?: string;
}

export interface Session {
    id: string;
    user_id: string;
    agent_type: string;
    livekit_room_name?: string;
    title: string;
    status: string;
    created_at: string;
    updated_at: string;
    last_activity_at: string;
    emotion_summary?: any;
}

export interface Message {
    id: string;
    session_id: string;
    role: 'user' | 'assistant';
    content: string;
    audio_url?: string;
    sentiment?: string;
    sentiment_score?: number;
    emotion_metadata?: any;
    metadata?: any;
    created_at: string;
}

export interface EmotionEvent {
    id: string;
    session_id: string;
    message_id?: string;
    emotion: string;
    confidence: number;
    intensity?: number;
    valence?: number;
    arousal?: number;
    context?: any;
    detected_at: string;
}

export interface LiveKitTokenRequest {
    room_name?: string;
    participant_name?: string;
    agent_name?: string;
}

export interface LiveKitTokenResponse {
    token: string;
    room_name: string;
    ws_url: string;
}

// =============================================================================
// Auth API
// =============================================================================

export const authAPI = {
    /**
     * Get current user info
     */
    async me(): Promise<User> {
        return apiRequest<User>('/api/v1/auth/me');
    },

    /**
     * Validate token
     */
    async validate(): Promise<{ valid: boolean; user_id: string; email: string }> {
        return apiRequest('/api/v1/auth/validate', { method: 'POST' });
    },
};

// =============================================================================
// Users API
// =============================================================================

export const usersAPI = {
    /**
     * Get user profile
     */
    async getProfile(): Promise<User> {
        return apiRequest<User>('/api/v1/users/profile');
    },

    /**
     * Update user profile
     */
    async updateProfile(data: Partial<User>): Promise<User> {
        return apiRequest<User>('/api/v1/users/profile', {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },
};

// =============================================================================
// Sessions API
// =============================================================================

export const sessionsAPI = {
    /**
     * Create new session
     */
    async create(data: { agent_type?: string; title?: string }): Promise<{ message: string; session: Session }> {
        return apiRequest('/api/v1/sessions/create', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },

    /**
     * List user sessions
     */
    async list(activeOnly: boolean = true): Promise<{ sessions: Session[]; count: number }> {
        return apiRequest(`/api/v1/sessions/?active_only=${activeOnly}`);
    },

    /**
     * Get session by ID
     */
    async get(sessionId: string): Promise<Session> {
        return apiRequest(`/api/v1/sessions/${sessionId}`);
    },

    /**
     * Update session
     */
    async update(sessionId: string, data: { title?: string; agent_type?: string }): Promise<{ message: string; session: Session }> {
        return apiRequest(`/api/v1/sessions/${sessionId}`, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    },

    /**
     * Delete session (soft delete)
     */
    async delete(sessionId: string): Promise<{ message: string }> {
        return apiRequest(`/api/v1/sessions/${sessionId}`, {
            method: 'DELETE',
        });
    },

    /**
     * Get session messages
     */
    async getMessages(sessionId: string, limit: number = 50, offset: number = 0): Promise<{ messages: Message[]; count: number }> {
        return apiRequest(`/api/v1/sessions/${sessionId}/messages?limit=${limit}&offset=${offset}`);
    },
};

// =============================================================================
// Agents API
// =============================================================================

export const agentsAPI = {
    /**
     * List available agent types
     */
    async list(): Promise<{ agents: any[]; count: number }> {
        return apiRequest('/api/v1/agents/');
    },

    /**
     * Get agent info
     */
    async get(agentType: string): Promise<any> {
        return apiRequest(`/api/v1/agents/${agentType}`);
    },
};

// =============================================================================
// Emotions API
// =============================================================================

export const emotionsAPI = {
    /**
     * Get emotion timeline for session
     */
    async getTimeline(sessionId: string): Promise<{ events: EmotionEvent[]; summary: any }> {
        return apiRequest(`/api/v1/emotions/timeline/${sessionId}`);
    },

    /**
     * Record emotion event
     */
    async record(data: {
        session_id: string;
        emotion: string;
        confidence: number;
        intensity?: number;
        valence?: number;
        arousal?: number;
        context?: any;
    }): Promise<{ message: string; event: EmotionEvent }> {
        return apiRequest('/api/v1/emotions/record', {
            method: 'POST',
            body: JSON.stringify(data),
        });
    },
};

// =============================================================================
// LiveKit API
// =============================================================================

export const livekitAPI = {
    /**
     * Get LiveKit room token
     */
    async getToken(request: LiveKitTokenRequest): Promise<LiveKitTokenResponse> {
        return apiRequest('/api/v1/livekit/token', {
            method: 'POST',
            body: JSON.stringify(request),
        });
    },
};

// =============================================================================
// Health API
// =============================================================================

export const healthAPI = {
    /**
     * Ping backend
     */
    async ping(): Promise<{ status: string; timestamp: string }> {
        return apiRequest('/api/v1/health/ping');
    },
};

/**
 * Combined API client
 */
export const api = {
    auth: authAPI,
    users: usersAPI,
    sessions: sessionsAPI,
    agents: agentsAPI,
    emotions: emotionsAPI,
    livekit: livekitAPI,
    health: healthAPI,
};

export default api;
