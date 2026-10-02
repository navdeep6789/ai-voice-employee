from datetime import datetime
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from app.providers.base import CRMProvider, CalendarProvider
from app.repositories.lead_repo import LeadRepository
from app.repositories.calendar_repo import CalendarRepository
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from app.schemas.calendar import CalendarSlotResponse, BookingCreate, BookingResponse


class DemoCRMProvider(CRMProvider):
    def __init__(self, db: AsyncSession):
        self.repo = LeadRepository(db)

    async def create_lead(self, lead_in: LeadCreate) -> LeadResponse:
        lead = await self.repo.create(lead_in)
        return LeadResponse.model_validate(lead)

    async def update_lead(self, lead_id: str, lead_update: LeadUpdate) -> Optional[LeadResponse]:
        lead = await self.repo.update(lead_id, lead_update)
        if not lead:
            return None
        return LeadResponse.model_validate(lead)

    async def get_lead(self, lead_id: str) -> Optional[LeadResponse]:
        lead = await self.repo.get_by_id(lead_id)
        if not lead:
            return None
        return LeadResponse.model_validate(lead)


class DemoCalendarProvider(CalendarProvider):
    def __init__(self, db: AsyncSession):
        self.repo = CalendarRepository(db)

    async def list_available_slots(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[CalendarSlotResponse]:
        slots = await self.repo.get_available_slots(start_date, end_date)
        return [CalendarSlotResponse.model_validate(s) for s in slots]

    async def book_meeting(self, booking_in: BookingCreate) -> Optional[BookingResponse]:
        booking = await self.repo.book_slot(booking_in)
        if not booking:
            return None
        return BookingResponse(
            booking_id=booking.id,
            slot_id=booking.slot_id,
            lead_id=booking.lead_id,
            name=booking.name,
            email=booking.email,
            company=booking.company,
            confirmed_start=booking.confirmed_start,
            confirmed_end=booking.confirmed_end,
            status=booking.status,
        )
