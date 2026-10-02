"use client";

import { useState } from "react";
import { Send, Loader2, MessageSquare } from "lucide-react";
import { sendChatMessage } from "@/lib/api";
import { AgentActivityEvent, CustomerContext, BookingDetails } from "@/types";

interface TextModeFallbackProps {
  sessionId: string;
  leadId?: string;
  onNewUserMessage: (text: string) => void;
  onNewAssistantMessage: (text: string) => void;
  onNewEvents: (events: AgentActivityEvent[]) => void;
  onCustomerContextUpdated: (ctx: CustomerContext) => void;
  onBookingConfirmed: (b: BookingDetails) => void;
  initialPrompt?: string;
}

export function TextModeFallback({
  sessionId,
  leadId,
  onNewUserMessage,
  onNewAssistantMessage,
  onNewEvents,
  onCustomerContextUpdated,
  onBookingConfirmed,
  initialPrompt,
}: TextModeFallbackProps) {
  const [inputText, setInputText] = useState(initialPrompt || "");
  const [isLoading, setIsLoading] = useState(false);

  const handleSend = async (e?: React.FormEvent) => {
    if (e) e.preventDefault();
    if (!inputText.trim() || isLoading) return;

    const message = inputText.trim();
    setInputText("");
    onNewUserMessage(message);
    setIsLoading(true);

    try {
      const response = await sendChatMessage(sessionId, message, leadId);
      if (response.reply) {
        onNewAssistantMessage(response.reply);
      }
      if (response.events && response.events.length > 0) {
        onNewEvents(response.events);
      }
      if (response.customer_context) {
        onCustomerContextUpdated(response.customer_context);
      }
      if (response.booking_confirmed) {
        onBookingConfirmed(response.booking_confirmed);
      }
    } catch (err: any) {
      onNewAssistantMessage(`[Service Notice]: ${err.message || "Unable to send message."}`);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <form onSubmit={handleSend} className="w-full relative mt-3">
      <div className="flex items-center rounded-xl bg-zinc-900 border border-zinc-800 focus-within:border-emerald-500/50 shadow-inner px-3 py-1.5 transition-colors">
        <MessageSquare className="w-4 h-4 text-zinc-500 mr-2 shrink-0" />
        <input
          type="text"
          value={inputText}
          onChange={(e) => setInputText(e.target.value)}
          placeholder="Type your question or request..."
          disabled={isLoading}
          className="flex-1 bg-transparent py-1.5 text-xs sm:text-sm text-zinc-100 placeholder-zinc-500 focus:outline-hidden disabled:opacity-50"
        />
        <button
          type="submit"
          disabled={!inputText.trim() || isLoading}
          className="p-1.5 rounded-lg bg-emerald-600 hover:bg-emerald-500 text-white disabled:opacity-30 transition-all cursor-pointer shrink-0 ml-1"
        >
          {isLoading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Send className="w-4 h-4" />}
        </button>
      </div>
    </form>
  );
}
