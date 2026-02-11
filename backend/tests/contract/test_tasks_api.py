"""Contract tests for POST /tasks with recurrence."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime

from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    # In real tests, this would use a valid JWT token
    return {"Authorization": "Bearer test_token"}


class TestTasksAPIContract:
    """Contract tests for tasks API with recurrence support."""

    def test_create_task_with_daily_recurrence(self, client: TestClient, auth_headers: dict):
        """Test creating a task with daily recurrence."""
        payload = {
            "title": "Daily standup",
            "description": "Team sync meeting",
            "priority": "high",
            "due_date": "2026-02-12T09:00:00Z",
            "recurrence": {
                "frequency": "DAILY",
                "interval": 1,
            },
        }

        response = client.post("/api/tasks", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["title"] == "Daily standup"
        assert data["data"]["is_recurring"] is True
        assert data["data"]["recurrence_id"] is not None
        assert data["message"] == "Task created successfully"

    def test_create_task_with_weekly_recurrence(self, client: TestClient, auth_headers: dict):
        """Test creating a task with weekly recurrence."""
        payload = {
            "title": "Weekly review",
            "priority": "medium",
            "due_date": "2026-02-16T14:00:00Z",
            "recurrence": {
                "frequency": "WEEKLY",
                "interval": 1,
                "day_of_week": 1,  # Monday
            },
        }

        response = client.post("/api/tasks", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["is_recurring"] is True

    def test_create_task_with_monthly_recurrence(self, client: TestClient, auth_headers: dict):
        """Test creating a task with monthly recurrence."""
        payload = {
            "title": "Monthly report",
            "priority": "high",
            "due_date": "2026-02-15T17:00:00Z",
            "recurrence": {
                "frequency": "MONTHLY",
                "interval": 1,
                "day_of_month": 15,
            },
        }

        response = client.post("/api/tasks", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["is_recurring"] is True

    def test_create_task_with_recurrence_end_date(self, client: TestClient, auth_headers: dict):
        """Test creating a recurring task with end date."""
        payload = {
            "title": "Limited recurring task",
            "due_date": "2026-02-12T09:00:00Z",
            "recurrence": {
                "frequency": "DAILY",
                "interval": 1,
                "end_date": "2026-12-31T23:59:59Z",
            },
        }

        response = client.post("/api/tasks", json=payload, headers=auth_headers)

        assert response.status_code == 201

    def test_create_task_without_recurrence(self, client: TestClient, auth_headers: dict):
        """Test creating a non-recurring task."""
        payload = {
            "title": "One-time task",
            "description": "Do this once",
            "priority": "low",
            "due_date": "2026-02-12T09:00:00Z",
        }

        response = client.post("/api/tasks", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["is_recurring"] is False
        assert data["data"]["recurrence_id"] is None

    def test_validation_weekly_requires_day_of_week(self, client: TestClient, auth_headers: dict):
        """Test that weekly recurrence requires day_of_week."""
        payload = {
            "title": "Invalid weekly task",
            "due_date": "2026-02-12T09:00:00Z",
            "recurrence": {
                "frequency": "WEEKLY",
                "interval": 1,
                # Missing day_of_week
            },
        }

        response = client.post("/api/tasks", json=payload, headers=auth_headers)

        assert response.status_code == 400
        assert "day_of_week" in response.json()["detail"].lower()

    def test_validation_monthly_requires_day_of_month(self, client: TestClient, auth_headers: dict):
        """Test that monthly recurrence requires day_of_month."""
        payload = {
            "title": "Invalid monthly task",
            "due_date": "2026-02-12T09:00:00Z",
            "recurrence": {
                "frequency": "MONTHLY",
                "interval": 1,
                # Missing day_of_month
            },
        }

        response = client.post("/api/tasks", json=payload, headers=auth_headers)

        assert response.status_code == 400
        assert "day_of_month" in response.json()["detail"].lower()

    def test_get_task_occurrences(self, client: TestClient, auth_headers: dict):
        """Test getting occurrences of a recurring task."""
        # First create a recurring task
        create_payload = {
            "title": "Daily task",
            "due_date": "2026-02-12T09:00:00Z",
            "recurrence": {
                "frequency": "DAILY",
                "interval": 1,
            },
        }

        create_response = client.post("/api/tasks", json=create_payload, headers=auth_headers)
        task_id = create_response.json()["data"]["id"]

        # Get occurrences
        response = client.get(f"/api/tasks/{task_id}/occurrences", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "parent_task" in data
        assert "occurrences" in data
        assert "total" in data
        assert "next_occurrence_date" in data
        assert data["parent_task"]["is_recurring"] is True

    def test_stop_recurrence(self, client: TestClient, auth_headers: dict):
        """Test stopping recurrence for a recurring task."""
        # First create a recurring task
        create_payload = {
            "title": "Daily task",
            "due_date": "2026-02-12T09:00:00Z",
            "recurrence": {
                "frequency": "DAILY",
                "interval": 1,
            },
        }

        create_response = client.post("/api/tasks", json=create_payload, headers=auth_headers)
        task_id = create_response.json()["data"]["id"]

        # Stop recurrence
        response = client.delete(
            f"/api/tasks/{task_id}/recurrence",
            params={"delete_future": True},
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Recurrence stopped"
        assert data["task"]["is_recurring"] is False
        assert data["task"]["recurrence"] is None

    def test_response_schema_includes_recurrence_fields(self, client: TestClient, auth_headers: dict):
        """Test that response schema includes all recurrence fields."""
        payload = {
            "title": "Test task",
            "due_date": "2026-02-12T09:00:00Z",
            "recurrence": {
                "frequency": "DAILY",
                "interval": 1,
            },
        }

        response = client.post("/api/tasks", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()["data"]

        # Verify all expected fields are present
        assert "id" in data
        assert "title" in data
        assert "description" in data
        assert "completed" in data
        assert "priority" in data
        assert "due_date" in data
        assert "is_recurring" in data
        assert "recurrence_id" in data
        assert "parent_task_id" in data
        assert "created_at" in data
        assert "updated_at" in data

    def test_validation_title_required(self, client: TestClient, auth_headers: dict):
        """Test that title is required."""
        payload = {
            "description": "No title",
            "recurrence": {
                "frequency": "DAILY",
                "interval": 1,
            },
        }

        response = client.post("/api/tasks", json=payload, headers=auth_headers)

        assert response.status_code == 422  # Validation error

    def test_validation_title_max_length(self, client: TestClient, auth_headers: dict):
        """Test that title has max length of 200 characters."""
        payload = {
            "title": "x" * 201,  # 201 characters
            "recurrence": {
                "frequency": "DAILY",
                "interval": 1,
            },
        }

        response = client.post("/api/tasks", json=payload, headers=auth_headers)

        assert response.status_code == 400
