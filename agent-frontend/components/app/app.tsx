'use client';

import { useState, useMemo } from 'react';
import { TokenSource } from 'livekit-client';
import {
  RoomAudioRenderer,
  SessionProvider,
  StartAudio,
  useSession,
} from '@livekit/components-react';
import type { AppConfig } from '@/app-config';
import { ViewController } from '@/components/app/view-controller';
import { Toaster } from '@/components/livekit/toaster';
import { useAgentErrors } from '@/hooks/useAgentErrors';
import { livekitAPI, sessionsAPI } from '@/lib/api-client';
import { PersonaProvider, usePersona } from '@/components/app/persona-context';
import { useDebugMode } from '@/hooks/useDebug';

const IN_DEVELOPMENT = process.env.NODE_ENV !== 'production';

function AppSetup() {
  useDebugMode({ enabled: IN_DEVELOPMENT });
  useAgentErrors();

  return null;
}

interface AppProps {
  appConfig: AppConfig;
}

export function App({ appConfig }: AppProps) {
  return (
    <PersonaProvider>
      <InnerApp appConfig={appConfig} />
    </PersonaProvider>
  );
}

function InnerApp({ appConfig }: AppProps) {
  const { currentPersona } = usePersona();
  const [currentSessionId, setCurrentSessionId] = useState<string | null>(null);

  const tokenSource = useMemo(() => {
    // Cast to any to avoid strict type mismatch with livekit-client vs components-react
    return (async (userInfo: any) => {
      // Create session in backend
      const { session: backendSession } = await sessionsAPI.create({
        agent_type: currentPersona.id,
        title: `Chat with ${currentPersona.name}`,
      });

      setCurrentSessionId(backendSession.id);

      // Get LiveKit token from backend
      const { token } = await livekitAPI.getToken({
        room_name: backendSession.livekit_room_name,
        agent_name: currentPersona.id,
      });

      return token;
    }) as any;
  }, [currentPersona]);

  const session = useSession(
    tokenSource,
    { agentName: currentPersona.id }
  );

  return (
    <SessionProvider session={session}>
      <AppSetup />
      <main className="grid h-svh grid-cols-1 place-content-center">
        <ViewController appConfig={appConfig} sessionId={currentSessionId} />
      </main>
      <StartAudio label="Start Audio" />
      <RoomAudioRenderer />
      <Toaster />
    </SessionProvider>
  );
}
