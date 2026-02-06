"""Authentication configuration."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class AuthConfig:
    """Authentication configuration from environment variables."""

    jwt_secret: str = os.getenv("JWT_SECRET", "your-secret-key-at-least-32-characters-here")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")


# Global config instance
auth_config = AuthConfig()
