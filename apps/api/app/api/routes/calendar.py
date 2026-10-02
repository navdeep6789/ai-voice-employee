from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.session import get_db
from app.services.calendar_service import CalendarService
from app.schemas.calendar import CalendarSlotResponse, BookingCreate, BookingResponse

router = APIRouter(prefix="/api/calendar", tags=["Calendar"])


@router.get("/slots", response_model=List[CalendarSlotResponse])
async def list_available_slots(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: AsyncSession = Depends(get_db)
):
    calendar = CalendarService(db)
    return await calendar.list_available_slots(start_date, end_date)


@router.post("/book", status_code=status.HTTP_201_CREATED)
async def book_meeting(booking_in: BookingCreate, db: AsyncSession = Depends(get_db)):
    calendar = CalendarService(db)
    result = await calendar.book_meeting(booking_in)
    if not result.get("ok"):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", {}).get("message", "Unable to book the requested slot.")
        )
    return result["data"]
