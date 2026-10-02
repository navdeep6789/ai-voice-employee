"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { fetchEvents } from "@/lib/api";
import { AgentActivityEvent } from "@/types";
import { Activity, Clock, CheckCircle2, AlertTriangle, Database, Search, Calendar, DollarSign, UserCheck, Shield } from "lucide-react";

export default function ActivityPage() {
  const [events, setEvents] = useState<AgentActivityEvent[]>([]);
  const [sessionId, setSessionId] = useState<string>("");

  useEffect(() => {
    const existing = sessionStorage.getItem("voice_agent_session") || "default-session";
    setSessionId(existing);
    fetchEvents(existing)
      .then((data) => setEvents(data))
      .catch((err) => console.error("Error fetching telemetry:", err));
  }, []);

  const getToolIcon = (toolName?: string) => {
    switch (toolName) {
      case "search_knowledge":
        return Search;
      case "check_pricing":
        return DollarSign;
      case "check_calendar":
      case "book_meeting":
        return Calendar;
      case "create_lead":
      case "update_lead":
      case "calculate_lead_qualification":
        return UserCheck;
      default:
        return Database;
    }
  };

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-6">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between pb-6 border-b border-zinc-900 gap-4">
          <div>
            <div className="flex items-center space-x-2 text-xs font-mono text-zinc-400 mb-1">
              <Activity className="w-4 h-4 text-cyan-400" />
              <span>INTERNAL OBSERVABILITY</span>
            </div>
            <h1 className="text-2xl font-bold tracking-tight text-white">Agent Telemetry & Tool Traces</h1>
            <p className="text-xs sm:text-sm text-zinc-400 mt-1">
              Real-time audit log of model tool calls, execution latencies in milliseconds, and structured return payloads.
            </p>
          </div>

          <div className="bg-zinc-900/90 border border-zinc-800 px-3 py-1.5 rounded-lg text-xs font-mono text-zinc-400">
            Session: <span className="text-zinc-200">{sessionId.substring(0, 16)}...</span>
          </div>
        </div>

        {/* Telemetry Feed Card */}
        <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 shadow-xl space-y-4">
          {events.length === 0 ? (
            <div className="py-16 text-center text-zinc-500 text-sm">
              No tool executions recorded yet for this session. Initiate a voice or text inquiry to view live traces.
            </div>
          ) : (
            <div className="space-y-3">
              {events.map((evt) => {
                const isCompleted = evt.event_type === "tool_completed";
                const isRunning = evt.event_type === "tool_started" || evt.status === "running";
                const isFailed = evt.event_type === "tool_failed" || evt.status === "failed";
                const Icon = getToolIcon(evt.tool_name);

                return (
                  <div
                    key={evt.id}
                    className="p-4 rounded-xl bg-zinc-950/80 border border-zinc-800/80 space-y-2 text-xs font-mono"
                  >
                    <div className="flex items-center justify-between">
                      <div className="flex items-center space-x-2">
                        <Icon className="w-4 h-4 text-zinc-400" />
                        <span className="font-semibold text-zinc-200">
                          {evt.tool_name || evt.event_type}
                        </span>
                        <span className="text-[10px] text-zinc-500 px-2 py-0.5 rounded bg-zinc-900">
                          {evt.event_type}
                        </span>
                      </div>

                      <div className="flex items-center space-x-3">
                        {evt.duration_ms !== undefined && evt.duration_ms !== null && (
                          <span className="text-emerald-400 font-bold">
                            {evt.duration_ms} ms
                          </span>
                        )}
                        {isCompleted && <CheckCircle2 className="w-4 h-4 text-emerald-400" />}
                        {isRunning && <Clock className="w-4 h-4 text-amber-400 animate-spin" />}
                        {isFailed && <AlertTriangle className="w-4 h-4 text-rose-400" />}
                      </div>
                    </div>

                    {evt.payload && (
                      <div className="bg-zinc-900/90 rounded-lg p-2.5 text-[11px] text-zinc-300 overflow-x-auto border border-zinc-850">
                        <pre>{JSON.stringify(evt.payload, null, 2)}</pre>
                      </div>
                    )}

                    <div className="text-[10px] text-zinc-600">
                      Timestamp: {new Date(evt.created_at).toLocaleTimeString()}
                    </div>
                  </div>
                );
              })}
            </div>
          )}
        </div>
      </main>

      <Footer />
    </div>
  );
}
