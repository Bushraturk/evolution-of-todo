"""Event schemas for Kafka messages."""

from datetime import datetime
from typing import Any, Dict, Optional
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class BaseEvent(BaseModel):
    """Base event schema with common fields."""

    event_id: UUID = Field(default_factory=uuid4)
    event_type: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    user_id: str


class TaskCreatedEvent(BaseEvent):
    """Event published when a task is created."""

    event_type: str = "task.created"
    task_id: UUID
    task_data: Dict[str, Any]


class TaskUpdatedEvent(BaseEvent):
    """Event published when a task is updated."""

    event_type: str = "task.updated"
    task_id: UUID
    task_data: Dict[str, Any]
    changes: Optional[Dict[str, Any]] = None


class TaskCompletedEvent(BaseEvent):
    """Event published when a task is completed."""

    event_type: str = "task.completed"
    task_id: UUID
    completed_at: datetime
    is_recurring: bool = False
    recurrence_id: Optional[UUID] = None
    next_occurrence_date: Optional[datetime] = None


class TaskDeletedEvent(BaseEvent):
    """Event published when a task is deleted."""

    event_type: str = "task.deleted"
    task_id: UUID


class ReminderScheduledEvent(BaseEvent):
    """Event published when a reminder is scheduled."""

    event_type: str = "reminder.scheduled"
    reminder_id: UUID
    task_id: UUID
    remind_at: datetime
    channel: str
    task_title: str
