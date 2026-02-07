"""Application configuration and settings."""
import os
from typing import Optional

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # Database Configuration
    database_url: str = os.getenv(
        "DATABASE_URL",
        "postgresql://user:password@localhost:5432/database"
    )

    # Groq API Configuration (using OpenAI-compatible endpoint)
    groq_api_key: str = os.getenv("GROQ_API_KEY", "")
    groq_base_url: str = os.getenv(
        "GROQ_BASE_URL",
        "https://api.groq.com/openai/v1"
    )
    groq_model: str = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")

    # JWT Authentication (reuse from Phase III)
    jwt_secret: str = os.getenv("JWT_SECRET", "your-jwt-secret-key")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    jwt_expiration_days: int = int(os.getenv("JWT_EXPIRATION_DAYS", "7"))

    # Server Configuration
    cors_origins: str = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000"
    )
    debug: bool = os.getenv("DEBUG", "true").lower() == "true"
    log_level: str = os.getenv("LOG_LEVEL", "INFO")

    # Application Settings
    max_conversation_history: int = int(os.getenv("MAX_CONVERSATION_HISTORY", "50"))
    conversation_archive_days: int = int(os.getenv("CONVERSATION_ARCHIVE_DAYS", "90"))
    llm_request_timeout: int = int(os.getenv("LLM_REQUEST_TIMEOUT", "30"))
    llm_max_retries: int = int(os.getenv("LLM_MAX_RETRIES", "3"))

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins from comma-separated string."""
        return [origin.strip() for origin in self.cors_origins.split(",")]

    class Config:
        """Pydantic settings configuration."""
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()
