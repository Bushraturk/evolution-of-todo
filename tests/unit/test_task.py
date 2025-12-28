"""Unit tests for Task model."""

import pytest
from datetime import datetime

from src.models.task import Task, validate_title, validate_description, MAX_TITLE_LENGTH
from src.services.exceptions import ValidationError


class TestTaskCreation:
    """Tests for Task creation and initialization."""

    def test_create_task_with_all_fields(self) -> None:
        """Test creating a task with all fields specified."""
        task = Task(
            id=1,
            title="Buy groceries",
            description="Milk, eggs, bread",
        )

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.completed is False
        assert isinstance(task.created_at, datetime)

    def test_create_task_with_minimal_fields(self) -> None:
        """Test creating a task with only required fields."""
        task = Task(id=1, title="Simple task")

        assert task.id == 1
        assert task.title == "Simple task"
        assert task.description == ""
        assert task.completed is False

    def test_task_strips_whitespace_from_title(self) -> None:
        """Test that title is stripped of whitespace."""
        task = Task(id=1, title="  Padded title  ")

        assert task.title == "Padded title"

    def test_task_strips_whitespace_from_description(self) -> None:
        """Test that description is stripped of whitespace."""
        task = Task(id=1, title="Task", description="  Padded description  ")

        assert task.description == "Padded description"


class TestTaskValidation:
    """Tests for Task validation."""

    def test_empty_title_raises_validation_error(self) -> None:
        """Test that empty title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Task(id=1, title="")

        assert "Task title is required" in str(exc_info.value)

    def test_whitespace_only_title_raises_validation_error(self) -> None:
        """Test that whitespace-only title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            Task(id=1, title="   ")

        assert "Task title is required" in str(exc_info.value)

    def test_none_title_raises_validation_error(self) -> None:
        """Test that None title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            validate_title(None)

        assert "Task title is required" in str(exc_info.value)

    def test_title_exceeding_max_length_raises_error(self) -> None:
        """Test that title exceeding max length raises ValidationError."""
        long_title = "a" * (MAX_TITLE_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            Task(id=1, title=long_title)

        assert f"{MAX_TITLE_LENGTH} characters" in str(exc_info.value)

    def test_title_at_max_length_is_valid(self) -> None:
        """Test that title at exactly max length is valid."""
        max_title = "a" * MAX_TITLE_LENGTH
        task = Task(id=1, title=max_title)

        assert len(task.title) == MAX_TITLE_LENGTH


class TestTaskCompletion:
    """Tests for Task completion methods."""

    def test_mark_complete(self, sample_task: Task) -> None:
        """Test marking a task as complete."""
        assert sample_task.completed is False

        sample_task.mark_complete()

        assert sample_task.completed is True

    def test_mark_incomplete(self, completed_task: Task) -> None:
        """Test marking a task as incomplete."""
        assert completed_task.completed is True

        completed_task.mark_incomplete()

        assert completed_task.completed is False

    def test_toggle_complete_from_incomplete(self, sample_task: Task) -> None:
        """Test toggling completion from incomplete to complete."""
        assert sample_task.completed is False

        sample_task.toggle_complete()

        assert sample_task.completed is True

    def test_toggle_complete_from_complete(self, completed_task: Task) -> None:
        """Test toggling completion from complete to incomplete."""
        assert completed_task.completed is True

        completed_task.toggle_complete()

        assert completed_task.completed is False


class TestTaskStatusIndicator:
    """Tests for Task status indicator property."""

    def test_status_indicator_incomplete(self, sample_task: Task) -> None:
        """Test status indicator for incomplete task."""
        assert sample_task.status_indicator == "[ ]"

    def test_status_indicator_complete(self, completed_task: Task) -> None:
        """Test status indicator for completed task."""
        assert completed_task.status_indicator == "[x]"


class TestValidateFunctions:
    """Tests for standalone validation functions."""

    def test_validate_description_none_returns_empty(self) -> None:
        """Test that None description returns empty string."""
        result = validate_description(None)

        assert result == ""

    def test_validate_description_empty_returns_empty(self) -> None:
        """Test that empty description returns empty string."""
        result = validate_description("")

        assert result == ""

    def test_validate_description_strips_whitespace(self) -> None:
        """Test that description is stripped of whitespace."""
        result = validate_description("  Test  ")

        assert result == "Test"
