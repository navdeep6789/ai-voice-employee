# System Architecture & Technical RFC: AI Voice Employee

## 1. Executive Summary
The **AI Voice Employee** is an enterprise-grade digital receptionist, solutions engineer, and qualification assistant platform.

The system replaces traditional fragmented customer intake (static web forms, delayed email follow-ups, or brittle IVR trees) with an intelligent real-time conversational agent capable of answering questions from an internal knowledge base, calculating deterministic lead qualification scores, querying calendar availability, booking meetings, and updating CRM records in real time.

---

## 2. High-Level System Architecture Diagram

```text
+-----------------------------------------------------------------------------------+
|                                CLIENT LAYER (Browser)                             |
|                                                                                   |
|   +-----------------------+     +------------------------+                        |
|   |  AudioWorklet (16kHz) |     |  Next.js 16 + React 19 |                        |
|   |  Linear PCM Streaming |     |  State Machine Console |                        |
|   +-----------+-----------+     +-----------+------------+                        |
+---------------|-----------------------------|-------------------------------------+
                | Audio Frames (Binary)       | JSON Events / Text Fallback
                |                             |
                v                             v
+-----------------------------------------------------------------------------------+
|                           FASTAPI VOICE & API GATEWAY                             |
|                                                                                   |
|   +------------------------+     +------------------------+                       |
|   |  WebSocket (/ws/voice) |     |   REST Endpoints (/api)|                       |
|   +-----------+------------+     +-----------+------------+                       |
|               |                              |                                    |
|               v                              v                                    |
|   +-------------------------------------------------------+                       |
|   |          GeminiLiveSession / TextAgentService         |                       |
|   +---------------------------+---------------------------+                       |
+-------------------------------|---------------------------------------------------+
                                |
                                v
+-----------------------------------------------------------------------------------+
|                           AI & AGENT WORKFLOW ENGINE                              |
|                                                                                   |
|   +-------------------------------------------------------+                       |
|   |  Google Gemini Live API (Native Multimodal Streaming) |                       |
|   +---------------------------+---------------------------+                       |
|                               | Tool Dispatches                                   |
|                               v                                                   |
|   +-------------------------------------------------------+                       |
|   |            ToolRouter & Pydantic Validation           |                       |
|   +---+-------------------+-------------------+-------+---+                       |
|       |                   |                   |       |                           |
|       v                   v                   v       v                           |
|  [PricingService]  [CalendarService]   [CRMService] [RAGService]                  |
+-------+-------------------+-------------------+-------+---------------------------+
        |                   |                   |       |
        +-------------------+---------+---------+-------+
                                      |
                                      v
+-----------------------------------------------------------------------------------+
|                           PERSISTENCE & REPOSITORIES                              |
|                                                                                   |
|   +-----------------------+     +------------------------+                        |
|   |  SQLAlchemy 2.0 Repos |     |  Deterministic Scoring |                        |
|   |  (Leads, Bookings,    |     |  LeadQualification     |                        |
|   |   Slots, Events, Docs)|     |  (0 - 100 Math Engine) |                        |
|   +-----------+-----------+     +------------------------+                        |
|               |                                                                   |
|               v                                                                   |
|   +-----------------------+                                                       |
|   |  SQLite / PostgreSQL  |                                                       |
|   +-----------------------+                                                       |
+-----------------------------------------------------------------------------------+
```

---

## 3. Component Deep Dive

### 3.1 Audio Ingest & Playback Pipeline
- **Microphone Capture**: The browser's `AudioContext` initializes at 16,000 Hz. An `AudioWorkletNode` processes input audio frames in an isolated audio thread, converting 32-bit float audio directly into 16-bit signed Linear PCM integers.
- **WebSocket Gateway**: The PCM byte buffers are pushed directly over a binary WebSocket connection (`/ws/voice`) to FastAPI without HTTP overhead.
- **Playback Scheduling**: Audio output received from Gemini Live is scheduled contiguously in Web Audio buffer queues, eliminating click, jitter, and frame duplication artifacts.

### 3.2 Reasoning & Tool Calling
- Gemini Live processes native streaming audio and identifies when business operations must occur.
- When a function call is emitted by the model, `GeminiLiveSession` intercepts the call, invokes `ToolRouter`, records execution telemetry, and returns the structured `FunctionResponse` back into the live session.

### 3.3 RAG Subsystem
- **Parsing**: Documents in `data/knowledge/` are parsed and semantically chunked along section headers.
- **Local Vectors**: Chunks are embedded and indexed locally using dense normalized TF-IDF vectorization with cosine similarity scoring.
- **Zero Hallucination Guardrails**: Only chunks exceeding the similarity threshold are injected into the agent context, with complete document and chunk citations.

### 3.4 Calendar & Concurrency State Protection
- The demo calendar seeds 25 availability slots.
- When `book_meeting` is invoked, the target slot is locked (`is_booked = True`), preventing race conditions or duplicate bookings.
- The booking requires explicit user verbal/text confirmation before execution.
