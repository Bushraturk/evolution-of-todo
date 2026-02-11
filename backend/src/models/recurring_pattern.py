"""RecurringPattern model for task recurrence configuration."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional, List
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .task import Task


class Frequency(str, Enum):
    """Recurrence frequency options."""

    DAILY = "DAILY"
    WEEKLY = "WEEKLY"
    MONTHLY = "MONTHLY"


class RecurringPatternBase(SQLModel):
    """Base recurring pattern model with common fields."""

    frequency: Frequency = Field(sa_column_kwargs={"nullable": False})
    interval: int = Field(default=1, ge=1)  # Every N days/weeks/months
    day_of_week: Optional[int] = Field(default=None, ge=0, le=6)  # 0=Sunday, 6=Saturday
    day_of_month: Optional[int] = Field(default=None, ge=1, le=31)  # 1-31
    next_occurrence_date: datetime = Field(sa_column_kwargs={"nullable": False}, index=True)
    end_date: Optional[datetime] = Field(default=None)


class RecurringPattern(RecurringPatternBase, table=True):
    """RecurringPattern database model."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to Tasks
    tasks: List["Task"] = Relationship(back_populates="recurrence")

    def __repr__(self) -> str:
        return f"RecurringPattern(id={self.id}, frequency={self.frequency}, interval={self.interval})"
