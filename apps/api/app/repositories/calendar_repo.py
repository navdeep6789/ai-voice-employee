from datetime import datetime, timezone
from typing import Optional, List
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import CalendarSlot, Booking
from app.schemas.calendar import BookingCreate


class CalendarRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_available_slots(
        self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None
    ) -> List[CalendarSlot]:
        query = select(CalendarSlot).where(CalendarSlot.is_booked == False)
        if start_date:
            query = query.where(CalendarSlot.start_time >= start_date)
        if end_date:
            query = query.where(CalendarSlot.start_time <= end_date)
        query = query.order_by(CalendarSlot.start_time.asc())
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_slot_by_id(self, slot_id: str) -> Optional[CalendarSlot]:
        result = await self.db.execute(select(CalendarSlot).where(CalendarSlot.id == slot_id))
        return result.scalar_one_or_none()

    async def book_slot(self, booking_in: BookingCreate) -> Optional[Booking]:
        # Lock slot checking is_booked == False
        slot = await self.get_slot_by_id(booking_in.slot_id)
        if not slot or slot.is_booked:
            return None

        # Mutate slot state
        slot.is_booked = True

        booking = Booking(
            slot_id=slot.id,
            lead_id=booking_in.lead_id,
            name=booking_in.name,
            email=booking_in.email,
            company=booking_in.company,
            meeting_type=booking_in.meeting_type or "AI Solutions Consultation",
            confirmed_start=slot.start_time,
            confirmed_end=slot.end_time,
            status="CONFIRMED"
        )
        self.db.add(booking)
        await self.db.commit()
        await self.db.refresh(booking)
        return booking

    async def get_booking_by_id(self, booking_id: str) -> Optional[Booking]:
        result = await self.db.execute(select(Booking).where(Booking.id == booking_id))
        return result.scalar_one_or_none()
