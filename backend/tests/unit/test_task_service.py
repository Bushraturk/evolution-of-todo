"""Unit tests for TaskService."""

import pytest
from uuid import uuid4

from src.models.task import Priority, Task
from src.services.task_service import TaskService, TaskNotFoundError, ValidationError


class TestGetAllTasks:
    """Tests for get_all_tasks method."""

    def test_returns_empty_list_when_no_tasks(self, task_service: TaskService) -> None:
        """Test that empty list is returned when no tasks exist."""
        tasks = task_service.get_all_tasks()
        assert tasks == []

    def test_returns_all_tasks(self, task_service: TaskService, multiple_tasks: list[Task]) -> None:
        """Test that all tasks are returned."""
        tasks = task_service.get_all_tasks()
        assert len(tasks) == 4

    def test_filter_by_completed_status(self, task_service: TaskService, multiple_tasks: list[Task]) -> None:
        """Test filtering by completed status."""
        tasks = task_service.get_all_tasks(status="completed")
        assert len(tasks) == 1
        assert all(t.completed for t in tasks)

    def test_filter_by_incomplete_status(self, task_service: TaskService, multiple_tasks: list[Task]) -> None:
        """Test filtering by incomplete status."""
        tasks = task_service.get_all_tasks(status="incomplete")
        assert len(tasks) == 3
        assert all(not t.completed for t in tasks)

    def test_filter_by_priority(self, task_service: TaskService, multiple_tasks: list[Task]) -> None:
        """Test filtering by priority."""
        tasks = task_service.get_all_tasks(priority=Priority.HIGH)
        assert len(tasks) == 1
        assert tasks[0].priority == Priority.HIGH

    def test_search_by_title(self, task_service: TaskService, multiple_tasks: list[Task]) -> None:
        """Test search by title."""
        tasks = task_service.get_all_tasks(search="High")
        assert len(tasks) == 1
        assert "High" in tasks[0].title

    def test_search_by_description(self, task_service: TaskService, multiple_tasks: list[Task]) -> None:
        """Test search by description."""
        tasks = task_service.get_all_tasks(search="Urgent")
        assert len(tasks) == 1
        assert "Urgent" in tasks[0].description

    def test_sort_by_priority_desc(self, task_service: TaskService, multiple_tasks: list[Task]) -> None:
        """Test sorting by priority descending."""
        tasks = task_service.get_all_tasks(sort_by="priority", sort_order="desc")
        assert tasks[0].priority == Priority.HIGH


class TestCreateTask:
    """Tests for create_task method."""

    def test_creates_task_with_required_fields(self, task_service: TaskService) -> None:
        """Test creating task with only required fields."""
        task = task_service.create_task(title="Test Task")
        assert task.title == "Test Task"
        assert task.description is None
        assert task.priority == Priority.MEDIUM
        assert task.completed is False

    def test_creates_task_with_all_fields(self, task_service: TaskService, sample_category) -> None:
        """Test creating task with all fields."""
        task = task_service.create_task(
            title="Full Task",
            description="Full description",
            priority=Priority.HIGH,
            category_id=sample_category.id,
        )
        assert task.title == "Full Task"
        assert task.description == "Full description"
        assert task.priority == Priority.HIGH
        assert task.category_id == sample_category.id

    def test_raises_error_for_empty_title(self, task_service: TaskService) -> None:
        """Test that empty title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            task_service.create_task(title="")
        assert "title" in str(exc_info.value).lower()

    def test_raises_error_for_whitespace_title(self, task_service: TaskService) -> None:
        """Test that whitespace-only title raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            task_service.create_task(title="   ")
        assert "title" in str(exc_info.value).lower()

    def test_raises_error_for_long_title(self, task_service: TaskService) -> None:
        """Test that title over 200 chars raises ValidationError."""
        with pytest.raises(ValidationError) as exc_info:
            task_service.create_task(title="a" * 201)
        assert "title" in str(exc_info.value).lower()

    def test_strips_whitespace_from_title(self, task_service: TaskService) -> None:
        """Test that title whitespace is stripped."""
        task = task_service.create_task(title="  Test Task  ")
        assert task.title == "Test Task"


class TestToggleComplete:
    """Tests for toggle_complete method."""

    def test_toggles_incomplete_to_complete(self, task_service: TaskService, sample_task: Task) -> None:
        """Test toggling incomplete task to complete."""
        assert not sample_task.completed
        task = task_service.toggle_complete(sample_task.id)
        assert task.completed is True

    def test_toggles_complete_to_incomplete(self, task_service: TaskService, session, sample_task: Task) -> None:
        """Test toggling complete task to incomplete."""
        sample_task.completed = True
        session.add(sample_task)
        session.commit()

        task = task_service.toggle_complete(sample_task.id)
        assert task.completed is False

    def test_raises_error_for_nonexistent_task(self, task_service: TaskService) -> None:
        """Test that toggling nonexistent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_service.toggle_complete(uuid4())


class TestUpdateTask:
    """Tests for update_task method."""

    def test_updates_title(self, task_service: TaskService, sample_task: Task) -> None:
        """Test updating task title."""
        task = task_service.update_task(sample_task.id, title="Updated Title")
        assert task.title == "Updated Title"

    def test_updates_description(self, task_service: TaskService, sample_task: Task) -> None:
        """Test updating task description."""
        task = task_service.update_task(sample_task.id, description="Updated Description")
        assert task.description == "Updated Description"

    def test_updates_priority(self, task_service: TaskService, sample_task: Task) -> None:
        """Test updating task priority."""
        task = task_service.update_task(sample_task.id, priority=Priority.HIGH)
        assert task.priority == Priority.HIGH

    def test_raises_error_for_empty_title(self, task_service: TaskService, sample_task: Task) -> None:
        """Test that empty title raises ValidationError."""
        with pytest.raises(ValidationError):
            task_service.update_task(sample_task.id, title="")

    def test_raises_error_for_nonexistent_task(self, task_service: TaskService) -> None:
        """Test that updating nonexistent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_service.update_task(uuid4(), title="New Title")


class TestDeleteTask:
    """Tests for delete_task method."""

    def test_deletes_task(self, task_service: TaskService, sample_task: Task) -> None:
        """Test deleting a task."""
        deleted = task_service.delete_task(sample_task.id)
        assert deleted.id == sample_task.id

        # Verify task is deleted
        with pytest.raises(TaskNotFoundError):
            task_service.get_task(sample_task.id)

    def test_raises_error_for_nonexistent_task(self, task_service: TaskService) -> None:
        """Test that deleting nonexistent task raises TaskNotFoundError."""
        with pytest.raises(TaskNotFoundError):
            task_service.delete_task(uuid4())
