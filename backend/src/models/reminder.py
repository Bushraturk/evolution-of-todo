"""Reminder model for task notifications."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .task import Task


class Channel(str, Enum):
    """Notification delivery channels."""

    EMAIL = "EMAIL"
    PUSH = "PUSH"
    BOTH = "BOTH"


class ReminderStatus(str, Enum):
    """Reminder status states."""

    PENDING = "PENDING"
    SCHEDULED = "SCHEDULED"
    SENT = "SENT"
    FAILED = "FAILED"


class ReminderBase(SQLModel):
    """Base reminder model with common fields."""

    task_id: UUID = Field(foreign_key="task.id", sa_column_kwargs={"nullable": False}, index=True)
    user_id: str = Field(sa_column_kwargs={"nullable": False}, index=True)
    remind_at: datetime = Field(sa_column_kwargs={"nullable": False}, index=True)
    offset_minutes: int = Field(ge=0)  # Minutes before due date
    channel: Channel = Field(sa_column_kwargs={"nullable": False})
    status: ReminderStatus = Field(default=ReminderStatus.PENDING)


class Reminder(ReminderBase, table=True):
    """Reminder database model."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"Reminder(id={self.id}, task_id={self.task_id}, remind_at={self.remind_at}, status={self.status})"
