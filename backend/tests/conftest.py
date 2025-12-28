"""Pytest configuration and fixtures."""

from typing import Generator
from uuid import uuid4

import pytest
from fastapi.testclient import TestClient
from sqlmodel import Session, SQLModel, create_engine
from sqlmodel.pool import StaticPool

from src.main import app
from src.models.category import Category
from src.models.task import Priority, Task
from src.services.task_service import TaskService


@pytest.fixture(name="engine")
def engine_fixture():
    """Create a test database engine."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    return engine


@pytest.fixture(name="session")
def session_fixture(engine) -> Generator[Session, None, None]:
    """Create a test database session."""
    with Session(engine) as session:
        yield session


@pytest.fixture(name="task_service")
def task_service_fixture(session: Session) -> TaskService:
    """Create a TaskService instance with test session."""
    return TaskService(session)


@pytest.fixture(name="sample_category")
def sample_category_fixture(session: Session) -> Category:
    """Create a sample category."""
    category = Category(name="Work", color="#3B82F6")
    session.add(category)
    session.commit()
    session.refresh(category)
    return category


@pytest.fixture(name="sample_task")
def sample_task_fixture(session: Session, sample_category: Category) -> Task:
    """Create a sample task."""
    task = Task(
        title="Sample Task",
        description="Sample description",
        priority=Priority.MEDIUM,
        category_id=sample_category.id,
    )
    session.add(task)
    session.commit()
    session.refresh(task)
    return task


@pytest.fixture(name="multiple_tasks")
def multiple_tasks_fixture(session: Session, sample_category: Category) -> list[Task]:
    """Create multiple tasks for testing."""
    tasks = [
        Task(
            title="High Priority Task",
            description="Urgent",
            priority=Priority.HIGH,
            completed=False,
        ),
        Task(
            title="Medium Priority Task",
            description="Normal",
            priority=Priority.MEDIUM,
            category_id=sample_category.id,
            completed=False,
        ),
        Task(
            title="Low Priority Task",
            description="Not urgent",
            priority=Priority.LOW,
            completed=True,
        ),
        Task(
            title="Another Task",
            description="Testing search",
            priority=Priority.MEDIUM,
            completed=False,
        ),
    ]
    for task in tasks:
        session.add(task)
    session.commit()
    for task in tasks:
        session.refresh(task)
    return tasks


@pytest.fixture(name="client")
def client_fixture(engine) -> Generator[TestClient, None, None]:
    """Create a test client with test database."""
    from src.database import get_session

    def get_test_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
