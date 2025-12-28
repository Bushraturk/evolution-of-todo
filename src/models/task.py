"""Task model for Todo App."""

from dataclasses import dataclass, field
from datetime import datetime

from src.services.exceptions import ValidationError


MAX_TITLE_LENGTH = 200
MAX_DESCRIPTION_LENGTH = 1000


def validate_title(title: str) -> str:
    """Validate and normalize task title.

    Args:
        title: The title to validate.

    Returns:
        The stripped title.

    Raises:
        ValidationError: If title is empty or too long.
    """
    if title is None:
        raise ValidationError("Task title is required.")

    stripped = title.strip()

    if not stripped:
        raise ValidationError("Task title is required.")

    if len(stripped) > MAX_TITLE_LENGTH:
        raise ValidationError(f"Task title must be {MAX_TITLE_LENGTH} characters or less.")

    return stripped


def validate_description(description: str | None) -> str:
    """Validate and normalize task description.

    Args:
        description: The description to validate.

    Returns:
        The stripped description or empty string.
    """
    if description is None:
        return ""

    stripped = description.strip()

    if len(stripped) > MAX_DESCRIPTION_LENGTH:
        return stripped[:MAX_DESCRIPTION_LENGTH]

    return stripped


@dataclass
class Task:
    """Represents a single todo item.

    Attributes:
        id: Unique numeric identifier (auto-generated, read-only).
        title: Brief description of what needs to be done (required, max 200 chars).
        description: Detailed information about the task (optional).
        completed: Whether the task is done (defaults to False).
        created_at: Timestamp when task was created (auto-generated).
    """

    id: int
    title: str
    description: str = ""
    completed: bool = False
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self) -> None:
        """Validate fields after initialization."""
        self.title = validate_title(self.title)
        self.description = validate_description(self.description)

    def mark_complete(self) -> None:
        """Mark the task as completed."""
        self.completed = True

    def mark_incomplete(self) -> None:
        """Mark the task as incomplete."""
        self.completed = False

    def toggle_complete(self) -> None:
        """Toggle the completion status of the task."""
        self.completed = not self.completed

    @property
    def status_indicator(self) -> str:
        """Return visual status indicator for display."""
        return "[x]" if self.completed else "[ ]"
