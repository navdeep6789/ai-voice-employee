import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.core.config import get_settings
from app.core.logging import logger
from app.db.base import Base
from app.db.session import sync_engine
from app.api.routes import health, config, leads, calendar, conversations, knowledge, chat, voice_ws

settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Ensure SQLite/Postgres tables are created
    logger.info("Initializing database schemas...")
    Base.metadata.create_all(bind=sync_engine)
    logger.info("Database initialized successfully.")
    yield
    # Shutdown
    logger.info("Application shutting down.")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Real-time AI Voice Employee & Agent Platform API",
    lifespan=lifespan,
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global controlled exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.method} {request.url.path}: {exc}", exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "error": "INTERNAL_SERVER_ERROR",
            "message": "An unexpected error occurred. The system remains operational.",
            "detail": str(exc) if settings.DEBUG else None
        }
    )

# Include API Routers
app.include_router(health.router)
app.include_router(config.router)
app.include_router(leads.router)
app.include_router(calendar.router)
app.include_router(conversations.router)
app.include_router(knowledge.router)
app.include_router(chat.router)
app.include_router(voice_ws.router)


@app.get("/")
async def root():
    return {
        "message": "AI Voice Employee Platform API is running.",
        "documentation": "/docs",
        "health": "/health"
    }
