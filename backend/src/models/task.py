"""Task model with Priority enum and user ownership."""

from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .category import Category
    from .recurring_pattern import RecurringPattern


class Priority(str, Enum):
    """Task priority levels."""

    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskBase(SQLModel):
    """Base task model with common fields."""

    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: Priority = Field(default=Priority.MEDIUM)
    category_id: Optional[UUID] = Field(default=None, foreign_key="category.id")
    user_id: str = Field(index=True)  # User ID from Better Auth (CUID format)

    # Advanced features (Phase VI)
    due_date: Optional[datetime] = Field(default=None, index=True)
    is_recurring: bool = Field(default=False)
    parent_task_id: Optional[UUID] = Field(default=None, foreign_key="task.id")
    recurrence_id: Optional[UUID] = Field(default=None, foreign_key="recurring_pattern.id")


class Task(TaskBase, table=True):
    """Task database model."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to Category
    category: Optional["Category"] = Relationship(back_populates="tasks")

    # Relationship to RecurringPattern
    recurrence: Optional["RecurringPattern"] = Relationship(back_populates="tasks")

    def __repr__(self) -> str:
        return f"Task(id={self.id}, title='{self.title}', completed={self.completed})"
