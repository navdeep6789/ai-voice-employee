from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.ai.chat_service import TextAgentService
from app.repositories.conversation_repo import ConversationRepository
from app.repositories.lead_repo import LeadRepository
from app.services.crm_service import CRMService
from app.schemas.chat import ChatRequest, ChatResponse

router = APIRouter(prefix="/api/chat", tags=["Chat"])


@router.post("", response_model=ChatResponse)
async def chat_message(req: ChatRequest, db: AsyncSession = Depends(get_db)):
    if not req.message or len(req.message.strip()) == 0:
        raise HTTPException(status_code=400, detail="Message cannot be empty")

    conv_repo = ConversationRepository(db)
    conv = await conv_repo.get_or_create(req.session_id, req.lead_id)

    agent = TextAgentService(db, conversation_id=conv.id)
    response_data = await agent.send_message(
        user_text=req.message.strip(),
        session_id=req.session_id,
        lead_id=req.lead_id
    )

    # Fetch updated customer context if lead is associated
    customer_context = None
    if conv.lead_id:
        lead_repo = LeadRepository(db)
        lead = await lead_repo.get_by_id(conv.lead_id)
        if lead:
            crm = CRMService(db)
            qual = await crm.get_qualification(lead.id)
            customer_context = {
                "id": lead.id,
                "name": lead.name,
                "email": lead.email,
                "company": lead.company,
                "role": lead.role,
                "intent": lead.intent,
                "use_case": lead.use_case,
                "requirements": lead.requirements,
                "timeline": lead.timeline,
                "budget_range": lead.budget_range,
                "qualification_score": lead.qualification_score,
                "lead_status": lead.lead_status,
                "qualification_details": qual.model_dump() if qual else None
            }

    response_data["customer_context"] = customer_context
    return response_data
