"""Configuration management for the Todo App backend."""

import os
from functools import lru_cache
from typing import List

from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""

    def __init__(self) -> None:
        # Default to SQLite for local development
        self.database_url: str = os.getenv(
            "DATABASE_URL",
            "sqlite:///./todo_app.db",
        )
        self.cors_origins: List[str] = self._parse_cors_origins()
        self.debug: bool = os.getenv("DEBUG", "true").lower() == "true"

    def _parse_cors_origins(self) -> List[str]:
        """Parse CORS origins from comma-separated string."""
        origins = os.getenv("CORS_ORIGINS", "http://localhost:3000")
        return [origin.strip() for origin in origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()
