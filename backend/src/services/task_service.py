"""Task service with business logic for CRUD operations."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select

from ..models.task import Priority, Task


class TaskNotFoundError(Exception):
    """Raised when a task is not found."""

    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")


class ValidationError(Exception):
    """Raised when validation fails."""

    def __init__(self, field: str, message: str) -> None:
        self.field = field
        self.message = message
        super().__init__(f"{field}: {message}")


class TaskService:
    """Service class for task operations."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def get_all_tasks(
        self,
        search: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[Priority] = None,
        category_id: Optional[UUID] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Task]:
        """Get all tasks with optional filtering and sorting."""
        statement = select(Task)

        # Apply search filter
        if search:
            search_term = f"%{search}%"
            statement = statement.where(
                (Task.title.ilike(search_term)) | (Task.description.ilike(search_term))
            )

        # Apply status filter
        if status == "completed":
            statement = statement.where(Task.completed == True)  # noqa: E712
        elif status == "incomplete":
            statement = statement.where(Task.completed == False)  # noqa: E712

        # Apply priority filter
        if priority:
            statement = statement.where(Task.priority == priority)

        # Apply category filter
        if category_id:
            statement = statement.where(Task.category_id == category_id)

        # Apply sorting
        sort_column = getattr(Task, sort_by, Task.created_at)
        if sort_order == "asc":
            statement = statement.order_by(sort_column.asc())
        else:
            statement = statement.order_by(sort_column.desc())

        return list(self.session.exec(statement).all())

    def get_task(self, task_id: UUID) -> Task:
        """Get a single task by ID."""
        task = self.session.get(Task, task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        return task

    def create_task(
        self,
        title: str,
        description: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        category_id: Optional[UUID] = None,
    ) -> Task:
        """Create a new task."""
        # Validate title
        if not title or not title.strip():
            raise ValidationError("title", "Title cannot be empty")

        if len(title) > 200:
            raise ValidationError("title", "Title must be 200 characters or less")

        # Validate description length if provided
        if description and len(description) > 1000:
            raise ValidationError(
                "description", "Description must be 1000 characters or less"
            )

        task = Task(
            title=title.strip(),
            description=description.strip() if description else None,
            priority=priority,
            category_id=category_id,
        )

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def update_task(
        self,
        task_id: UUID,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[Priority] = None,
        category_id: Optional[UUID] = None,
    ) -> Task:
        """Update an existing task."""
        task = self.get_task(task_id)

        # Validate title if provided
        if title is not None:
            if not title.strip():
                raise ValidationError("title", "Title cannot be empty")
            if len(title) > 200:
                raise ValidationError("title", "Title must be 200 characters or less")
            task.title = title.strip()

        # Update description
        if description is not None:
            if len(description) > 1000:
                raise ValidationError(
                    "description", "Description must be 1000 characters or less"
                )
            task.description = description.strip() if description else None

        # Update priority
        if priority is not None:
            task.priority = priority

        # Update category (can be set to None to remove category)
        if category_id is not None or "category_id" in locals():
            task.category_id = category_id

        # Update timestamp
        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def toggle_complete(self, task_id: UUID) -> Task:
        """Toggle task completion status."""
        task = self.get_task(task_id)
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)
        return task

    def delete_task(self, task_id: UUID) -> Task:
        """Delete a task."""
        task = self.get_task(task_id)
        self.session.delete(task)
        self.session.commit()
        return task
