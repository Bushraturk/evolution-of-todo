"""Task model for chatbot backend.

This is a simplified copy of the main backend's Task model.
We need this to avoid importing from the main backend which isn't
available on Hugging Face Spaces.
"""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class Priority(str, Enum):
    """Task priority levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskBase(SQLModel):
    """Base task model with common fields."""

    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: Priority = Field(default=Priority.MEDIUM)
    category_id: Optional[UUID] = Field(default=None)
    user_id: str = Field(index=True)  # User ID from Better Auth (CUID format)


class Task(TaskBase, table=True):
    """Task database model."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"Task(id={self.id}, title='{self.title}', completed={self.completed})"
