from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.crm_service import CRMService
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse, LeadQualificationResult

router = APIRouter(prefix="/api/leads", tags=["Leads"])


@router.get("", response_model=List[LeadResponse])
async def list_leads(limit: int = 50, offset: int = 0, db: AsyncSession = Depends(get_db)):
    crm = CRMService(db)
    return await crm.list_leads(limit, offset)


@router.post("", response_model=LeadResponse, status_code=status.HTTP_201_CREATED)
async def create_lead(lead_in: LeadCreate, db: AsyncSession = Depends(get_db)):
    crm = CRMService(db)
    return await crm.create_lead(lead_in)


@router.get("/{lead_id}", response_model=LeadResponse)
async def get_lead(lead_id: str, db: AsyncSession = Depends(get_db)):
    crm = CRMService(db)
    lead = await crm.get_lead(lead_id)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.patch("/{lead_id}", response_model=LeadResponse)
async def update_lead(lead_id: str, lead_update: LeadUpdate, db: AsyncSession = Depends(get_db)):
    crm = CRMService(db)
    lead = await crm.update_lead(lead_id, lead_update)
    if not lead:
        raise HTTPException(status_code=404, detail="Lead not found")
    return lead


@router.get("/{lead_id}/qualification", response_model=LeadQualificationResult)
async def get_qualification(lead_id: str, db: AsyncSession = Depends(get_db)):
    crm = CRMService(db)
    qual = await crm.get_qualification(lead_id)
    if not qual:
        raise HTTPException(status_code=404, detail="Lead not found")
    return qual
