"""RecurringPatternService for managing task recurrence logic."""

from datetime import datetime, timedelta
from typing import Optional
from uuid import UUID

from sqlmodel import Session, select

from models.recurring_pattern import Frequency, RecurringPattern


class RecurringPatternService:
    """Service for managing recurring task patterns."""

    def __init__(self, session: Session):
        """Initialize service with database session.

        Args:
            session: SQLModel database session
        """
        self.session = session

    def create_pattern(
        self,
        frequency: Frequency,
        interval: int = 1,
        day_of_week: Optional[int] = None,
        day_of_month: Optional[int] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> RecurringPattern:
        """Create a new recurring pattern.

        Args:
            frequency: Recurrence frequency (DAILY, WEEKLY, MONTHLY)
            interval: Interval between occurrences
            day_of_week: Day of week for weekly recurrence (0=Sunday)
            day_of_month: Day of month for monthly recurrence (1-31)
            start_date: Start date for recurrence
            end_date: Optional end date for recurrence

        Returns:
            Created RecurringPattern
        """
        # Calculate next occurrence date
        next_occurrence = self.calculate_next_occurrence(
            frequency=frequency,
            interval=interval,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            from_date=start_date or datetime.utcnow(),
        )

        pattern = RecurringPattern(
            frequency=frequency,
            interval=interval,
            day_of_week=day_of_week,
            day_of_month=day_of_month,
            next_occurrence_date=next_occurrence,
            end_date=end_date,
        )

        self.session.add(pattern)
        self.session.commit()
        self.session.refresh(pattern)

        return pattern

    def calculate_next_occurrence(
        self,
        frequency: Frequency,
        interval: int,
        day_of_week: Optional[int] = None,
        day_of_month: Optional[int] = None,
        from_date: Optional[datetime] = None,
    ) -> datetime:
        """Calculate the next occurrence date based on recurrence pattern.

        Args:
            frequency: Recurrence frequency
            interval: Interval between occurrences
            day_of_week: Day of week for weekly recurrence
            day_of_month: Day of month for monthly recurrence
            from_date: Date to calculate from (defaults to now)

        Returns:
            Next occurrence datetime
        """
        base_date = from_date or datetime.utcnow()

        if frequency == Frequency.DAILY:
            return base_date + timedelta(days=interval)

        elif frequency == Frequency.WEEKLY:
            if day_of_week is None:
                raise ValueError("day_of_week is required for weekly recurrence")

            # Calculate days until target day of week
            current_day = base_date.weekday()
            # Convert Sunday=0 to Monday=0 format
            target_day = (day_of_week - 1) % 7
            days_ahead = (target_day - current_day) % 7

            if days_ahead == 0:
                # If today is the target day, schedule for next week
                days_ahead = 7 * interval
            else:
                # Add interval weeks
                days_ahead += 7 * (interval - 1)

            return base_date + timedelta(days=days_ahead)

        elif frequency == Frequency.MONTHLY:
            if day_of_month is None:
                raise ValueError("day_of_month is required for monthly recurrence")

            # Calculate next month
            next_month = base_date.month + interval
            next_year = base_date.year

            while next_month > 12:
                next_month -= 12
                next_year += 1

            # Handle day overflow (e.g., Feb 31 -> Feb 28)
            try:
                next_date = base_date.replace(
                    year=next_year,
                    month=next_month,
                    day=day_of_month,
                )
            except ValueError:
                # Day doesn't exist in target month, use last day of month
                if next_month == 12:
                    next_date = base_date.replace(
                        year=next_year + 1,
                        month=1,
                        day=1,
                    ) - timedelta(days=1)
                else:
                    next_date = base_date.replace(
                        year=next_year,
                        month=next_month + 1,
                        day=1,
                    ) - timedelta(days=1)

            return next_date

        else:
            raise ValueError(f"Unsupported frequency: {frequency}")

    def update_next_occurrence(
        self,
        pattern_id: UUID,
        completed_date: Optional[datetime] = None,
    ) -> RecurringPattern:
        """Update the next occurrence date for a pattern.

        Args:
            pattern_id: Pattern ID
            completed_date: Date the task was completed (defaults to now)

        Returns:
            Updated RecurringPattern
        """
        pattern = self.session.get(RecurringPattern, pattern_id)
        if not pattern:
            raise ValueError(f"Pattern {pattern_id} not found")

        # Calculate next occurrence from completion date
        next_occurrence = self.calculate_next_occurrence(
            frequency=pattern.frequency,
            interval=pattern.interval,
            day_of_week=pattern.day_of_week,
            day_of_month=pattern.day_of_month,
            from_date=completed_date or datetime.utcnow(),
        )

        pattern.next_occurrence_date = next_occurrence
        pattern.updated_at = datetime.utcnow()

        self.session.add(pattern)
        self.session.commit()
        self.session.refresh(pattern)

        return pattern

    def get_pattern(self, pattern_id: UUID) -> Optional[RecurringPattern]:
        """Get a recurring pattern by ID.

        Args:
            pattern_id: Pattern ID

        Returns:
            RecurringPattern or None if not found
        """
        return self.session.get(RecurringPattern, pattern_id)

    def delete_pattern(self, pattern_id: UUID) -> None:
        """Delete a recurring pattern.

        Args:
            pattern_id: Pattern ID
        """
        pattern = self.session.get(RecurringPattern, pattern_id)
        if pattern:
            self.session.delete(pattern)
            self.session.commit()
