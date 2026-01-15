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
import { SessionSidebar } from '@/components/app/session-sidebar';
import { api } from '@/lib/api';

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
  } as any,
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

interface SessionViewProps {
  appConfig: AppConfig;
}

export const SessionView = ({
  appConfig,
  ...props
}: React.ComponentProps<'section'> & SessionViewProps) => {
  const session = useSessionContext();
  const { messages: liveMessages } = useSessionMessages(session);
  const [chatOpen, setChatOpen] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);

  const { localParticipant } = useLocalParticipant();
  const { currentPersona } = usePersona();
  const [transcription, setTranscription] = useState('');

  // --- Session History State ---
  const [selectedSessionId, setSelectedSessionId] = useState<string | undefined>(undefined);
  const [historyMessages, setHistoryMessages] = useState<any[]>([]); // Using any[] for now to match structure roughly
  const [sidebarOpen, setSidebarOpen] = useState(false); // Mobile toggle if needed, or desktop default

  // Fetch messages when a past session is selected
  useEffect(() => {
    if (selectedSessionId) {
      const loadHistory = async () => {
        try {
          const { messages } = await api.getSessionMessages(selectedSessionId);
          // Transform backend messages to ReceivedMessage format if needed
          // Backend: { id, role, content, ... }
          // Frontend expects: { id, message, from: { isLocal: boolean }, ... }
          const formatted = messages.map(m => ({
            id: m.id,
            message: m.content,
            timestamp: new Date(m.created_at).getTime(),
            from: { isLocal: m.role === 'user' },
            type: 'chatMessage'
          }));
          setHistoryMessages(formatted);
        } catch (e) {
          console.error("Failed to load history", e);
        }
      };
      loadHistory();
    } else {
      setHistoryMessages([]);
    }
  }, [selectedSessionId]);

  const handleSessionSelect = (s: any) => {
    setSelectedSessionId(s.id);
    setChatOpen(true); // Auto-open chat to show legacy messages
  };

  const handleDisconnect = () => {
    console.log("Attempting to disconnect...");
    if ((session as any).disconnect) {
      (session as any).disconnect();
    } else if ((session as any).room) {
      (session as any).room.disconnect();
    } else {
      console.warn("No disconnect method found on session object");
    }
  };

  const handleNewChat = () => {
    setSelectedSessionId(undefined);
    setHistoryMessages([]);
    if (session.connectionState === 'connected') {
      handleDisconnect();
    }
  };
  // -----------------------------

  const localMicrophoneTrack = useMemo(() => ({
    source: Track.Source.Microphone,
    participant: localParticipant,
  }), [localParticipant]);

  const { segments } = useTrackTranscription(localMicrophoneTrack);

  useEffect(() => {
    if (segments.length > 0) {
      const lastSegment = segments[segments.length - 1];
      if (!lastSegment.final) {
        setTranscription(lastSegment.text);
      } else {
        setTranscription(lastSegment.text);
      }
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
  }, [liveMessages, historyMessages]); // Scroll on both

  // Determine which messages to show
  const displayMessages = selectedSessionId ? historyMessages : liveMessages;
  const showLiveElements = !selectedSessionId; // Hide video/controls if viewing history? Or keep them?
  // User request: "hop on to prevois calls... connected to backend... looks good... prev like a message app"
  // Usually history view is read-only or distinct. Let's keep it simple: Overlap the video.

  return (
    <section className="bg-transparent relative z-10 h-full w-full overflow-hidden flex" {...props}>
      {/* Sidebar */}
      <SessionSidebar
        onSessionSelect={handleSessionSelect}
        onNewChat={handleNewChat}
        selectedSessionId={selectedSessionId}
        className="hidden md:flex" // Hide on mobile for now or implement toggle
      />

      <div className="relative flex-1 h-full w-full overflow-hidden">
        {/* Immersive Background */}
        <div className="fixed inset-0 -z-10 h-full w-full bg-black">
          <img
            src={currentPersona.image}
            alt="immersive-bg"
            className="h-full w-full object-cover opacity-90 blur-[100px] hover:blur-[80px] transition-all duration-1000 scale-110 brightness-90 contrast-125 saturate-200"
          />
          <div className="absolute inset-0 bg-black/10" />
        </div>

        {/* Chat Transcript - ALWAYS visible if in history mode, or if chatOpen in live mode */}
        <div
          className={cn(
            'fixed inset-0 grid grid-cols-1 grid-rows-1 z-[60] md:pl-[280px]',
            (!chatOpen && showLiveElements) && 'pointer-events-none' // Pass through clicks if chat closed AND in live mode
          )}
        >
          <Fade top className="absolute inset-x-4 top-0 h-40 z-30" />
          <ScrollArea ref={scrollAreaRef} className="px-4 pt-40 pb-[150px] md:px-6 md:pb-[200px] h-full">
            {/* Added h-full to confirm scroll area takes space */}
            <ChatTranscript
              hidden={!chatOpen}
              messages={displayMessages}
              lastLocalMessage={showLiveElements ? transcription : undefined}
              className="mx-auto max-w-2xl space-y-3 transition-opacity duration-300 ease-out text-white"
            />
          </ScrollArea>
        </div>

        {/* Live Mode Elements */}
        {showLiveElements && (
          <>
            {/* Tile Layout */}
            <TileLayout chatOpen={chatOpen} />

            {/* Bottom Controls */}
            <MotionBottom
              {...BOTTOM_VIEW_MOTION_PROPS}
              className="fixed inset-x-3 bottom-0 z-[70] md:inset-x-12 md:pl-[280px]"
            >
              {appConfig.isPreConnectBufferEnabled && (
                <PreConnectMessage messages={liveMessages} className="pb-4" />
              )}
              <div className="bg-background relative mx-auto max-w-2xl pb-3 md:pb-12">
                <Fade bottom className="absolute inset-x-0 top-0 h-4 -translate-y-full" />
                <AgentControlBar
                  controls={controls}
                  isConnected={session.isConnected}
                  onDisconnect={handleDisconnect}
                  onChatOpenChange={setChatOpen}
                />
              </div>
            </MotionBottom>
          </>
        )}
      </div>
    </section>
  );
};

