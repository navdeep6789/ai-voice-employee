from datetime import datetime
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, EmailStr, Field, ConfigDict


class LeadBase(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    intent: Optional[str] = None
    use_case: Optional[str] = None
    requirements: Optional[str] = None
    timeline: Optional[str] = None
    budget_range: Optional[str] = None


class LeadCreate(LeadBase):
    source: Optional[str] = "ai_voice_employee"


class LeadUpdate(BaseModel):
    name: Optional[str] = None
    email: Optional[str] = None
    company: Optional[str] = None
    role: Optional[str] = None
    intent: Optional[str] = None
    use_case: Optional[str] = None
    requirements: Optional[str] = None
    timeline: Optional[str] = None
    budget_range: Optional[str] = None
    lead_status: Optional[str] = None
    qualification_score: Optional[int] = None


class LeadQualificationResult(BaseModel):
    lead_id: str
    qualification_score: int
    reasons: List[str]
    missing_fields: List[str]
    recommended_status: str


class LeadResponse(LeadBase):
    id: str
    qualification_score: int
    lead_status: str
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
