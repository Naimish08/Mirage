'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'motion/react';
import { ArrowRight, Brain, Heart, VideoCamera } from '@phosphor-icons/react';
import { useSupabaseAuth } from '@/hooks/useSupabaseAuth';

export function LandingPage() {
    const { user, loading, signIn, signUp, signOut } = useSupabaseAuth();
    const [isLogin, setIsLogin] = useState(true);
    const [email, setEmail] = useState('');
    const [password, setPassword] = useState('');
    const [fullName, setFullName] = useState('');
    const [authLoading, setAuthLoading] = useState(false);
    const [authError, setAuthError] = useState('');
    const [authMessage, setAuthMessage] = useState('');

    const handleAuth = async (e: React.FormEvent) => {
        e.preventDefault();
        setAuthLoading(true);
        setAuthError('');
        setAuthMessage('');

        if (isLogin) {
            const { error } = await signIn(email, password);
            if (error) {
                setAuthError(error.message);
            }
        } else {
            if (!fullName.trim()) {
                setAuthError('Full name is required');
                setAuthLoading(false);
                return;
            }
            const { error } = await signUp(email, password, fullName);
            if (error) {
                setAuthError(error.message);
            } else {
                setAuthMessage('Please check your email and click the verification link to complete your registration.');
            }
        }

        setAuthLoading(false);
    };

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-[#0a0d14] text-white">
                <div>Loading...</div>
            </div>
        );
    }

    return (
        <div className="relative min-h-screen w-full overflow-hidden bg-[#0a0d14] text-white font-sans selection:bg-cyan-500/30">
            {/* Background Elements */}
            <div className="absolute inset-0 z-0 select-none">
                <img
                    src="/landing-bg.png"
                    alt="Background"
                    className="h-full w-full object-cover opacity-80"
                />
                <div className="absolute inset-0 bg-gradient-to-b from-[#0a0d14]/80 via-transparent to-[#0a0d14]" />
                <div className="absolute inset-0 bg-[url('https://grainy-gradients.vercel.app/noise.svg')] opacity-20 brightness-100 contrast-150 mix-blend-overlay"></div>
            </div>

            {/* Hero Content */}
            <div className="relative z-10 flex min-h-screen flex-col">
                {/* Header */}
                <header className="w-full p-6 md:p-10">
                    <div className="mx-auto flex max-w-7xl items-center justify-between">
                        <div className="flex items-center gap-2">
                            <div className="size-8 rounded-lg bg-gradient-to-br from-cyan-400 to-blue-600"></div>
                            <span className="text-xl font-bold tracking-tight">LIVEKIT AGENTS</span>
                        </div>
                        <nav className="hidden md:flex items-center gap-8 text-sm font-medium text-white/60">
                            <Link href="#" className="hover:text-white transition-colors">Personas</Link>
                            <Link href="#" className="hover:text-white transition-colors">Features</Link>
                            <Link href="#" className="hover:text-white transition-colors">Docs</Link>
                        </nav>
                        {user ? (
                            user.email_confirmed_at ? (
                                <div className="flex items-center gap-4">
                                    <span className="text-sm text-white/60">
                                        Welcome, {user.user_metadata?.full_name || user.email?.split('@')[0]}
                                    </span>
                                    <button
                                        onClick={signOut}
                                        className="rounded-full bg-white/10 px-4 py-2 text-sm font-semibold text-white/90 backdrop-blur-md transition-all hover:bg-white/20 border border-white/10"
                                    >
                                        Sign Out
                                    </button>
                                </div>
                            ) : (
                                <div className="flex items-center gap-4">
                                    <span className="text-sm text-yellow-400">
                                        Please check your email and verify your account
                                    </span>
                                    <button
                                        onClick={signOut}
                                        className="rounded-full bg-white/10 px-4 py-2 text-sm font-semibold text-white/90 backdrop-blur-md transition-all hover:bg-white/20 border border-white/10"
                                    >
                                        Sign Out
                                    </button>
                                </div>
                            )
                        ) : (
                            <div className="flex items-center gap-4">
                                <button
                                    onClick={() => setIsLogin(true)}
                                    className={`px-4 py-2 text-sm font-semibold transition-all ${isLogin ? 'text-cyan-400' : 'text-white/60 hover:text-white'}`}
                                >
                                    Sign In
                                </button>
                                <button
                                    onClick={() => setIsLogin(false)}
                                    className={`px-4 py-2 text-sm font-semibold transition-all ${!isLogin ? 'text-cyan-400' : 'text-white/60 hover:text-white'}`}
                                >
                                    Sign Up
                                </button>
                            </div>
                        )}
                    </div>
                </header>

                <main className="flex flex-1 flex-col items-center justify-center px-4 text-center">
                    {user ? (
                        user.email_confirmed_at ? (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.8, ease: "easeOut" }}
                                className="mx-auto max-w-2xl"
                            >
                                <h1 className="mb-6 text-4xl font-extrabold tracking-tight md:text-6xl leading-[1.1]">
                                    <span className="block text-transparent bg-clip-text bg-gradient-to-b from-white to-white/60 drop-shadow-sm">
                                        Welcome back,
                                    </span>
                                    <span className="block text-transparent bg-clip-text bg-gradient-to-r from-cyan-200 via-white to-cyan-200 drop-shadow-[0_0_30px_rgba(0,255,255,0.3)]">
                                        {user?.user_metadata?.full_name || user?.email?.split('@')[0]}
                                    </span>
                                </h1>
                                <p className="mx-auto mb-12 max-w-xl text-lg text-white/50 md:text-xl font-light leading-relaxed">
                                    Ready to continue your conversation with our AI assistant?
                                </p>
                                <Link href="/agent">
                                    <button className="group relative rounded-full px-8 py-4 text-lg font-semibold text-white transition-all hover:scale-105 active:scale-95">
                                        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500 blur-md opacity-70 group-hover:opacity-100 transition-opacity duration-300"></div>
                                        <div className="absolute inset-0 rounded-full bg-gradient-to-r from-cyan-400 to-blue-500"></div>
                                        <span className="relative flex items-center gap-2">
                                            Enter Agent
                                            <ArrowRight weight="bold" />
                                        </span>
                                    </button>
                                </Link>
                            </motion.div>
                        ) : (
                            <motion.div
                                initial={{ opacity: 0, y: 20 }}
                                animate={{ opacity: 1, y: 0 }}
                                transition={{ duration: 0.8, ease: "easeOut" }}
                                className="mx-auto max-w-md"
                            >
                                <h1 className="mb-6 text-4xl font-extrabold tracking-tight md:text-5xl leading-[1.1]">
                                    <span className="block text-transparent bg-clip-text bg-gradient-to-b from-white to-white/60 drop-shadow-sm">
                                        Check Your Email
                                    </span>
                                </h1>
                                <p className="mx-auto mb-8 text-lg text-white/70">
                                    We've sent a verification link to <strong>{user.email}</strong>.
                                    Please click the link to verify your account and start chatting with our AI assistant.
                                </p>
                                <div className="text-sm text-white/50">
                                    Didn't receive the email? Check your spam folder or{' '}
                                    <button
                                        onClick={() => {
                                            // You could implement resend verification here
                                            alert('Resend functionality would be implemented here');
                                        }}
                                        className="text-cyan-400 hover:text-cyan-300 underline"
                                    >
                                        click here to resend
                                    </button>
                                </div>
                            </motion.div>
                        )
                    ) : (
                        <motion.div
                            initial={{ opacity: 0, y: 20 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.8, ease: "easeOut" }}
                            className="mx-auto max-w-md"
                        >
                            <h1 className="mb-6 text-4xl font-extrabold tracking-tight md:text-5xl leading-[1.1]">
                                <span className="block text-transparent bg-clip-text bg-gradient-to-b from-white to-white/60 drop-shadow-sm">
                                    {isLogin ? 'Sign In' : 'Sign Up'}
                                </span>
                                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-cyan-200 via-white to-cyan-200 drop-shadow-[0_0_30px_rgba(0,255,255,0.3)]">
                                    to Continue
                                </span>
                            </h1>
                            <form onSubmit={handleAuth} className="space-y-4">
                                {!isLogin && (
                                    <div>
                                        <input
                                            type="text"
                                            placeholder="Full Name"
                                            value={fullName}
                                            onChange={(e) => setFullName(e.target.value)}
                                            className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-cyan-400"
                                            required
                                        />
                                    </div>
                                )}
                                <div>
                                    <input
                                        type="email"
                                        placeholder="Email"
                                        value={email}
                                        onChange={(e) => setEmail(e.target.value)}
                                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-cyan-400"
                                        required
                                    />
                                </div>
                                <div>
                                    <input
                                        type="password"
                                        placeholder="Password"
                                        value={password}
                                        onChange={(e) => setPassword(e.target.value)}
                                        className="w-full px-4 py-3 bg-white/10 border border-white/20 rounded-lg text-white placeholder-white/50 focus:outline-none focus:ring-2 focus:ring-cyan-400"
                                        required
                                    />
                                </div>
                                {authError && (
                                    <div className="text-red-400 text-sm">{authError}</div>
                                )}
                                {authMessage && (
                                    <div className="text-green-400 text-sm">{authMessage}</div>
                                )}
                                <button
                                    type="submit"
                                    disabled={authLoading}
                                    className="w-full py-3 bg-gradient-to-r from-cyan-400 to-blue-500 rounded-lg font-semibold text-white hover:from-cyan-500 hover:to-blue-600 transition-all disabled:opacity-50"
                                >
                                    {authLoading ? 'Loading...' : (isLogin ? 'Sign In' : 'Sign Up')}
                                </button>
                            </form>
                            <div className="mt-6 text-white/60">
                                {isLogin ? "Don't have an account? " : "Already have an account? "}
                                <button
                                    onClick={() => setIsLogin(!isLogin)}
                                    className="text-cyan-400 hover:text-cyan-300 transition-colors"
                                >
                                    {isLogin ? 'Sign Up' : 'Sign In'}
                                </button>
                            </div>
                        </motion.div>
                    )}
                </main>
            </div>
        </div>
    );
}

function FeatureCard({ icon, title, description, color }: { icon: React.ReactNode; title: string; description: string, color: 'pink' | 'cyan' | 'purple' }) {
    const glowColors = {
        pink: 'group-hover:shadow-[0_0_40px_rgba(244,114,182,0.3)]',
        cyan: 'group-hover:shadow-[0_0_40px_rgba(34,211,238,0.3)]',
        purple: 'group-hover:shadow-[0_0_40px_rgba(192,132,252,0.3)]',
    }
    return (
        <div className={`group relative rounded-3xl border border-white/5 bg-white/5 p-8 backdrop-blur-sm transition-all duration-500 hover:-translate-y-2 hover:bg-white/10 ${glowColors[color]}`}>
            <div className="mb-6 inline-flex rounded-2xl bg-white/5 p-4 shadow-inner ring-1 ring-white/10">
                {icon}
            </div>
            <h3 className="mb-3 text-xl font-bold text-white">{title}</h3>
            <p className="text-white/60 leading-relaxed">{description}</p>
        </div>
    );
}
