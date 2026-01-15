'use client';

import { useAuth } from '@/contexts/auth-context';
import { SignOut } from '@phosphor-icons/react';

export function LogoutButton() {
    const { signOut, user } = useAuth();

    if (!user) return null;

    return (
        <button
            onClick={signOut}
            className="flex items-center gap-2 px-3 py-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-lg text-white/70 hover:text-white transition-all duration-200 text-sm font-medium"
            title="Sign Out"
        >
            <SignOut weight="bold" className="size-4" />
            <span>Logout</span>
        </button>
    );
}
