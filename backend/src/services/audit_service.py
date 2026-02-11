"""Audit Service - Consumes and logs all task events for audit trail."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import UUID

from sqlmodel import Session

from database import get_session
from services.event_publisher import get_event_publisher

logger = logging.getLogger(__name__)


class AuditService:
    """Service for auditing task events."""

    def __init__(self, session: Session):
        """Initialize service.

        Args:
            session: Database session
        """
        self.session = session
        self.event_publisher = get_event_publisher()

    async def handle_task_created(self, event: Dict[str, Any]) -> None:
        """Handle task.created event.

        Args:
            event: Event data containing task_id, user_id, task_data
        """
        try:
            task_id = event.get("task_id")
            user_id = event.get("user_id")
            task_data = event.get("task_data", {})

            logger.info(
                f"[AUDIT] Task created: task_id={task_id}, user_id={user_id}, "
                f"title={task_data.get('title')}, priority={task_data.get('priority')}"
            )

            # Optional: Store in task_events table
            # For now, we rely on Kafka retention for audit trail
            # In production, you might want to store critical events in DB

        except Exception as e:
            logger.error(f"Error handling task.created event: {e}", exc_info=True)

    async def handle_task_updated(self, event: Dict[str, Any]) -> None:
        """Handle task.updated event.

        Args:
            event: Event data containing task_id, user_id, task_data
        """
        try:
            task_id = event.get("task_id")
            user_id = event.get("user_id")
            task_data = event.get("task_data", {})

            logger.info(
                f"[AUDIT] Task updated: task_id={task_id}, user_id={user_id}, "
                f"changes={task_data}"
            )

        except Exception as e:
            logger.error(f"Error handling task.updated event: {e}", exc_info=True)

    async def handle_task_completed(self, event: Dict[str, Any]) -> None:
        """Handle task.completed event.

        Args:
            event: Event data containing task_id, user_id, completed_at
        """
        try:
            task_id = event.get("task_id")
            user_id = event.get("user_id")
            completed_at = event.get("completed_at")
            is_recurring = event.get("is_recurring", False)

            logger.info(
                f"[AUDIT] Task completed: task_id={task_id}, user_id={user_id}, "
                f"completed_at={completed_at}, is_recurring={is_recurring}"
            )

        except Exception as e:
            logger.error(f"Error handling task.completed event: {e}", exc_info=True)

    async def handle_task_deleted(self, event: Dict[str, Any]) -> None:
        """Handle task.deleted event.

        Args:
            event: Event data containing task_id, user_id
        """
        try:
            task_id = event.get("task_id")
            user_id = event.get("user_id")

            logger.info(
                f"[AUDIT] Task deleted: task_id={task_id}, user_id={user_id}"
            )

        except Exception as e:
            logger.error(f"Error handling task.deleted event: {e}", exc_info=True)

    async def handle_reminder_scheduled(self, event: Dict[str, Any]) -> None:
        """Handle reminder.scheduled event.

        Args:
            event: Event data containing reminder_id, task_id, user_id, remind_at
        """
        try:
            reminder_id = event.get("reminder_id")
            task_id = event.get("task_id")
            user_id = event.get("user_id")
            remind_at = event.get("remind_at")
            channel = event.get("channel")

            logger.info(
                f"[AUDIT] Reminder scheduled: reminder_id={reminder_id}, "
                f"task_id={task_id}, user_id={user_id}, remind_at={remind_at}, "
                f"channel={channel}"
            )

        except Exception as e:
            logger.error(f"Error handling reminder.scheduled event: {e}", exc_info=True)

    async def subscribe_to_events(self) -> None:
        """Subscribe to all task events.

        This method would use Dapr pub/sub subscriptions in production.
        For now, it's a placeholder for the subscription logic.
        """
        logger.info("Audit Service subscribing to task events")

        # In production with Dapr, you would:
        # 1. Register subscription endpoints with Dapr
        # 2. Dapr would call these endpoints when events are published
        # 3. Each endpoint would call the appropriate handler

        # Example Dapr subscription configuration:
        # POST /dapr/subscribe returns:
        # [
        #   {
        #     "pubsubname": "todo-pubsub",
        #     "topic": "task.created",
        #     "route": "/events/task-created"
        #   },
        #   {
        #     "pubsubname": "todo-pubsub",
        #     "topic": "task.updated",
        #     "route": "/events/task-updated"
        #   },
        #   ...
        # ]

    async def run_audit_service(self) -> None:
        """Run audit service (main loop).

        This would be the main entry point for the audit service.
        """
        try:
            logger.info("Starting Audit Service")
            await self.subscribe_to_events()

            # Keep service running
            while True:
                await asyncio.sleep(60)

        except KeyboardInterrupt:
            logger.info("Shutting down Audit Service")


async def main():
    """Main entry point for audit service."""
    logger.info("Initializing Audit Service")

    # Get database session
    session = next(get_session())

    # Initialize service
    service = AuditService(session)

    # Run service
    await service.run_audit_service()


if __name__ == "__main__":
    asyncio.run(main())
