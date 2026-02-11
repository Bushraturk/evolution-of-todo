"""Integration tests for advanced task filtering."""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4

from sqlmodel import Session

from models.task import Task, Priority
from services.task_service import TaskService
from services.tag_service import TagService


@pytest.fixture
def task_service(session: Session) -> TaskService:
    """Create TaskService instance."""
    return TaskService(session)


@pytest.fixture
def tag_service(session: Session) -> TagService:
    """Create TagService instance."""
    return TagService(session)


class TestAdvancedFiltering:
    """Test advanced task filtering functionality."""

    def test_filter_by_search_title(
        self, session: Session, task_service: TaskService
    ):
        """Test filtering tasks by search term in title."""
        user_id = "test_user_123"

        # Create tasks
        task_service.create_task(user_id=user_id, title="Buy groceries", priority=Priority.MEDIUM)
        task_service.create_task(user_id=user_id, title="Call dentist", priority=Priority.HIGH)
        task_service.create_task(user_id=user_id, title="Buy birthday gift", priority=Priority.LOW)

        # Search for "buy"
        results = task_service.get_all_tasks(user_id=user_id, search="buy")

        assert len(results) == 2
        titles = {task.title for task in results}
        assert "Buy groceries" in titles
        assert "Buy birthday gift" in titles

    def test_filter_by_search_description(
        self, session: Session, task_service: TaskService
    ):
        """Test filtering tasks by search term in description."""
        user_id = "test_user_123"

        task_service.create_task(
            user_id=user_id,
            title="Task 1",
            description="Important meeting with client",
            priority=Priority.HIGH,
        )
        task_service.create_task(
            user_id=user_id,
            title="Task 2",
            description="Review code changes",
            priority=Priority.MEDIUM,
        )

        # Search for "meeting"
        results = task_service.get_all_tasks(user_id=user_id, search="meeting")

        assert len(results) == 1
        assert results[0].title == "Task 1"

    def test_filter_by_status_completed(
        self, session: Session, task_service: TaskService
    ):
        """Test filtering tasks by completed status."""
        user_id = "test_user_123"

        task1 = task_service.create_task(user_id=user_id, title="Task 1", priority=Priority.MEDIUM)
        task2 = task_service.create_task(user_id=user_id, title="Task 2", priority=Priority.HIGH)

        # Complete task1
        task_service.toggle_complete(task1.id, user_id)

        # Filter by completed
        results = task_service.get_all_tasks(user_id=user_id, status="completed")

        assert len(results) == 1
        assert results[0].id == task1.id

    def test_filter_by_status_incomplete(
        self, session: Session, task_service: TaskService
    ):
        """Test filtering tasks by incomplete status."""
        user_id = "test_user_123"

        task1 = task_service.create_task(user_id=user_id, title="Task 1", priority=Priority.MEDIUM)
        task2 = task_service.create_task(user_id=user_id, title="Task 2", priority=Priority.HIGH)

        # Complete task1
        task_service.toggle_complete(task1.id, user_id)

        # Filter by incomplete
        results = task_service.get_all_tasks(user_id=user_id, status="incomplete")

        assert len(results) == 1
        assert results[0].id == task2.id

    def test_filter_by_priority(self, session: Session, task_service: TaskService):
        """Test filtering tasks by priority."""
        user_id = "test_user_123"

        task_service.create_task(user_id=user_id, title="High priority", priority=Priority.HIGH)
        task_service.create_task(user_id=user_id, title="Medium priority", priority=Priority.MEDIUM)
        task_service.create_task(user_id=user_id, title="Low priority", priority=Priority.LOW)

        # Filter by high priority
        results = task_service.get_all_tasks(user_id=user_id, priority=Priority.HIGH)

        assert len(results) == 1
        assert results[0].title == "High priority"

    def test_filter_by_category(self, session: Session, task_service: TaskService):
        """Test filtering tasks by category."""
        from models.category import Category

        user_id = "test_user_123"

        # Create categories
        work_category = Category(id=uuid4(), user_id=user_id, name="Work", color="#000000")
        personal_category = Category(id=uuid4(), user_id=user_id, name="Personal", color="#ffffff")
        session.add_all([work_category, personal_category])
        session.commit()

        # Create tasks
        task_service.create_task(
            user_id=user_id,
            title="Work task",
            priority=Priority.MEDIUM,
            category_id=work_category.id,
        )
        task_service.create_task(
            user_id=user_id,
            title="Personal task",
            priority=Priority.LOW,
            category_id=personal_category.id,
        )

        # Filter by work category
        results = task_service.get_all_tasks(user_id=user_id, category_id=work_category.id)

        assert len(results) == 1
        assert results[0].title == "Work task"

    def test_sort_by_created_at_desc(
        self, session: Session, task_service: TaskService
    ):
        """Test sorting tasks by created_at descending."""
        user_id = "test_user_123"

        task1 = task_service.create_task(user_id=user_id, title="First", priority=Priority.MEDIUM)
        task2 = task_service.create_task(user_id=user_id, title="Second", priority=Priority.MEDIUM)
        task3 = task_service.create_task(user_id=user_id, title="Third", priority=Priority.MEDIUM)

        # Get tasks sorted by created_at desc (default)
        results = task_service.get_all_tasks(
            user_id=user_id,
            sort_by="created_at",
            sort_order="desc",
        )

        assert len(results) == 3
        assert results[0].title == "Third"
        assert results[1].title == "Second"
        assert results[2].title == "First"

    def test_sort_by_priority(self, session: Session, task_service: TaskService):
        """Test sorting tasks by priority."""
        user_id = "test_user_123"

        task_service.create_task(user_id=user_id, title="Low", priority=Priority.LOW)
        task_service.create_task(user_id=user_id, title="High", priority=Priority.HIGH)
        task_service.create_task(user_id=user_id, title="Medium", priority=Priority.MEDIUM)

        # Get tasks sorted by priority
        results = task_service.get_all_tasks(
            user_id=user_id,
            sort_by="priority",
            sort_order="desc",
        )

        assert len(results) == 3
        # Priority order: high > medium > low
        assert results[0].priority == Priority.HIGH
        assert results[1].priority == Priority.MEDIUM
        assert results[2].priority == Priority.LOW

    def test_sort_by_title(self, session: Session, task_service: TaskService):
        """Test sorting tasks by title."""
        user_id = "test_user_123"

        task_service.create_task(user_id=user_id, title="Zebra", priority=Priority.MEDIUM)
        task_service.create_task(user_id=user_id, title="Apple", priority=Priority.MEDIUM)
        task_service.create_task(user_id=user_id, title="Mango", priority=Priority.MEDIUM)

        # Get tasks sorted by title ascending
        results = task_service.get_all_tasks(
            user_id=user_id,
            sort_by="title",
            sort_order="asc",
        )

        assert len(results) == 3
        assert results[0].title == "Apple"
        assert results[1].title == "Mango"
        assert results[2].title == "Zebra"

    def test_combined_filters(self, session: Session, task_service: TaskService):
        """Test combining multiple filters."""
        user_id = "test_user_123"

        # Create tasks
        task1 = task_service.create_task(
            user_id=user_id,
            title="Important work task",
            description="Urgent",
            priority=Priority.HIGH,
        )
        task2 = task_service.create_task(
            user_id=user_id,
            title="Regular work task",
            priority=Priority.MEDIUM,
        )
        task3 = task_service.create_task(
            user_id=user_id,
            title="Important personal task",
            priority=Priority.HIGH,
        )

        # Complete task3
        task_service.toggle_complete(task3.id, user_id)

        # Filter: search="work", priority=HIGH, status=incomplete
        results = task_service.get_all_tasks(
            user_id=user_id,
            search="work",
            priority=Priority.HIGH,
            status="incomplete",
        )

        assert len(results) == 1
        assert results[0].id == task1.id

    def test_case_insensitive_search(
        self, session: Session, task_service: TaskService
    ):
        """Test that search is case-insensitive."""
        user_id = "test_user_123"

        task_service.create_task(user_id=user_id, title="IMPORTANT TASK", priority=Priority.HIGH)

        # Search with lowercase
        results = task_service.get_all_tasks(user_id=user_id, search="important")

        assert len(results) == 1
        assert results[0].title == "IMPORTANT TASK"

    def test_partial_match_search(self, session: Session, task_service: TaskService):
        """Test that search matches partial strings."""
        user_id = "test_user_123"

        task_service.create_task(user_id=user_id, title="Development task", priority=Priority.MEDIUM)

        # Search with partial match
        results = task_service.get_all_tasks(user_id=user_id, search="dev")

        assert len(results) == 1
        assert results[0].title == "Development task"

    def test_empty_search_returns_all(
        self, session: Session, task_service: TaskService
    ):
        """Test that empty search returns all tasks."""
        user_id = "test_user_123"

        task_service.create_task(user_id=user_id, title="Task 1", priority=Priority.MEDIUM)
        task_service.create_task(user_id=user_id, title="Task 2", priority=Priority.HIGH)

        # Empty search
        results = task_service.get_all_tasks(user_id=user_id, search="")

        assert len(results) == 2

    def test_no_results_for_nonmatching_search(
        self, session: Session, task_service: TaskService
    ):
        """Test that nonmatching search returns empty results."""
        user_id = "test_user_123"

        task_service.create_task(user_id=user_id, title="Task 1", priority=Priority.MEDIUM)

        # Search for nonexistent term
        results = task_service.get_all_tasks(user_id=user_id, search="nonexistent")

        assert len(results) == 0
