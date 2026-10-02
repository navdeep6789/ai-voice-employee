"use client";

import { useEffect, useState } from "react";
import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { fetchConfig, fetchHealth } from "@/lib/api";
import { Settings, Shield, Server, CheckCircle2, AlertCircle, Key, Cpu, Database } from "lucide-react";

export default function SettingsPage() {
  const [config, setConfig] = useState<any>(null);
  const [health, setHealth] = useState<any>(null);

  useEffect(() => {
    fetchConfig().then(setConfig).catch(console.error);
    fetchHealth().then(setHealth).catch(console.error);
  }, []);

  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-4xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-8 space-y-8">
        <div className="space-y-2 border-b border-zinc-900 pb-6">
          <div className="flex items-center space-x-2 text-xs font-mono text-zinc-400">
            <Settings className="w-4 h-4 text-emerald-400" />
            <span>CONFIGURATION & AUDIT</span>
          </div>
          <h1 className="text-2xl font-bold tracking-tight text-white">System Settings & Guardrails</h1>
          <p className="text-xs sm:text-sm text-zinc-400">
            Live technical verification of backend configuration, security boundaries, and model parameterization.
          </p>
        </div>

        {/* Status Overview Card */}
        <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 shadow-xl space-y-5">
          <h2 className="text-sm font-semibold uppercase tracking-wider text-zinc-300 font-mono flex items-center space-x-2">
            <Server className="w-4 h-4 text-emerald-400" />
            <span>Runtime Health & Provider Status</span>
          </h2>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs">
            <div className="p-3.5 rounded-xl bg-zinc-950/80 border border-zinc-800 space-y-1">
              <span className="text-[10px] text-zinc-500 font-mono uppercase">Backend Health</span>
              <div className="flex items-center space-x-2 font-medium">
                {health?.status === "healthy" ? (
                  <>
                    <CheckCircle2 className="w-4 h-4 text-emerald-400" />
                    <span className="text-emerald-300">Operational ({health.version})</span>
                  </>
                ) : (
                  <>
                    <AlertCircle className="w-4 h-4 text-amber-400" />
                    <span className="text-amber-300">Checking...</span>
                  </>
                )}
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-zinc-950/80 border border-zinc-800 space-y-1">
              <span className="text-[10px] text-zinc-500 font-mono uppercase">Gemini API Key</span>
              <div className="flex items-center space-x-2 font-medium">
                <Key className="w-4 h-4 text-zinc-400" />
                <span className="text-zinc-300">
                  {config?.has_api_key ? "Configured (Server-Side Only)" : "Demo Simulation Mode"}
                </span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-zinc-950/80 border border-zinc-800 space-y-1">
              <span className="text-[10px] text-zinc-500 font-mono uppercase">Gemini Live Model</span>
              <div className="flex items-center space-x-2 font-medium font-mono text-zinc-300">
                <Cpu className="w-4 h-4 text-cyan-400" />
                <span>{config?.live_model || "gemini-2.0-flash-exp"}</span>
              </div>
            </div>

            <div className="p-3.5 rounded-xl bg-zinc-950/80 border border-zinc-800 space-y-1">
              <span className="text-[10px] text-zinc-500 font-mono uppercase">RAG Embedding Engine</span>
              <div className="flex items-center space-x-2 font-medium font-mono text-zinc-300">
                <Database className="w-4 h-4 text-indigo-400" />
                <span>Local Cosine Vectorizer (Free-First)</span>
              </div>
            </div>
          </div>
        </div>

        {/* Security Guardrails Card */}
        <div className="bg-zinc-900/40 border border-zinc-800 rounded-2xl p-6 shadow-xl space-y-4 text-xs">
          <div className="flex items-center space-x-2 text-emerald-400 font-semibold text-sm">
            <Shield className="w-4 h-4" />
            <span>Active Enterprise Guardrails</span>
          </div>

          <ul className="space-y-2 text-zinc-300">
            <li className="flex items-start space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Zero Client Secrets:</strong> GEMINI_API_KEY resides strictly on the backend. Never exposed to browser bundle.</span>
            </li>
            <li className="flex items-start space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Input Sanitization:</strong> Audio streams and message buffers are constrained by strict payload size and rate limits.</span>
            </li>
            <li className="flex items-start space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Pydantic v2 Schema Validation:</strong> Tool inputs are strictly validated before execution; arbitrary SQL or shell injections are rejected.</span>
            </li>
            <li className="flex items-start space-x-2">
              <CheckCircle2 className="w-4 h-4 text-emerald-400 shrink-0 mt-0.5" />
              <span><strong>Explicit Confirmation Rule:</strong> Meeting bookings require user confirmation and real calendar slot locking to prevent double bookings.</span>
            </li>
          </ul>
        </div>
      </main>

      <Footer />
    </div>
  );
}
