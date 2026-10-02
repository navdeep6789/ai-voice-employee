from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.schemas.lead import LeadCreate, LeadUpdate, LeadResponse
from app.schemas.calendar import CalendarSlotResponse, BookingCreate, BookingResponse


class CRMProvider(ABC):
    """Abstract interface for CRM operations (e.g. HubSpot, Salesforce, DemoCRM)."""

    @abstractmethod
    async def create_lead(self, lead_in: LeadCreate) -> LeadResponse:
        pass

    @abstractmethod
    async def update_lead(self, lead_id: str, lead_update: LeadUpdate) -> Optional[LeadResponse]:
        pass

    @abstractmethod
    async def get_lead(self, lead_id: str) -> Optional[LeadResponse]:
        pass


class CalendarProvider(ABC):
    """Abstract interface for Calendar booking (e.g. Google Calendar, Calendly, DemoCalendar)."""

    @abstractmethod
    async def list_available_slots(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[CalendarSlotResponse]:
        pass

    @abstractmethod
    async def book_meeting(self, booking_in: BookingCreate) -> Optional[BookingResponse]:
        pass
