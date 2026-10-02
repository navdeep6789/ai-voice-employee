"use client";

import { Sparkles, ArrowUpRight } from "lucide-react";

interface DemoScenariosProps {
  onSelectPrompt: (promptText: string) => void;
}

export function DemoScenarios({ onSelectPrompt }: DemoScenariosProps) {
  const scenarios = [
    {
      label: "Ask about AI voice agents",
      prompt: "Can you explain how your real-time AI Voice Agents work and what technologies you use?",
    },
    {
      label: "Ask about pricing",
      prompt: "What is your pricing for an AI customer support system?",
    },
    {
      label: "Book a consultation meeting",
      prompt: "I'd like to check your available demo slots and book a consultation meeting next week.",
    },
    {
      label: "Explain Enterprise RAG",
      prompt: "How do you implement Enterprise RAG without hallucinations?",
    },
    {
      label: "Inbound sales qualification",
      prompt: "We are an agency looking to qualify inbound leads automatically. My name is David from Apex.",
    },
  ];

  return (
    <div className="space-y-2">
      <div className="flex items-center space-x-1.5 text-xs text-zinc-400 font-mono">
        <Sparkles className="w-3.5 h-3.5 text-emerald-400" />
        <span>Try a portfolio scenario:</span>
      </div>

      <div className="flex flex-wrap gap-2">
        {scenarios.map((sc, i) => (
          <button
            key={i}
            onClick={() => onSelectPrompt(sc.prompt)}
            className="group inline-flex items-center space-x-1 px-3 py-1.5 rounded-lg bg-zinc-900/90 border border-zinc-800 text-xs text-zinc-300 hover:text-white hover:border-zinc-700 hover:bg-zinc-800/80 transition-all cursor-pointer shadow-2xs"
          >
            <span>{sc.label}</span>
            <ArrowUpRight className="w-3 h-3 text-zinc-500 group-hover:text-emerald-400 transition-colors" />
          </button>
        ))}
      </div>
    </div>
  );
}
