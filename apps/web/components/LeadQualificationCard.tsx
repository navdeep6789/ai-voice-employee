"use client";

import { CustomerContext } from "@/types";
import { CheckCircle2, AlertCircle, BarChart3 } from "lucide-react";

interface LeadQualificationCardProps {
  context: CustomerContext | null;
}

export function LeadQualificationCard({ context }: LeadQualificationCardProps) {
  const score = context?.qualification_score || 0;
  const details = context?.qualification_details;
  const reasons = details?.reasons || [];
  const missing = details?.missing_fields || [];

  const getScoreColor = () => {
    if (score >= 65) return "text-emerald-400 border-emerald-500/30 bg-emerald-950/20";
    if (score >= 30) return "text-amber-400 border-amber-500/30 bg-amber-950/20";
    return "text-zinc-400 border-zinc-700 bg-zinc-900";
  };

  return (
    <div className="bg-zinc-900/50 border border-zinc-800/80 rounded-xl p-4 shadow-xs">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800/60 mb-3">
        <div className="flex items-center space-x-2">
          <BarChart3 className="w-4 h-4 text-emerald-400" />
          <h3 className="text-xs font-semibold tracking-wider text-zinc-300 uppercase font-mono">
            Lead Qualification
          </h3>
        </div>
        <div className={`px-2.5 py-0.5 rounded-full border text-xs font-mono font-bold ${getScoreColor()}`}>
          {score} / 100
        </div>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-zinc-800/80 rounded-full h-2 mb-3 overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            score >= 65
              ? "bg-gradient-to-r from-teal-500 to-emerald-400"
              : score >= 30
              ? "bg-gradient-to-r from-amber-500 to-amber-300"
              : "bg-zinc-600"
          }`}
          style={{ width: `${Math.max(4, score)}%` }}
        />
      </div>

      {/* Deterministic Evaluation Points */}
      <div className="space-y-2 text-xs">
        {reasons.length > 0 && (
          <div>
            <span className="text-[10px] font-mono uppercase text-zinc-400 font-semibold tracking-wider">
              Identified Criteria:
            </span>
            <ul className="mt-1 space-y-1">
              {reasons.slice(0, 3).map((r, i) => (
                <li key={i} className="flex items-start space-x-1.5 text-zinc-300">
                  <CheckCircle2 className="w-3.5 h-3.5 text-emerald-400 shrink-0 mt-0.5" />
                  <span className="truncate">{r}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {missing.length > 0 && (
          <div>
            <span className="text-[10px] font-mono uppercase text-zinc-400 font-semibold tracking-wider">
              Pending Factors:
            </span>
            <ul className="mt-1 space-y-1">
              {missing.slice(0, 2).map((m, i) => (
                <li key={i} className="flex items-start space-x-1.5 text-zinc-400">
                  <AlertCircle className="w-3.5 h-3.5 text-zinc-500 shrink-0 mt-0.5" />
                  <span className="truncate">{m}</span>
                </li>
              ))}
            </ul>
          </div>
        )}

        {reasons.length === 0 && missing.length === 0 && (
          <p className="text-zinc-500 italic text-[11px]">
            Qualification criteria will evaluate in real time as project scope is discussed.
          </p>
        )}
      </div>
    </div>
  );
}
