'use client';

import { type HTMLAttributes, useCallback, useState } from 'react';
import { Track } from 'livekit-client';
import { useChat, useRemoteParticipants } from '@livekit/components-react';
import { ChatTextIcon, PhoneDisconnectIcon } from '@phosphor-icons/react/dist/ssr';
import { TrackToggle } from '@/components/livekit/agent-control-bar/track-toggle';
import { Button } from '@/components/livekit/button';
import { Toggle } from '@/components/livekit/toggle';
import { cn } from '@/lib/utils';
import { ChatInput } from './chat-input';
import { UseInputControlsProps, useInputControls } from './hooks/use-input-controls';
import { usePublishPermissions } from './hooks/use-publish-permissions';
import { TrackSelector } from './track-selector';
import { AudioVisualizerBar } from '@/components/app/audio-visualizer-bar';
import { useVoiceAssistant } from '@livekit/components-react';
import { usePersona } from '@/components/app/persona-context';

export interface ControlBarControls {
  leave?: boolean;
  camera?: boolean;
  microphone?: boolean;
  screenShare?: boolean;
  chat?: boolean;
}

export interface AgentControlBarProps extends UseInputControlsProps {
  controls?: ControlBarControls;
  isConnected?: boolean;
  onChatOpenChange?: (open: boolean) => void;
  onDeviceError?: (error: { source: Track.Source; error: Error }) => void;
}

export function AgentControlBar({
  controls,
  saveUserChoices = true,
  className,
  isConnected = false,
  onDisconnect,
  onDeviceError,
  onChatOpenChange,
  ...props
}: AgentControlBarProps & HTMLAttributes<HTMLDivElement>) {
  const { send } = useChat();
  const participants = useRemoteParticipants();
  const [chatOpen, setChatOpen] = useState(false);
  const publishPermissions = usePublishPermissions();
  const { audioTrack: agentAudioTrack } = useVoiceAssistant();
  const { currentPersona } = usePersona();
  const {
    micTrackRef,
    cameraToggle,
    microphoneToggle,
    screenShareToggle,
    handleAudioDeviceChange,
    handleVideoDeviceChange,
    handleMicrophoneDeviceSelectError,
    handleCameraDeviceSelectError,
  } = useInputControls({ onDeviceError, saveUserChoices });

  const handleSendMessage = async (message: string) => {
    await send(message);
  };

  const handleToggleTranscript = useCallback(
    (open: boolean) => {
      setChatOpen(open);
      onChatOpenChange?.(open);
    },
    [onChatOpenChange, setChatOpen]
  );

  const visibleControls = {
    leave: controls?.leave ?? true,
    microphone: controls?.microphone ?? publishPermissions.microphone,
    screenShare: controls?.screenShare ?? publishPermissions.screenShare,
    camera: controls?.camera ?? publishPermissions.camera,
    chat: controls?.chat ?? publishPermissions.data,
  };

  const isAgentAvailable = participants.some((p) => p.isAgent);

  return (
    <div className={cn('flex flex-col items-center gap-4', className)} {...props}>
      {/* Chat Input (Floating above) */}
      {visibleControls.chat && (
        <div className={cn("w-full transition-all duration-300", chatOpen ? "opacity-100 translate-y-0" : "opacity-0 translate-y-4 pointer-events-none absolute bottom-full mb-4")}>
          <ChatInput
            chatOpen={chatOpen}
            isAgentAvailable={isAgentAvailable}
            onSend={handleSendMessage}
          />
        </div>
      )}

      {/* Main Control Dock */}
      <div className="flex items-center gap-3 rounded-full bg-black/40 p-2 backdrop-blur-xl ring-1 ring-white/10 transition-all hover:bg-black/50 hover:ring-white/20 hover:shadow-2xl">
        <div className="flex gap-2">
          {/* Toggle Microphone */}
          {visibleControls.microphone && (
            <TrackSelector
              kind="audioinput"
              aria-label="Toggle microphone"
              source={Track.Source.Microphone}
              pressed={microphoneToggle.enabled}
              disabled={microphoneToggle.pending}
              audioTrackRef={micTrackRef}
              onPressedChange={microphoneToggle.toggle}
              onMediaDeviceError={handleMicrophoneDeviceSelectError}
              onActiveDeviceChange={handleAudioDeviceChange}
              className="h-12 w-12 rounded-full border-none bg-white/5 hover:bg-white/10"
            />
          )}

          {/* Audio Visualizer */}
          <AudioVisualizerBar
            trackRef={agentAudioTrack}
            className="mx-2 hidden md:block self-center"
          />

          {/* Toggle Camera */}
          {visibleControls.camera && (
            <TrackSelector
              kind="videoinput"
              aria-label="Toggle camera"
              source={Track.Source.Camera}
              pressed={cameraToggle.enabled}
              pending={cameraToggle.pending}
              disabled={cameraToggle.pending}
              onPressedChange={cameraToggle.toggle}
              onMediaDeviceError={handleCameraDeviceSelectError}
              onActiveDeviceChange={handleVideoDeviceChange}
              className="h-12 w-12 rounded-full border-none bg-white/5 hover:bg-white/10"
            />
          )}

          {/* Toggle Screen Share */}
          {visibleControls.screenShare && (
            <TrackToggle
              size="custom"
              className="h-12 w-12 rounded-full border-none bg-white/5 p-3 hover:bg-white/10"
              aria-label="Toggle screen share"
              source={Track.Source.ScreenShare}
              pressed={screenShareToggle.enabled}
              disabled={screenShareToggle.pending}
              onPressedChange={screenShareToggle.toggle}
            />
          )}

          {/* Toggle Transcript */}
          <Toggle
            size="custom"
            className="h-12 w-12 rounded-full border-none bg-white/5 p-3 hover:bg-white/10"
            aria-label="Toggle transcript"
            pressed={chatOpen}
            onPressedChange={handleToggleTranscript}
          >
            <ChatTextIcon weight="bold" className="h-6 w-6" />
          </Toggle>
        </div>

        {/* Divider */}
        {(visibleControls.leave) && (
          <div className="h-8 w-[1px] bg-white/10 mx-1" />
        )}

        {/* Disconnect */}
        {visibleControls.leave && (
          <Button
            size="custom"
            variant="destructive"
            onClick={onDisconnect}
            disabled={!isConnected}
            className="h-12 rounded-full px-6 font-semibold tracking-wide"
          >
            <PhoneDisconnectIcon weight="fill" className="mr-2 h-5 w-5" />
            END
          </Button>
        )}
      </div>
    </div>
  );
}
