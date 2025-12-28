"""Pytest fixtures for Todo App tests."""

import pytest

from src.services.task_service import TaskService
from src.models.task import Task


@pytest.fixture
def task_service() -> TaskService:
    """Provide a fresh TaskService instance for each test."""
    return TaskService()


@pytest.fixture
def task_service_with_tasks(task_service: TaskService) -> TaskService:
    """Provide a TaskService with sample tasks."""
    task_service.add_task("Buy groceries", "Milk, eggs, bread")
    task_service.add_task("Call mom")
    task_service.add_task("Write report", "Q4 sales analysis")
    return task_service


@pytest.fixture
def sample_task() -> Task:
    """Provide a sample Task object."""
    return Task(
        id=1,
        title="Test task",
        description="Test description",
    )


@pytest.fixture
def completed_task() -> Task:
    """Provide a completed Task object."""
    task = Task(
        id=2,
        title="Completed task",
        description="This task is done",
    )
    task.mark_complete()
    return task
