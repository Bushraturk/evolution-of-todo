"""Recurring Task Service - Event consumer for task.completed events."""

import asyncio
import logging
from datetime import datetime
from typing import Dict, Any
from uuid import UUID

from sqlmodel import Session, select

from models.task import Task
from models.recurring_pattern import RecurringPattern
from services.recurring_pattern_service import RecurringPatternService
from services.event_publisher import get_event_publisher
from dapr.pubsub import get_pubsub_client
from database import get_session

logger = logging.getLogger(__name__)


class RecurringTaskService:
    """Service for handling recurring task logic."""

    def __init__(self, session: Session):
        """Initialize service.

        Args:
            session: Database session
        """
        self.session = session
        self.recurring_service = RecurringPatternService(session)
        self.event_publisher = get_event_publisher()

    async def handle_task_completed(self, event: Dict[str, Any]) -> None:
        """Handle task.completed event and create next occurrence.

        Args:
            event: Task completed event data
        """
        try:
            # Extract event data
            task_id = UUID(event.get("task_id"))
            user_id = event.get("user_id")
            is_recurring = event.get("is_recurring", False)
            recurrence_id = event.get("recurrence_id")

            if not is_recurring or not recurrence_id:
                logger.info(f"Task {task_id} is not recurring, skipping")
                return

            # Get the completed task
            task = self.session.get(Task, task_id)
            if not task:
                logger.warning(f"Task {task_id} not found")
                return

            # Get recurrence pattern
            pattern = self.recurring_service.get_pattern(UUID(recurrence_id))
            if not pattern:
                logger.warning(f"Recurrence pattern {recurrence_id} not found")
                return

            # Check if pattern has ended
            if pattern.end_date and pattern.next_occurrence_date > pattern.end_date:
                logger.info(f"Recurrence pattern {recurrence_id} has ended")
                return

            # Create next occurrence
            await self.create_next_occurrence(task, pattern)

            logger.info(f"Created next occurrence for task {task_id}")

        except Exception as e:
            logger.error(f"Error handling task.completed event: {e}", exc_info=True)

    async def create_next_occurrence(
        self,
        parent_task: Task,
        pattern: RecurringPattern,
    ) -> Task:
        """Create the next occurrence of a recurring task.

        Args:
            parent_task: Parent task
            pattern: Recurrence pattern

        Returns:
            Created task
        """
        # Check for duplicate (idempotency)
        existing = self.session.exec(
            select(Task).where(
                Task.parent_task_id == parent_task.id,
                Task.due_date == pattern.next_occurrence_date,
            )
        ).first()

        if existing:
            logger.info(f"Next occurrence already exists for task {parent_task.id}")
            return existing

        # Create new task occurrence
        next_task = Task(
            user_id=parent_task.user_id,
            title=parent_task.title,
            description=parent_task.description,
            priority=parent_task.priority,
            category_id=parent_task.category_id,
            due_date=pattern.next_occurrence_date,
            is_recurring=False,  # Occurrences are not recurring themselves
            parent_task_id=parent_task.id,
            recurrence_id=None,
        )

        self.session.add(next_task)
        self.session.commit()
        self.session.refresh(next_task)

        # Update pattern's next occurrence date
        self.recurring_service.update_next_occurrence(
            pattern_id=pattern.id,
            completed_date=datetime.utcnow(),
        )

        # Publish task.created event for the new occurrence
        task_data = {
            "title": next_task.title,
            "description": next_task.description,
            "priority": next_task.priority.value,
            "due_date": next_task.due_date.isoformat() if next_task.due_date else None,
            "parent_task_id": str(parent_task.id),
        }

        await self.event_publisher.publish_task_created(
            task_id=next_task.id,
            user_id=next_task.user_id,
            task_data=task_data,
        )

        return next_task

    async def run_safety_net(self) -> None:
        """Run safety net to catch missed recurring task occurrences.

        This is triggered by a cron job every 5 minutes.
        """
        try:
            logger.info("Running recurring task safety net")

            # Find all recurring patterns that need next occurrence created
            statement = select(RecurringPattern).where(
                RecurringPattern.next_occurrence_date <= datetime.utcnow()
            )

            patterns = self.session.exec(statement).all()

            for pattern in patterns:
                # Find parent task for this pattern
                parent_task = self.session.exec(
                    select(Task).where(
                        Task.recurrence_id == pattern.id,
                        Task.parent_task_id == None,  # noqa: E711
                    )
                ).first()

                if not parent_task:
                    logger.warning(f"No parent task found for pattern {pattern.id}")
                    continue

                # Check if parent task is still active
                if not parent_task.is_recurring:
                    logger.info(f"Parent task {parent_task.id} is no longer recurring")
                    continue

                # Create next occurrence
                await self.create_next_occurrence(parent_task, pattern)

            logger.info(f"Safety net processed {len(patterns)} patterns")

        except Exception as e:
            logger.error(f"Error in safety net: {e}", exc_info=True)


async def main():
    """Main entry point for recurring task service."""
    logger.info("Starting Recurring Task Service")

    # Get database session
    session = next(get_session())

    # Initialize service
    service = RecurringTaskService(session)

    # Subscribe to task-events topic
    pubsub_client = get_pubsub_client()

    # TODO: Implement Dapr pub/sub subscription
    # For now, this is a placeholder for the event consumer logic

    logger.info("Recurring Task Service started")

    # Keep service running
    try:
        while True:
            await asyncio.sleep(60)
    except KeyboardInterrupt:
        logger.info("Shutting down Recurring Task Service")


if __name__ == "__main__":
    asyncio.run(main())
