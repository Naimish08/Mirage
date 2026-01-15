'use client';

import React from 'react';
import Link from 'next/link';
import { motion } from 'motion/react';
import { ArrowRight, Brain, Heart, VideoCamera } from '@phosphor-icons/react';

export function LandingPage() {
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
                        <Link href="/agent">
                            <button className="rounded-full bg-white/10 px-6 py-2 text-sm font-semibold text-white/90 backdrop-blur-md transition-all hover:bg-white/20 border border-white/10 shadow-[0_0_20px_rgba(0,255,255,0.1)] hover:shadow-[0_0_30px_rgba(0,255,255,0.2)]">
                                Join us!
                            </button>
                        </Link>
                    </div>
                </header>

                <main className="flex flex-1 flex-col items-center justify-center px-4 text-center">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ duration: 0.8, ease: "easeOut" }}
                        className="mx-auto max-w-7xl"
                    >
                        <h1 className="mb-6 text-5xl font-extrabold tracking-tight md:text-7xl leading-[1.1]">
                            <span className="block text-transparent bg-clip-text bg-gradient-to-b from-white to-white/60 drop-shadow-sm">
                                AN AI THAT TRULY
                            </span>
                            <span className="block text-transparent bg-clip-text bg-gradient-to-r from-cyan-200 via-white to-cyan-200 drop-shadow-[0_0_30px_rgba(0,255,255,0.3)]">
                                UNDERSTANDS YOU.
                            </span>
                        </h1>
                        <p className="mx-auto mb-12 max-w-2xl text-lg text-white/50 md:text-xl font-light leading-relaxed">
                            Beyond information. It recognizes your emotions, adapts to your mood, and provides legitimate support when you need it most.
                        </p>

                        {/* Hero Visual Placeholder - Replicating the laptop/phone composition */}
                        <div className="relative mx-auto mt-16 w-full max-w-5xl">
                            <div className="relative aspect-[16/9] w-full rounded-2xl border border-white/10 bg-white/5 shadow-2xl backdrop-blur-sm overflow-hidden flex items-center justify-center group">
                                <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/10 to-purple-500/10 opacity-50 group-hover:opacity-70 transition-opacity duration-700"></div>
                                <div className="text-white/20 font-mono text-sm">Interactive Demo Preview</div>
                                {/* Glowing orb effect behind */}
                                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 h-[50%] w-[50%] rounded-full bg-cyan-400/20 blur-[100px]"></div>
                            </div>
                        </div>

                        {/* Feature Grid */}
                        <div className="mt-32 grid grid-cols-1 gap-8 text-left md:grid-cols-3">
                            <FeatureCard
                                icon={<Heart weight="duotone" className="size-8 text-pink-400" />}
                                title="Empathetic Guides"
                                description="From expert advice to casual console, choose your perfect guide and mode."
                                color="pink"
                            />
                            <FeatureCard
                                icon={<VideoCamera weight="duotone" className="size-8 text-cyan-400" />}
                                title="Adaptive Presence"
                                description="Video or honest chat, choose your perfect position and mode."
                                color="cyan"
                            />
                            <FeatureCard
                                icon={<Brain weight="duotone" className="size-8 text-purple-400" />}
                                title="Emotional Intelligence"
                                description="Instant connection to neither erotand your conmstion experience."
                                color="purple"
                            />
                        </div>
                    </motion.div>
                </main>

                <footer className="w-full p-10 flex justify-center pb-20">
                    <Link href="/agent">
                        <button className="group relative rounded-full px-8 py-4 text-lg font-semibold text-white transition-all hover:scale-105 active:scale-95">
                            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-orange-400 to-pink-500 blur-md opacity-70 group-hover:opacity-100 transition-opacity duration-300"></div>
                            <div className="absolute inset-0 rounded-full bg-gradient-to-r from-orange-400 to-pink-500"></div>
                            <span className="relative flex items-center gap-2">
                                Experience Supportive AI
                                <ArrowRight weight="bold" />
                            </span>
                        </button>
                    </Link>
                </footer>
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
