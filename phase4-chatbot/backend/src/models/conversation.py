"""Conversation model for chat sessions."""
from datetime import datetime, timezone
from typing import Optional, TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .message import Message


class Conversation(SQLModel, table=True):
    """Chat session between user and AI assistant.

    Represents a conversation thread that contains multiple messages.
    Conversations are soft-deleted via archived_at timestamp.
    """

    __tablename__ = "conversation"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    user_id: str = Field(index=True)  # No FK - user table is in main backend (CUID from Better Auth)
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    updated_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False
    )
    archived_at: Optional[datetime] = Field(default=None, index=True)

    # Relationships
    messages: list["Message"] = Relationship(back_populates="conversation")

    class Config:
        """SQLModel configuration."""
        json_schema_extra = {
            "example": {
                "id": "d17cb5d1-5a51-4f2f-9cb8-8cd7f19720e2",
                "user_id": "323fc8dc-e29e-4868-aa93-8351ff5f6261",
                "created_at": "2026-01-29T10:00:00Z",
                "updated_at": "2026-01-29T10:30:00Z",
                "archived_at": None
            }
        }
