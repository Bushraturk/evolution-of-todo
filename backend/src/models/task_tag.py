"""TaskTag junction model for many-to-many relationship between tasks and tags."""

from datetime import datetime
from uuid import UUID

from sqlmodel import Field, SQLModel


class TaskTag(SQLModel, table=True):
    """TaskTag junction table for many-to-many relationship."""

    task_id: UUID = Field(foreign_key="task.id", primary_key=True, index=True)
    tag_id: UUID = Field(foreign_key="tag.id", primary_key=True, index=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"TaskTag(task_id={self.task_id}, tag_id={self.tag_id})"
