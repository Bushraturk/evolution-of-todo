"""Unit tests for TaskService."""

import pytest

from src.services.task_service import TaskService
from src.services.exceptions import TaskNotFoundError, ValidationError
from src.models.task import MAX_TITLE_LENGTH


class TestAddTask:
    """Tests for TaskService.add_task method."""

    def test_add_task_with_title_and_description(self, task_service: TaskService) -> None:
        """Test adding a task with both title and description."""
        task = task_service.add_task("Buy groceries", "Milk, eggs, bread")

        assert task.id == 1
        assert task.title == "Buy groceries"
        assert task.description == "Milk, eggs, bread"
        assert task.completed is False

    def test_add_task_with_title_only(self, task_service: TaskService) -> None:
        """Test adding a task with only title."""
        task = task_service.add_task("Call mom")

        assert task.id == 1
        assert task.title == "Call mom"
        assert task.description == ""

    def test_add_multiple_tasks_increments_id(self, task_service: TaskService) -> None:
        """Test that adding multiple tasks increments IDs correctly."""
        task1 = task_service.add_task("Task 1")
        task2 = task_service.add_task("Task 2")
        task3 = task_service.add_task("Task 3")

        assert task1.id == 1
        assert task2.id == 2
        assert task3.id == 3

    def test_add_task_empty_title_raises_error(self, task_service: TaskService) -> None:
        """Test that adding task with empty title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            task_service.add_task("")

        assert "Task title is required" in str(exc_info.value)

    def test_add_task_whitespace_title_raises_error(self, task_service: TaskService) -> None:
        """Test that adding task with whitespace-only title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            task_service.add_task("   ")

        assert "Task title is required" in str(exc_info.value)

    def test_add_task_title_too_long_raises_error(self, task_service: TaskService) -> None:
        """Test that adding task with too long title raises ValidationError."""
        long_title = "a" * (MAX_TITLE_LENGTH + 1)

        with pytest.raises(ValidationError) as exc_info:
            task_service.add_task(long_title)

        assert f"{MAX_TITLE_LENGTH} characters" in str(exc_info.value)


class TestGetAllTasks:
    """Tests for TaskService.get_all_tasks method."""

    def test_get_all_tasks_empty(self, task_service: TaskService) -> None:
        """Test getting all tasks from empty list."""
        tasks = task_service.get_all_tasks()

        assert tasks == []

    def test_get_all_tasks_returns_all(self, task_service_with_tasks: TaskService) -> None:
        """Test getting all tasks returns all added tasks."""
        tasks = task_service_with_tasks.get_all_tasks()

        assert len(tasks) == 3
        assert tasks[0].title == "Buy groceries"
        assert tasks[1].title == "Call mom"
        assert tasks[2].title == "Write report"


class TestGetTask:
    """Tests for TaskService.get_task method."""

    def test_get_task_by_id(self, task_service_with_tasks: TaskService) -> None:
        """Test getting a task by its ID."""
        task = task_service_with_tasks.get_task(2)

        assert task.id == 2
        assert task.title == "Call mom"

    def test_get_task_not_found_raises_error(self, task_service: TaskService) -> None:
        """Test that getting non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_service.get_task(99)

        assert "Task with ID 99 not found" in str(exc_info.value)


class TestToggleComplete:
    """Tests for TaskService.toggle_complete method."""

    def test_toggle_complete_from_incomplete(self, task_service_with_tasks: TaskService) -> None:
        """Test toggling task from incomplete to complete."""
        task = task_service_with_tasks.toggle_complete(1)

        assert task.completed is True

    def test_toggle_complete_from_complete(self, task_service_with_tasks: TaskService) -> None:
        """Test toggling task from complete to incomplete."""
        # First toggle to complete
        task_service_with_tasks.toggle_complete(1)
        # Then toggle back to incomplete
        task = task_service_with_tasks.toggle_complete(1)

        assert task.completed is False

    def test_toggle_complete_not_found_raises_error(self, task_service: TaskService) -> None:
        """Test that toggling non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_service.toggle_complete(99)

        assert "Task with ID 99 not found" in str(exc_info.value)


class TestUpdateTask:
    """Tests for TaskService.update_task method."""

    def test_update_task_title(self, task_service_with_tasks: TaskService) -> None:
        """Test updating task title."""
        task = task_service_with_tasks.update_task(1, title="Buy organic groceries")

        assert task.title == "Buy organic groceries"
        assert task.description == "Milk, eggs, bread"  # Unchanged

    def test_update_task_description(self, task_service_with_tasks: TaskService) -> None:
        """Test updating task description."""
        task = task_service_with_tasks.update_task(1, description="Include vegetables")

        assert task.title == "Buy groceries"  # Unchanged
        assert task.description == "Include vegetables"

    def test_update_task_both_fields(self, task_service_with_tasks: TaskService) -> None:
        """Test updating both title and description."""
        task = task_service_with_tasks.update_task(
            1,
            title="New Title",
            description="New Description",
        )

        assert task.title == "New Title"
        assert task.description == "New Description"

    def test_update_task_not_found_raises_error(self, task_service: TaskService) -> None:
        """Test that updating non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_service.update_task(99, title="New Title")

        assert "Task with ID 99 not found" in str(exc_info.value)

    def test_update_task_empty_title_raises_error(self, task_service_with_tasks: TaskService) -> None:
        """Test that updating with empty title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            task_service_with_tasks.update_task(1, title="")

        assert "Task title cannot be empty" in str(exc_info.value)

    def test_update_task_no_changes_raises_error(self, task_service_with_tasks: TaskService) -> None:
        """Test that updating with no changes raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            task_service_with_tasks.update_task(1)

        assert "No updates provided" in str(exc_info.value)


class TestDeleteTask:
    """Tests for TaskService.delete_task method."""

    def test_delete_task(self, task_service_with_tasks: TaskService) -> None:
        """Test deleting a task."""
        deleted_task = task_service_with_tasks.delete_task(1)

        assert deleted_task.id == 1
        assert deleted_task.title == "Buy groceries"

        # Verify task is actually deleted
        with pytest.raises(TaskNotFoundError):
            task_service_with_tasks.get_task(1)

    def test_delete_task_not_found_raises_error(self, task_service: TaskService) -> None:
        """Test that deleting non-existent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError) as exc_info:
            task_service.delete_task(99)

        assert "Task with ID 99 not found" in str(exc_info.value)

    def test_delete_task_reduces_count(self, task_service_with_tasks: TaskService) -> None:
        """Test that deleting a task reduces the task count."""
        assert task_service_with_tasks.task_count == 3

        task_service_with_tasks.delete_task(1)

        assert task_service_with_tasks.task_count == 2


class TestTaskCounts:
    """Tests for TaskService count properties."""

    def test_task_count(self, task_service_with_tasks: TaskService) -> None:
        """Test task count property."""
        assert task_service_with_tasks.task_count == 3

    def test_completed_count(self, task_service_with_tasks: TaskService) -> None:
        """Test completed count property."""
        task_service_with_tasks.toggle_complete(1)
        task_service_with_tasks.toggle_complete(2)

        assert task_service_with_tasks.completed_count == 2

    def test_pending_count(self, task_service_with_tasks: TaskService) -> None:
        """Test pending count property."""
        task_service_with_tasks.toggle_complete(1)

        assert task_service_with_tasks.pending_count == 2
