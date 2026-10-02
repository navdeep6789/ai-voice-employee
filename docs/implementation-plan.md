
# Implementation Plan: AI Voice Employee Platform

## Project Overview

A production-quality, open-source AI Voice Employee platform. The system features real-time voice interaction with Gemini Live API, streaming Web Audio / AudioWorklet bidirectional PCM audio, stateful tool calling, RAG knowledge retrieval, calendar availability & booking, deterministic lead qualification, demo CRM management, real-time UI agent event observability, and a text fallback mode.

---

## Architecture & Technology Stack

### Frontend (`/apps/web`)

- **Framework**: Next.js 14/15 (App Router), React 18/19, TypeScript
- **Styling**: Vanilla Tailwind CSS, dark charcoal / graphite modern SaaS aesthetic (Linear/Vercel inspired)
- **Audio Processing**: Web Audio API with `AudioWorklet` (capturing 16kHz 16-bit PCM mono; low-latency streaming playback)
- **Communications**: Bidirectional WebSocket (`/ws/voice`) + typed HTTP REST client for text chat and CRM endpoints
- **State Machine**: Explicit state transitions: `IDLE`, `CONNECTING`, `CONNECTED`, `LISTENING`, `PROCESSING`, `SPEAKING`, `TOOL_CALL`, `ERROR`, `ENDING`, `ENDED`

### Backend (`/apps/api`)

- **Runtime**: Python 3.12+ with FastAPI & Uvicorn
- **AI Integration**: Official `google-genai` SDK with Gemini Live API (`client.aio.live.connect`) and fallback standard chat (`client.aio.models.generate_content`)
- **Database**: SQLite (dev) / PostgreSQL compatible via SQLAlchemy 2.0 (async/sync repository pattern) & Alembic
- **RAG Subsystem**: Document chunker with metadata + semantic embedding retrieval (sentence-transformers / local vectors with cosine similarity fallback)
- **Tools**:
  - `search_knowledge(query)`
  - `check_pricing(service_name)`
  - `get_customer_context(session_id)`
  - `create_lead(...)`
  - `update_lead(lead_id, ...)`
  - `calculate_lead_qualification(lead_id)`
  - `check_calendar(date, time_range)`
  - `book_meeting(lead_id, name, email, company, slot, meeting_type)`
  - `transfer_to_human(reason, priority, lead_id)`
- **Event Bus / Observability**: Strongly typed agent events emitted on actual backend execution (`tool_started`, `tool_completed`, `tool_failed`, `agent_state_changed`)

---

## Controlled Phases of Execution

### Phase 0: Inspection & Planning (Current)

- [X] Inspect local tools: Python 3.12.5, Node v24.14.1, npm 11.11.0, Git 2.41.
- [X] Check `google-genai` SDK support and install required backend packages.
- [X] Write `docs/implementation-plan.md`.

### Phase 1: Project Scaffolding

- [ ] Initialize `/apps/web` with Next.js, Tailwind CSS, TypeScript, and lucide icons.
- [ ] Set up `/apps/api` with FastAPI application structure, configuration, CORS, and `/health` route.
- [ ] Create shared `.env.example` and environment configuration loaders.
- [ ] Verify frontend loads and backend `/health` returns status `healthy`.

### Phase 2: Database Models, Repositories, and Seed Data

- [ ] Implement SQLAlchemy 2.0 models: `Lead`, `Conversation`, `Message`, `AgentEvent`, `Booking`, `CalendarSlot`, `KnowledgeDocument`, `KnowledgeChunk`.
- [ ] Implement repository and service layer: `LeadRepository`, `CalendarRepository`, `ConversationRepository`.
- [ ] Build idempotent database seeder (`scripts/seed.py`) with 20–30 calendar slots, 10 demo services, and knowledge documents.
- [ ] Write automated tests for models, repositories, and deterministic lead scoring.

### Phase 3: Knowledge Base & RAG Pipeline

- [ ] Write rich, realistic markdown knowledge documents in `/data/knowledge/` (company overview, services, ai voice agents, rag systems, process, pricing, security, faq).
- [ ] Implement `RAGService` with chunking, local embedding / similarity search, top-k retrieval, and source citation extraction.
- [ ] Build `python -m app.rag.ingest` command.
- [ ] Unit test RAG retrieval accuracy and citation accuracy.

### Phase 4: Core Agent Tools & Business Services

- [ ] Implement business services:
  - `PricingService` (strictly approved demo pricing catalog).
  - `CalendarService` (slot availability, slot locking, booking mutation, double-booking prevention).
  - `CRMService` (lead creation, updates, status transitions).
  - `LeadQualificationService` (transparent deterministic scoring: max 100 with clear weights).
- [ ] Define Pydantic tool schemas and tool router.
- [ ] Unit test all tools independently.

### Phase 5: Text Chat & Fallback Agent

- [ ] Implement `/api/chat` endpoint using Gemini API with tool-calling loop and safety controls (max turns, loop prevention).
- [ ] Ensure full tool calling functionality works identically in text mode.
- [ ] Test multi-step scenarios (service inquiry -> pricing -> qualification -> slot check -> booking).

### Phase 6: Real-Time Voice Pipeline (Gemini Live API)

- [ ] Build `GeminiLiveSession` manager: handles WebSocket connection to Google GenAI Live API, audio streaming, manual tool call dispatch, and session lifecycle.
- [ ] Implement FastAPI WebSocket route `/ws/voice`.
- [ ] Implement browser `AudioWorklet` processor for 16kHz PCM capture and playback.
- [ ] Handle connection, disconnection, interruption, and error recovery cleanly.

### Phase 7: Real-Time Agent Activity Stream & Observability

- [ ] Stream structured activity events (`tool_started`, `tool_completed`, `tool_failed`) over WebSocket and HTTP SSE/polling.
- [ ] Implement structured internal logging (request ID, session ID, tool latency, turn count).
- [ ] Verify frontend shows only real events.

### Phase 8: Polished Frontend UI

- [ ] Design and build responsive modern dark SaaS UI (Linear/Vercel styling):
  - Top Navigation: Product branding, demo badge, status indicator, navigation links (`/`, `/leads`, `/activity`, `/about`, `/settings`).
  - Left / Main Area: AI Employee voice orb, real-time audio visualization, clear status badge, conversation transcript, voice/text mode toggle, scenario quick-buttons.
  - Right Context Panel: Real-time Customer Context card, deterministic Lead Qualification meter, live Agent Activity Feed, and Booking Confirmation card.
  - Text fallback modal / inline interface for accessibility and mic denial.
  - Conversation summary export / view.

### Phase 9: Automated Testing & Verification

- [ ] Write pytest test suite:
  - Repository CRUD and constraint verification.
  - Deterministic qualification score computation.
  - Pricing lookup correctness.
  - Calendar slot booking and duplicate prevention.
  - RAG ingestion and retrieval with citations.
  - Tool router validation and error handling.
  - Chat endpoint integration flow.
- [ ] Run type checks and frontend build.

### Phase 10: Production Readiness, Documentation & QA

- [ ] Write `docs/architecture.md` with ASCII diagrams and layer explanation.
- [ ] Write `docs/decisions.md` detailing architectural trade-offs.
- [ ] Write comprehensive `README.md` with setup guides, env variables, demo walkthroughs, and security practices.
- [ ] Perform end-to-end smoke test across both voice and text modes.
