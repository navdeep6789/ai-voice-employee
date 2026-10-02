from typing import Optional, List, Dict, Any
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Conversation, Message, AgentEvent
from app.schemas.events import AgentEventCreate


class ConversationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_or_create(self, session_id: str, lead_id: Optional[str] = None) -> Conversation:
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages), selectinload(Conversation.events))
            .where(Conversation.session_id == session_id)
        )
        conversation = result.scalar_one_or_none()
        if not conversation:
            conversation = Conversation(session_id=session_id, lead_id=lead_id)
            self.db.add(conversation)
            await self.db.commit()
            await self.db.refresh(conversation)
        return conversation

    async def get_by_session_id(self, session_id: str) -> Optional[Conversation]:
        result = await self.db.execute(
            select(Conversation)
            .options(selectinload(Conversation.messages), selectinload(Conversation.events))
            .where(Conversation.session_id == session_id)
        )
        return result.scalar_one_or_none()

    async def add_message(self, conversation_id: str, speaker: str, text: str) -> Message:
        message = Message(conversation_id=conversation_id, speaker=speaker, text=text)
        self.db.add(message)
        await self.db.commit()
        await self.db.refresh(message)
        return message

    async def add_event(self, event_in: AgentEventCreate) -> AgentEvent:
        event = AgentEvent(
            conversation_id=event_in.conversation_id,
            event_type=event_in.event_type,
            tool_name=event_in.tool_name,
            status=event_in.status,
            duration_ms=event_in.duration_ms,
            payload=event_in.payload,
        )
        self.db.add(event)
        await self.db.commit()
        await self.db.refresh(event)
        return event

    async def get_events(self, conversation_id: str, limit: int = 50) -> List[AgentEvent]:
        result = await self.db.execute(
            select(AgentEvent)
            .where(AgentEvent.conversation_id == conversation_id)
            .order_by(AgentEvent.created_at.asc())
            .limit(limit)
        )
        return list(result.scalars().all())

    async def update_summary(self, conversation_id: str, summary_data: dict, status: Optional[str] = None):
        result = await self.db.execute(select(Conversation).where(Conversation.id == conversation_id))
        conv = result.scalar_one_or_none()
        if conv:
            conv.summary = summary_data
            if status:
                conv.status = status
            await self.db.commit()
            await self.db.refresh(conv)
        return conv
