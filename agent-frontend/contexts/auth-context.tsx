'use client';

import {
    createContext,
    useContext,
    useEffect,
    useState,
    ReactNode
} from 'react';
import { User, Session } from '@supabase/supabase-js';
import { supabase, getCurrentUser, signOut as supabaseSignOut } from '@/lib/supabase';
import { authAPI, usersAPI } from '@/lib/api-client';

interface AuthContextType {
    user: User | null;
    session: Session | null;
    profile: any | null;
    isLoading: boolean;
    isAuthenticated: boolean;
    signOut: () => Promise<void>;
    refreshProfile: () => Promise<void>;
}

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
    const [user, setUser] = useState<User | null>(null);
    const [session, setSession] = useState<Session | null>(null);
    const [profile, setProfile] = useState<any | null>(null);
    const [isLoading, setIsLoading] = useState(true);

    // Initialize auth state
    useEffect(() => {
        const initializeAuth = async () => {
            try {
                const { data: { session } } = await supabase.auth.getSession();
                setSession(session);
                setUser(session?.user ?? null);

                if (session?.user) {
                    try {
                        // Try to fetch profile from backend
                        // This verifies the token works with our backend
                        const userProfile = await usersAPI.getProfile();
                        setProfile(userProfile);
                    } catch (error) {
                        console.error('Failed to fetch user profile:', error);
                    }
                }
            } catch (error) {
                console.error('Error initializing auth:', error);
            } finally {
                setIsLoading(false);
            }
        };

        initializeAuth();

        // Listen for auth changes
        const { data: { subscription } } = supabase.auth.onAuthStateChange(
            async (event, session) => {
                setSession(session);
                setUser(session?.user ?? null);
                setIsLoading(false);

                if (event === 'SIGNED_IN' && session?.user) {
                    try {
                        const userProfile = await usersAPI.getProfile();
                        setProfile(userProfile);
                    } catch (error) {
                        console.error('Failed to fetch profile after sign in:', error);
                    }
                } else if (event === 'SIGNED_OUT') {
                    setProfile(null);
                }
            }
        );

        return () => {
            subscription.unsubscribe();
        };
    }, []);

    const signOut = async () => {
        await supabaseSignOut();
        setUser(null);
        setSession(null);
        setProfile(null);
    };

    const refreshProfile = async () => {
        if (user) {
            try {
                const userProfile = await usersAPI.getProfile();
                setProfile(userProfile);
            } catch (error) {
                console.error('Failed to refresh profile:', error);
            }
        }
    };

    const value = {
        user,
        session,
        profile,
        isLoading,
        isAuthenticated: !!user,
        signOut,
        refreshProfile
    };

    return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
    const context = useContext(AuthContext);
    if (context === undefined) {
        throw new Error('useAuth must be used within an AuthProvider');
    }
    return context;
}
