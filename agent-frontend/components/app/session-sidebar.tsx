'use client';

import React, { useEffect, useState } from 'react';

import { motion, AnimatePresence } from 'motion/react';
import { ChatCircleDots, Plus, Trash, Clock, CaretLeft, CaretRight } from '@phosphor-icons/react';
import { cn } from '@/lib/utils';
import { api, type Session } from '@/lib/api';



interface SessionSidebarProps {
    onSessionSelect: (session: Session) => void;
    onNewChat: () => void;
    selectedSessionId?: string;
    isOpen?: boolean;
    onToggle?: () => void;
    className?: string;
    refreshTrigger?: number; // Add refresh trigger
}

export function SessionSidebar({
    onSessionSelect,
    onNewChat,
    selectedSessionId,
    isOpen = true,
    onToggle,
    className,
    refreshTrigger,
}: SessionSidebarProps) {
    const [sessions, setSessions] = useState<Session[]>([]);
    const [loading, setLoading] = useState(true);

    const fetchSessions = async () => {
        try {
            setLoading(true);
            const { sessions } = await api.getSessions();
            setSessions(sessions);
        } catch (error) {
            console.error('Failed to fetch sessions:', error);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        if (isOpen) {
            fetchSessions();
        }
    }, [isOpen, refreshTrigger]);

    const handleDelete = async (e: React.MouseEvent, sessionId: string) => {
        e.stopPropagation();
        try {
            await api.deleteSession(sessionId);
            setSessions((prev) => prev.filter((s) => s.id !== sessionId));
            if (selectedSessionId === sessionId) {
                onNewChat();
            }
        } catch (error) {
            console.error('Failed to delete session:', error);
        }
    };

    return (
        <div
            className={cn(
                'fixed left-0 top-0 z-50 h-full bg-black/80 backdrop-blur-2xl border-r border-white/5 transition-all duration-300 ease-in-out',
                isOpen ? 'w-[280px] translate-x-0' : 'w-0 -translate-x-full',
                className
            )}
        >
            <div className="flex flex-col h-full w-full">
                {/* Header */}
                <div className="flex items-center justify-between px-5 py-6">
                    <span className="text-lg font-bold text-white tracking-tight">
                        History
                    </span>
                    <div className="flex items-center gap-2">
                        <button
                            onClick={onNewChat}
                            className="group flex items-center justify-center p-2 rounded-full bg-white/5 hover:bg-cyan-500/20 text-white/70 hover:text-cyan-400 transition-all duration-300 ring-1 ring-white/10 hover:ring-cyan-500/30"
                            title="New Chat"
                        >
                            <Plus className="size-5" />
                        </button>
                        {onToggle && (
                            <button
                                onClick={onToggle}
                                className="md:hidden group flex items-center justify-center p-2 rounded-full bg-white/5 hover:bg-red-500/20 text-white/70 hover:text-red-400 transition-all duration-300 ring-1 ring-white/10 hover:ring-red-500/30"
                                title="Close History"
                            >
                                <CaretLeft className="size-5" />
                            </button>
                        )}
                    </div>
                </div>

                {/* Session List */}
                <div className="flex-1 overflow-y-auto px-3 pb-4 space-y-1 custom-scrollbar">
                    {loading ? (
                        <div className="flex flex-col items-center justify-center h-32 space-y-3">
                            <div className="size-5 rounded-full border-2 border-white/10 border-t-cyan-400 animate-spin" />
                            <span className="text-xs font-medium text-white/30">Loading conversations...</span>
                        </div>
                    ) : sessions.length === 0 ? (
                        <div className="flex flex-col items-center justify-center h-48 text-center px-6">
                            <div className="mb-3 p-3 rounded-full bg-white/5 text-white/20">
                                <ChatCircleDots className="size-6" />
                            </div>
                            <span className="text-sm text-white/40">No past conversations</span>
                        </div>
                    ) : (
                        <AnimatePresence>
                            {sessions.map((session) => (
                                <motion.div
                                    key={session.id}
                                    initial={{ opacity: 0, x: -10 }}
                                    animate={{ opacity: 1, x: 0 }}
                                    exit={{ opacity: 0, height: 0 }}
                                    layout
                                    className="relative"
                                >
                                    <button
                                        onClick={() => onSessionSelect(session)}
                                        className={cn(
                                            'group relative flex w-full flex-col gap-1 rounded-xl px-4 py-3 text-left transition-all duration-200 border border-transparent',
                                            selectedSessionId === session.id
                                                ? 'bg-white/10 text-white border-white/10 shadow-lg shadow-black/20'
                                                : 'text-white/60 hover:bg-white/5 hover:text-white/90 hover:border-white/5'
                                        )}
                                    >
                                        <div className="flex items-center justify-between w-full">
                                            <h4 className={cn(
                                                "truncate text-sm font-medium pr-6",
                                                selectedSessionId === session.id ? "text-cyan-50" : ""
                                            )}>
                                                {session.title || 'Untitled Chat'}
                                            </h4>
                                        </div>

                                        <div className="flex items-center gap-2 text-[10px] uppercase tracking-wider font-medium text-white/30 group-hover:text-white/40 transition-colors">
                                            {new Date(session.created_at).toLocaleDateString(undefined, { month: 'short', day: 'numeric' })}
                                            <span>•</span>
                                            {new Date(session.created_at).toLocaleTimeString(undefined, { hour: '2-digit', minute: '2-digit' })}
                                        </div>

                                        {/* Delete Action - Only visible on hover */}
                                        <div
                                            className="absolute right-2 top-1/2 -translate-y-1/2 opacity-0 group-hover:opacity-100 transition-opacity"
                                            onClick={(e) => handleDelete(e, session.id)}
                                        >
                                            <div className="p-2 rounded-lg hover:bg-red-500/20 hover:text-red-400 text-white/20 transition-colors">
                                                <Trash className="size-4" />
                                            </div>
                                        </div>

                                        {/* Active Indicator Bar */}
                                        {selectedSessionId === session.id && (
                                            <div className="absolute left-0 top-3 bottom-3 w-1 bg-cyan-400 rounded-r-full shadow-[0_0_12px_rgba(34,211,238,0.6)]" />
                                        )}
                                    </button>
                                </motion.div>
                            ))}
                        </AnimatePresence>
                    )}
                </div>

                {/* Footer / User Info could go here */}
                {/* <div className="p-4 border-t border-white/5 mt-auto">
                    ...
                </div> */}
            </div>
        </div>
    );
}
