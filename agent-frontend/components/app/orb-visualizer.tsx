import { useEffect, useRef } from "react";
import { type TrackReference } from "@livekit/components-react";
import { Track } from "livekit-client";
import { cn } from "@/lib/utils";

interface OrbVisualizerProps {
    state: string;
    trackRef?: TrackReference;
    className?: string;
}

export function OrbVisualizer({ state, trackRef, className }: OrbVisualizerProps) {
    const canvasRef = useRef<HTMLCanvasElement>(null);
    const analyserRef = useRef<AnalyserNode | null>(null);
    const rafRef = useRef<number | null>(null);
    const audioContextRef = useRef<AudioContext | null>(null);

    // 1. Audio Analysis Setup Effect
    useEffect(() => {
        if (!trackRef?.publication?.track || trackRef.publication.track.kind !== Track.Kind.Audio) {
            return;
        }

        const track = trackRef.publication.track;
        const stream = new MediaStream([track.mediaStreamTrack]);

        // Cleanup old context if exists
        if (audioContextRef.current) {
            audioContextRef.current.close();
        }

        const AudioContext = window.AudioContext || (window as any).webkitAudioContext;
        const audioContext = new AudioContext();
        audioContextRef.current = audioContext;

        const source = audioContext.createMediaStreamSource(stream);
        const analyser = audioContext.createAnalyser();
        analyser.fftSize = 256;
        source.connect(analyser);

        analyserRef.current = analyser;

        return () => {
            source.disconnect();
            analyser.disconnect();
            if (audioContext.state !== 'closed') {
                audioContext.close();
            }
            analyserRef.current = null;
        };
    }, [trackRef]);

    // 2. Rendering Loop Effect
    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;
        const ctx = canvas.getContext("2d");
        if (!ctx) return;

        // Set canvas size (consider using ResizeObserver for responsiveness, but fixed is fine for now)
        canvas.width = 400;
        canvas.height = 400;

        let phase = 0;
        const dataArray = new Uint8Array(128); // fftSize/2

        const render = () => {
            let volume = 0;

            const analyser = analyserRef.current;
            if (analyser) {
                analyser.getByteFrequencyData(dataArray);
                let sum = 0;
                // Calculate root mean square for better volume approximation or just average
                for (let i = 0; i < dataArray.length; i++) {
                    sum += dataArray[i];
                }
                volume = sum / dataArray.length / 255;
            } else {
                // IDLE / FALLBACK ANIMATION
                // Pulse gently if speaking but no audio track yet, or just breathing
                const time = Date.now() / 1000;
                volume = state === "speaking" ? 0.3 + Math.sin(time * 3) * 0.1 : 0.05 + Math.sin(time) * 0.02;
            }

            ctx.clearRect(0, 0, canvas.width, canvas.height);
            const centerX = canvas.width / 2;
            const centerY = canvas.height / 2;
            const baseRadius = 80; // Slightly smaller base

            phase += 0.02; // constant rotation

            // Colors: Cyan, Purple, Blue
            const waves = [
                { color: "rgba(0, 240, 255, 0.6)", offset: 0, freq: 8, speed: 2 },
                { color: "rgba(189, 0, 255, 0.6)", offset: Math.PI / 3, freq: 6, speed: -1.5 },
                { color: "rgba(0, 87, 255, 0.5)", offset: Math.PI, freq: 10, speed: 1 },
            ];

            // Draw each wave
            waves.forEach((wave) => {
                ctx.beginPath();
                for (let i = 0; i <= 360; i += 2) { // Step 2 for performance
                    const angle = (i * Math.PI) / 180;

                    // Modulate radius
                    // r = base + volume * (max_amplitude)
                    const waveAmp = 40 * volume + 5;
                    const r =
                        baseRadius +
                        waveAmp * Math.sin(angle * wave.freq + phase * wave.speed + wave.offset) +
                        (volume * 20); // expand outward with volume

                    const x = centerX + r * Math.cos(angle);
                    const y = centerY + r * Math.sin(angle);

                    if (i === 0) ctx.moveTo(x, y);
                    else ctx.lineTo(x, y);
                }
                ctx.closePath();

                ctx.strokeStyle = wave.color;
                ctx.lineWidth = 2 + volume * 2;
                ctx.shadowBlur = 15 + volume * 20;
                ctx.shadowColor = wave.color;
                ctx.stroke();
            });

            rafRef.current = requestAnimationFrame(render);
        };

        render();

        return () => {
            if (rafRef.current) cancelAnimationFrame(rafRef.current);
        };
    }, [state]); // Re-bind if state changes (optional, but render loop handles state ref reading ideally)

    return (
        <div className={cn("relative flex items-center justify-center", className)}>
            <canvas
                ref={canvasRef}
                className="h-[300px] w-[300px]"
            />
        </div>
    );
}
