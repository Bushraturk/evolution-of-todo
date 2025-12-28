# API Contract: Full-Stack Web Application Todo App

**Feature**: 002-fullstack-webapp
**Date**: 2025-12-28
**Base URL**: `http://localhost:8000/api`

## Overview

RESTful API for task management with CRUD operations, filtering, sorting, and search capabilities.

## Authentication

**Phase II**: No authentication required (single-user mode)

## Response Format

All responses use JSON format with consistent structure:

### Success Response
```json
{
  "data": { ... },
  "message": "Success message (optional)"
}
```

### Error Response
```json
{
  "detail": "Error description",
  "errors": [
    {
      "field": "field_name",
      "message": "Validation error message"
    }
  ]
}
```

## HTTP Status Codes

| Code | Meaning | Usage |
|------|---------|-------|
| 200 | OK | Successful GET, PUT, PATCH |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Validation errors |
| 404 | Not Found | Resource doesn't exist |
| 500 | Internal Server Error | Server-side errors |

---

## Task Endpoints

### GET /api/tasks

List all tasks with optional filtering, sorting, and search.

**Query Parameters**:
| Parameter | Type | Required | Default | Description |
|-----------|------|----------|---------|-------------|
| search | string | No | - | Search in title and description |
| status | string | No | all | Filter: `all`, `completed`, `incomplete` |
| priority | string | No | - | Filter: `high`, `medium`, `low` |
| category_id | uuid | No | - | Filter by category |
| sort_by | string | No | created_at | Sort field: `created_at`, `priority`, `title` |
| sort_order | string | No | desc | Order: `asc`, `desc` |

**Request**:
```http
GET /api/tasks?status=incomplete&priority=high&sort_by=created_at&sort_order=desc
```

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "priority": "high",
      "category_id": "660e8400-e29b-41d4-a716-446655440001",
      "category": {
        "id": "660e8400-e29b-41d4-a716-446655440001",
        "name": "Shopping",
        "color": "#F59E0B"
      },
      "created_at": "2025-12-28T10:00:00Z",
      "updated_at": "2025-12-28T10:00:00Z"
    }
  ],
  "count": 1
}
```

---

### POST /api/tasks

Create a new task.

**Request Body**:
| Field | Type | Required | Default | Constraints |
|-------|------|----------|---------|-------------|
| title | string | Yes | - | Max 200 chars, non-empty |
| description | string | No | null | Max 1000 chars |
| priority | string | No | medium | high, medium, low |
| category_id | uuid | No | null | Must exist if provided |

**Request**:
```http
POST /api/tasks
Content-Type: application/json

{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "category_id": "660e8400-e29b-41d4-a716-446655440001"
}
```

**Response** (201 Created):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "priority": "high",
    "category_id": "660e8400-e29b-41d4-a716-446655440001",
    "category": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Shopping",
      "color": "#F59E0B"
    },
    "created_at": "2025-12-28T10:00:00Z",
    "updated_at": "2025-12-28T10:00:00Z"
  },
  "message": "Task created successfully"
}
```

**Error Response** (400 Bad Request):
```json
{
  "detail": "Validation error",
  "errors": [
    {
      "field": "title",
      "message": "Title cannot be empty"
    }
  ]
}
```

---

### GET /api/tasks/{id}

Get a single task by ID.

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | uuid | Task ID |

**Request**:
```http
GET /api/tasks/550e8400-e29b-41d4-a716-446655440000
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "priority": "high",
    "category_id": "660e8400-e29b-41d4-a716-446655440001",
    "category": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Shopping",
      "color": "#F59E0B"
    },
    "created_at": "2025-12-28T10:00:00Z",
    "updated_at": "2025-12-28T10:00:00Z"
  }
}
```

**Error Response** (404 Not Found):
```json
{
  "detail": "Task with ID 550e8400-e29b-41d4-a716-446655440000 not found"
}
```

---

### PUT /api/tasks/{id}

Update a task's details.

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | uuid | Task ID |

**Request Body**:
| Field | Type | Required | Constraints |
|-------|------|----------|-------------|
| title | string | No | Max 200 chars, non-empty if provided |
| description | string | No | Max 1000 chars |
| priority | string | No | high, medium, low |
| category_id | uuid | No | Must exist or null to remove |

**Request**:
```http
PUT /api/tasks/550e8400-e29b-41d4-a716-446655440000
Content-Type: application/json

{
  "title": "Buy organic groceries",
  "priority": "medium"
}
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy organic groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "priority": "medium",
    "category_id": "660e8400-e29b-41d4-a716-446655440001",
    "category": {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Shopping",
      "color": "#F59E0B"
    },
    "created_at": "2025-12-28T10:00:00Z",
    "updated_at": "2025-12-28T11:30:00Z"
  },
  "message": "Task updated successfully"
}
```

