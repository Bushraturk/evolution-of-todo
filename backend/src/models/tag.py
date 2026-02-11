"""Tag model for task categorization."""

from datetime import datetime
from typing import Optional
from uuid import UUID, uuid4

from sqlmodel import Field, SQLModel


class TagBase(SQLModel):
    """Base tag model with common fields."""

    name: str = Field(max_length=50, sa_column_kwargs={"nullable": False})
    user_id: str = Field(sa_column_kwargs={"nullable": False}, index=True)
    color: Optional[str] = Field(default=None, max_length=7)  # Hex color code


class Tag(TagBase, table=True):
    """Tag database model."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    def __repr__(self) -> str:
        return f"Tag(id={self.id}, name='{self.name}', user_id='{self.user_id}')"
