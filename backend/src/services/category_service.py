"""Category service with business logic for CRUD operations."""

from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from ..models.category import Category


class CategoryNotFoundError(Exception):
    """Raised when a category is not found."""

    def __init__(self, category_id: UUID) -> None:
        self.category_id = category_id
        super().__init__(f"Category with ID {category_id} not found")


class CategoryService:
    """Service class for category operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_categories(self) -> List[Category]:
        """Get all categories."""
        statement = select(Category).order_by(Category.name)
        return list(self.session.exec(statement).all())

    def get_category(self, category_id: UUID) -> Category:
        """Get a single category by ID."""
        category = self.session.get(Category, category_id)
        if not category:
            raise CategoryNotFoundError(category_id)
        return category

    def create_category(
        self,
        name: str,
        color: str = "#808080",
    ) -> Category:
        """Create a new category."""
        category = Category(
            name=name.strip(),
            color=color,
        )

        self.session.add(category)
        self.session.commit()
        self.session.refresh(category)
        return category

    def delete_category(self, category_id: UUID) -> Category:
        """Delete a category."""
        category = self.get_category(category_id)
        self.session.delete(category)
        self.session.commit()
        return category
