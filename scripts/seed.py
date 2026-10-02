import sys
import os
from pathlib import Path
from datetime import datetime, timedelta, timezone

# Ensure project root is in sys.path
root_dir = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(root_dir / "apps" / "api"))

import asyncio
from sqlalchemy import select
from app.db.session import AsyncSessionLocal, sync_engine
from app.db.base import Base
from app.models import CalendarSlot, Lead, KnowledgeDocument
from app.rag.ingest import ingest_all_documents
from app.core.logging import logger


async def seed_calendar_slots(session):
    """Seed 24 realistic demo calendar slots across the next 2 weeks (Mon-Fri)."""
    # Check if slots already exist
    existing = await session.execute(select(CalendarSlot))
    if existing.scalars().first():
        logger.info("Calendar slots already seeded. Skipping.")
        return

    now = datetime.now(timezone.utc)
    # Start from tomorrow morning 10:00 AM UTC
    current_day = now.date() + timedelta(days=1)
    slots_created = 0

    target_times = [
        (10, 0),  # 10:00 AM
        (11, 30), # 11:30 AM
        (14, 0),  # 2:00 PM
        (15, 30), # 3:30 PM
        (17, 0),  # 5:00 PM
    ]

    while slots_created < 25:
        # Mon=0, Sun=6. Skip weekends
        if current_day.weekday() < 5:
            for hour, minute in target_times:
                start_dt = datetime(
                    current_day.year, current_day.month, current_day.day,
                    hour, minute, tzinfo=timezone.utc
                )
                end_dt = start_dt + timedelta(minutes=45)
                slot = CalendarSlot(
                    start_time=start_dt,
                    end_time=end_dt,
                    is_booked=False
                )
                session.add(slot)
                slots_created += 1
                if slots_created >= 25:
                    break
        current_day += timedelta(days=1)

    await session.commit()
    logger.info(f"Seeded {slots_created} demo calendar availability slots.")


async def seed_demo_leads(session):
    """Seed 2 sample leads for demonstration inspection."""
    existing = await session.execute(select(Lead))
    if existing.scalars().first():
        logger.info("Demo leads already seeded. Skipping.")
        return

    sample_leads = [
        Lead(
            name="Alex Rivera",
            email="alex.rivera@acmelabs.demo",
            company="Acme Labs",
            role="VP of Engineering",
            intent="Customer support ticket deflection",
            use_case="Automating tier-1 customer inquiries with Zendesk integration",
            requirements="Zendesk ticket API, web chat widget, SLA tracking",
            timeline="1-2 months",
            budget_range="$5,000 - $10,000",
            qualification_score=78,
            lead_status="QUALIFIED",
            source="ai_voice_employee"
        ),
        Lead(
            name="Marcus Vance",
            email="marcus@vancerealty.demo",
            company="Vance Realty Group",
            role="Managing Broker",
            intent="Voice receptionist for inbound property calls",
            use_case="After-hours phone reception and appointment booking for agents",
            requirements="Phone IVR, Google Calendar sync, SMS confirmation",
            timeline="Immediate (2 weeks)",
            budget_range="$3,000 - $5,000",
            qualification_score=85,
            lead_status="QUALIFIED",
            source="ai_voice_employee"
        )
    ]
    for lead in sample_leads:
        session.add(lead)

    await session.commit()
    logger.info("Seeded 2 initial demo CRM leads.")


async def run_seed():
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=sync_engine)

    async with AsyncSessionLocal() as session:
        await seed_calendar_slots(session)
        await seed_demo_leads(session)

    # Ingest knowledge documents
    logger.info("Ingesting knowledge documents...")
    await ingest_all_documents(str(root_dir / "data" / "knowledge"))
    logger.info("All seed operations completed successfully.")


if __name__ == "__main__":
    asyncio.run(run_seed())
