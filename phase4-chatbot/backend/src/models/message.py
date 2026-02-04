"""Message model for conversation messages."""
from datetime import datetime, timezone
from enum import Enum
from typing import TYPE_CHECKING
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel, Relationship, Column
from sqlalchemy import Text

if TYPE_CHECKING:
    from .conversation import Conversation


class MessageRole(str, Enum):
    """Message sender role."""
    USER = "user"
    ASSISTANT = "assistant"

    def __str__(self):
        """Return the value (not name) when converted to string."""
        return self.value


class Message(SQLModel, table=True):
    """Single message in a conversation.

    Messages are immutable - no updates, only inserts.
    Messages are never deleted to preserve conversation history.
    """

    __tablename__ = "message"

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    conversation_id: UUID = Field(
        foreign_key="conversation.id",
        index=True,
        nullable=False
    )
    user_id: str = Field(nullable=False)  # No FK - user table is in main backend (CUID from Better Auth)
    role: str = Field(nullable=False)  # Store as string to avoid enum serialization issues
    content: str = Field(sa_column=Column(Text, nullable=False))
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        nullable=False,
        index=True
    )

    # Relationships
    conversation: "Conversation" = Relationship(back_populates="messages")

    class Config:
        """SQLModel configuration."""
        json_schema_extra = {
            "example": {
                "id": "456def78-1234-5678-90ab-cdef12345678",
                "conversation_id": "d17cb5d1-5a51-4f2f-9cb8-8cd7f19720e2",
                "user_id": "323fc8dc-e29e-4868-aa93-8351ff5f6261",
                "role": "user",
                "content": "Add a task to buy groceries",
                "created_at": "2026-01-29T10:00:00Z"
            }
        }
