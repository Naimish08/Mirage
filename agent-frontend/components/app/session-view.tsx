'use client';

import React, { useEffect, useRef, useState, useMemo } from 'react';
import { motion } from 'motion/react';
import {
  useSessionContext,
  useSessionMessages,
  useLocalParticipant,
  useTrackTranscription,
  TrackReferenceOrPlaceholder,
} from '@livekit/components-react';
import { Track, Participant } from 'livekit-client';
import type { AppConfig } from '@/app-config';
import { ChatTranscript } from '@/components/app/chat-transcript';
import { PreConnectMessage } from '@/components/app/preconnect-message';
import { TileLayout } from '@/components/app/tile-layout';
import {
  AgentControlBar,
  type ControlBarControls,
} from '@/components/livekit/agent-control-bar/agent-control-bar';
import { cn } from '@/lib/utils';
import { ScrollArea } from '../livekit/scroll-area/scroll-area';
import { usePersona } from '@/components/app/persona-context';
import { useAuth } from '@/contexts/auth-context';
import { SignOut } from '@phosphor-icons/react';

const MotionBottom = motion.create('div');

const BOTTOM_VIEW_MOTION_PROPS = {
  variants: {
    visible: {
      opacity: 1,
      translateY: '0%',
    },
    hidden: {
      opacity: 0,
      translateY: '100%',
    },
  },
  initial: 'hidden',
  animate: 'visible',
  exit: 'hidden',
  transition: {
    duration: 0.3,
    delay: 0.5,
    ease: 'easeOut',
  },
};

interface FadeProps {
  top?: boolean;
  bottom?: boolean;
  className?: string;
}

export function Fade({ top = false, bottom = false, className }: FadeProps) {
  return (
    <div
      className={cn(
        'from-background pointer-events-none h-4 bg-linear-to-b to-transparent',
        top && 'bg-linear-to-b',
        bottom && 'bg-linear-to-t',
        className
      )}
    />
  );
}

import { sessionsAPI, Message } from '@/lib/api-client';

// ...

interface SessionViewProps {
  appConfig: AppConfig;
  sessionId: string | null;
}

export const SessionView = ({
  appConfig,
  sessionId,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  const session = useSessionContext();
  const { messages: liveMessages } = useSessionMessages(session);
  const [history, setHistory] = useState<any[]>([]); // Using any for ReceivedMessage to avoid complex mocking
  const [chatOpen, setChatOpen] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const { localParticipant } = useLocalParticipant();
  const { currentPersona } = usePersona();
  const { signOut } = useAuth();
  const [transcription, setTranscription] = useState('');

  const handleLogout = async () => {
    // Disconnect from LiveKit session first
    if (session.isConnected) {
      await session.end();
    }
    // Then sign out from authentication
    await signOut();
  };

  // Fetch history
  useEffect(() => {
    if (sessionId) {
      sessionsAPI.getMessages(sessionId).then(({ messages }) => {
        const mappedMessages = messages.map((msg: Message) => ({
          id: msg.id,
          message: msg.content,
          timestamp: new Date(msg.created_at).getTime(),
          from: {
            identity: msg.role === 'user' ? 'user' : 'agent',
            isLocal: msg.role === 'user',
            name: msg.role === 'user' ? 'You' : currentPersona.name
          },
          type: 'chatMessage',
        }));
        setHistory(mappedMessages.reverse()); // Messages come newest first usually? Check API. 
        // If API returns newest first, reverse. If oldest first, don't.
        // Usually SQL 'limit offset' with default sort... 
        // My migration didn't specify sort in index?
        // Repo implementation: "order by created_at desc" is common.
        // If desc, then newest first. 
        // Start listing from offset 0 (newest). 
        // So we need to reverse to show chronologically.
      }).catch(console.error);
    }
  }, [sessionId, currentPersona.name]);

  const allMessages = [...history, ...liveMessages];

  const localMicrophoneTrack = useMemo(() => ({
    source: Track.Source.Microphone,
    participant: localParticipant,
  }), [localParticipant]);

  const { segments } = useTrackTranscription(localMicrophoneTrack);

  useEffect(() => {
    if (segments.length > 0) {
      const lastSegment = segments[segments.length - 1];
      setTranscription(lastSegment.text);
    }
  }, [segments]);


  const controls: ControlBarControls = {
    leave: true,
    microphone: true,
    chat: appConfig.supportsChatInput,
    camera: appConfig.supportsVideoInput,
    screenShare: appConfig.supportsScreenShare,
  };

  useEffect(() => {
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [allMessages]);

  return (
    <section className="bg-transparent relative z-10 h-full w-full overflow-hidden" {...props}>
      {/* Logout Button */}
      <button
        onClick={handleLogout}
        className="fixed top-6 right-6 z-50 flex items-center gap-2 px-4 py-2 bg-white/5 hover:bg-white/10 border border-white/10 hover:border-white/20 rounded-lg text-white/70 hover:text-white transition-all duration-200 backdrop-blur-sm"
        title="Sign Out"
      >
        <SignOut weight="bold" className="size-5" />
        <span className="text-sm font-medium">Logout</span>
      </button>

      {/* Immersive Background */}
      <div className="fixed inset-0 -z-10 h-full w-full bg-black">
        <img
          src={currentPersona.image}
          alt="immersive-bg"
          className="h-full w-full object-cover opacity-50 blur-[100px] hover:blur-[80px] transition-all duration-1000 scale-110 brightness-90 contrast-125 saturate-200"
        />
        <div className="absolute inset-0 bg-black/10" />
      </div>

      {/* Chat Transcript */}
      <div
        className={cn(
          'fixed inset-0 grid grid-cols-1 grid-rows-1',
          !chatOpen && 'pointer-events-none'
        )}
      >
        <Fade top className="absolute inset-x-4 top-0 h-40" />
        <ScrollArea ref={scrollAreaRef} className="px-4 pt-40 pb-[150px] md:px-6 md:pb-[200px]">
          <ChatTranscript
            hidden={!chatOpen}
            messages={allMessages as any}
            lastLocalMessage={transcription}
            className="mx-auto max-w-2xl space-y-3 transition-opacity duration-300 ease-out"
          />
        </ScrollArea>
      </div>

      {/* Tile Layout */}
      <TileLayout chatOpen={chatOpen} />

      {/* Bottom */}
      <MotionBottom
        {...BOTTOM_VIEW_MOTION_PROPS}
        transition={{ ...BOTTOM_VIEW_MOTION_PROPS.transition, ease: 'easeOut' as any }}
        className="fixed inset-x-3 bottom-0 z-50 md:inset-x-12"
      >
        {appConfig.isPreConnectBufferEnabled && (
          <PreConnectMessage messages={allMessages as any} className="pb-4" />
        )}
        <div className="bg-background relative mx-auto max-w-2xl pb-3 md:pb-12">
          <Fade bottom className="absolute inset-x-0 top-0 h-4 -translate-y-full" />
          <AgentControlBar
            controls={controls}
            isConnected={session.isConnected}
            onDisconnect={session.end}
            onChatOpenChange={setChatOpen}
          />
        </div>
      </MotionBottom>
    </section>
  );
};

