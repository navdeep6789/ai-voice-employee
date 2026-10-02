from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.lead_repo import LeadRepository
from app.repositories.calendar_repo import CalendarRepository
from app.services.summary_service import ConversationSummaryService
from app.schemas.conversation import ConversationResponse, ConversationSummary
from app.schemas.events import AgentEventResponse

router = APIRouter(prefix="/api/conversations", tags=["Conversations"])


@router.get("/{session_id}", response_model=ConversationResponse)
async def get_conversation(session_id: str, db: AsyncSession = Depends(get_db)):
    repo = ConversationRepository(db)
    conv = await repo.get_by_session_id(session_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return conv


@router.get("/{session_id}/events", response_model=List[AgentEventResponse])
async def get_events(session_id: str, db: AsyncSession = Depends(get_db)):
    repo = ConversationRepository(db)
    conv = await repo.get_by_session_id(session_id)
    if not conv:
        return []
    events = await repo.get_events(conv.id)
    return [AgentEventResponse.model_validate(e) for e in events]


@router.post("/{session_id}/summary", response_model=ConversationSummary)
async def generate_summary(session_id: str, db: AsyncSession = Depends(get_db)):
    conv_repo = ConversationRepository(db)
    lead_repo = LeadRepository(db)
    
    conv = await conv_repo.get_by_session_id(session_id)
    if not conv:
        raise HTTPException(status_code=404, detail="Conversation not found")

    lead = await lead_repo.get_by_id(conv.lead_id) if conv.lead_id else None
    
    # Check if a booking was made for this lead
    booking = None
    if lead and lead.bookings:
        booking = lead.bookings[-1]

    summary = ConversationSummaryService.generate_summary(conv, lead, booking)
    await conv_repo.update_summary(conv.id, summary.model_dump(), status="COMPLETED")
    return summary
