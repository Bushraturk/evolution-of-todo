"""Contract tests for reminders API."""

import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta

from main import app


@pytest.fixture
def client():
    """Create a test client."""
    return TestClient(app)


@pytest.fixture
def auth_headers():
    """Mock authentication headers."""
    return {"Authorization": "Bearer test_token"}


class TestRemindersAPIContract:
    """Contract tests for reminders API."""

    def test_create_reminder_for_task(self, client: TestClient, auth_headers: dict):
        """Test creating a reminder for a task."""
        # First create a task with due date
        task_payload = {
            "title": "Task with reminder",
            "description": "Test task",
            "priority": "high",
            "due_date": (datetime.utcnow() + timedelta(hours=2)).isoformat() + "Z",
        }

        task_response = client.post("/api/tasks", json=task_payload, headers=auth_headers)
        assert task_response.status_code == 201
        task_id = task_response.json()["data"]["id"]

        # Create reminder
        reminder_payload = {
            "offset_minutes": 30,
            "channel": "EMAIL",
        }

        response = client.post(
            f"/api/tasks/{task_id}/reminders",
            json=reminder_payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert "id" in data
        assert "task_id" in data
        assert data["task_id"] == task_id
        assert "remind_at" in data
        assert data["offset_minutes"] == 30
        assert data["channel"] == "EMAIL"
        assert data["status"] == "PENDING"

    def test_create_reminder_with_push_channel(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating a reminder with push notification channel."""
        # Create task with due date
        task_payload = {
            "title": "Task with push reminder",
            "priority": "medium",
            "due_date": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
        }

        task_response = client.post("/api/tasks", json=task_payload, headers=auth_headers)
        task_id = task_response.json()["data"]["id"]

        # Create reminder with PUSH channel
        reminder_payload = {
            "offset_minutes": 15,
            "channel": "PUSH",
        }

        response = client.post(
            f"/api/tasks/{task_id}/reminders",
            json=reminder_payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["channel"] == "PUSH"

    def test_create_reminder_with_both_channels(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating a reminder with both email and push channels."""
        # Create task with due date
        task_payload = {
            "title": "Task with both channels",
            "priority": "high",
            "due_date": (datetime.utcnow() + timedelta(days=1)).isoformat() + "Z",
        }

        task_response = client.post("/api/tasks", json=task_payload, headers=auth_headers)
        task_id = task_response.json()["data"]["id"]

        # Create reminder with BOTH channels
        reminder_payload = {
            "offset_minutes": 1440,  # 1 day
            "channel": "BOTH",
        }

        response = client.post(
            f"/api/tasks/{task_id}/reminders",
            json=reminder_payload,
            headers=auth_headers,
        )

        assert response.status_code == 201
        data = response.json()
        assert data["channel"] == "BOTH"

    def test_create_reminder_without_due_date_fails(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that creating a reminder for task without due date fails."""
        # Create task WITHOUT due date
        task_payload = {
            "title": "Task without due date",
            "priority": "low",
        }

        task_response = client.post("/api/tasks", json=task_payload, headers=auth_headers)
        task_id = task_response.json()["data"]["id"]

        # Try to create reminder
        reminder_payload = {
            "offset_minutes": 30,
            "channel": "EMAIL",
        }

        response = client.post(
            f"/api/tasks/{task_id}/reminders",
            json=reminder_payload,
            headers=auth_headers,
        )

        assert response.status_code == 400
        assert "due date" in response.json()["detail"].lower()

    def test_create_reminder_for_nonexistent_task(
        self, client: TestClient, auth_headers: dict
    ):
        """Test creating a reminder for a task that doesn't exist."""
        fake_task_id = "00000000-0000-0000-0000-000000000000"

        reminder_payload = {
            "offset_minutes": 30,
            "channel": "EMAIL",
        }

        response = client.post(
            f"/api/tasks/{fake_task_id}/reminders",
            json=reminder_payload,
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_get_task_reminders(self, client: TestClient, auth_headers: dict):
        """Test getting all reminders for a task."""
        # Create task with due date
        task_payload = {
            "title": "Task with multiple reminders",
            "priority": "high",
            "due_date": (datetime.utcnow() + timedelta(hours=3)).isoformat() + "Z",
        }

        task_response = client.post("/api/tasks", json=task_payload, headers=auth_headers)
        task_id = task_response.json()["data"]["id"]

        # Create first reminder
        reminder1_payload = {
            "offset_minutes": 30,
            "channel": "EMAIL",
        }
        client.post(
            f"/api/tasks/{task_id}/reminders",
            json=reminder1_payload,
            headers=auth_headers,
        )

        # Create second reminder
        reminder2_payload = {
            "offset_minutes": 60,
            "channel": "PUSH",
        }
        client.post(
            f"/api/tasks/{task_id}/reminders",
            json=reminder2_payload,
            headers=auth_headers,
        )

        # Get all reminders
        response = client.get(f"/api/tasks/{task_id}/reminders", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "reminders" in data
        assert "total" in data
        assert data["total"] == 2
        assert len(data["reminders"]) == 2

    def test_delete_reminder(self, client: TestClient, auth_headers: dict):
        """Test deleting a reminder."""
        # Create task with due date
        task_payload = {
            "title": "Task with reminder to delete",
            "priority": "medium",
            "due_date": (datetime.utcnow() + timedelta(hours=2)).isoformat() + "Z",
        }

        task_response = client.post("/api/tasks", json=task_payload, headers=auth_headers)
        task_id = task_response.json()["data"]["id"]

        # Create reminder
        reminder_payload = {
            "offset_minutes": 30,
            "channel": "EMAIL",
        }

        reminder_response = client.post(
            f"/api/tasks/{task_id}/reminders",
            json=reminder_payload,
            headers=auth_headers,
        )
        reminder_id = reminder_response.json()["id"]

        # Delete reminder
        response = client.delete(
            f"/api/reminders/{reminder_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204

        # Verify reminder is deleted
        get_response = client.get(
            f"/api/tasks/{task_id}/reminders",
            headers=auth_headers,
        )
        assert get_response.json()["total"] == 0

    def test_delete_nonexistent_reminder(self, client: TestClient, auth_headers: dict):
        """Test deleting a reminder that doesn't exist."""
        fake_reminder_id = "00000000-0000-0000-0000-000000000000"

        response = client.delete(
            f"/api/reminders/{fake_reminder_id}",
            headers=auth_headers,
        )

        assert response.status_code == 404

    def test_validation_offset_minutes_required(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that offset_minutes is required."""
        # Create task with due date
        task_payload = {
            "title": "Task for validation test",
            "due_date": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
        }

        task_response = client.post("/api/tasks", json=task_payload, headers=auth_headers)
        task_id = task_response.json()["data"]["id"]

        # Try to create reminder without offset_minutes
        reminder_payload = {
            "channel": "EMAIL",
        }

        response = client.post(
            f"/api/tasks/{task_id}/reminders",
            json=reminder_payload,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_validation_offset_minutes_positive(
        self, client: TestClient, auth_headers: dict
    ):
        """Test that offset_minutes must be positive."""
        # Create task with due date
        task_payload = {
            "title": "Task for validation test",
            "due_date": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
        }

        task_response = client.post("/api/tasks", json=task_payload, headers=auth_headers)
        task_id = task_response.json()["data"]["id"]

        # Try to create reminder with negative offset
        reminder_payload = {
            "offset_minutes": -30,
            "channel": "EMAIL",
        }

        response = client.post(
            f"/api/tasks/{task_id}/reminders",
            json=reminder_payload,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_validation_channel_required(self, client: TestClient, auth_headers: dict):
        """Test that channel is required."""
        # Create task with due date
        task_payload = {
            "title": "Task for validation test",
            "due_date": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
        }

        task_response = client.post("/api/tasks", json=task_payload, headers=auth_headers)
        task_id = task_response.json()["data"]["id"]

        # Try to create reminder without channel
        reminder_payload = {
            "offset_minutes": 30,
        }

        response = client.post(
            f"/api/tasks/{task_id}/reminders",
            json=reminder_payload,
            headers=auth_headers,
        )

        assert response.status_code == 422

    def test_validation_invalid_channel(self, client: TestClient, auth_headers: dict):
        """Test that invalid channel values are rejected."""
        # Create task with due date
        task_payload = {
            "title": "Task for validation test",
            "due_date": (datetime.utcnow() + timedelta(hours=1)).isoformat() + "Z",
        }

        task_response = client.post("/api/tasks", json=task_payload, headers=auth_headers)
        task_id = task_response.json()["data"]["id"]

        # Try to create reminder with invalid channel
        reminder_payload = {
            "offset_minutes": 30,
            "channel": "INVALID",
        }

        response = client.post(
            f"/api/tasks/{task_id}/reminders",
            json=reminder_payload,
            headers=auth_headers,
        )

        assert response.status_code == 422
