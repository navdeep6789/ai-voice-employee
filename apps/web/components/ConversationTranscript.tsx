"use client";

import { useEffect, useRef } from "react";
import { ChatMessage } from "@/types";
import { Bot, User } from "lucide-react";

interface ConversationTranscriptProps {
  messages: ChatMessage[];
  isThinking?: boolean;
}

export function ConversationTranscript({ messages, isThinking }: ConversationTranscriptProps) {
  const bottomRef = useRef<HTMLDivElement>(null);
  const containerRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    // Only scroll if the user is near the bottom
    if (containerRef.current) {
      const { scrollTop, scrollHeight, clientHeight } = containerRef.current;
      const isNearBottom = scrollHeight - scrollTop - clientHeight < 150;
      if (isNearBottom) {
        bottomRef.current?.scrollIntoView({ behavior: "smooth" });
      }
    }
  }, [messages, isThinking]);

  return (
    <div
      ref={containerRef}
      className="flex-1 overflow-y-auto px-4 py-4 space-y-4 rounded-xl bg-zinc-950/60 border border-zinc-900/80 min-h-[280px] max-h-[420px] scrollbar-thin scrollbar-thumb-zinc-800"
    >
      {messages.length === 0 ? (
        <div className="flex flex-col items-center justify-center h-full text-center py-12 text-zinc-500">
          <Bot className="w-8 h-8 mb-2 text-zinc-600" />
          <p className="text-sm font-medium text-zinc-400">No conversation yet</p>
          <p className="text-xs text-zinc-600 mt-1 max-w-xs">
            Click "Talk to our AI Employee" or try one of the prompt scenarios below to begin.
          </p>
        </div>
      ) : (
        messages.map((msg) => {
          const isAi = msg.speaker === "assistant";
          return (
            <div
              key={msg.id}
              className={`flex items-start space-x-2.5 ${isAi ? "justify-start" : "justify-end"}`}
            >
              {isAi && (
                <div className="w-6 h-6 rounded-full bg-emerald-950 border border-emerald-800/60 flex items-center justify-center shrink-0 mt-0.5">
                  <Bot className="w-3.5 h-3.5 text-emerald-400" />
                </div>
              )}

              <div
                className={`max-w-[82%] rounded-2xl px-4 py-2.5 text-xs sm:text-sm leading-relaxed shadow-xs ${
                  isAi
                    ? "bg-zinc-900/90 text-zinc-200 border border-zinc-800/80 rounded-tl-xs"
                    : "bg-emerald-600 text-white rounded-tr-xs"
                }`}
              >
                <div className="flex items-center justify-between space-x-2 mb-1">
                  <span
                    className={`text-[10px] font-mono uppercase tracking-wider font-semibold ${
                      isAi ? "text-emerald-400" : "text-emerald-200"
                    }`}
                  >
                    {isAi ? "Voice AI" : "You"}
                  </span>
                  <span
                    className={`text-[10px] font-mono ${
                      isAi ? "text-zinc-500" : "text-emerald-200/80"
                    }`}
                  >
                    {msg.timestamp}
                  </span>
                </div>
                <p className="whitespace-pre-wrap">{msg.text}</p>
              </div>

              {!isAi && (
                <div className="w-6 h-6 rounded-full bg-zinc-800 border border-zinc-700 flex items-center justify-center shrink-0 mt-0.5">
                  <User className="w-3.5 h-3.5 text-zinc-300" />
                </div>
              )}
            </div>
          );
        })
      )}

      {isThinking && (
        <div className="flex items-center space-x-2 text-zinc-500 text-xs py-2 px-1">
          <div className="w-2 h-2 rounded-full bg-emerald-400 animate-ping" />
          <span className="font-mono text-zinc-400">AI is reasoning...</span>
        </div>
      )}

      <div ref={bottomRef} />
    </div>
  );
}
