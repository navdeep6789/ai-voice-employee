from typing import Optional, List
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Lead
from app.schemas.lead import LeadCreate, LeadUpdate


class LeadRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_by_id(self, lead_id: str) -> Optional[Lead]:
        result = await self.db.execute(select(Lead).where(Lead.id == lead_id))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> Optional[Lead]:
        result = await self.db.execute(select(Lead).where(Lead.email == email))
        return result.scalar_one_or_none()

    async def list_all(self, limit: int = 50, offset: int = 0) -> List[Lead]:
        result = await self.db.execute(
            select(Lead).order_by(Lead.created_at.desc()).offset(offset).limit(limit)
        )
        return list(result.scalars().all())

    async def create(self, lead_in: LeadCreate) -> Lead:
        lead_dict = lead_in.model_dump(exclude_unset=True)
        lead = Lead(**lead_dict)
        self.db.add(lead)
        await self.db.commit()
        await self.db.refresh(lead)
        return lead

    async def update(self, lead_id: str, lead_update: LeadUpdate) -> Optional[Lead]:
        lead = await self.get_by_id(lead_id)
        if not lead:
            return None
        
        update_data = lead_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            if value is not None:
                setattr(lead, key, value)

        await self.db.commit()
        await self.db.refresh(lead)
        return lead
