"""Authentication configuration."""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass
class AuthConfig:
    """Authentication configuration from environment variables."""

    jwks_url: str = os.getenv("JWKS_URL", "http://localhost:3000/api/auth/jwks")
    jwt_issuer: str = os.getenv("JWT_ISSUER", "http://localhost:3000")
    jwt_algorithms: list[str] = None

    def __post_init__(self):
        if self.jwt_algorithms is None:
            self.jwt_algorithms = ["EdDSA", "RS256"]


# Global config instance
auth_config = AuthConfig()
