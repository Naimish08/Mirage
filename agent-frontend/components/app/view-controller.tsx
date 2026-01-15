'use client';

import { AnimatePresence, motion } from 'motion/react';
import { useSessionContext } from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { SessionView } from '@/components/app/session-view';
import { WelcomeView } from '@/components/app/welcome-view';
import { LoginForm } from '@/components/auth/login-form';
import { useAuth } from '@/contexts/auth-context';

const MotionWelcomeView = motion.create(WelcomeView);
const MotionSessionView = motion.create(SessionView);

const VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
    },
    hidden: {
      opacity: 0,
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.5,
    ease: 'linear' as any,
  },
};

interface ViewControllerProps {
  appConfig: AppConfig;
  sessionId: string | null;
}

export function ViewController({ appConfig, sessionId }: ViewControllerProps) {
  const { isConnected, start } = useSessionContext();
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="flex h-full items-center justify-center">
        <div className="size-8 animate-spin rounded-full border-4 border-primary border-t-transparent" />
      </div>
    );
  }

  return (
    <AnimatePresence mode="wait">
      {/* Login view */}
      {!isAuthenticated && (
        <motion.div
          key="login"
          {...VIEW_MOTION_PROPS}
          className="flex h-full items-center justify-center p-4"
        >
          <LoginForm />
        </motion.div>
      )}

      {/* Welcome view */}
      {isAuthenticated && !isConnected && (
        <MotionWelcomeView
          key="welcome"
          {...VIEW_MOTION_PROPS}
          startButtonText={appConfig.startButtonText}
          onStartCall={start}
        />
      )}

      {/* Session view */}
      {isAuthenticated && isConnected && (
        <MotionSessionView
          key="session-view"
          {...VIEW_MOTION_PROPS}
          appConfig={appConfig}
          sessionId={sessionId}
        />
      )}
    </AnimatePresence>
  );
}
