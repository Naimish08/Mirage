'use client';

import { AnimatePresence, type HTMLMotionProps, motion } from 'motion/react';
import { type ReceivedMessage } from '@livekit/components-react';
import { ChatEntry } from '@/components/livekit/chat-entry';
import { cn } from '@/lib/utils';

const MotionContainer = motion.create('div');
const MotionChatEntry = motion.create(ChatEntry);

// ... (PROPS CONSTANTS REMAIN SAME if needed, or remove if unused)

interface ChatTranscriptProps {
  hidden?: boolean;
  messages?: ReceivedMessage[];
  lastLocalMessage?: string;
}

export function ChatTranscript({
  hidden = false,
  messages = [],
  lastLocalMessage,
  className,
  ...props
}: ChatTranscriptProps & React.HTMLAttributes<HTMLDivElement>) {
  if (hidden) return null;

  return (
    <div className={cn("flex flex-col gap-2", className)} {...props}>
      {messages.map((receivedMessage) => {
        const { id, timestamp, from, message } = receivedMessage;
        const locale = 'en-US'; // Hardcoded for hydration stability
        const messageOrigin = from?.isLocal ? 'local' : 'remote';
        const hasBeenEdited =
          receivedMessage.type === 'chatMessage' && !!receivedMessage.editTimestamp;

        return (
          <ChatEntry
            key={id}
            locale={locale}
            timestamp={timestamp}
            message={message}
            messageOrigin={messageOrigin}
            hasBeenEdited={hasBeenEdited}
          />
        );
      })}
      {lastLocalMessage && (
        <ChatEntry
          key="local-transcript"
          locale={'en-US'}
          timestamp={Date.now()}
          message={lastLocalMessage}
          messageOrigin="local"
        />
      )}
    </div>
  );
}
