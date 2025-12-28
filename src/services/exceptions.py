"""Custom exceptions for Todo App."""


class TaskNotFoundError(Exception):
    """Raised when a task with the specified ID is not found."""

    def __init__(self, task_id: int) -> None:
        self.task_id = task_id
        super().__init__(f"Task with ID {task_id} not found.")


class ValidationError(Exception):
    """Raised when input validation fails."""

    def __init__(self, message: str) -> None:
        self.message = message
        super().__init__(message)
