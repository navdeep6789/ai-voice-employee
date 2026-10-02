"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Bot, Users, Activity, FileText, Settings, ShieldCheck } from "lucide-react";

export function Navbar() {
  const pathname = usePathname();

  const navLinks = [
    { href: "/", label: "AI Employee", icon: Bot },
    { href: "/leads", label: "Demo CRM", icon: Users },
    { href: "/activity", label: "Agent Telemetry", icon: Activity },
    { href: "/about", label: "Architecture", icon: FileText },
    { href: "/settings", label: "Config & Guardrails", icon: Settings },
  ];

  return (
    <header className="border-b border-zinc-800/80 bg-zinc-950/90 backdrop-blur-md sticky top-0 z-50">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
        {/* Brand & Product Title */}
        <div className="flex items-center space-x-3">
          <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-indigo-500 to-emerald-400 p-[1px] shadow-sm">
            <div className="w-full h-full bg-zinc-950 rounded-[7px] flex items-center justify-center">
              <Bot className="w-4 h-4 text-emerald-400" />
            </div>
          </div>
          <div>
            <div className="flex items-center space-x-2">
              <span className="font-semibold tracking-tight text-white text-sm sm:text-base">
                VOICE AGENT
              </span>
              <span className="text-zinc-500 text-xs">/</span>
              <span className="text-zinc-300 text-xs sm:text-sm font-medium">
                AI Employee
              </span>
            </div>
            <div className="text-[10px] text-zinc-400 font-mono tracking-wide hidden sm:block">
              Open-Source Real-Time AI Receptionist, Sales & Qualification Platform
            </div>
          </div>
        </div>

        {/* Center Nav Links */}
        <nav className="hidden md:flex items-center space-x-1">
          {navLinks.map((link) => {
            const Icon = link.icon;
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`px-3 py-1.5 text-xs font-medium rounded-md transition-colors flex items-center space-x-1.5 ${
                  isActive
                    ? "bg-zinc-800 text-white shadow-xs"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
                }`}
              >
                <Icon className="w-3.5 h-3.5" />
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>

        {/* Demo Badges */}
        <div className="flex items-center space-x-2">
          <div className="flex items-center space-x-1.5 bg-emerald-950/60 border border-emerald-800/60 text-emerald-400 text-[11px] px-2.5 py-1 rounded-full font-mono">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span>LIVE DEMO</span>
          </div>
          <div className="hidden lg:flex items-center space-x-1 bg-zinc-900 border border-zinc-800 text-zinc-400 text-[11px] px-2.5 py-1 rounded-full font-mono">
            <ShieldCheck className="w-3 h-3 text-zinc-400" />
            <span>FICTIONAL DATA</span>
          </div>
        </div>
      </div>
    </header>
  );
}
