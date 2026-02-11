"""Unit tests for RecurringPatternService."""

import pytest
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, SQLModel
from sqlmodel.pool import StaticPool

from models.recurring_pattern import Frequency, RecurringPattern
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


@pytest.fixture(name="service")
def service_fixture(session: Session):
    """Create a RecurringPatternService instance."""
    return RecurringPatternService(session)


class TestCalculateNextOccurrence:
    """Tests for calculate_next_occurrence method."""

    def test_daily_recurrence(self, service: RecurringPatternService):
        """Test daily recurrence calculation."""
        base_date = datetime(2026, 2, 11, 9, 0, 0)
        next_date = service.calculate_next_occurrence(
            frequency=Frequency.DAILY,
            interval=1,
            from_date=base_date,
        )

        expected = base_date + timedelta(days=1)
        assert next_date == expected

    def test_daily_recurrence_with_interval(self, service: RecurringPatternService):
        """Test daily recurrence with interval > 1."""
        base_date = datetime(2026, 2, 11, 9, 0, 0)
        next_date = service.calculate_next_occurrence(
            frequency=Frequency.DAILY,
            interval=3,
            from_date=base_date,
        )

        expected = base_date + timedelta(days=3)
        assert next_date == expected

    def test_weekly_recurrence(self, service: RecurringPatternService):
        """Test weekly recurrence calculation."""
        # Tuesday, Feb 11, 2026
        base_date = datetime(2026, 2, 11, 9, 0, 0)

        # Next Monday (day_of_week=1)
        next_date = service.calculate_next_occurrence(
            frequency=Frequency.WEEKLY,
            interval=1,
            day_of_week=1,
            from_date=base_date,
        )

        # Should be Feb 16, 2026 (next Monday)
        expected = datetime(2026, 2, 16, 9, 0, 0)
        assert next_date == expected

    def test_weekly_recurrence_same_day(self, service: RecurringPatternService):
        """Test weekly recurrence when today is the target day."""
        # Monday, Feb 10, 2026
        base_date = datetime(2026, 2, 10, 9, 0, 0)

        # Next Monday (day_of_week=1)
        next_date = service.calculate_next_occurrence(
            frequency=Frequency.WEEKLY,
            interval=1,
            day_of_week=1,
            from_date=base_date,
        )

        # Should be Feb 17, 2026 (next week Monday)
        expected = datetime(2026, 2, 17, 9, 0, 0)
        assert next_date == expected

    def test_monthly_recurrence(self, service: RecurringPatternService):
        """Test monthly recurrence calculation."""
        base_date = datetime(2026, 2, 11, 9, 0, 0)

        # 15th of next month
        next_date = service.calculate_next_occurrence(
            frequency=Frequency.MONTHLY,
            interval=1,
            day_of_month=15,
            from_date=base_date,
        )

        expected = datetime(2026, 3, 15, 9, 0, 0)
        assert next_date == expected

    def test_monthly_recurrence_invalid_day(self, service: RecurringPatternService):
        """Test monthly recurrence with invalid day (e.g., Feb 31)."""
        base_date = datetime(2026, 1, 15, 9, 0, 0)

        # 31st of February (doesn't exist)
        next_date = service.calculate_next_occurrence(
            frequency=Frequency.MONTHLY,
            interval=1,
            day_of_month=31,
            from_date=base_date,
        )

        # Should use last day of February (28th in 2026)
        expected = datetime(2026, 2, 28, 9, 0, 0)
        assert next_date == expected

    def test_weekly_requires_day_of_week(self, service: RecurringPatternService):
        """Test that weekly recurrence requires day_of_week."""
        with pytest.raises(ValueError, match="day_of_week is required"):
            service.calculate_next_occurrence(
                frequency=Frequency.WEEKLY,
                interval=1,
                from_date=datetime.utcnow(),
            )

    def test_monthly_requires_day_of_month(self, service: RecurringPatternService):
        """Test that monthly recurrence requires day_of_month."""
        with pytest.raises(ValueError, match="day_of_month is required"):
            service.calculate_next_occurrence(
                frequency=Frequency.MONTHLY,
                interval=1,
                from_date=datetime.utcnow(),
            )


class TestCreatePattern:
    """Tests for create_pattern method."""

    def test_create_daily_pattern(self, service: RecurringPatternService, session: Session):
        """Test creating a daily recurring pattern."""
        pattern = service.create_pattern(
            frequency=Frequency.DAILY,
            interval=1,
            start_date=datetime(2026, 2, 11, 9, 0, 0),
        )

        assert pattern.id is not None
        assert pattern.frequency == Frequency.DAILY
        assert pattern.interval == 1
        assert pattern.next_occurrence_date == datetime(2026, 2, 12, 9, 0, 0)

    def test_create_weekly_pattern(self, service: RecurringPatternService, session: Session):
        """Test creating a weekly recurring pattern."""
        pattern = service.create_pattern(
            frequency=Frequency.WEEKLY,
            interval=1,
            day_of_week=1,  # Monday
            start_date=datetime(2026, 2, 11, 9, 0, 0),
        )

        assert pattern.id is not None
        assert pattern.frequency == Frequency.WEEKLY
        assert pattern.day_of_week == 1

    def test_create_pattern_with_end_date(self, service: RecurringPatternService, session: Session):
        """Test creating a pattern with end date."""
        end_date = datetime(2026, 12, 31, 23, 59, 59)
        pattern = service.create_pattern(
            frequency=Frequency.DAILY,
            interval=1,
            start_date=datetime(2026, 2, 11, 9, 0, 0),
            end_date=end_date,
        )

        assert pattern.end_date == end_date


class TestUpdateNextOccurrence:
    """Tests for update_next_occurrence method."""

    def test_update_next_occurrence(self, service: RecurringPatternService, session: Session):
        """Test updating next occurrence date."""
        # Create pattern
        pattern = service.create_pattern(
            frequency=Frequency.DAILY,
            interval=1,
            start_date=datetime(2026, 2, 11, 9, 0, 0),
        )

        original_next = pattern.next_occurrence_date

        # Update next occurrence
        updated_pattern = service.update_next_occurrence(
            pattern_id=pattern.id,
            completed_date=datetime(2026, 2, 12, 10, 0, 0),
        )

        # Should be one day after completion date
        expected = datetime(2026, 2, 13, 10, 0, 0)
        assert updated_pattern.next_occurrence_date == expected
        assert updated_pattern.next_occurrence_date != original_next
