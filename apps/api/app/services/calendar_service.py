from datetime import datetime
from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from app.providers.demo_providers import DemoCalendarProvider
from app.repositories.lead_repo import LeadRepository
from app.schemas.calendar import CalendarSlotResponse, BookingCreate, BookingResponse
from app.services.qualification_service import LeadQualificationService
from app.core.constants import LeadStatus


class CalendarService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.provider = DemoCalendarProvider(db)
        self.lead_repo = LeadRepository(db)

    async def list_available_slots(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[CalendarSlotResponse]:
        return await self.provider.list_available_slots(start_date, end_date)

    async def book_meeting(self, booking_in: BookingCreate) -> Dict[str, Any]:
        booking = await self.provider.book_meeting(booking_in)
        if not booking:
            return {
                "ok": False,
                "data": None,
                "error": {
                    "code": "SLOT_UNAVAILABLE",
                    "message": "The requested demo slot is no longer available or already booked."
                }
            }

        # If lead exists, update lead status to MEETING_BOOKED and re-evaluate qualification
        if booking_in.lead_id:
            lead = await self.lead_repo.get_by_id(booking_in.lead_id)
            if lead:
                lead.lead_status = LeadStatus.MEETING_BOOKED.value
                qual = LeadQualificationService.evaluate(lead)
                lead.qualification_score = qual.qualification_score
                await self.db.commit()

        return {
            "ok": True,
            "data": booking.model_dump(),
            "error": None
        }
