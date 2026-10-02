import { Navbar } from "@/components/Navbar";
import { Footer } from "@/components/Footer";
import { Cpu, Server, Database, Volume2, ShieldCheck, Layers, GitBranch, Terminal } from "lucide-react";

export default function AboutPage() {
  return (
    <div className="min-h-screen bg-zinc-950 text-zinc-100 flex flex-col font-sans">
      <Navbar />

      <main className="flex-1 max-w-5xl w-full mx-auto px-4 sm:px-6 lg:px-8 py-10 space-y-10">
        {/* Header */}
        <div className="space-y-3 border-b border-zinc-900 pb-6">
          <div className="inline-flex items-center space-x-2 px-2.5 py-1 rounded-md bg-zinc-900 border border-zinc-800 text-[11px] font-mono text-emerald-400">
            <span>ENGINEERING RFC & SPECIFICATION</span>
          </div>
          <h1 className="text-3xl font-bold tracking-tight text-white">System Architecture</h1>
          <p className="text-zinc-400 text-sm leading-relaxed max-w-3xl">
            A production-grade, observable AI Voice Employee built as a modular monolith.
            Engineered with strict separation of concerns: Web Audio streaming, FastAPI WebSocket gateway,
            Gemini Live API native multimodal reasoning, local vectorized RAG, and deterministic business state mutation.
          </p>
        </div>

        {/* ASCII Architecture Diagram Box */}
        <div className="bg-zinc-900/60 border border-zinc-800 rounded-xl p-6 font-mono text-xs text-zinc-300 overflow-x-auto shadow-xl">
          <div className="text-emerald-400 font-semibold mb-3"># Real-Time Voice & Business Pipeline Architecture</div>
          <pre className="text-[11px] leading-relaxed text-zinc-300">
{`Browser (Next.js 16 + React 19)
  |  
  |-- [Microphone Audio] -> AudioWorklet (16kHz 16-bit Mono Linear PCM)
  |-- [Bidirectional WebSocket] (/ws/voice)
  v
FastAPI Voice Gateway (Python 3.12 + Uvicorn)
  |
  +------> Gemini Live API Session (Persistent WebSocket)
  |           |
  |           +------> Native Multimodal Reasoning & Low-Latency Audio Streaming
  |           |
  |           +------> Tool Call Dispatcher (ToolRouter)
  |                      |
  |                      +----> PricingService (Verified Demo Service Catalog)
  |                      |
  |                      +----> CalendarService (Slot Availability & Locking Mutation)
  |                      |
  |                      +----> CRMService (Lead Creation & Transparent Qualification)
  |                      |
  |                      +----> RAGService (Document Chunking + Local Vector Retrieval)
  |
  +------> Real-Time Agent Activity Telemetry (tool_started, tool_completed, tool_failed)
  |
  v
Persistence Layer (SQLAlchemy 2.0 + SQLite / PostgreSQL)`}
          </pre>
        </div>

        {/* Architectural Principles */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800 space-y-2.5">
            <div className="flex items-center space-x-2 text-emerald-400 font-semibold text-sm">
              <ShieldCheck className="w-4 h-4" />
              <span>Grounded, Deterministic Business Logic</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              The LLM is strictly prohibited from inventing pricing, calendar availability, or qualification scores.
              Pricing is fetched strictly from the verified demo catalog. Meeting bookings require explicit confirmation and execute real database mutations.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800 space-y-2.5">
            <div className="flex items-center space-x-2 text-cyan-400 font-semibold text-sm">
              <Volume2 className="w-4 h-4" />
              <span>Sub-Second Latency Audio Streaming</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Bypasses traditional multi-hop STT → LLM → TTS cascades. Audio streams directly as 16kHz PCM frames over WebSockets into Gemini Live,
              delivering natural human conversational pauses and real-time interruption handling.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800 space-y-2.5">
            <div className="flex items-center space-x-2 text-indigo-400 font-semibold text-sm">
              <Database className="w-4 h-4" />
              <span>Free-First Offline Local RAG</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              Knowledge retrieval is completely self-contained. Chunks are embedded and indexed locally using dense cosine similarity without paid vector databases or external embeddings APIs, guaranteeing immediate setup and zero operating costs.
            </p>
          </div>

          <div className="p-5 rounded-xl bg-zinc-900/40 border border-zinc-800 space-y-2.5">
            <div className="flex items-center space-x-2 text-amber-400 font-semibold text-sm">
              <Terminal className="w-4 h-4" />
              <span>100% Feature-Parity Text Fallback</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed">
              If a user denies microphone permissions or has an unsupported browser, the application seamlessly provides an inline text chat with the exact same tools, business logic, RAG retrieval, and CRM state mutations.
            </p>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
}
