from datetime import datetime
from typing import Optional
from pydantic import BaseModel, ConfigDict


class CalendarSlotResponse(BaseModel):
    id: str
    start_time: datetime
    end_time: datetime
    is_booked: bool

    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    slot_id: str
    lead_id: Optional[str] = None
    name: str
    email: str
    company: Optional[str] = None
    meeting_type: Optional[str] = "AI Solutions Consultation"


class BookingResponse(BaseModel):
    booking_id: str
    slot_id: str
    lead_id: Optional[str] = None
    name: str
    email: str
    company: Optional[str] = None
    confirmed_start: datetime
    confirmed_end: datetime
    status: str

    model_config = ConfigDict(from_attributes=True)
