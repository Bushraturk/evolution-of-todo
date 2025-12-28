"""Task service for managing todo tasks."""

from datetime import datetime

from src.models.task import Task, validate_title, validate_description
from src.services.exceptions import TaskNotFoundError, ValidationError


class TaskService:
    """Service class for managing tasks with in-memory storage.

    Provides CRUD operations for tasks with auto-incrementing IDs.
    """

    def __init__(self) -> None:
        """Initialize the task service with empty storage."""
        self._tasks: dict[int, Task] = {}
        self._next_id: int = 1

    def add_task(self, title: str, description: str = "") -> Task:
        """Add a new task to the list.

        Args:
            title: The task title (required, max 200 chars).
            description: The task description (optional).

        Returns:
            The created Task object.

        Raises:
            ValidationError: If title is empty or too long.
        """
        # Validate inputs
        validated_title = validate_title(title)
        validated_description = validate_description(description)

        # Create task with auto-generated ID
        task = Task(
            id=self._next_id,
            title=validated_title,
            description=validated_description,
            completed=False,
            created_at=datetime.now(),
        )

        # Store and increment counter
        self._tasks[self._next_id] = task
        self._next_id += 1

        return task

    def get_all_tasks(self) -> list[Task]:
        """Get all tasks in the list.

        Returns:
            List of all tasks, ordered by ID.
        """
        return list(self._tasks.values())

    def get_task(self, task_id: int) -> Task:
        """Get a task by its ID.

        Args:
            task_id: The ID of the task to retrieve.

        Returns:
            The Task object.

        Raises:
            TaskNotFoundError: If no task with the given ID exists.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)
        return self._tasks[task_id]

    def update_task(
        self,
        task_id: int,
        title: str | None = None,
        description: str | None = None,
    ) -> Task:
        """Update an existing task.

        Args:
            task_id: The ID of the task to update.
            title: New title (optional, pass None to keep current).
            description: New description (optional, pass None to keep current).

        Returns:
            The updated Task object.

        Raises:
            TaskNotFoundError: If no task with the given ID exists.
            ValidationError: If title is empty, too long, or no changes provided.
        """
        # Check if task exists
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        # Check if any updates provided
        if title is None and description is None:
            raise ValidationError("No updates provided. Use --title or --description.")

        task = self._tasks[task_id]

        # Validate and update title if provided
        if title is not None:
            if title.strip() == "":
                raise ValidationError("Task title cannot be empty.")
            task.title = validate_title(title)

        # Validate and update description if provided
        if description is not None:
            task.description = validate_description(description)

        return task

    def delete_task(self, task_id: int) -> Task:
        """Delete a task by its ID.

        Args:
            task_id: The ID of the task to delete.

        Returns:
            The deleted Task object (for confirmation display).

        Raises:
            TaskNotFoundError: If no task with the given ID exists.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        task = self._tasks.pop(task_id)
        return task

    def toggle_complete(self, task_id: int) -> Task:
        """Toggle the completion status of a task.

        Args:
            task_id: The ID of the task to toggle.

        Returns:
            The updated Task object.

        Raises:
            TaskNotFoundError: If no task with the given ID exists.
        """
        if task_id not in self._tasks:
            raise TaskNotFoundError(task_id)

        task = self._tasks[task_id]
        task.toggle_complete()
        return task

    @property
    def task_count(self) -> int:
        """Return the total number of tasks."""
        return len(self._tasks)

    @property
    def completed_count(self) -> int:
        """Return the number of completed tasks."""
        return sum(1 for task in self._tasks.values() if task.completed)

    @property
    def pending_count(self) -> int:
        """Return the number of pending (incomplete) tasks."""
        return self.task_count - self.completed_count
