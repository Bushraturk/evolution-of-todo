"""Custom exceptions for services."""

from uuid import UUID


class TaskNotFoundError(Exception):
    """Raised when a task is not found."""

    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")


class CategoryNotFoundError(Exception):
    """Raised when a category is not found."""

    def __init__(self, category_id: UUID) -> None:
        self.category_id = category_id
        super().__init__(f"Category with ID {category_id} not found")


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")
