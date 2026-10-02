from functools import lru_cache
import os
from pathlib import Path
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field

# Base directory for the API app
BASE_DIR = Path(__file__).resolve().parent.parent.parent
# Root directory of the repository
ROOT_DIR = BASE_DIR.parent.parent


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=str(ROOT_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Project metadata
    PROJECT_NAME: str = "AI Voice Employee Platform"
    VERSION: str = "1.0.0"
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    PORT: int = 8000
    HOST: str = "127.0.0.1"

    # CORS
    CORS_ORIGINS: List[str] = [
        "http://127.0.0.1:3000",
        "http://127.0.0.1:8000",
        "http://localhost:3000",
        "http://localhost:8000",
    ]

    # Database
    # Default to local SQLite with aiosqlite for async operations
    DATABASE_URL: str = f"sqlite+aiosqlite:///{ROOT_DIR / 'ai_voice_employee.db'}"
    DATABASE_SYNC_URL: str = f"sqlite:///{ROOT_DIR / 'ai_voice_employee.db'}"

    # AI Configuration (Gemini)
    GEMINI_API_KEY: str = Field(default="", description="Google Gemini API Key")
    GEMINI_LIVE_MODEL: str = "gemini-2.0-flash-exp"
    GEMINI_TEXT_MODEL: str = "gemini-2.0-flash"

    # RAG Settings
    EMBEDDING_PROVIDER: str = "local"
    KNOWLEDGE_DIR: str = str(ROOT_DIR / "data" / "knowledge")

    # Safety & Limits
    MAX_TOOL_CALLS_PER_TURN: int = 5
    MAX_CONVERSATION_DURATION_SECONDS: int = 900
    RATE_LIMIT_MESSAGES_PER_MINUTE: int = 60


@lru_cache()
def get_settings() -> Settings:
    return Settings()
