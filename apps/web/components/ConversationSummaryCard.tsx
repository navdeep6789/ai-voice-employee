"use client";

import { ConversationSummary } from "@/types";
import { FileCheck, ArrowRight, UserCheck, CheckCircle2 } from "lucide-react";

interface ConversationSummaryCardProps {
  summary: ConversationSummary;
}

export function ConversationSummaryCard({ summary }: ConversationSummaryCardProps) {
  return (
    <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-5 shadow-lg space-y-4">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800">
        <div className="flex items-center space-x-2">
          <FileCheck className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-semibold uppercase tracking-wider text-zinc-200 font-mono">
            Conversation Summary
          </h3>
        </div>
        <div className="flex items-center space-x-2">
          <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-emerald-950/70 border border-emerald-800 text-emerald-300">
            Score: {summary.qualification_score}/100
          </span>
          <span className="text-[11px] font-mono px-2 py-0.5 rounded-full bg-zinc-800 text-zinc-300">
            {summary.lead_status}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
        <div>
          <span className="text-[10px] text-zinc-400 font-mono uppercase">Customer</span>
          <div className="font-medium text-zinc-200 mt-0.5">
            {summary.customer_name || "Not provided"} {summary.company ? `(${summary.company})` : ""}
          </div>
        </div>

        <div>
          <span className="text-[10px] text-zinc-400 font-mono uppercase">Email</span>
          <div className="font-medium text-zinc-200 mt-0.5">
            {summary.email || "Not provided"}
          </div>
        </div>

        <div>
          <span className="text-[10px] text-zinc-400 font-mono uppercase">Project Scope / Use Case</span>
          <div className="font-medium text-zinc-200 mt-0.5">
            {summary.use_case || summary.intent || "General inquiry"}
          </div>
        </div>

        <div>
          <span className="text-[10px] text-zinc-400 font-mono uppercase">Timeline & Budget</span>
          <div className="font-medium text-zinc-200 mt-0.5">
            {summary.timeline || "Not specified"} · {summary.budget_range || "Not specified"}
          </div>
        </div>
      </div>

      {summary.requirements && summary.requirements.length > 0 && (
        <div className="pt-2 border-t border-zinc-800/60">
          <span className="text-[10px] text-zinc-400 font-mono uppercase">Documented Requirements</span>
          <div className="flex flex-wrap gap-1.5 mt-1.5">
            {summary.requirements.map((req, i) => (
              <span
                key={i}
                className="text-[11px] px-2 py-0.5 bg-zinc-950 border border-zinc-800 rounded-md text-zinc-300 font-mono"
              >
                {req}
              </span>
            ))}
          </div>
        </div>
      )}

      {summary.next_action && (
        <div className="p-3 bg-zinc-950/80 rounded-lg border border-zinc-800/80 flex items-center space-x-2 text-xs">
          <ArrowRight className="w-3.5 h-3.5 text-emerald-400 shrink-0" />
          <span className="text-zinc-400">Next Action:</span>
          <strong className="text-zinc-200 font-medium">{summary.next_action}</strong>
        </div>
      )}
    </div>
  );
}
