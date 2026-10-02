import json
import logging
import sys
from datetime import datetime, timezone
from typing import Any, Dict


class StructuredFormatter(logging.Formatter):
    """
    Format logs as JSON or formatted text with timestamp, level, event metadata.
    Avoids logging sensitive keys (e.g. GEMINI_API_KEY).
    """

    def format(self, record: logging.LogRecord) -> str:
        timestamp = datetime.now(timezone.utc).isoformat()
        log_obj: Dict[str, Any] = {
            "timestamp": timestamp,
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
        }

        # Include custom extra fields if provided
        if hasattr(record, "session_id"):
            log_obj["session_id"] = getattr(record, "session_id")
        if hasattr(record, "tool"):
            log_obj["tool"] = getattr(record, "tool")
        if hasattr(record, "duration_ms"):
            log_obj["duration_ms"] = getattr(record, "duration_ms")
        if hasattr(record, "event_type"):
            log_obj["event_type"] = getattr(record, "event_type")

        if record.exc_info:
            log_obj["exception"] = self.formatException(record.exc_info)

        return json.dumps(log_obj)


def setup_logger(name: str = "ai_voice_employee", level: int = logging.INFO) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.setLevel(level)
    if not logger.handlers:
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(StructuredFormatter())
        logger.addHandler(handler)
    return logger


logger = setup_logger()
