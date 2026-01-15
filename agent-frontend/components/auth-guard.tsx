'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useSupabaseAuth } from '@/hooks/useSupabaseAuth';

export function AuthGuard({ children }: { children: React.ReactNode }) {
    const { user, loading } = useSupabaseAuth();
    const router = useRouter();

    useEffect(() => {
        if (!loading) {
            if (!user) {
                router.push('/');
            } else if (!user.email_confirmed_at) {
                // User signed up but hasn't verified email
                router.push('/');
            }
        }
    }, [user, loading, router]);

    if (loading) {
        return (
            <div className="min-h-screen flex items-center justify-center bg-black text-white">
                <div>Loading...</div>
            </div>
        );
    }

    if (!user || !user.email_confirmed_at) {
        return null;
    }

    return <>{children}</>;
}