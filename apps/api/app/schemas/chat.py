from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from app.schemas.events import AgentEventResponse


class ChatMessage(BaseModel):
    role: str  # "user", "assistant", "system"
    content: str


class ChatRequest(BaseModel):
    session_id: str
    message: str
    lead_id: Optional[str] = None


class ChatResponse(BaseModel):
    reply: str
    session_id: str
    lead_id: Optional[str] = None
    events: List[AgentEventResponse] = []
    customer_context: Optional[Dict[str, Any]] = None
    booking_confirmed: Optional[Dict[str, Any]] = None