---

### DELETE /api/tasks/{id}

Delete a task.

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | uuid | Task ID |

**Request**:
```http
DELETE /api/tasks/550e8400-e29b-41d4-a716-446655440000
```

**Response** (200 OK):
```json
{
  "message": "Task deleted successfully",
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy organic groceries"
  }
}
```

---

### PATCH /api/tasks/{id}/toggle

Toggle task completion status.

**Path Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| id | uuid | Task ID |

**Request**:
```http
PATCH /api/tasks/550e8400-e29b-41d4-a716-446655440000/toggle
```

**Response** (200 OK):
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy organic groceries",
    "completed": true,
    "updated_at": "2025-12-28T12:00:00Z"
  },
  "message": "Task marked as complete"
}
```

---

## Category Endpoints

### GET /api/categories

List all categories.

**Request**:
```http
GET /api/categories
```

**Response** (200 OK):
```json
{
  "data": [
    {
      "id": "660e8400-e29b-41d4-a716-446655440001",
      "name": "Shopping",
      "color": "#F59E0B"
    },
    {
      "id": "660e8400-e29b-41d4-a716-446655440002",
      "name": "Work",
      "color": "#3B82F6"
    }
  ],
  "count": 2
}
```

---

### POST /api/categories

Create a new category.

**Request Body**:
| Field | Type | Required | Default | Constraints |
|-------|------|----------|---------|-------------|
| name | string | Yes | - | Max 50 chars, unique |
| color | string | No | #808080 | Hex color format |

**Request**:
```http
POST /api/categories
Content-Type: application/json

{
  "name": "Health",
  "color": "#EF4444"
}
```

**Response** (201 Created):
```json
{
  "data": {
    "id": "660e8400-e29b-41d4-a716-446655440003",
    "name": "Health",
    "color": "#EF4444"
  },
  "message": "Category created successfully"
}
```

---

## Frontend API Client

TypeScript client for consuming the API:

```typescript
// frontend/src/services/api.ts

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface TaskFilters {
  search?: string;
  status?: 'all' | 'completed' | 'incomplete';
  priority?: 'high' | 'medium' | 'low';
  category_id?: string;
  sort_by?: 'created_at' | 'priority' | 'title';
  sort_order?: 'asc' | 'desc';
}

export const taskApi = {
  async getAll(filters?: TaskFilters): Promise<Task[]> {
    const params = new URLSearchParams();
    if (filters) {
      Object.entries(filters).forEach(([key, value]) => {
        if (value) params.append(key, value);
      });
    }
    const response = await fetch(`${API_URL}/api/tasks?${params}`);
    if (!response.ok) throw new Error('Failed to fetch tasks');
    const json = await response.json();
    return json.data;
  },

  async create(task: CreateTaskRequest): Promise<Task> {
    const response = await fetch(`${API_URL}/api/tasks`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(task),
    });
    if (!response.ok) throw new Error('Failed to create task');
    const json = await response.json();
    return json.data;
  },

  async update(id: string, task: UpdateTaskRequest): Promise<Task> {
    const response = await fetch(`${API_URL}/api/tasks/${id}`, {
      method: 'PUT',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(task),
    });
    if (!response.ok) throw new Error('Failed to update task');
    const json = await response.json();
    return json.data;
  },

  async delete(id: string): Promise<void> {
    const response = await fetch(`${API_URL}/api/tasks/${id}`, {
      method: 'DELETE',
    });
    if (!response.ok) throw new Error('Failed to delete task');
  },

  async toggle(id: string): Promise<Task> {
    const response = await fetch(`${API_URL}/api/tasks/${id}/toggle`, {
      method: 'PATCH',
    });
    if (!response.ok) throw new Error('Failed to toggle task');
    const json = await response.json();
    return json.data;
  },
};

export const categoryApi = {
  async getAll(): Promise<Category[]> {
    const response = await fetch(`${API_URL}/api/categories`);
    if (!response.ok) throw new Error('Failed to fetch categories');
    const json = await response.json();
    return json.data;
  },

  async create(category: { name: string; color?: string }): Promise<Category> {
    const response = await fetch(`${API_URL}/api/categories`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(category),
    });
    if (!response.ok) throw new Error('Failed to create category');
    const json = await response.json();
    return json.data;
  },
};
```
