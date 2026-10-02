"use client";

import { VoiceState } from "@/types";
import { Mic, Volume2, Loader2, Sparkles, AlertCircle } from "lucide-react";

interface VoiceOrbProps {
  state: VoiceState;
  audioLevel: number;
}

export function VoiceOrb({ state, audioLevel }: VoiceOrbProps) {
  // Scale pulse intensity according to actual audio level (0-100)
  const scale = 1 + (audioLevel / 100) * 0.25;
  const glowOpacity = Math.min(0.8, 0.2 + (audioLevel / 100) * 0.6);

  const getStatusBadge = () => {
    switch (state) {
      case "LISTENING":
        return {
          text: "Listening to you...",
          color: "border-emerald-500/40 bg-emerald-950/40 text-emerald-300",
          dot: "bg-emerald-400 animate-ping",
          icon: Mic,
        };
      case "SPEAKING":
        return {
          text: "AI Speaking...",
          color: "border-cyan-500/40 bg-cyan-950/40 text-cyan-300",
          dot: "bg-cyan-400 animate-pulse",
          icon: Volume2,
        };
      case "PROCESSING":
      case "TOOL_CALL":
        return {
          text: state === "TOOL_CALL" ? "Executing Tool..." : "Reasoning & Searching...",
          color: "border-indigo-500/40 bg-indigo-950/40 text-indigo-300",
          dot: "bg-indigo-400",
          icon: Loader2,
        };
      case "CONNECTING":
        return {
          text: "Connecting to Gemini Live...",
          color: "border-amber-500/40 bg-amber-950/40 text-amber-300",
          dot: "bg-amber-400 animate-pulse",
          icon: Loader2,
        };
      case "ERROR":
        return {
          text: "Voice Unavailable (Use Text Mode)",
          color: "border-rose-500/40 bg-rose-950/40 text-rose-300",
          dot: "bg-rose-400",
          icon: AlertCircle,
        };
      case "ENDED":
        return {
          text: "Conversation Ended",
          color: "border-zinc-700 bg-zinc-900 text-zinc-400",
          dot: "bg-zinc-500",
          icon: Sparkles,
        };
      default:
        return {
          text: "Ready to Talk",
          color: "border-zinc-800 bg-zinc-900 text-zinc-400",
          dot: "bg-zinc-500",
          icon: Sparkles,
        };
    }
  };

  const badge = getStatusBadge();
  const Icon = badge.icon;

  return (
    <div className="flex flex-col items-center justify-center py-6 select-none">
      {/* Visual Orb Container */}
      <div className="relative flex items-center justify-center w-40 h-40">
        {/* Ambient Ring / Glow */}
        <div
          className={`absolute inset-0 rounded-full transition-all duration-300 ${
            state === "SPEAKING"
              ? "bg-gradient-to-tr from-cyan-500 to-indigo-600 blur-xl"
              : state === "LISTENING"
              ? "bg-gradient-to-tr from-emerald-500 to-teal-600 blur-xl"
              : "bg-zinc-800/40 blur-lg"
          }`}
          style={{
            opacity: state === "IDLE" ? 0.15 : glowOpacity,
            transform: `scale(${scale * 1.1})`,
          }}
        />

        {/* Outer Ring */}
        <div
          className={`absolute w-36 h-36 rounded-full border border-dashed transition-all duration-500 ${
            state === "LISTENING"
              ? "border-emerald-500/50 animate-[spin_12s_linear_infinite]"
              : state === "SPEAKING"
              ? "border-cyan-500/50 animate-[spin_8s_linear_infinite]"
              : "border-zinc-800"
          }`}
        />

        {/* Center Spherical Core */}
        <div
          className={`relative z-10 w-28 h-28 rounded-full shadow-2xl flex items-center justify-center transition-transform duration-150 border ${
            state === "SPEAKING"
              ? "bg-gradient-to-b from-zinc-900 to-cyan-950 border-cyan-500/50"
              : state === "LISTENING"
              ? "bg-gradient-to-b from-zinc-900 to-emerald-950 border-emerald-500/50"
              : state === "ERROR"
              ? "bg-zinc-900 border-rose-800/50"
              : "bg-zinc-900 border-zinc-800"
          }`}
          style={{
            transform: `scale(${scale})`,
          }}
        >
          {/* Internal Waveform Bars (Restrained, Real Level Driven) */}
          <div className="flex items-center space-x-1.5 h-10">
            {[0.4, 0.7, 1.0, 0.7, 0.4].map((multiplier, idx) => {
              const barHeight =
                state === "IDLE" || state === "ENDED"
                  ? 4
                  : Math.max(6, Math.min(36, 6 + (audioLevel / 100) * 30 * multiplier));
              return (
                <div
                  key={idx}
                  className={`w-1 rounded-full transition-all duration-100 ${
                    state === "SPEAKING"
                      ? "bg-cyan-400"
                      : state === "LISTENING"
                      ? "bg-emerald-400"
                      : "bg-zinc-600"
                  }`}
                  style={{ height: `${barHeight}px` }}
                />
              );
            })}
          </div>
        </div>
      </div>

      {/* State Badge */}
      <div
        className={`mt-4 px-3 py-1 rounded-full border text-xs font-mono flex items-center space-x-2 transition-all ${badge.color}`}
      >
        <span className={`w-1.5 h-1.5 rounded-full ${badge.dot}`} />
        <Icon className={`w-3.5 h-3.5 ${state === "PROCESSING" || state === "CONNECTING" ? "animate-spin" : ""}`} />
        <span className="font-medium tracking-wide">{badge.text}</span>
      </div>
    </div>
  );
}
