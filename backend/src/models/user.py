"""User model for authentication."""

from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


def utc_now() -> datetime:
    """Get current UTC time (Python 3.13 compatible)."""
    return datetime.now(timezone.utc)


class User(SQLModel, table=True):
    """User database model for authentication."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    email: str = Field(unique=True, index=True)
    name: Optional[str] = Field(default=None, max_length=200)
    hashed_password: str
    created_at: datetime = Field(default_factory=utc_now)
    updated_at: datetime = Field(default_factory=utc_now)
