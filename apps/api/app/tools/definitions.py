from typing import List, Dict, Any

# Tool schemas defined for the Google GenAI SDK (and Gemini Live API)
TOOL_DECLARATIONS: List[Dict[str, Any]] = [
    {
        "name": "search_knowledge",
        "description": "Searches internal knowledge documents for answers regarding services, case studies, technologies, RAG, and processes.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "query": {
                    "type": "STRING",
                    "description": "The search topic or question to retrieve company documentation for."
                }
            },
            "required": ["query"]
        }
    },
    {
        "name": "check_pricing",
        "description": "Retrieves verified demo pricing and package details for services from the approved service catalog. Never quote a price without calling this.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "service_name": {
                    "type": "STRING",
                    "description": "The name or keywords of the service (e.g. 'voice agent', 'customer support', 'rag', 'sales automation')."
                }
            },
            "required": ["service_name"]
        }
    },
    {
        "name": "check_calendar",
        "description": "Checks available consultation demo slots for upcoming dates. Call this before offering or confirming any booking.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "date": {
                    "type": "STRING",
                    "description": "Optional specific date to check (YYYY-MM-DD) or day name (e.g. 'Tuesday', 'tomorrow')."
                },
                "time_range": {
                    "type": "STRING",
                    "description": "Optional time of day preference (e.g. 'morning', 'afternoon', 'after 2pm')."
                }
            }
        }
    },
    {
        "name": "book_meeting",
        "description": "Books a confirmed demo meeting in the calendar. ONLY call this after the user has explicitly agreed to a specific slot and provided their email.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "slot_id": {
                    "type": "STRING",
                    "description": "The exact ID of the calendar slot chosen by the user."
                },
                "name": {
                    "type": "STRING",
                    "description": "The prospect's full name."
                },
                "email": {
                    "type": "STRING",
                    "description": "The prospect's verified contact email address."
                },
                "company": {
                    "type": "STRING",
                    "description": "The prospect's company name."
                },
                "lead_id": {
                    "type": "STRING",
                    "description": "Optional ID of an existing lead if created during this session."
                },
                "meeting_type": {
                    "type": "STRING",
                    "description": "Type of meeting, default 'AI Solutions Consultation'."
                }
            },
            "required": ["slot_id", "name", "email"]
        }
    },
    {
        "name": "create_lead",
        "description": "Creates a new prospect lead record in the demo CRM with captured qualification details.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "name": {"type": "STRING", "description": "Prospect's name."},
                "email": {"type": "STRING", "description": "Prospect's email address."},
                "company": {"type": "STRING", "description": "Company or organization name."},
                "role": {"type": "STRING", "description": "Prospect's job title or role."},
                "intent": {"type": "STRING", "description": "Primary goal or inquiry intent."},
                "use_case": {"type": "STRING", "description": "Detailed description of the AI use case."},
                "requirements": {"type": "STRING", "description": "Technical requirements or integrations needed."},
                "timeline": {"type": "STRING", "description": "Target implementation timeline (e.g. 'immediate', '1-2 months')."},
                "budget_range": {"type": "STRING", "description": "Estimated budget or budget tier."}
            },
            "required": ["intent"]
        }
    },
    {
        "name": "update_lead",
        "description": "Updates an existing lead in the demo CRM with additional captured data points.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "lead_id": {"type": "STRING", "description": "The unique ID of the lead to update."},
                "name": {"type": "STRING", "description": "Prospect's name."},
                "email": {"type": "STRING", "description": "Prospect's email."},
                "company": {"type": "STRING", "description": "Company name."},
                "role": {"type": "STRING", "description": "Prospect's role."},
                "use_case": {"type": "STRING", "description": "Expanded use case details."},
                "requirements": {"type": "STRING", "description": "Technical requirements or integrations."},
                "timeline": {"type": "STRING", "description": "Project timeline."},
                "budget_range": {"type": "STRING", "description": "Budget range."}
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "calculate_lead_qualification",
        "description": "Calculates the deterministic qualification score (0-100) and evaluation breakdown for a lead.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "lead_id": {"type": "STRING", "description": "The unique ID of the lead to evaluate."}
            },
            "required": ["lead_id"]
        }
    },
    {
        "name": "transfer_to_human",
        "description": "Initiates a live handoff ticket to a human solutions engineer when requested or required.",
        "parameters": {
            "type": "OBJECT",
            "properties": {
                "reason": {"type": "STRING", "description": "The reason why human escalation is requested."},
                "priority": {"type": "STRING", "description": "Priority level ('standard', 'urgent')."},
                "lead_id": {"type": "STRING", "description": "Optional lead ID."}
            },
            "required": ["reason"]
        }
    }
]
