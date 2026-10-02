# Open Voice Agent Platform — Full-Duplex AI Voice Employee

*A production-grade, observable, full-duplex conversational voice agent and inbound qualification platform powered by Gemini Live API, Next.js, and FastAPI.*

[![FastAPI](https://img.shields.io/badge/FastAPI-0.115+-009688.svg?logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com)
[![Next.js](https://img.shields.io/badge/Next.js-16+-black.svg?logo=next.js&logoColor=white)](https://nextjs.org)
[![Python](https://img.shields.io/badge/Python-3.12+-3776AB.svg?logo=python&logoColor=white)](https://www.python.org)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.0+-3178C6.svg?logo=typescript&logoColor=white)](https://www.typescriptlang.org)
[![Gemini Live](https://img.shields.io/badge/Gemini_Live-Multimodal_Streaming-4E73DF.svg)](https://ai.google.dev)
[![Tests](https://img.shields.io/badge/Tests-6%20Passing-10B981.svg)](tests/)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

---

## 1. Overview

**Open Voice Agent Platform** is an end-to-end, modular voice AI employee engineered for businesses, consultancies, customer support centers, and sales teams.

Unlike standard "STT → LLM → TTS" cascades that suffer from 3–5 second turnaround latencies and unnatural conversations, this platform implements a native **bidirectional multimodal streaming pipeline**:

1. **Audio Ingest**: Captures microphone input at 16kHz 16-bit mono Linear PCM using a dedicated browser `AudioWorkletNode`.
2. **WebSocket Streaming**: Streams binary PCM frames over WebSockets directly to the FastAPI voice gateway.
3. **Gemini Live Reasoning**: Communicates natively with the Google Gemini Live API (`gemini-2.0-flash-exp`) over persistent WebSockets for sub-second human-like voice responses and real-time interruption handling.
4. **Deterministic Tool Execution**: The model triggers strictly-typed Pydantic v2 tools (`search_knowledge`, `check_pricing`, `create_lead`, `calculate_lead_qualification`, `check_calendar`, `book_meeting`, `transfer_to_human`).
5. **State Mutation & Observability**: Real database updates (CRM leads, locked calendar slots, deterministic qualification scores) reflect immediately across real-time UI telemetry.
6. **Contiguous Audio Playback**: Receives 24kHz PCM chunks back from Gemini Live and streams them directly into the client Web Audio buffer queue.
7. **100% Feature-Parity Text Fallback**: Provides immediate keyboard chat fallback with identical tools, RAG grounding, and CRM persistence.

---

## 2. System Architecture

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

Detailed architectural diagrams and component RFCs are documented in [`docs/architecture.md`](docs/architecture.md).

---

## 3. Key Capabilities & Features

### 🎙️ Sub-Second Streaming Voice Pipeline
- Native 16kHz audio capture with zero frontend transcoding libraries.
- Persistent duplex WebSocket pipe between Client ↔ FastAPI ↔ Google Gemini Live.
- Instant client-side speech ducking and interruption recovery.

### 📚 Free-First Offline RAG (Zero API Cost)
- Markdown files placed in `data/knowledge/` are semantically chunked along headers.
- Embedded using local dense cosine vector indexing.
- **100% free and offline** — requires no paid external vector database or embeddings subscription.

### 🎯 Deterministic Commercial Lead Qualification (0–100)
Eliminates probabilistic hallucinations in qualification by computing exact score rubrics:
- **Use Case Identified**: +20 pts
- **Concrete Technical Scope**: +15 pts
- **Project Timeline Given**: +15 pts
- **Budget Allocation Known**: +15 pts
- **Company & Domain Context**: +10 pts
- **Stakeholder Role Identified**: +10 pts
- **Consultation Meeting Requested**: +15 pts
- *Score is transparently displayed with point breakdowns in the UI in real time.*

### 📅 Anti-Collision Calendar Booking
- Dynamic calendar slot availability inspection (`check_calendar`).
- Database-backed concurrency locking on booking (`book_meeting`) to prevent double-booking.
- Mandatory user confirmation protocol enforced before slot mutations.

### 🔍 Real-Time Agent Telemetry
- Structured telemetry events (`tool_started`, `tool_completed`, `tool_failed`) recorded with millisecond duration tracking.
- Live inspection drawer at `/activity` and embedded live feed on the main console.

---

## 4. Repository Structure

```text
├── apps/
│   ├── api/                   # FastAPI backend application
│   │   ├── app/
│   │   │   ├── ai/            # Gemini Live & Text Agent services + system prompts
│   │   │   ├── api/routes/    # REST endpoints (/health, /leads, /calendar, /chat, /ws)
│   │   │   ├── core/          # Pydantic settings, constants, structured logging
│   │   │   ├── db/            # SQLAlchemy 2.0 async/sync sessions & Base models
│   │   │   ├── models/        # ORM entities (Lead, Booking, Slot, Conversation, Event)
│   │   │   ├── providers/     # Decoupled CRM & Calendar interfaces
│   │   │   ├── rag/           # Semantic chunker, local vectorizer, search service
│   │   │   ├── repositories/  # Database repositories
│   │   │   ├── schemas/       # Pydantic v2 schemas for requests & responses
│   │   │   ├── services/      # Business services (CRM, Calendar, Pricing, Scoring)
│   │   │   ├── tools/         # Function declarations & ToolRouter dispatcher
│   │   │   └── voice/         # Gemini Live bidirectional session manager
│   │   ├── requirements.txt   # Backend dependencies
│   │   └── Dockerfile
│   │
│   └── web/                   # Next.js 16 (App Router) + TypeScript frontend
│       ├── app/               # Pages (/, /leads, /activity, /about, /settings)
│       ├── components/        # VoiceOrb, Transcript, CustomerContext, Telemetry
│       ├── hooks/             # useVoiceSession Web Audio & WebSocket hook
│       ├── lib/               # Typed API client
│       ├── public/            # AudioWorklet processor scripts
│       └── types/             # Shared TypeScript models
│
├── data/
│   └── knowledge/             # Markdown business & product documents for RAG
├── docs/                      # Architecture RFC & technical documentation
├── scripts/
│   └── seed.py                # Idempotent database & knowledge seeder
├── tests/                     # Pytest automated test suite
├── .env.example               # Environment template
└── docker-compose.yml         # Container deployment configuration
```

---

## 5. Quickstart & Local Setup

### Prerequisites
- **Python**: 3.12+
- **Node.js**: 18+ (tested on Node 20 / 22 / 24)
- **Google Gemini API Key**: [Get a key from Google AI Studio](https://aistudio.google.com/) *(Free tier supported)*

---

### Step 1: Clone & Configure Environment

```bash
git clone https://github.com/your-username/open-voice-agent.git
cd open-voice-agent

# Create environment file
cp .env.example .env
```

Open `.env` and set your `GEMINI_API_KEY`:

```env
GEMINI_API_KEY=AIzaSy...your_gemini_api_key...
GEMINI_LIVE_MODEL=gemini-2.0-flash-exp
GEMINI_TEXT_MODEL=gemini-2.0-flash
```

> 💡 **Demo Mode**: If no API key is provided, the platform automatically runs in simulated demo mode.

---

### Step 2: Set Up & Run Backend

#### On Windows (PowerShell):
```powershell
python -m venv .venv
.\.venv\Scripts\activate
pip install -r apps/api/requirements.txt

# Seed demo slots, initial leads, and index knowledge base
python scripts/seed.py

# Start FastAPI server on port 8000
uvicorn app.main:app --app-dir apps/api --reload --port 8000
```

#### On macOS / Linux:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r apps/api/requirements.txt

# Seed demo data
python scripts/seed.py

# Start FastAPI server
uvicorn app.main:app --app-dir apps/api --reload --port 8000
```

- **Health Check**: [http://127.0.0.1:8000/health](http://127.0.0.1:8000/health)
- **Interactive OpenAPI Docs**: [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

---

### Step 3: Set Up & Run Frontend

In a **new terminal window**:

```bash
# Install frontend dependencies
npm --prefix apps/web install

# Start Next.js development server
npm --prefix apps/web run dev -- -H 127.0.0.1 -p 3000
```

Open your browser at **[http://127.0.0.1:3000](http://127.0.0.1:3000)**.

---

## 6. How to Customize for Your Business

This repository is designed to be easily customized for any organization, SaaS product, medical clinic, law firm, or agency:

### 1. Customize AI Persona & Instructions
Edit [`apps/api/app/ai/prompts/voice_employee.md`](apps/api/app/ai/prompts/voice_employee.md) to define your assistant's name, brand identity, conversation style, and escalation triggers.

### 2. Plug In Your Company Knowledge Base
Drop your own markdown files into [`data/knowledge/`](data/knowledge/). Then run:
```bash
python scripts/seed.py
```
The semantic chunker and vector indexer will automatically parse, embed, and enable RAG retrieval over your documents.

### 3. Configure Your Service Catalog & Pricing
Edit [`apps/api/app/core/constants.py`](apps/api/app/core/constants.py) to customize `DEMO_SERVICES` with your product packages, descriptions, and pricing tiers.

### 4. Connect to Your Real CRM / Calendar
Implement the abstract interfaces in [`apps/api/app/providers/`](apps/api/app/providers/) (`CRMProvider`, `CalendarProvider`) to pipe data directly into HubSpot, Salesforce, Google Calendar, Cal.com, or PostgreSQL.

---

## 7. Running Automated Tests

Run the complete test suite:

```bash
# Windows PowerShell
$env:PYTHONPATH="apps/api"; python -m pytest tests/ -v

# macOS / Linux
PYTHONPATH="apps/api" python -m pytest tests/ -v
```

The test suite validates:
- **`test_fastapi_endpoints`**: Health check, CORS headers, public config sanitization, RAG queries, and chat endpoints.
- **`test_lead_creation_and_deterministic_qualification`**: CRM storage and deterministic 0–100 mathematical scoring.
- **`test_pricing_service_never_invents_prices`**: Prevention of hallucinated prices.
- **`test_calendar_booking_and_double_booking_prevention`**: Concurrency locking and anti-collision.
- **`test_tool_router_validation_and_safety`**: Pydantic schema validation and error recovery.
- **`test_rag_chunking_and_retrieval`**: Semantic chunking and cosine similarity retrieval.

---

## 8. Docker Deployment

Deploy the entire stack with Docker Compose:

```bash
# Set your API key in .env, then run:
docker-compose up --build
```

- Frontend: `http://localhost:3000`
- Backend: `http://localhost:8000`

---

## 9. Security & Guardrails

- **Zero Secrets in Client**: The browser bundle never receives API keys or database connection strings.
- **Pydantic Validation**: All tool arguments are strongly typed and validated before reaching business logic.
- **Strict Grounding**: The voice assistant refuses to guess prices or invent slots without tool confirmation.
- **Rate & Payload Limits**: Audio buffers and WebSocket frames are capped to prevent denial-of-service and memory exhaustion.

---

## 10. License

This project is open-source software licensed under the **[MIT License](LICENSE)**.
