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
from src.auth.dependencies import get_current_user


# Test user constants
TEST_USER_ID = "test-user-id-12345"
TEST_USER_EMAIL = "test@example.com"
TEST_USER_NAME = "Test User"

TEST_USER_2_ID = "test-user-2-id-67890"
TEST_USER_2_EMAIL = "test2@example.com"
TEST_USER_2_NAME = "Test User 2"


@pytest.fixture(name="mock_user")
def mock_user_fixture() -> dict:
    """Return a mock user dictionary."""
    return {
        "id": TEST_USER_ID,
        "email": TEST_USER_EMAIL,
        "name": TEST_USER_NAME,
    }


@pytest.fixture(name="mock_user_2")
def mock_user_2_fixture() -> dict:
    """Return a second mock user dictionary for isolation tests."""
    return {
        "id": TEST_USER_2_ID,
        "email": TEST_USER_2_EMAIL,
        "name": TEST_USER_2_NAME,
    }


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
    """Create a sample task for the default test user."""
    task = Task(
        user_id=TEST_USER_ID,
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
    """Create multiple tasks for the default test user."""
    tasks = [
        Task(
            user_id=TEST_USER_ID,
            title="High Priority Task",
            description="Urgent",
            priority=Priority.HIGH,
            completed=False,
        ),
        Task(
            user_id=TEST_USER_ID,
            title="Medium Priority Task",
            description="Normal",
            priority=Priority.MEDIUM,
            category_id=sample_category.id,
            completed=False,
        ),
        Task(
            user_id=TEST_USER_ID,
            title="Low Priority Task",
            description="Not urgent",
            priority=Priority.LOW,
            completed=True,
        ),
        Task(
            user_id=TEST_USER_ID,
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
def client_fixture(engine, mock_user) -> Generator[TestClient, None, None]:
    """Create a test client with test database and mocked auth."""
    from src.database import get_session

    def get_test_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    async def get_mock_user():
        return mock_user

    app.dependency_overrides[get_session] = get_test_session
    app.dependency_overrides[get_current_user] = get_mock_user
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="client_user_2")
def client_user_2_fixture(engine, mock_user_2) -> Generator[TestClient, None, None]:
    """Create a test client with test database as second user."""
    from src.database import get_session

    def get_test_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    async def get_mock_user_2():
        return mock_user_2

    app.dependency_overrides[get_session] = get_test_session
    app.dependency_overrides[get_current_user] = get_mock_user_2
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture(name="unauthenticated_client")
def unauthenticated_client_fixture(engine) -> Generator[TestClient, None, None]:
    """Create a test client without authentication."""
    from src.database import get_session

    def get_test_session() -> Generator[Session, None, None]:
        with Session(engine) as session:
            yield session

    app.dependency_overrides[get_session] = get_test_session
    # Don't override get_current_user - will require real auth
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
