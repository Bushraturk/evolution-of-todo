"""Event publisher service for publishing events to Kafka via Dapr."""

import logging
from typing import Any, Dict
from uuid import UUID

from models.events import (
    BaseEvent,
    ReminderScheduledEvent,
    TaskCompletedEvent,
    TaskCreatedEvent,
    TaskDeletedEvent,
    TaskUpdatedEvent,
)

from dapr.pubsub import get_pubsub_client

logger = logging.getLogger(__name__)


class EventPublisher:
    """Service for publishing domain events."""

    def __init__(self):
        """Initialize event publisher."""
        self.pubsub_client = get_pubsub_client()
        self.topic = "task-events"

    async def publish_event(self, event: BaseEvent) -> None:
        """Publish an event to Kafka.

        Args:
            event: Event to publish
        """
        try:
            # Convert event to dict
            event_data = event.model_dump(mode="json")

            # Publish to Dapr pub/sub
            await self.pubsub_client.publish(
                topic=self.topic,
                data=event_data,
            )

            logger.info(
                f"Published event: {event.event_type} (id={event.event_id})"
            )
        except Exception as e:
            logger.error(f"Failed to publish event {event.event_type}: {e}")
            # Don't raise - event publishing should not block main operations
            # Events will be caught by safety net mechanisms

    async def publish_task_created(
        self,
        task_id: UUID,
        user_id: str,
        task_data: Dict[str, Any],
    ) -> None:
        """Publish task created event.

        Args:
            task_id: Task ID
            user_id: User ID
            task_data: Task data
        """
        event = TaskCreatedEvent(
            task_id=task_id,
            user_id=user_id,
            task_data=task_data,
        )
        await self.publish_event(event)

    async def publish_task_updated(
        self,
        task_id: UUID,
        user_id: str,
        task_data: Dict[str, Any],
        changes: Dict[str, Any] = None,
    ) -> None:
        """Publish task updated event.

        Args:
            task_id: Task ID
            user_id: User ID
            task_data: Updated task data
            changes: Changes made
        """
        event = TaskUpdatedEvent(
            task_id=task_id,
            user_id=user_id,
            task_data=task_data,
            changes=changes,
        )
        await self.publish_event(event)

    async def publish_task_completed(
        self,
        task_id: UUID,
        user_id: str,
        completed_at,
        is_recurring: bool = False,
        recurrence_id: UUID = None,
        next_occurrence_date=None,
    ) -> None:
        """Publish task completed event.

        Args:
            task_id: Task ID
            user_id: User ID
            completed_at: Completion timestamp
            is_recurring: Whether task is recurring
            recurrence_id: Recurrence pattern ID
            next_occurrence_date: Next occurrence date
        """
        event = TaskCompletedEvent(
            task_id=task_id,
            user_id=user_id,
            completed_at=completed_at,
            is_recurring=is_recurring,
            recurrence_id=recurrence_id,
            next_occurrence_date=next_occurrence_date,
        )
        await self.publish_event(event)

    async def publish_task_deleted(
        self,
        task_id: UUID,
        user_id: str,
    ) -> None:
        """Publish task deleted event.

        Args:
            task_id: Task ID
            user_id: User ID
        """
        event = TaskDeletedEvent(
            task_id=task_id,
            user_id=user_id,
        )
        await self.publish_event(event)

    async def publish_reminder_scheduled(
        self,
        reminder_id: UUID,
        task_id: UUID,
        user_id: str,
        remind_at,
        channel: str,
        task_title: str,
    ) -> None:
        """Publish reminder scheduled event.

        Args:
            reminder_id: Reminder ID
            task_id: Task ID
            user_id: User ID
            remind_at: Reminder time
            channel: Notification channel
            task_title: Task title
        """
        event = ReminderScheduledEvent(
            reminder_id=reminder_id,
            task_id=task_id,
            user_id=user_id,
            remind_at=remind_at,
            channel=channel,
            task_title=task_title,
        )
        # Publish to reminders topic
        await self.pubsub_client.publish(
            topic="reminders",
            data=event.model_dump(mode="json"),
        )


# Global publisher instance
_event_publisher = None


def get_event_publisher() -> EventPublisher:
    """Get or create the global event publisher instance.

    Returns:
        EventPublisher instance
    """
    global _event_publisher
    if _event_publisher is None:
        _event_publisher = EventPublisher()
    return _event_publisher
