"use client";

import { VoiceState } from "@/types";
import { Mic, MicOff, PhoneOff, MessageSquare, Loader2, Play } from "lucide-react";

interface VoiceControlsProps {
  state: VoiceState;
  isMuted: boolean;
  onStart: () => void;
  onEnd: () => void;
  onToggleMute: () => void;
  onToggleTextMode: () => void;
  isTextMode: boolean;
}

export function VoiceControls({
  state,
  isMuted,
  onStart,
  onEnd,
  onToggleMute,
  onToggleTextMode,
  isTextMode,
}: VoiceControlsProps) {
  const isCallActive =
    state === "CONNECTED" ||
    state === "LISTENING" ||
    state === "PROCESSING" ||
    state === "SPEAKING" ||
    state === "TOOL_CALL";

  return (
    <div className="flex flex-col items-center space-y-3 w-full max-w-md mx-auto">
      {/* Primary Action Button */}
      {!isCallActive ? (
        <button
          onClick={onStart}
          disabled={state === "CONNECTING"}
          className="w-full group relative inline-flex items-center justify-center px-6 py-3.5 text-sm font-medium text-white transition-all bg-gradient-to-r from-emerald-600 to-teal-600 rounded-xl shadow-lg hover:from-emerald-500 hover:to-teal-500 focus:outline-hidden focus:ring-2 focus:ring-emerald-500/50 disabled:opacity-50 cursor-pointer"
        >
          {state === "CONNECTING" ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              <span>Connecting Voice Gateway...</span>
            </>
          ) : (
            <>
              <Mic className="w-4 h-4 mr-2 text-emerald-200 group-hover:scale-110 transition-transform" />
              <span>Talk to our AI Employee</span>
            </>
          )}
        </button>
      ) : (
        <div className="flex items-center justify-center space-x-3 w-full">
          {/* Mute Button */}
          <button
            onClick={onToggleMute}
            className={`p-3 rounded-xl border text-sm font-medium transition-colors flex items-center justify-center cursor-pointer ${
              isMuted
                ? "bg-amber-950/40 border-amber-800 text-amber-300 hover:bg-amber-900/50"
                : "bg-zinc-900 border-zinc-800 text-zinc-300 hover:bg-zinc-800"
            }`}
            title={isMuted ? "Unmute Microphone" : "Mute Microphone"}
          >
            {isMuted ? <MicOff className="w-4 h-4" /> : <Mic className="w-4 h-4 text-emerald-400" />}
          </button>

          {/* End Call Button */}
          <button
            onClick={onEnd}
            className="flex-1 inline-flex items-center justify-center px-5 py-3 text-sm font-medium text-white bg-rose-600/90 hover:bg-rose-500 border border-rose-500/30 rounded-xl shadow-md transition-colors cursor-pointer"
          >
            <PhoneOff className="w-4 h-4 mr-2" />
            <span>End Call & Summarize</span>
          </button>
        </div>
      )}

      {/* Secondary Controls / Mode Switch */}
      <div className="flex items-center justify-between w-full px-1 text-xs text-zinc-400">
        <button
          onClick={onToggleTextMode}
          className="inline-flex items-center space-x-1.5 text-zinc-400 hover:text-zinc-200 transition-colors py-1 cursor-pointer"
        >
          <MessageSquare className="w-3.5 h-3.5" />
          <span>{isTextMode ? "Close Text Mode" : "Switch to Text Mode"}</span>
        </button>

        <span className="font-mono text-[11px] text-zinc-500">
          Sample Rate: 16kHz PCM
        </span>
      </div>
    </div>
  );
}
