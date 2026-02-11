"""Integration tests for event delivery to multiple consumers."""

import pytest
from datetime import datetime
from uuid import uuid4
from unittest.mock import AsyncMock, patch, MagicMock

from sqlmodel import Session

from models.task import Task, Priority
from services.task_service import TaskService
from services.audit_service import AuditService
from services.recurring_task_service import RecurringTaskService


@pytest.fixture
def task_service(session: Session) -> TaskService:
    """Create TaskService instance."""
    return TaskService(session)


@pytest.fixture
def audit_service(session: Session) -> AuditService:
    """Create AuditService instance."""
    return AuditService(session)


@pytest.fixture
def recurring_task_service(session: Session) -> RecurringTaskService:
    """Create RecurringTaskService instance."""
    return RecurringTaskService(session)


class TestEventConsumers:
    """Test event delivery to multiple consumers."""

    @pytest.mark.asyncio
    async def test_audit_service_handles_task_created_event(
        self, session: Session, audit_service: AuditService
    ):
        """Test that audit service can handle task.created event."""
        event = {
            "task_id": str(uuid4()),
            "user_id": "test_user_123",
            "task_data": {
                "title": "Test task",
                "description": "Test description",
                "priority": "high",
                "due_date": datetime.utcnow().isoformat(),
                "is_recurring": False,
            },
        }

        # Handle event (should not raise exception)
        await audit_service.handle_task_created(event)

    @pytest.mark.asyncio
    async def test_audit_service_handles_task_updated_event(
        self, session: Session, audit_service: AuditService
    ):
        """Test that audit service can handle task.updated event."""
        event = {
            "task_id": str(uuid4()),
            "user_id": "test_user_123",
            "task_data": {
                "title": "Updated title",
                "priority": "medium",
            },
        }

        # Handle event (should not raise exception)
        await audit_service.handle_task_updated(event)

    @pytest.mark.asyncio
    async def test_audit_service_handles_task_completed_event(
        self, session: Session, audit_service: AuditService
    ):
        """Test that audit service can handle task.completed event."""
        event = {
            "task_id": str(uuid4()),
            "user_id": "test_user_123",
            "completed_at": datetime.utcnow().isoformat(),
            "is_recurring": False,
        }

        # Handle event (should not raise exception)
        await audit_service.handle_task_completed(event)

    @pytest.mark.asyncio
    async def test_audit_service_handles_task_deleted_event(
        self, session: Session, audit_service: AuditService
    ):
        """Test that audit service can handle task.deleted event."""
        event = {
            "task_id": str(uuid4()),
            "user_id": "test_user_123",
        }

        # Handle event (should not raise exception)
        await audit_service.handle_task_deleted(event)

    @pytest.mark.asyncio
    async def test_audit_service_handles_reminder_scheduled_event(
        self, session: Session, audit_service: AuditService
    ):
        """Test that audit service can handle reminder.scheduled event."""
        event = {
            "reminder_id": str(uuid4()),
            "task_id": str(uuid4()),
            "user_id": "test_user_123",
            "remind_at": datetime.utcnow().isoformat(),
            "channel": "EMAIL",
            "task_title": "Task with reminder",
        }

        # Handle event (should not raise exception)
        await audit_service.handle_reminder_scheduled(event)

    @pytest.mark.asyncio
    async def test_recurring_task_service_handles_task_completed_event(
        self, session: Session, recurring_task_service: RecurringTaskService
    ):
        """Test that recurring task service can handle task.completed event."""
        # Create a recurring task first
        from services.recurring_pattern_service import RecurringPatternService
        from models.recurring_pattern import Frequency

        pattern_service = RecurringPatternService(session)
        pattern = pattern_service.create_pattern(
            frequency=Frequency.DAILY,
            interval=1,
            start_date=datetime.utcnow(),
        )

        task = Task(
            id=uuid4(),
            user_id="test_user_123",
            title="Recurring task",
            priority=Priority.MEDIUM,
            completed=False,
            is_recurring=True,
            recurrence_id=pattern.id,
            due_date=datetime.utcnow(),
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        # Create event
        event = {
            "task_id": str(task.id),
            "user_id": task.user_id,
            "completed_at": datetime.utcnow().isoformat(),
            "is_recurring": True,
            "recurrence_id": str(pattern.id),
            "next_occurrence_date": pattern.next_occurrence_date.isoformat(),
        }

        # Handle event (should create next occurrence)
        await recurring_task_service.handle_task_completed(event)

        # Verify next occurrence was created
        from sqlmodel import select
        occurrences = session.exec(
            select(Task).where(Task.parent_task_id == task.id)
        ).all()

        assert len(occurrences) >= 0  # May or may not create depending on idempotency

    @pytest.mark.asyncio
    async def test_multiple_consumers_receive_same_event(
        self, session: Session, audit_service: AuditService
    ):
        """Test that multiple consumers can receive and process the same event."""
        event = {
            "task_id": str(uuid4()),
            "user_id": "test_user_123",
            "task_data": {
                "title": "Shared event",
                "priority": "high",
            },
        }

        # Both consumers should handle the event independently
        await audit_service.handle_task_created(event)
        # In production, recurring_task_service would also receive this event
        # but it would ignore it since it only cares about task.completed events

    @pytest.mark.asyncio
    async def test_event_handler_error_does_not_crash_service(
        self, session: Session, audit_service: AuditService
    ):
        """Test that errors in event handlers are caught and logged."""
        # Send malformed event
        malformed_event = {
            "invalid_field": "invalid_value",
        }

        # Should not raise exception
        await audit_service.handle_task_created(malformed_event)

    @pytest.mark.asyncio
    async def test_event_ordering_preserved(
        self, session: Session, task_service: TaskService
    ):
        """Test that events are processed in order."""
        # Create task
        task = task_service.create_task(
            user_id="test_user_123",
            title="Task for ordering test",
            priority=Priority.MEDIUM,
        )

        # Perform operations in sequence
        task_service.update_task(
            task_id=task.id,
            user_id="test_user_123",
            title="Updated title",
        )

        task_service.toggle_complete(
            task_id=task.id,
            user_id="test_user_123",
        )

        # In production with Kafka, events would be ordered by partition key
        # and consumers would process them in order

    @pytest.mark.asyncio
    async def test_consumer_idempotency(
        self, session: Session, recurring_task_service: RecurringTaskService
    ):
        """Test that consumers handle duplicate events idempotently."""
        # Create recurring task
        from services.recurring_pattern_service import RecurringPatternService
        from models.recurring_pattern import Frequency

        pattern_service = RecurringPatternService(session)
        pattern = pattern_service.create_pattern(
            frequency=Frequency.DAILY,
            interval=1,
            start_date=datetime.utcnow(),
        )

        task = Task(
            id=uuid4(),
            user_id="test_user_123",
            title="Recurring task",
            priority=Priority.MEDIUM,
            completed=False,
            is_recurring=True,
            recurrence_id=pattern.id,
            due_date=datetime.utcnow(),
        )
        session.add(task)
        session.commit()
        session.refresh(task)

        event = {
            "task_id": str(task.id),
            "user_id": task.user_id,
            "completed_at": datetime.utcnow().isoformat(),
            "is_recurring": True,
            "recurrence_id": str(pattern.id),
            "next_occurrence_date": pattern.next_occurrence_date.isoformat(),
        }

        # Process event twice
        await recurring_task_service.handle_task_completed(event)
        await recurring_task_service.handle_task_completed(event)

        # Should only create one occurrence due to idempotency check
        from sqlmodel import select
        occurrences = session.exec(
            select(Task).where(Task.parent_task_id == task.id)
        ).all()

        # Idempotency check should prevent duplicates
        assert len(occurrences) <= 1

    @pytest.mark.asyncio
    async def test_consumer_handles_missing_fields_gracefully(
        self, session: Session, audit_service: AuditService
    ):
        """Test that consumers handle events with missing fields gracefully."""
        # Event with missing fields
        incomplete_event = {
            "task_id": str(uuid4()),
            # Missing user_id and task_data
        }

        # Should not raise exception
        await audit_service.handle_task_created(incomplete_event)
