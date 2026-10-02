from typing import Optional, List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.providers.demo_providers import DemoCRMProvider
from app.repositories.lead_repo import LeadRepository
from app.services.qualification_service import LeadQualificationService
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadQualificationResult


class CRMService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = DemoCRMProvider(db)
        self.repo = LeadRepository(db)

    async def create_lead(self, lead_in: LeadCreate) -> LeadResponse:
        lead = await self.repo.create(lead_in)
        # Calculate initial qualification score
        qual = LeadQualificationService.evaluate(lead)
        lead.qualification_score = qual.qualification_score
        lead.lead_status = qual.recommended_status
        await self.db.commit()
        await self.db.refresh(lead)
        return LeadResponse.model_validate(lead)

    async def update_lead(self, lead_id: str, lead_update: LeadUpdate) -> Optional[LeadResponse]:
        lead = await self.repo.get_by_id(lead_id)
        if not lead:
            return None

        update_dict = lead_update.model_dump(exclude_unset=True)
        for k, v in update_dict.items():
            if v is not None:
                setattr(lead, k, v)

        # Re-evaluate qualification automatically
        qual = LeadQualificationService.evaluate(lead)
        lead.qualification_score = qual.qualification_score
        if not lead_update.lead_status:
            lead.lead_status = qual.recommended_status

        await self.db.commit()
        await self.db.refresh(lead)
        return LeadResponse.model_validate(lead)

    async def get_lead(self, lead_id: str) -> Optional[LeadResponse]:
        return await self.provider.get_lead(lead_id)

    async def list_leads(self, limit: int = 50, offset: int = 0) -> List[LeadResponse]:
        leads = await self.repo.list_all(limit, offset)
        return [LeadResponse.model_validate(l) for l in leads]

    async def get_qualification(self, lead_id: str) -> Optional[LeadQualificationResult]:
        lead = await self.repo.get_by_id(lead_id)
        if not lead:
            return None
        return LeadQualificationService.evaluate(lead)
