"""Category model for task organization."""

from typing import TYPE_CHECKING, List
from uuid import UUID, uuid4

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .task import Task


class CategoryBase(SQLModel):
    """Base category model with common fields."""

    name: str = Field(max_length=50, unique=True)
    color: str = Field(default="#808080", max_length=7)


class Category(CategoryBase, table=True):
    """Category database model."""

    id: UUID = Field(default_factory=uuid4, primary_key=True)

    # Relationship to Tasks
    tasks: List["Task"] = Relationship(back_populates="category")

    def __repr__(self) -> str:
        return f"Category(id={self.id}, name='{self.name}')"
