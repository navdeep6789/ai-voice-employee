"use client";

import { CustomerContext } from "@/types";
import { User, Building, Target, Clock, DollarSign, Layers } from "lucide-react";

interface CustomerContextCardProps {
  context: CustomerContext | null;
}

export function CustomerContextCard({ context }: CustomerContextCardProps) {
  const fields = [
    {
      label: "Customer Name",
      value: context?.name || "Not identified",
      icon: User,
      isIdentified: Boolean(context?.name),
    },
    {
      label: "Company",
      value: context?.company || "Not identified",
      icon: Building,
      isIdentified: Boolean(context?.company),
    },
    {
      label: "Inquiry Intent",
      value: context?.intent || "General inquiry",
      icon: Target,
      isIdentified: Boolean(context?.intent),
    },
    {
      label: "Timeline",
      value: context?.timeline || "Unknown",
      icon: Clock,
      isIdentified: Boolean(context?.timeline),
    },
    {
      label: "Budget",
      value: context?.budget_range || "Unknown",
      icon: DollarSign,
      isIdentified: Boolean(context?.budget_range),
    },
    {
      label: "Requirements",
      value: context?.requirements || "Evaluating scope",
      icon: Layers,
      isIdentified: Boolean(context?.requirements),
    },
  ];

  const getStatusColor = (status?: string) => {
    switch (status) {
      case "MEETING_BOOKED":
        return "bg-emerald-950/80 border-emerald-700 text-emerald-300";
      case "QUALIFIED":
        return "bg-cyan-950/80 border-cyan-700 text-cyan-300";
      case "QUALIFYING":
        return "bg-amber-950/80 border-amber-700 text-amber-300";
      case "HANDOFF":
        return "bg-purple-950/80 border-purple-700 text-purple-300";
      default:
        return "bg-zinc-900 border-zinc-800 text-zinc-400";
    }
  };

  return (
    <div className="bg-zinc-900/50 border border-zinc-800/80 rounded-xl p-4 shadow-xs">
      <div className="flex items-center justify-between pb-3 border-b border-zinc-800/60 mb-3">
        <div className="flex items-center space-x-2">
          <span className="w-2 h-2 rounded-full bg-emerald-400" />
          <h3 className="text-xs font-semibold tracking-wider text-zinc-300 uppercase font-mono">
            Customer Context
          </h3>
        </div>
        <span
          className={`text-[10px] font-mono px-2 py-0.5 rounded-full border ${getStatusColor(
            context?.lead_status
          )}`}
        >
          {context?.lead_status || "NEW"}
        </span>
      </div>

      <div className="grid grid-cols-2 gap-2.5 text-xs">
        {fields.map((f, i) => {
          const Icon = f.icon;
          return (
            <div
              key={i}
              className={`p-2 rounded-lg border transition-colors ${
                f.isIdentified
                  ? "bg-zinc-900/80 border-zinc-800 text-zinc-200"
                  : "bg-zinc-950/40 border-zinc-900/60 text-zinc-500"
              }`}
            >
              <div className="flex items-center space-x-1.5 text-[10px] text-zinc-400 mb-1 font-mono">
                <Icon className="w-3 h-3 text-zinc-500" />
                <span>{f.label}</span>
              </div>
              <div className="font-medium truncate" title={f.value}>
                {f.value}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
