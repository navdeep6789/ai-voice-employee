from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, ConfigDict
from app.schemas.events import AgentEventResponse


class MessageResponse(BaseModel):
    id: str
    speaker: str
    text: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ConversationSummary(BaseModel):
    customer_name: Optional[str] = None
    company: Optional[str] = None
    email: Optional[str] = None
    intent: Optional[str] = None
    use_case: Optional[str] = None
    requirements: List[str] = []
    timeline: Optional[str] = None
    budget_range: Optional[str] = None
    qualification_score: int = 0
    lead_status: str = "NEW"
    next_action: Optional[str] = None


class ConversationResponse(BaseModel):
    id: str
    session_id: str
    lead_id: Optional[str] = None
    status: str
    summary: Optional[ConversationSummary] = None
    messages: List[MessageResponse] = []
    events: List[AgentEventResponse] = []
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
