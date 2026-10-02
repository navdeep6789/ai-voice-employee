"use client";

import { useState, useEffect } from "react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { VoiceOrb } from "@/components/VoiceOrb";
import { VoiceControls } from "@/components/VoiceControls";
import { ConversationTranscript } from "@/components/ConversationTranscript";
import { CustomerContextCard } from "@/components/CustomerContextCard";
import { LeadQualificationCard } from "@/components/LeadQualificationCard";
import { AgentActivityFeed } from "@/components/AgentActivityFeed";
import { BookingConfirmationCard } from "@/components/BookingConfirmationCard";
import { ConversationSummaryCard } from "@/components/ConversationSummaryCard";
import { DemoScenarios } from "@/components/DemoScenarios";
import { TextModeFallback } from "@/components/TextModeFallback";
import { useVoiceSession } from "@/hooks/useVoiceSession";
import { AlertCircle, ShieldAlert, Sparkles, RefreshCw } from "lucide-react";

export default function HomePage() {
  const [sessionId, setSessionId] = useState<string>("");
  const [isTextMode, setIsTextMode] = useState<boolean>(false);
  const [prefilledPrompt, setPrefilledPrompt] = useState<string>("");

  useEffect(() => {
    // Generate or retrieve persistent session ID for caller
    const existing = sessionStorage.getItem("voice_agent_session");
    if (existing) {
      setSessionId(existing);
    } else {
      const newId = `session-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 6)}`;
      sessionStorage.setItem("voice_agent_session", newId);
      setSessionId(newId);
    }
  }, []);

  const {
    voiceState,
    transcript,
    activityEvents,
    customerContext,
    bookingConfirmed,
    summary,
    audioLevel,
    errorMessage,
    isMuted,
    startVoice,
    endVoice,
    toggleMute,
    setCustomerContext,
    setBookingConfirmed,
    addManualTranscriptMessage,
    recordManualEvents,
  } = useVoiceSession({ sessionId });

  const handleScenarioSelect = (promptText: string) => {
    setIsTextMode(true);
    setPrefilledPrompt(promptText);
  };

  const handleResetSession = () => {
    const newId = `session-${Date.now().toString(36)}-${Math.random().toString(36).substring(2, 6)}`;
    sessionStorage.setItem("voice_agent_session", newId);
    window.location.reload();
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans selection:bg-emerald-500/30 selection:text-emerald-200">
      <Navbar />

      <main className="flex-1 max-w-7xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        {/* Landing Product Header */}
        <div className="flex flex-col md:flex-row md:items-end justify-between border-b border-zinc-900 pb-6 gap-4">
          <div className="space-y-2 max-w-2xl">
            <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-md bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-zinc-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
              <span>OPEN SOURCE VOICE AGENT PLATFORM</span>
            </div>
            <h1 className="text-2xl sm:text-3xl lg:text-4xl font-semibold tracking-tight text-white">
              AI Voice Employee
            </h1>
            <p className="text-sm sm:text-base text-zinc-400 leading-relaxed">
              An AI employee that understands voice in real time, retrieves company knowledge,
              determines commercial qualification, and executes calendar and CRM actions.
            </p>
          </div>

          <div className="flex items-center space-x-2">
            <button
              onClick={handleResetSession}
              className="inline-flex items-center space-x-1.5 px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900/60 hover:bg-zinc-800 text-xs text-zinc-400 hover:text-zinc-200 transition-colors font-mono cursor-pointer"
              title="Reset Session Data"
            >
              <RefreshCw className="w-3 h-3" />
              <span>Reset Demo State</span>
            </button>
          </div>
        </div>

        {/* Error Banner if any */}
        {errorMessage && (
          <div className="p-4 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-center justify-between shadow-xs">
            <div className="flex items-center space-x-2">
              <AlertCircle className="w-4 h-4 text-rose-400 shrink-0" />
              <span>{errorMessage}</span>
            </div>
            <button
              onClick={() => setIsTextMode(true)}
              className="underline hover:text-rose-200 font-medium cursor-pointer"
            >
              Use Text Mode
            </button>
          </div>
        )}

        {/* Main Product Command Center */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Column: Voice Interaction & Transcript (7 Cols) */}
          <div className="lg:col-span-7 space-y-6 flex flex-col">
            {/* Interactive Voice Console Card */}
            <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-2xl p-6 shadow-xl relative overflow-hidden backdrop-blur-xs">
              <div className="absolute top-3 right-4 flex items-center space-x-1.5 text-[10px] font-mono text-zinc-500">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-500/80" />
                <span>Web Audio & WebSocket</span>
              </div>

              {/* Voice Orb Visualization */}
              <VoiceOrb state={voiceState} audioLevel={audioLevel} />

              {/* Voice Controls */}
              <VoiceControls
                state={voiceState}
                isMuted={isMuted}
                onStart={startVoice}
                onEnd={endVoice}
                onToggleMute={toggleMute}
                onToggleTextMode={() => setIsTextMode((prev) => !prev)}
                isTextMode={isTextMode}
              />
            </div>

            {/* Conversation Transcript */}
            <div className="bg-zinc-900/30 border border-zinc-800/80 rounded-2xl p-5 shadow-xl flex flex-col space-y-3">
              <div className="flex items-center justify-between pb-2 border-b border-zinc-800/60">
                <span className="text-xs font-semibold text-zinc-300 font-mono uppercase tracking-wider">
                  Live Conversation Transcript
                </span>
                <span className="text-[10px] font-mono text-zinc-500">
                  {transcript.length} {transcript.length === 1 ? "turn" : "turns"}
                </span>
              </div>

              <ConversationTranscript
                messages={transcript}
                isThinking={voiceState === "PROCESSING" || voiceState === "TOOL_CALL"}
              />

              {/* Text Fallback Input Box */}
              {isTextMode && (
                <TextModeFallback
                  sessionId={sessionId}
                  leadId={customerContext?.id}
                  onNewUserMessage={(text) => addManualTranscriptMessage("user", text)}
                  onNewAssistantMessage={(text) => addManualTranscriptMessage("assistant", text)}
                  onNewEvents={recordManualEvents}
                  onCustomerContextUpdated={setCustomerContext}
                  onBookingConfirmed={setBookingConfirmed}
                  initialPrompt={prefilledPrompt}
                />
              )}
            </div>

            {/* Scenario Shortcuts */}
            <DemoScenarios onSelectPrompt={handleScenarioSelect} />
          </div>

          {/* Right Column: Real-time Business Context & Telemetry (5 Cols) */}
          <div className="lg:col-span-5 space-y-5">
            {/* Booking Confirmed Card (Appears if meeting booked!) */}
            {bookingConfirmed && <BookingConfirmationCard booking={bookingConfirmed} />}

            {/* Customer Context Card */}
            <CustomerContextCard context={customerContext} />

            {/* Lead Qualification Deterministic Card */}
            <LeadQualificationCard context={customerContext} />

            {/* Real Agent Activity Event Stream */}
            <AgentActivityFeed events={activityEvents} />

            {/* Conversation Summary Card (Appears on call end or summary) */}
            {summary && <ConversationSummaryCard summary={summary} />}
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
