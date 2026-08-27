"""Shared configuration loaded from the project's .env file."""

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")


def _required(name: str) -> str:
    value = os.getenv(name)
    if value is None:
        raise RuntimeError(f"Missing required environment variable: {name}")
    return value


@dataclass(frozen=True)
class Settings:
    database_url: str
    docs_dir: str
    embed_model: str
    language_model: str
    groq_model: str
    log_debug_mode: str


settings = Settings(
    database_url=_required("DATABASE_URL"),
    docs_dir=_required("DOCS_DIR"),
    embed_model=os.getenv("EMBED_MODEL", "nomic-embed-text"),
    language_model=os.getenv("LANGUAGE_MODEL", "qwen3.5:2b"),
    groq_model=os.getenv("GROQ_MODEL", "qwen/qwen3.6-27b"),
    log_debug_mode=os.getenv("LOG_LEVEL", "INFO"),
)
