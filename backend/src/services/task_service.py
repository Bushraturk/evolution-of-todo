"""Task service with business logic for CRUD operations."""

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from sqlmodel import Session, select

from ..models.task import Priority, Task
from ..models.recurring_pattern import Frequency, RecurringPattern
from .recurring_pattern_service import RecurringPatternService
from .event_publisher import get_event_publisher


class TaskNotFoundError(Exception):
    """Raised when a task is not found."""

    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found")


class AccessDeniedError(Exception):
    """Raised when user tries to access a task they don't own."""

    def __init__(self, task_id: UUID) -> None:
        self.task_id = task_id
        super().__init__(f"Access denied to task with ID {task_id}")


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
        self.recurring_service = RecurringPatternService(session)
        self.event_publisher = get_event_publisher()

    def get_all_tasks(
        self,
        user_id: str,
        search: Optional[str] = None,
        status: Optional[str] = None,
        priority: Optional[Priority] = None,
        category_id: Optional[UUID] = None,
        sort_by: str = "created_at",
        sort_order: str = "desc",
    ) -> List[Task]:
        """Get all tasks for a specific user with optional filtering and sorting."""
        statement = select(Task).where(Task.user_id == user_id)

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

    def get_task(self, task_id: UUID, user_id: str) -> Task:
        """Get a single task by ID, verifying user ownership."""
        task = self.session.get(Task, task_id)
        if not task:
            raise TaskNotFoundError(task_id)
        if task.user_id != user_id:
            raise AccessDeniedError(task_id)
        return task

    def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None,
        priority: Priority = Priority.MEDIUM,
        category_id: Optional[UUID] = None,
        due_date: Optional[datetime] = None,
        recurrence: Optional[Dict[str, Any]] = None,
    ) -> Task:
        """Create a new task for a user.

        Args:
            user_id: User ID
            title: Task title
            description: Task description
            priority: Task priority
            category_id: Category ID
            due_date: Due date for the task
            recurrence: Recurrence configuration dict with keys:
                - frequency: DAILY, WEEKLY, or MONTHLY
                - interval: Interval between occurrences (default 1)
                - day_of_week: Day of week for weekly (0-6, 0=Sunday)
                - day_of_month: Day of month for monthly (1-31)
                - end_date: Optional end date for recurrence

        Returns:
            Created Task
        """
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

        # Create recurring pattern if recurrence is provided
        recurrence_id = None
        is_recurring = False

        if recurrence:
            is_recurring = True
            frequency = Frequency(recurrence.get("frequency"))
            interval = recurrence.get("interval", 1)
            day_of_week = recurrence.get("day_of_week")
            day_of_month = recurrence.get("day_of_month")
            end_date = recurrence.get("end_date")

            # Validate recurrence fields
            if frequency == Frequency.WEEKLY and day_of_week is None:
                raise ValidationError("day_of_week", "Required for weekly recurrence")
            if frequency == Frequency.MONTHLY and day_of_month is None:
                raise ValidationError("day_of_month", "Required for monthly recurrence")

            # Create recurring pattern
            pattern = self.recurring_service.create_pattern(
                frequency=frequency,
                interval=interval,
                day_of_week=day_of_week,
                day_of_month=day_of_month,
                start_date=due_date or datetime.utcnow(),
                end_date=end_date,
            )
            recurrence_id = pattern.id

        task = Task(
            user_id=user_id,
            title=title.strip(),
            description=description.strip() if description else None,
            priority=priority,
            category_id=category_id,
            due_date=due_date,
            is_recurring=is_recurring,
            recurrence_id=recurrence_id,
        )

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        # Publish task.created event
        task_data = {
            "title": task.title,
            "description": task.description,
            "priority": task.priority.value,
            "due_date": task.due_date.isoformat() if task.due_date else None,
            "is_recurring": task.is_recurring,
            "recurrence": recurrence if recurrence else None,
        }

        # Fire and forget - don't await
        import asyncio
        try:
            asyncio.create_task(
                self.event_publisher.publish_task_created(
                    task_id=task.id,
                    user_id=user_id,
                    task_data=task_data,
                )
            )
        except RuntimeError:
            # No event loop running, skip event publishing
            pass

        return task

    def update_task(
        self,
        task_id: UUID,
        user_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        priority: Optional[Priority] = None,
        category_id: Optional[UUID] = None,
    ) -> Task:
        """Update an existing task, verifying user ownership."""
        task = self.get_task(task_id, user_id)

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

    def toggle_complete(self, task_id: UUID, user_id: str) -> Task:
        """Toggle task completion status, verifying user ownership."""
        task = self.get_task(task_id, user_id)
        was_completed = task.completed
        task.completed = not task.completed
        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        # Publish task.completed event if task was just completed and is recurring
        if task.completed and not was_completed and task.is_recurring:
            import asyncio
            try:
                # Get recurrence pattern for next occurrence date
                next_occurrence_date = None
                if task.recurrence_id:
                    pattern = self.recurring_service.get_pattern(task.recurrence_id)
                    if pattern:
                        next_occurrence_date = pattern.next_occurrence_date

                asyncio.create_task(
                    self.event_publisher.publish_task_completed(
                        task_id=task.id,
                        user_id=user_id,
                        completed_at=task.updated_at,
                        is_recurring=task.is_recurring,
                        recurrence_id=task.recurrence_id,
                        next_occurrence_date=next_occurrence_date,
                    )
                )
            except RuntimeError:
                # No event loop running, skip event publishing
                pass

        return task

    def delete_task(self, task_id: UUID, user_id: str) -> Task:
        """Delete a task, verifying user ownership."""
        task = self.get_task(task_id, user_id)
        self.session.delete(task)
        self.session.commit()

        # Publish task.deleted event
        import asyncio
        try:
            asyncio.create_task(
                self.event_publisher.publish_task_deleted(
                    task_id=task.id,
                    user_id=user_id,
                )
            )
        except RuntimeError:
            # No event loop running, skip event publishing
            pass

        return task

    def get_task_occurrences(
        self,
        task_id: UUID,
        user_id: str,
    ) -> Dict[str, Any]:
        """Get all occurrences of a recurring task.

        Args:
            task_id: Parent task ID
            user_id: User ID

        Returns:
            Dict with parent task info and list of occurrences
        """
        parent_task = self.get_task(task_id, user_id)

        if not parent_task.is_recurring:
            raise ValidationError("task", "Task is not recurring")

        # Get all child tasks (occurrences)
        statement = select(Task).where(
            Task.parent_task_id == task_id,
            Task.user_id == user_id,
        ).order_by(Task.due_date.asc())

        occurrences = list(self.session.exec(statement).all())

        # Get next occurrence date from pattern
        next_occurrence_date = None
        if parent_task.recurrence_id:
            pattern = self.recurring_service.get_pattern(parent_task.recurrence_id)
            if pattern:
                next_occurrence_date = pattern.next_occurrence_date

        return {
            "parent_task": {
                "id": str(parent_task.id),
                "title": parent_task.title,
                "is_recurring": parent_task.is_recurring,
            },
            "occurrences": [
                {
                    "id": str(occ.id),
                    "due_date": occ.due_date.isoformat() if occ.due_date else None,
                    "completed": occ.completed,
                    "completed_at": occ.updated_at.isoformat() if occ.completed else None,
                }
                for occ in occurrences
            ],
            "total": len(occurrences),
            "next_occurrence_date": next_occurrence_date.isoformat() if next_occurrence_date else None,
        }

    def stop_recurrence(
        self,
        task_id: UUID,
        user_id: str,
        delete_future: bool = True,
        delete_all: bool = False,
    ) -> Dict[str, Any]:
        """Stop recurrence for a recurring task.

        Args:
            task_id: Task ID
            user_id: User ID
            delete_future: Delete all future occurrences
            delete_all: Delete all occurrences including completed

        Returns:
            Dict with deletion info
        """
        task = self.get_task(task_id, user_id)

        if not task.is_recurring:
            raise ValidationError("task", "Task is not recurring")

        deleted_count = 0

        if delete_all:
            # Delete all child tasks
            statement = select(Task).where(
                Task.parent_task_id == task_id,
                Task.user_id == user_id,
            )
            child_tasks = list(self.session.exec(statement).all())
            for child in child_tasks:
                self.session.delete(child)
                deleted_count += 1
        elif delete_future:
            # Delete only incomplete child tasks
            statement = select(Task).where(
                Task.parent_task_id == task_id,
                Task.user_id == user_id,
                Task.completed == False,  # noqa: E712
            )
            child_tasks = list(self.session.exec(statement).all())
            for child in child_tasks:
                self.session.delete(child)
                deleted_count += 1

        # Update parent task to stop recurrence
        task.is_recurring = False

        # Delete recurring pattern
        if task.recurrence_id:
            self.recurring_service.delete_pattern(task.recurrence_id)
            task.recurrence_id = None

        task.updated_at = datetime.utcnow()

        self.session.add(task)
        self.session.commit()
        self.session.refresh(task)

        return {
            "message": "Recurrence stopped",
            "deleted_count": deleted_count,
            "task": {
                "id": str(task.id),
                "is_recurring": task.is_recurring,
                "recurrence": None,
            },
        }
