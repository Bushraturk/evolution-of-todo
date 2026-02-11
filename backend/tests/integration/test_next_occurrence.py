"""Integration tests for next occurrence generation."""

import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, SQLModel, select
from sqlmodel.pool import StaticPool

from models.task import Task
from models.recurring_pattern import Frequency, RecurringPattern
from services.task_service import TaskService
from services.recurring_task_service import RecurringTaskService


@pytest.fixture(name="session")
def session_fixture():
    """Create a test database session."""
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    with Session(engine) as session:
        yield session


@pytest.fixture(name="task_service")
def task_service_fixture(session: Session):
    """Create a TaskService instance."""
    return TaskService(session)


@pytest.fixture(name="recurring_service")
def recurring_service_fixture(session: Session):
    """Create a RecurringTaskService instance."""
    return RecurringTaskService(session)


class TestNextOccurrenceGeneration:
    """Tests for next occurrence generation."""

    @pytest.mark.asyncio
    async def test_create_next_occurrence_daily(
        self,
        task_service: TaskService,
        recurring_service: RecurringTaskService,
        session: Session,
    ):
        """Test creating next occurrence for daily recurring task."""
        # Create recurring task
        parent_task = task_service.create_task(
            user_id="test_user_123",
            title="Daily standup",
            due_date=datetime(2026, 2, 12, 9, 0, 0),
            recurrence={
                "frequency": "DAILY",
                "interval": 1,
            },
        )

        pattern = session.get(RecurringPattern, parent_task.recurrence_id)

        # Create next occurrence
        next_task = await recurring_service.create_next_occurrence(parent_task, pattern)

        # Verify next task was created
        assert next_task.id is not None
        assert next_task.title == parent_task.title
        assert next_task.description == parent_task.description
        assert next_task.priority == parent_task.priority
        assert next_task.parent_task_id == parent_task.id
        assert next_task.is_recurring is False  # Occurrences are not recurring
        assert next_task.due_date == datetime(2026, 2, 13, 9, 0, 0)

        # Verify pattern was updated
        session.refresh(pattern)
        assert pattern.next_occurrence_date == datetime(2026, 2, 14, 9, 0, 0)

    @pytest.mark.asyncio
    async def test_idempotency_prevents_duplicates(
        self,
        task_service: TaskService,
        recurring_service: RecurringTaskService,
        session: Session,
    ):
        """Test that idempotency check prevents duplicate occurrences."""
        # Create recurring task
        parent_task = task_service.create_task(
            user_id="test_user_123",
            title="Daily task",
            due_date=datetime(2026, 2, 12, 9, 0, 0),
            recurrence={
                "frequency": "DAILY",
                "interval": 1,
            },
        )

        pattern = session.get(RecurringPattern, parent_task.recurrence_id)

        # Create next occurrence
        first_occurrence = await recurring_service.create_next_occurrence(parent_task, pattern)

        # Try to create again (should return existing)
        second_occurrence = await recurring_service.create_next_occurrence(parent_task, pattern)

        # Should return the same task
        assert first_occurrence.id == second_occurrence.id

        # Verify only one occurrence exists
        occurrences = session.exec(
            select(Task).where(Task.parent_task_id == parent_task.id)
        ).all()
        assert len(occurrences) == 1

    @pytest.mark.asyncio
    async def test_handle_task_completed_event(
        self,
        task_service: TaskService,
        recurring_service: RecurringTaskService,
        session: Session,
    ):
        """Test handling task.completed event."""
        # Create recurring task
        parent_task = task_service.create_task(
            user_id="test_user_123",
            title="Daily task",
            due_date=datetime(2026, 2, 12, 9, 0, 0),
            recurrence={
                "frequency": "DAILY",
                "interval": 1,
            },
        )

        # Simulate task.completed event
        event = {
            "task_id": str(parent_task.id),
            "user_id": "test_user_123",
            "is_recurring": True,
            "recurrence_id": str(parent_task.recurrence_id),
        }

        # Handle event
        await recurring_service.handle_task_completed(event)

        # Verify next occurrence was created
        occurrences = session.exec(
            select(Task).where(Task.parent_task_id == parent_task.id)
        ).all()
        assert len(occurrences) == 1
        assert occurrences[0].due_date == datetime(2026, 2, 13, 9, 0, 0)

    @pytest.mark.asyncio
    async def test_safety_net_catches_missed_occurrences(
        self,
        task_service: TaskService,
        recurring_service: RecurringTaskService,
        session: Session,
    ):
        """Test that safety net catches missed occurrences."""
        # Create recurring task with past next_occurrence_date
        parent_task = task_service.create_task(
            user_id="test_user_123",
            title="Daily task",
            due_date=datetime(2026, 2, 10, 9, 0, 0),
            recurrence={
                "frequency": "DAILY",
                "interval": 1,
            },
        )

        # Manually set next_occurrence_date to past
        pattern = session.get(RecurringPattern, parent_task.recurrence_id)
        pattern.next_occurrence_date = datetime(2026, 2, 11, 9, 0, 0)
        session.add(pattern)
        session.commit()

        # Run safety net
        await recurring_service.run_safety_net()

        # Verify occurrence was created
        occurrences = session.exec(
            select(Task).where(Task.parent_task_id == parent_task.id)
        ).all()
        assert len(occurrences) >= 1

    @pytest.mark.asyncio
    async def test_respects_end_date(
        self,
        task_service: TaskService,
        recurring_service: RecurringTaskService,
        session: Session,
    ):
        """Test that recurrence respects end date."""
        # Create recurring task with end date in the past
        parent_task = task_service.create_task(
            user_id="test_user_123",
            title="Limited task",
            due_date=datetime(2026, 2, 10, 9, 0, 0),
            recurrence={
                "frequency": "DAILY",
                "interval": 1,
                "end_date": datetime(2026, 2, 11, 23, 59, 59),
            },
        )

        # Set next_occurrence_date past end_date
        pattern = session.get(RecurringPattern, parent_task.recurrence_id)
        pattern.next_occurrence_date = datetime(2026, 2, 12, 9, 0, 0)
        session.add(pattern)
        session.commit()

        # Try to create next occurrence
        event = {
            "task_id": str(parent_task.id),
            "user_id": "test_user_123",
            "is_recurring": True,
            "recurrence_id": str(parent_task.recurrence_id),
        }

        await recurring_service.handle_task_completed(event)

        # Verify no occurrence was created (past end date)
        occurrences = session.exec(
            select(Task).where(Task.parent_task_id == parent_task.id)
        ).all()
        assert len(occurrences) == 0

    @pytest.mark.asyncio
    async def test_weekly_occurrence_generation(
        self,
        task_service: TaskService,
        recurring_service: RecurringTaskService,
        session: Session,
    ):
        """Test weekly occurrence generation."""
        # Create weekly recurring task (every Monday)
        parent_task = task_service.create_task(
            user_id="test_user_123",
            title="Weekly meeting",
            due_date=datetime(2026, 2, 16, 14, 0, 0),  # Monday
            recurrence={
                "frequency": "WEEKLY",
                "interval": 1,
                "day_of_week": 1,  # Monday
            },
        )

        pattern = session.get(RecurringPattern, parent_task.recurrence_id)

        # Create next occurrence
        next_task = await recurring_service.create_next_occurrence(parent_task, pattern)

        # Should be next Monday
        assert next_task.due_date == datetime(2026, 2, 23, 14, 0, 0)

    @pytest.mark.asyncio
    async def test_monthly_occurrence_generation(
        self,
        task_service: TaskService,
        recurring_service: RecurringTaskService,
        session: Session,
    ):
        """Test monthly occurrence generation."""
        # Create monthly recurring task (15th of each month)
        parent_task = task_service.create_task(
            user_id="test_user_123",
            title="Monthly report",
            due_date=datetime(2026, 2, 15, 17, 0, 0),
            recurrence={
                "frequency": "MONTHLY",
                "interval": 1,
                "day_of_month": 15,
            },
        )

        pattern = session.get(RecurringPattern, parent_task.recurrence_id)

        # Create next occurrence
        next_task = await recurring_service.create_next_occurrence(parent_task, pattern)

        # Should be March 15th
        assert next_task.due_date == datetime(2026, 3, 15, 17, 0, 0)
