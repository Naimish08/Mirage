'use client';

import { useState } from 'react';
import { signIn, signUp } from '@/lib/supabase';
import { Button } from '@/components/livekit/button';

interface LoginFormProps {
    onSuccess?: () => void;
}

export function LoginForm({ onSuccess }: LoginFormProps) {
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);
    const [message, setMessage] = useState<string | null>(null);

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError(null);
        setMessage(null);

        try {
            if (isLogin) {
                await signIn(email, password);
                if (onSuccess) onSuccess();
            } else {
                await signUp(email, password, fullName);
                setMessage('Registration successful! Please check your email to confirm your account.');
                // Don't call onSuccess yet for signup as they might need to confirm email
                // or if auto-confirm is on, supabase might sign them in auto.
                // If the backend handles auto-confirm, they might be signed in.
            }
        } catch (err: any) {
            console.error('Auth error:', err);
            setError(err.message || 'An error occurred');
        } finally {
            setLoading(false);
        }
    };

    return (
        <div className="w-full max-w-sm p-6 bg-black/40 backdrop-blur-md rounded-xl border border-white/10 shadow-xl">
            <h2 className="text-2xl font-bold mb-6 text-center text-white">
                {isLogin ? 'Welcome Back' : 'Create Account'}
            </h2>

            <form onSubmit={handleSubmit} className="space-y-4">
                <div>
                    <label className="block text-sm font-medium text-white/70 mb-1">Email</label>
                    <input
                        type="email"
                        value={email}
                        onChange={(e) => setEmail(e.target.value)}
                        required
                        className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 text-white placeholder-white/30"
                        placeholder="you@example.com"
                    />
                </div>

                {!isLogin && (
                    <div>
                        <label className="block text-sm font-medium text-white/70 mb-1">Full Name</label>
                        <input
                            type="text"
                            value={fullName}
                            onChange={(e) => setFullName(e.target.value)}
                            required
                            className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 text-white placeholder-white/30"
                            placeholder="John Doe"
                        />
                    </div>
                )}

                <div>
                    <label className="block text-sm font-medium text-white/70 mb-1">Password</label>
                    <input
                        type="password"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        required
                        minLength={6}
                        className="w-full px-4 py-2 bg-white/5 border border-white/10 rounded-lg focus:outline-none focus:ring-2 focus:ring-cyan-500 text-white placeholder-white/30"
                        placeholder="••••••••"
                    />
                </div>

                {error && (
                    <div className="p-3 bg-red-500/20 border border-red-500/50 rounded-lg text-red-200 text-sm">
                        {error}
                    </div>
                )}

                {message && (
                    <div className="p-3 bg-green-500/20 border border-green-500/50 rounded-lg text-green-200 text-sm">
                        {message}
                    </div>
                )}

                <Button
                    type="submit"
                    className="w-full bg-cyan-600 hover:bg-cyan-500 text-white font-medium py-2 rounded-lg transition-colors"
                    disabled={loading}
                >
                    {loading ? 'Processing...' : (isLogin ? 'Sign In' : 'Sign Up')}
                </Button>
            </form>

            <div className="mt-6 text-center text-sm text-white/50">
                {isLogin ? "Don't have an account? " : "Already have an account? "}
                <button
                    onClick={() => {
                        setIsLogin(!isLogin);
                        setError(null);
                        setMessage(null);
                    }}
                    className="text-cyan-400 hover:text-cyan-300 font-medium focus:outline-none"
                >
                    {isLogin ? 'Sign Up' : 'Sign In'}
                </button>
            </div>
        </div>
    );
}
