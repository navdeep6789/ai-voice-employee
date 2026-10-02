# Frequently Asked Questions (FAQ)

## General & Business Questions

### Q: Can your platform integrate with our existing CRM?
A: Yes. While this interactive demo operates using a local database provider (`DemoCRMProvider`), our architecture is strictly decoupled using provider interfaces (`CRMProvider`). We can plug into HubSpot, Salesforce, Close, Pipedrive, or custom Postgres databases without altering agent reasoning.

### Q: How do you prevent voice AI from hallucinating or making false promises?
A: We enforce three strict architectural layers:
1. **Tool-gated facts**: Business facts such as pricing, calendar slots, and service availability can ONLY be fetched via validated tool calls.
2. **Deterministic business logic**: Qualification scores and booking confirmations are computed by deterministic Python code, never by free-form model intuition.
3. **Structured RAG Grounding**: Responses to questions regarding company policies and capabilities are strictly retrieved from our vectorized knowledge base.

### Q: Can the voice agent transfer a call to a live human?
A: Absolutely. Our `transfer_to_human` tool updates the lead status to `HANDOFF`, emits a priority alert to your on-call team via Slack/Webhook, and summarizes the caller's objective so the human agent has full context.

### Q: What browsers support the real-time voice mode?
A: Any modern browser supporting the Web Audio API and WebSocket streaming (Chrome, Edge, Brave, Safari, Firefox). For users with microphone restrictions or noisy environments, our interface provides an instant, zero-lag Text Mode fallback.
