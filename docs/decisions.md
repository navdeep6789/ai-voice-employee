# Engineering Decision Records (ADR)

## ADR 01: Native Gemini Live API vs. Cascaded STT-LLM-TTS
- **Context**: Real-time voice agents can either be built via a cascaded pipeline (Whisper STT → GPT/Claude text LLM → ElevenLabs TTS) or a native multimodal streaming model (Gemini Live).
- **Decision**: Adopt native Gemini Live API.
- **Rationale**: Cascaded pipelines introduce 2,500ms–4,000ms of lag due to audio chunking, model turn latencies, and audio synthesis roundtrips. Gemini Live streams audio bidirectionally with sub-second response times and handles natural turn-taking and interruptions natively.

---

## ADR 02: Modular Monolith vs. Microservices
- **Context**: The portfolio project must demonstrate enterprise-level architectural maturity without unnecessary infrastructure overhead.
- **Decision**: Build a clean modular monolith using FastAPI (Backend) + Next.js (Frontend).
- **Rationale**: Microservices introduce distributed tracing complexity, container orchestration overhead, and multi-network failure modes without adding value for this application scale. A well-factored modular monolith with strict domain boundaries (services, repositories, providers) demonstrates superior engineering judgment.

---

## ADR 03: Deterministic Lead Scoring vs. Free-form LLM Scoring
- **Context**: Lead qualification could be estimated by asking an LLM to generate a score from 1 to 100 based on conversation impressions.
- **Decision**: Enforce a deterministic, weighted mathematical scoring engine in Python.
- **Rationale**: LLM-generated numbers fluctuate across calls and are prone to hallucinations or bias. Our scoring engine uses documented, transparent weights (use case: +20, timeline: +15, budget: +15, company: +10, decision-maker: +10, concrete requirements: +15, meeting requested: +15) capped at 100. This guarantees mathematical reproducibility.

---

## ADR 04: Provider Interfaces with Demo Implementations
- **Context**: The demo should be free to run locally without requiring paid CRM (HubSpot/Salesforce) or scheduling (Calendly) subscriptions.
- **Decision**: Define abstract provider interfaces (`CRMProvider`, `CalendarProvider`) and implement local database adapters (`DemoCRMProvider`, `DemoCalendarProvider`).
- **Rationale**: This allows swapping in real enterprise CRM and Calendar adapters with zero changes to agent prompting or business logic.

---

## ADR 05: Server-Side Secret Isolation
- **Context**: Web clients require access to AI responses.
- **Decision**: The client communicates solely via our authenticated FastAPI backend. `GEMINI_API_KEY` is never transmitted to the browser.
- **Rationale**: Committing or exposing API keys in client-side bundles creates severe security vulnerabilities and token abuse risks.

---

## ADR 06: Zero-Cost Local RAG Pipeline
- **Context**: RAG requires document indexing and similarity search.
- **Decision**: Utilize local dense n-gram vectorization with cosine similarity and markdown section chunking.
- **Rationale**: Avoids spinning up paid vector databases or external embeddings APIs. The RAG pipeline runs 100% offline, free-first, and deterministically.
