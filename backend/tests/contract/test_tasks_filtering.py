"""Contract tests for GET /tasks with filters."""

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
    return {"Authorization": "Bearer test_token"}


class TestTasksFilteringContract:
    """Contract tests for tasks API with filtering."""

    def test_get_tasks_with_search_filter(self, client: TestClient, auth_headers: dict):
        """Test GET /tasks with search parameter."""
        # Create tasks
        client.post(
            "/api/tasks",
            json={"title": "Buy groceries", "priority": "medium"},
            headers=auth_headers,
        )
        client.post(
            "/api/tasks",
            json={"title": "Call dentist", "priority": "high"},
            headers=auth_headers,
        )

        # Search for "buy"
        response = client.get("/api/tasks?search=buy", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data
        # Should find at least the "Buy groceries" task
        assert any("buy" in task["title"].lower() for task in data["data"])

    def test_get_tasks_with_status_filter(self, client: TestClient, auth_headers: dict):
        """Test GET /tasks with status parameter."""
        response = client.get("/api/tasks?status=incomplete", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data

    def test_get_tasks_with_priority_filter(self, client: TestClient, auth_headers: dict):
        """Test GET /tasks with priority parameter."""
        response = client.get("/api/tasks?priority=high", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data

    def test_get_tasks_with_sort_by(self, client: TestClient, auth_headers: dict):
        """Test GET /tasks with sort_by parameter."""
        response = client.get("/api/tasks?sort_by=title&sort_order=asc", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data

    def test_get_tasks_with_multiple_filters(self, client: TestClient, auth_headers: dict):
        """Test GET /tasks with multiple filter parameters."""
        response = client.get(
            "/api/tasks?search=important&priority=high&status=incomplete&sort_by=created_at&sort_order=desc",
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data

    def test_get_tasks_invalid_priority(self, client: TestClient, auth_headers: dict):
        """Test GET /tasks with invalid priority value."""
        response = client.get("/api/tasks?priority=invalid", headers=auth_headers)

        # Should return 422 validation error
        assert response.status_code == 422

    def test_get_tasks_invalid_sort_by(self, client: TestClient, auth_headers: dict):
        """Test GET /tasks with invalid sort_by value."""
        # Note: The API might accept any sort_by value and default to created_at
        response = client.get("/api/tasks?sort_by=invalid_field", headers=auth_headers)

        # Should still return 200 (might use default sorting)
        assert response.status_code in [200, 400]

    def test_get_tags(self, client: TestClient, auth_headers: dict):
        """Test GET /tags endpoint."""
        response = client.get("/api/tags", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data
        assert isinstance(data["data"], list)

    def test_create_tag(self, client: TestClient, auth_headers: dict):
        """Test POST /tags endpoint."""
        payload = {
            "name": "Urgent",
            "color": "#ef4444",
        }

        response = client.post("/api/tags", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert "data" in data
        assert data["data"]["name"] == "Urgent"
        assert data["data"]["color"] == "#ef4444"
        assert "id" in data["data"]

    def test_create_tag_with_default_color(self, client: TestClient, auth_headers: dict):
        """Test POST /tags with default color."""
        payload = {
            "name": "Work",
        }

        response = client.post("/api/tags", json=payload, headers=auth_headers)

        assert response.status_code == 201
        data = response.json()
        assert data["data"]["color"] == "#6366f1"

    def test_create_duplicate_tag_fails(self, client: TestClient, auth_headers: dict):
        """Test that creating duplicate tag fails."""
        payload = {
            "name": "Important",
        }

        # Create first tag
        client.post("/api/tags", json=payload, headers=auth_headers)

        # Try to create duplicate
        response = client.post("/api/tags", json=payload, headers=auth_headers)

        assert response.status_code == 400
        assert "already exists" in response.json()["detail"].lower()

    def test_update_tag(self, client: TestClient, auth_headers: dict):
        """Test PUT /tags/:id endpoint."""
        # Create tag
        create_response = client.post(
            "/api/tags",
            json={"name": "Old Name"},
            headers=auth_headers,
        )
        tag_id = create_response.json()["data"]["id"]

        # Update tag
        update_payload = {
            "name": "New Name",
            "color": "#000000",
        }

        response = client.put(
            f"/api/tags/{tag_id}",
            json=update_payload,
            headers=auth_headers,
        )

        assert response.status_code == 200
        data = response.json()
        assert data["data"]["name"] == "New Name"
        assert data["data"]["color"] == "#000000"

    def test_delete_tag(self, client: TestClient, auth_headers: dict):
        """Test DELETE /tags/:id endpoint."""
        # Create tag
        create_response = client.post(
            "/api/tags",
            json={"name": "To Delete"},
            headers=auth_headers,
        )
        tag_id = create_response.json()["data"]["id"]

        # Delete tag
        response = client.delete(f"/api/tags/{tag_id}", headers=auth_headers)

        assert response.status_code == 204

        # Verify tag is deleted
        get_response = client.get("/api/tags", headers=auth_headers)
        tags = get_response.json()["data"]
        assert not any(tag["id"] == tag_id for tag in tags)

    def test_get_task_stats(self, client: TestClient, auth_headers: dict):
        """Test GET /tasks/stats endpoint."""
        response = client.get("/api/tasks/stats", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()

        # Verify response structure
        assert "total_tasks" in data
        assert "completed_tasks" in data
        assert "incomplete_tasks" in data
        assert "completion_rate" in data
        assert "by_priority" in data
        assert "high" in data["by_priority"]
        assert "medium" in data["by_priority"]
        assert "low" in data["by_priority"]
        assert "recurring_tasks" in data
        assert "tasks_with_due_dates" in data
        assert "overdue_tasks" in data

    def test_validation_tag_name_required(self, client: TestClient, auth_headers: dict):
        """Test that tag name is required."""
        payload = {
            "color": "#000000",
        }

        response = client.post("/api/tags", json=payload, headers=auth_headers)

        assert response.status_code == 422

    def test_validation_tag_name_max_length(self, client: TestClient, auth_headers: dict):
        """Test that tag name has max length."""
        payload = {
            "name": "x" * 51,  # 51 characters (max is 50)
        }

        response = client.post("/api/tags", json=payload, headers=auth_headers)

        assert response.status_code == 422

    def test_add_tag_to_task(self, client: TestClient, auth_headers: dict):
        """Test POST /tags/:id/tasks/:id endpoint."""
        # Create task
        task_response = client.post(
            "/api/tasks",
            json={"title": "Test task", "priority": "medium"},
            headers=auth_headers,
        )
        task_id = task_response.json()["data"]["id"]

        # Create tag
        tag_response = client.post(
            "/api/tags",
            json={"name": "Important"},
            headers=auth_headers,
        )
        tag_id = tag_response.json()["data"]["id"]

        # Add tag to task
        response = client.post(
            f"/api/tags/{tag_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 201
        assert "message" in response.json()

    def test_get_task_tags(self, client: TestClient, auth_headers: dict):
        """Test GET /tags/tasks/:id endpoint."""
        # Create task
        task_response = client.post(
            "/api/tasks",
            json={"title": "Test task", "priority": "medium"},
            headers=auth_headers,
        )
        task_id = task_response.json()["data"]["id"]

        # Get tags for task
        response = client.get(f"/api/tags/tasks/{task_id}", headers=auth_headers)

        assert response.status_code == 200
        data = response.json()
        assert "data" in data
        assert "count" in data
        assert isinstance(data["data"], list)

    def test_remove_tag_from_task(self, client: TestClient, auth_headers: dict):
        """Test DELETE /tags/:id/tasks/:id endpoint."""
        # Create task
        task_response = client.post(
            "/api/tasks",
            json={"title": "Test task", "priority": "medium"},
            headers=auth_headers,
        )
        task_id = task_response.json()["data"]["id"]

        # Create tag
        tag_response = client.post(
            "/api/tags",
            json={"name": "Important"},
            headers=auth_headers,
        )
        tag_id = tag_response.json()["data"]["id"]

        # Add tag to task
        client.post(f"/api/tags/{tag_id}/tasks/{task_id}", headers=auth_headers)

        # Remove tag from task
        response = client.delete(
            f"/api/tags/{tag_id}/tasks/{task_id}",
            headers=auth_headers,
        )

        assert response.status_code == 204
