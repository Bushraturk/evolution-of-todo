"""ScheduledNotification model for notification queue."""

from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class NotificationStatus(str, Enum):
    """Notification status states."""

    PENDING = "PENDING"
    QUEUED = "QUEUED"
    SENT = "SENT"
    FAILED = "FAILED"


class ScheduledNotificationBase(SQLModel):
    """Base scheduled notification model with common fields."""

    reminder_id: UUID = Field(foreign_key="reminder.id", sa_column_kwargs={"nullable": False})
    task_id: UUID = Field(foreign_key="task.id", sa_column_kwargs={"nullable": False})
    user_id: str = Field(sa_column_kwargs={"nullable": False}, index=True)
    scheduled_for: datetime = Field(sa_column_kwargs={"nullable": False}, index=True)
    delivery_channel: str = Field(max_length=20, sa_column_kwargs={"nullable": False})
    status: NotificationStatus = Field(default=NotificationStatus.PENDING, index=True)
    retry_count: int = Field(default=0, ge=0, le=3)
    last_attempt_at: Optional[datetime] = Field(default=None)
    error_message: Optional[str] = Field(default=None)


class ScheduledNotification(ScheduledNotificationBase, table=True):
    """ScheduledNotification database model."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"ScheduledNotification(id={self.id}, scheduled_for={self.scheduled_for}, status={self.status})"
