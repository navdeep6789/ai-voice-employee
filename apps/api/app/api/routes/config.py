from fastapi import APIRouter
from app.core.config import get_settings
from app.core.constants import DEMO_SERVICES

router = APIRouter(prefix="/api/config", tags=["Configuration"])
settings = get_settings()


@router.get("")
async def get_public_config():
    """Returns safe, public application configuration for frontend clients."""
    return {
        "project_name": settings.PROJECT_NAME,
        "company": "Open Voice Agent Platform",
        "demo_mode": True,
        "live_model": settings.GEMINI_LIVE_MODEL,
        "text_model": settings.GEMINI_TEXT_MODEL,
        "embedding_provider": settings.EMBEDDING_PROVIDER,
        "has_api_key": bool(settings.GEMINI_API_KEY and not settings.GEMINI_API_KEY.startswith("your_")),
        "services": DEMO_SERVICES,
        "disclaimer": "Interactive open source demonstration using modular business records and demo pricing.",
    }
