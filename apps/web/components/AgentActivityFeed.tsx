"use client";

import { AgentActivityEvent } from "@/types";
import { CheckCircle2, Clock, AlertTriangle, ArrowRight, Database, Search, Calendar, DollarSign, UserCheck } from "lucide-react";

interface AgentActivityFeedProps {
  events: AgentActivityEvent[];
}

export function AgentActivityFeed({ events }: AgentActivityFeedProps) {
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
    <div className="bg-zinc-900/50 border border-zinc-800/80 rounded-xl p-4 shadow-xs flex flex-col">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800/60 mb-3">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-cyan-400" />
          <h3 className="text-xs font-semibold tracking-wider text-zinc-300 uppercase font-mono">
            Agent Real-time Activity
          </h3>
        </div>
        <span className="text-[10px] font-mono text-zinc-500">
          {events.length} {events.length === 1 ? "event" : "events"}
        </span>
      </div>

      <div className="space-y-2.5 max-h-56 overflow-y-auto pr-1 scrollbar-thin scrollbar-thumb-zinc-800">
        {events.length === 0 ? (
          <div className="py-6 text-center text-zinc-600 text-xs italic">
            Waiting for caller speech or tool execution...
          </div>
        ) : (
          events.map((evt) => {
            const isCompleted = evt.event_type === "tool_completed";
            const isRunning = evt.event_type === "tool_started" || evt.status === "running";
            const isFailed = evt.event_type === "tool_failed" || evt.status === "failed";
            const Icon = getToolIcon(evt.tool_name);

            return (
              <div
                key={evt.id}
                className="p-2.5 rounded-lg bg-zinc-950/60 border border-zinc-800/60 text-xs space-y-1"
              >
                <div className="flex items-center justify-between">
                  <div className="flex items-center space-x-2">
                    <Icon className="w-3.5 h-3.5 text-zinc-400" />
                    <span className="font-mono font-medium text-zinc-200">
                      {evt.tool_name || evt.event_type}
                    </span>
                  </div>

                  <div className="flex items-center space-x-1.5">
                    {evt.duration_ms !== undefined && evt.duration_ms !== null && (
                      <span className="font-mono text-[10px] text-zinc-500">
                        {evt.duration_ms}ms
                      </span>
                    )}

                    {isCompleted && <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400" />}
                    {isRunning && <Clock className="w-3.5 h-3.5 text-amber-400 animate-spin" />}
                    {isFailed && <AlertTriangle className="w-3.5 h-3.5 text-rose-400" />}
                  </div>
                </div>

                {/* Brief Result Snippet */}
                {evt.payload && (
                  <div className="text-[11px] text-zinc-400 bg-zinc-900/80 px-2 py-1 rounded font-mono truncate">
                    {typeof evt.payload === "string"
                      ? evt.payload
                      : JSON.stringify(evt.payload).substring(0, 75)}
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
}
