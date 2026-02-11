"""Integration tests for recurring task creation flow."""

import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, SQLModel, select
from sqlmodel.pool import StaticPool

from models.task import Task
from models.recurring_pattern import Frequency, RecurringPattern
from services.task_service import TaskService
from services.recurring_pattern_service import RecurringPatternService


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


class TestRecurringTaskCreation:
    """Tests for recurring task creation flow."""

    def test_create_daily_recurring_task(self, task_service: TaskService, session: Session):
        """Test creating a daily recurring task."""
        # Create recurring task
        task = task_service.create_task(
            user_id="test_user_123",
            title="Daily standup",
            description="Team sync meeting",
            due_date=datetime(2026, 2, 12, 9, 0, 0),
            recurrence={
                "frequency": "DAILY",
                "interval": 1,
            },
        )

        # Verify task was created
        assert task.id is not None
        assert task.title == "Daily standup"
        assert task.is_recurring is True
        assert task.recurrence_id is not None

        # Verify recurring pattern was created
        pattern = session.get(RecurringPattern, task.recurrence_id)
        assert pattern is not None
        assert pattern.frequency == Frequency.DAILY
        assert pattern.interval == 1
        assert pattern.next_occurrence_date == datetime(2026, 2, 13, 9, 0, 0)

    def test_create_weekly_recurring_task(self, task_service: TaskService, session: Session):
        """Test creating a weekly recurring task."""
        task = task_service.create_task(
            user_id="test_user_123",
            title="Weekly review",
            due_date=datetime(2026, 2, 16, 14, 0, 0),  # Monday
            recurrence={
                "frequency": "WEEKLY",
                "interval": 1,
                "day_of_week": 1,  # Monday
            },
        )

        assert task.is_recurring is True
        pattern = session.get(RecurringPattern, task.recurrence_id)
        assert pattern.frequency == Frequency.WEEKLY
        assert pattern.day_of_week == 1

    def test_create_monthly_recurring_task(self, task_service: TaskService, session: Session):
        """Test creating a monthly recurring task."""
        task = task_service.create_task(
            user_id="test_user_123",
            title="Monthly report",
            due_date=datetime(2026, 2, 15, 17, 0, 0),
            recurrence={
                "frequency": "MONTHLY",
                "interval": 1,
                "day_of_month": 15,
            },
        )

        assert task.is_recurring is True
        pattern = session.get(RecurringPattern, task.recurrence_id)
        assert pattern.frequency == Frequency.MONTHLY
        assert pattern.day_of_month == 15

    def test_create_recurring_task_with_end_date(self, task_service: TaskService, session: Session):
        """Test creating a recurring task with end date."""
        end_date = datetime(2026, 12, 31, 23, 59, 59)
        task = task_service.create_task(
            user_id="test_user_123",
            title="Limited recurring task",
            due_date=datetime(2026, 2, 12, 9, 0, 0),
            recurrence={
                "frequency": "DAILY",
                "interval": 1,
                "end_date": end_date,
            },
        )

        pattern = session.get(RecurringPattern, task.recurrence_id)
        assert pattern.end_date == end_date

    def test_create_non_recurring_task(self, task_service: TaskService, session: Session):
        """Test creating a non-recurring task."""
        task = task_service.create_task(
            user_id="test_user_123",
            title="One-time task",
            due_date=datetime(2026, 2, 12, 9, 0, 0),
        )

        assert task.is_recurring is False
        assert task.recurrence_id is None

    def test_get_task_occurrences_empty(self, task_service: TaskService, session: Session):
        """Test getting occurrences for a recurring task with no occurrences yet."""
        task = task_service.create_task(
            user_id="test_user_123",
            title="Daily task",
            due_date=datetime(2026, 2, 12, 9, 0, 0),
            recurrence={
                "frequency": "DAILY",
                "interval": 1,
            },
        )

        occurrences = task_service.get_task_occurrences(task.id, "test_user_123")

        assert occurrences["parent_task"]["id"] == str(task.id)
        assert occurrences["total"] == 0
        assert len(occurrences["occurrences"]) == 0
        assert occurrences["next_occurrence_date"] is not None

    def test_stop_recurrence(self, task_service: TaskService, session: Session):
        """Test stopping recurrence for a recurring task."""
        task = task_service.create_task(
            user_id="test_user_123",
            title="Daily task",
            due_date=datetime(2026, 2, 12, 9, 0, 0),
            recurrence={
                "frequency": "DAILY",
                "interval": 1,
            },
        )

        original_recurrence_id = task.recurrence_id
        assert task.is_recurring is True

        # Stop recurrence
        result = task_service.stop_recurrence(task.id, "test_user_123")

        assert result["message"] == "Recurrence stopped"
        assert result["task"]["is_recurring"] is False
        assert result["task"]["recurrence"] is None

        # Verify pattern was deleted
        pattern = session.get(RecurringPattern, original_recurrence_id)
        assert pattern is None

    def test_validation_weekly_requires_day_of_week(self, task_service: TaskService):
        """Test that weekly recurrence requires day_of_week."""
        with pytest.raises(Exception):  # Should raise ValidationError
            task_service.create_task(
                user_id="test_user_123",
                title="Invalid weekly task",
                due_date=datetime(2026, 2, 12, 9, 0, 0),
                recurrence={
                    "frequency": "WEEKLY",
                    "interval": 1,
                    # Missing day_of_week
                },
            )

    def test_validation_monthly_requires_day_of_month(self, task_service: TaskService):
        """Test that monthly recurrence requires day_of_month."""
        with pytest.raises(Exception):  # Should raise ValidationError
            task_service.create_task(
                user_id="test_user_123",
                title="Invalid monthly task",
                due_date=datetime(2026, 2, 12, 9, 0, 0),
                recurrence={
                    "frequency": "MONTHLY",
                    "interval": 1,
                    # Missing day_of_month
                },
            )
