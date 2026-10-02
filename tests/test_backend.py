import pytest
import pytest_asyncio
import asyncio
from datetime import datetime, timezone, timedelta
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.db.base import Base
from app.models import Lead, CalendarSlot, Booking, Conversation, Message, AgentEvent
from app.repositories.lead_repo import LeadRepository
from app.repositories.calendar_repo import CalendarRepository
from app.repositories.conversation_repo import ConversationRepository
from app.services.crm_service import CRMService
from app.services.calendar_service import CalendarService
from app.services.pricing_service import PricingService
from app.services.qualification_service import LeadQualificationService
from app.rag.service import RAGService
from app.tools.router import ToolRouter
from app.schemas.lead import LeadCreate, LeadUpdate
from app.schemas.calendar import BookingCreate


@pytest_asyncio.fixture
async def test_db():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    session_factory = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with session_factory() as session:
        yield session

    await engine.dispose()


@pytest.mark.asyncio
async def test_lead_creation_and_deterministic_qualification(test_db):
    crm = CRMService(test_db)
    lead_in = LeadCreate(
        name="Sarah Connor",
        email="sarah@skynetdefense.demo",
        company="Cyberdyne Systems",
        role="Director of Operations",
        intent="Automate customer inbound support",
        use_case="24/7 Voice reception and support ticket deflection",
        requirements="Zendesk integration, call transcription, SMS alerts",
        timeline="1 month",
        budget_range="$5,000 - $10,000"
    )
    lead = await crm.create_lead(lead_in)
    assert lead.id is not None
    assert lead.name == "Sarah Connor"
    assert lead.qualification_score >= 80
    assert lead.lead_status == "QUALIFIED"

    qual = await crm.get_qualification(lead.id)
    assert qual is not None
    assert len(qual.reasons) >= 5
    assert "Clear business use case identified" in qual.reasons


def test_pricing_service_never_invents_prices():
    pricing_res = PricingService.get_service_pricing("AI Voice Agents")
    assert pricing_res["success"] is True
    assert "$4,500 setup" in pricing_res["starting_price"]
    assert pricing_res["is_demo"] is True

    unknown_res = PricingService.get_service_pricing("quantum teleportation")
    assert unknown_res["success"] is False
    assert unknown_res["pricing"] is None


@pytest.mark.asyncio
async def test_calendar_booking_and_double_booking_prevention(test_db):
    cal = CalendarService(test_db)
    slot_time = datetime.now(timezone.utc) + timedelta(days=2)
    slot = CalendarSlot(
        start_time=slot_time,
        end_time=slot_time + timedelta(minutes=45),
        is_booked=False
    )
    test_db.add(slot)
    await test_db.commit()
    await test_db.refresh(slot)

    # 1. Book the slot
    booking_req = BookingCreate(
        slot_id=slot.id,
        name="Jordan Lee",
        email="jordan@innovate.demo",
        company="Innovate Corp",
        meeting_type="AI Solutions Consultation"
    )
    res = await cal.book_meeting(booking_req)
    assert res["ok"] is True
    assert res["data"]["slot_id"] == slot.id

    # 2. Check slot is now booked
    await test_db.refresh(slot)
    assert slot.is_booked is True

    # 3. Attempt to double-book the same slot -> MUST FAIL
    second_req = BookingCreate(
        slot_id=slot.id,
        name="Another Caller",
        email="caller2@test.demo",
    )
    double_book_res = await cal.book_meeting(second_req)
    assert double_book_res["ok"] is False
    assert double_book_res["error"]["code"] == "SLOT_UNAVAILABLE"


@pytest.mark.asyncio
async def test_tool_router_validation_and_safety(test_db):
    conv_repo = ConversationRepository(test_db)
    conv = await conv_repo.get_or_create("test-session-router")
    router = ToolRouter(test_db, conversation_id=conv.id)

    # Test check_pricing tool
    res = await router.execute_tool("check_pricing", {"service_name": "customer support"})
    assert res["ok"] is True
    assert res["data"]["success"] is True

    # Test malformed book_meeting tool (missing email)
    bad_booking = await router.execute_tool("book_meeting", {"slot_id": "fake-slot", "name": "No Email"})
    assert bad_booking["ok"] is False
    assert "TOOL_EXECUTION_ERROR" in bad_booking["error"]["code"]

    # Verify AgentEvent was logged in DB
    events = await conv_repo.get_events(conv.id)
    assert len(events) >= 2
