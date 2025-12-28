"""Integration tests for API endpoints."""

import pytest
from fastapi.testclient import TestClient
from uuid import uuid4

from src.models.task import Priority


class TestTasksAPI:
    """Integration tests for /api/tasks endpoints."""

    def test_get_tasks_empty(self, client: TestClient) -> None:
        """Test GET /api/tasks returns empty list."""
        response = client.get("/api/tasks")
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["count"] == 0

    def test_create_task(self, client: TestClient) -> None:
        """Test POST /api/tasks creates a task."""
        response = client.post(
            "/api/tasks",
            json={"title": "Test Task", "description": "Test Description"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["title"] == "Test Task"
        assert data["data"]["description"] == "Test Description"
        assert data["data"]["completed"] is False
        assert data["data"]["priority"] == "medium"
        assert data["message"] == "Task created successfully"

    def test_create_task_with_priority(self, client: TestClient) -> None:
        """Test POST /api/tasks with priority."""
        response = client.post(
            "/api/tasks",
            json={"title": "High Priority Task", "priority": "high"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["priority"] == "high"

    def test_create_task_empty_title_fails(self, client: TestClient) -> None:
        """Test POST /api/tasks with empty title fails."""
        response = client.post("/api/tasks", json={"title": ""})
        assert response.status_code == 422  # Validation error

    def test_get_task_by_id(self, client: TestClient) -> None:
        """Test GET /api/tasks/{id} returns task."""
        # Create a task first
        create_response = client.post("/api/tasks", json={"title": "Test Task"})
        task_id = create_response.json()["data"]["id"]

        response = client.get(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["id"] == task_id

    def test_get_task_not_found(self, client: TestClient) -> None:
        """Test GET /api/tasks/{id} with invalid ID returns 404."""
        response = client.get(f"/api/tasks/{uuid4()}")
        assert response.status_code == 404

    def test_toggle_task(self, client: TestClient) -> None:
        """Test PATCH /api/tasks/{id}/toggle toggles completion."""
        # Create a task
        create_response = client.post("/api/tasks", json={"title": "Test Task"})
        task_id = create_response.json()["data"]["id"]

        # Toggle to complete
        response = client.patch(f"/api/tasks/{task_id}/toggle")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["completed"] is True
        assert "complete" in data["message"]

        # Toggle back to incomplete
        response = client.patch(f"/api/tasks/{task_id}/toggle")
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["completed"] is False
        assert "incomplete" in data["message"]

    def test_update_task(self, client: TestClient) -> None:
        """Test PUT /api/tasks/{id} updates task."""
        # Create a task
        create_response = client.post("/api/tasks", json={"title": "Original Title"})
        task_id = create_response.json()["data"]["id"]

        # Update the task
        response = client.put(
            f"/api/tasks/{task_id}",
            json={"title": "Updated Title", "priority": "high"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["data"]["title"] == "Updated Title"
        assert data["data"]["priority"] == "high"
        assert data["message"] == "Task updated successfully"

    def test_delete_task(self, client: TestClient) -> None:
        """Test DELETE /api/tasks/{id} deletes task."""
        # Create a task
        create_response = client.post("/api/tasks", json={"title": "To Delete"})
        task_id = create_response.json()["data"]["id"]

        # Delete the task
        response = client.delete(f"/api/tasks/{task_id}")
        assert response.status_code == 200
        data = response.json()
        assert data["message"] == "Task deleted successfully"

        # Verify task is deleted
        get_response = client.get(f"/api/tasks/{task_id}")
        assert get_response.status_code == 404

    def test_filter_by_status(self, client: TestClient) -> None:
        """Test GET /api/tasks with status filter."""
        # Create tasks
        client.post("/api/tasks", json={"title": "Incomplete Task"})
        create_response = client.post("/api/tasks", json={"title": "Complete Task"})
        task_id = create_response.json()["data"]["id"]
        client.patch(f"/api/tasks/{task_id}/toggle")

        # Filter by incomplete
        response = client.get("/api/tasks?status=incomplete")
        assert response.status_code == 200
        data = response.json()
        assert all(not t["completed"] for t in data["data"])

        # Filter by completed
        response = client.get("/api/tasks?status=completed")
        assert response.status_code == 200
        data = response.json()
        assert all(t["completed"] for t in data["data"])

    def test_search_tasks(self, client: TestClient) -> None:
        """Test GET /api/tasks with search parameter."""
        # Create tasks
        client.post("/api/tasks", json={"title": "Buy groceries"})
        client.post("/api/tasks", json={"title": "Call mom"})

        # Search for groceries
        response = client.get("/api/tasks?search=groceries")
        assert response.status_code == 200
        data = response.json()
        assert len(data["data"]) == 1
        assert "groceries" in data["data"][0]["title"]


class TestCategoriesAPI:
    """Integration tests for /api/categories endpoints."""

    def test_get_categories_empty(self, client: TestClient) -> None:
        """Test GET /api/categories returns empty list."""
        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert data["data"] == []
        assert data["count"] == 0

    def test_create_category(self, client: TestClient) -> None:
        """Test POST /api/categories creates a category."""
        response = client.post(
            "/api/categories",
            json={"name": "Work", "color": "#3B82F6"},
        )
        assert response.status_code == 201
        data = response.json()
        assert data["data"]["name"] == "Work"
        assert data["data"]["color"] == "#3B82F6"
        assert data["message"] == "Category created successfully"

    def test_get_categories(self, client: TestClient) -> None:
        """Test GET /api/categories returns categories."""
        # Create categories
        client.post("/api/categories", json={"name": "Work"})
        client.post("/api/categories", json={"name": "Personal"})

        response = client.get("/api/categories")
        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
