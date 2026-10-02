from enum import Enum
from typing import Dict, Any, List

class VoiceState(str, Enum):
    IDLE = "IDLE"
    CONNECTING = "CONNECTING"
    CONNECTED = "CONNECTED"
    LISTENING = "LISTENING"
    PROCESSING = "PROCESSING"
    SPEAKING = "SPEAKING"
    TOOL_CALL = "TOOL_CALL"
    ERROR = "ERROR"
    ENDING = "ENDING"
    ENDED = "ENDED"

class LeadStatus(str, Enum):
    NEW = "NEW"
    QUALIFYING = "QUALIFYING"
    QUALIFIED = "QUALIFIED"
    MEETING_BOOKED = "MEETING_BOOKED"
    HANDOFF = "HANDOFF"
    CLOSED = "CLOSED"

# Deterministic scoring rubrics (Sum to 100)
# Documented transparent scoring logic:
LEAD_SCORING_WEIGHTS = {
    "use_case_identified": 20,       # Clear business problem / specific AI application
    "timeline_identified": 15,       # Specific timeframe (e.g., immediate, 1-3 months)
    "budget_identified": 15,         # Budget range discussed/provided
    "company_identified": 10,        # Business name and industry known
    "decision_maker_identified": 10, # Role/title indicates decision maker or evaluator
    "concrete_requirements": 15,     # Detailed specifications (channels, integrations)
    "meeting_requested": 15,         # User agreed to or requested consultation
}

# DEMO Service Catalog with approved demo pricing
DEMO_SERVICES: List[Dict[str, Any]] = [
    {
        "service_id": "ai-voice-agents",
        "name": "AI Voice Agents & Digital Receptionists",
        "category": "Voice AI",
        "description": "Real-time conversational voice agents for incoming customer inquiries, appointment booking, and tier-1 support.",
        "ideal_for": "SaaS companies, clinics, professional services, customer service desks.",
        "capabilities": ["Sub-second latency voice responses", "Real-time CRM & calendar tool integration", "Smart human escalation"],
        "starting_price": "$4,500 setup + $350/mo maintenance",
        "pricing_notes": "DEMO PRICING: Includes custom voice persona, workflow design, and calendar/CRM integration.",
        "delivery_range": "2–4 weeks",
        "status": "Available"
    },
    {
        "service_id": "ai-customer-support",
        "name": "AI Customer Support Systems",
        "category": "Customer Support",
        "description": "Omnichannel AI support agents capable of resolving tier-1 and tier-2 tickets across web chat, email, and knowledge bases.",
        "ideal_for": "E-commerce and SaaS teams needing 24/7 ticket triage and resolution.",
        "capabilities": ["Knowledge base grounding", "Actionable API triggers for refunds/lookups", "Automated escalation summaries"],
        "starting_price": "$3,800 setup + $290/mo maintenance",
        "pricing_notes": "DEMO PRICING: Includes helpdesk integration (Zendesk/Intercom) and custom deflection flows.",
        "delivery_range": "2–3 weeks",
        "status": "Available"
    },
    {
        "service_id": "rag-enterprise-assistants",
        "name": "Enterprise Knowledge Assistants (RAG)",
        "category": "Knowledge AI",
        "description": "Secure semantic search and question-answering systems over internal company docs, SOPs, Notion, and databases.",
        "ideal_for": "Engineering teams, legal/compliance, internal operations.",
        "capabilities": ["Hybrid semantic + BM25 search", "Document citations with page-level links", "Strict hallucination guardrails"],
        "starting_price": "$5,000 setup + $400/mo maintenance",
        "pricing_notes": "DEMO PRICING: Includes embedding pipeline, vector storage, and access control layer.",
        "delivery_range": "3–5 weeks",
        "status": "Available"
    },
    {
        "service_id": "ai-sales-automation",
        "name": "AI Inbound Sales Qualification Assistant",
        "category": "Sales AI",
        "description": "Conversational assistant that qualifies incoming inbound traffic, captures project scope, and schedules meetings for account executives.",
        "ideal_for": "B2B agencies, software consultancies, high-volume inbound sales pipelines.",
        "capabilities": ["Dynamic qualification scoring", "Direct CRM lead ingestion", "Calendar synchronization"],
        "starting_price": "$3,500 setup + $250/mo maintenance",
        "pricing_notes": "DEMO PRICING: Includes custom qualification rules and CRM pipeline mapping.",
        "delivery_range": "2–3 weeks",
        "status": "Available"
    },
    {
        "service_id": "custom-ai-engineering",
        "name": "Custom AI Agent & Workflow Engineering",
        "category": "Product Engineering",
        "description": "Bespoke agentic systems, multi-step autonomous workflows, and custom backend API integrations for enterprise products.",
        "ideal_for": "Product teams looking to embed production AI agents into existing software.",
        "capabilities": ["Autonomous task execution", "Secure sandbox execution", "Telemetry & monitoring"],
        "starting_price": "$8,000 - $20,000 per engagement",
        "pricing_notes": "DEMO PRICING: Scoped by sprint (typically 2-week milestones).",
        "delivery_range": "4–8 weeks",
        "status": "Available"
    }
]
