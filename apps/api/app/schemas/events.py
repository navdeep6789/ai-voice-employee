from datetime import datetime
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field, ConfigDict


class AgentEventCreate(BaseModel):
    conversation_id: Optional[str] = None
    event_type: str
    tool_name: Optional[str] = None
    status: str = "INFO"
    duration_ms: Optional[int] = None
    payload: Optional[Dict[str, Any]] = None


class AgentEventResponse(BaseModel):
    id: str
    conversation_id: Optional[str] = None
    event_type: str
    tool_name: Optional[str] = None
    status: str
    duration_ms: Optional[int] = None
    payload: Optional[Dict[str, Any]] = None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
