# API Contracts: Advanced Cloud Deployment

**Feature**: 006-advanced-cloud-deployment
**Date**: 2026-02-11
**API Version**: v1
**Base URL**: `/api/v1`

## Overview

This document defines REST API contracts for advanced features:
- Recurring tasks
- Due dates and reminders
- Tags and advanced filtering
- Event publishing (internal)

All endpoints require authentication via JWT token in `Authorization: Bearer <token>` header.

---

## 1. Recurring Tasks API

### POST /tasks (Extended)

Create a new task with optional recurrence

**Request**:
```json
{
  "title": "Daily standup",
  "description": "Team sync meeting",
  "priority": "HIGH",
  "category_id": "uuid",
  "due_date": "2026-02-12T09:00:00Z",
  "recurrence": {
    "frequency": "DAILY",
    "interval": 1,
    "end_date": "2026-12-31T23:59:59Z"
  },
  "reminder": {
    "offset_minutes": 60,
    "channel": "EMAIL"
  },
  "tags": ["work", "urgent"]
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "title": "Daily standup",
  "description": "Team sync meeting",
  "priority": "HIGH",
  "completed": false,
  "category_id": "uuid",
  "user_id": "cuid",
  "due_date": "2026-02-12T09:00:00Z",
  "is_recurring": true,
  "recurrence": {
    "id": "uuid",
    "frequency": "DAILY",
    "interval": 1,
    "next_occurrence_date": "2026-02-13T09:00:00Z",
    "end_date": "2026-12-31T23:59:59Z"
  },
  "reminder": {
    "id": "uuid",
    "remind_at": "2026-02-12T08:00:00Z",
    "offset_minutes": 60,
    "channel": "EMAIL",
    "status": "PENDING"
  },
  "tags": [
    {"id": "uuid", "name": "work", "color": "#FF5733"},
    {"id": "uuid", "name": "urgent", "color": "#C70039"}
  ],
  "created_at": "2026-02-11T10:00:00Z",
  "updated_at": "2026-02-11T10:00:00Z"
}
```

**Validation**:
- `title`: Required, max 200 chars
- `priority`: Optional, must be HIGH/MEDIUM/LOW
- `due_date`: Optional, must be ISO 8601 format
- `recurrence.frequency`: Required if recurrence provided, must be DAILY/WEEKLY/MONTHLY
- `recurrence.interval`: Optional, default 1, must be positive
- `reminder.offset_minutes`: Required if reminder provided, must be positive
- `reminder.channel`: Required if reminder provided, must be EMAIL/PUSH/BOTH

**Error Responses**:
- 400: Invalid request body
- 401: Unauthorized
- 422: Validation error

---

### GET /tasks/:id/occurrences

Get all occurrences of a recurring task

**Response** (200 OK):
```json
{
  "parent_task": {
    "id": "uuid",
    "title": "Daily standup",
    "is_recurring": true
  },
  "occurrences": [
    {
      "id": "uuid",
      "due_date": "2026-02-12T09:00:00Z",
      "completed": true,
      "completed_at": "2026-02-12T09:15:00Z"
    },
    {
      "id": "uuid",
      "due_date": "2026-02-13T09:00:00Z",
      "completed": false,
      "completed_at": null
    }
  ],
  "total": 2,
  "next_occurrence_date": "2026-02-14T09:00:00Z"
}
```

---

### DELETE /tasks/:id/recurrence

Stop recurrence for a recurring task (delete future occurrences)

**Query Parameters**:
- `delete_future`: boolean (default: true) - Delete all future occurrences
- `delete_all`: boolean (default: false) - Delete all occurrences including completed

**Response** (200 OK):
```json
{
  "message": "Recurrence stopped",
  "deleted_count": 5,
  "task": {
    "id": "uuid",
    "is_recurring": false,
    "recurrence": null
  }
}
```

---

## 2. Reminders API

### POST /tasks/:id/reminders

Add a reminder to a task

**Request**:
```json
{
  "offset_minutes": 60,
  "channel": "EMAIL"
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "task_id": "uuid",
  "remind_at": "2026-02-12T08:00:00Z",
  "offset_minutes": 60,
  "channel": "EMAIL",
  "status": "PENDING",
  "created_at": "2026-02-11T10:00:00Z"
}
```

**Validation**:
- Task must have a due_date
- `offset_minutes`: Required, must be positive
- `channel`: Required, must be EMAIL/PUSH/BOTH

---

### GET /tasks/:id/reminders

Get all reminders for a task

**Response** (200 OK):
```json
{
  "reminders": [
    {
      "id": "uuid",
      "remind_at": "2026-02-12T08:00:00Z",
      "offset_minutes": 60,
      "channel": "EMAIL",
      "status": "PENDING"
    }
  ],
  "total": 1
}
```

---

### DELETE /reminders/:id

Delete a reminder

**Response** (204 No Content)

---

## 3. Tags API

### GET /tags

Get all tags for the authenticated user

**Response** (200 OK):
```json
{
  "tags": [
    {
      "id": "uuid",
      "name": "work",
      "color": "#FF5733",
      "task_count": 15,
      "created_at": "2026-01-01T00:00:00Z"
    },
    {
      "id": "uuid",
      "name": "personal",
      "color": "#C70039",
      "task_count": 8,
      "created_at": "2026-01-01T00:00:00Z"
    }
  ],
  "total": 2
}
```

---

### POST /tags

Create a new tag

**Request**:
```json
{
  "name": "urgent",
  "color": "#FF0000"
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "name": "urgent",
  "color": "#FF0000",
  "task_count": 0,
  "created_at": "2026-02-11T10:00:00Z"
}
```

**Validation**:
- `name`: Required, max 50 chars, unique per user
- `color`: Optional, must be valid hex color (#RRGGBB)

---

### PUT /tags/:id

Update a tag

**Request**:
```json
{
  "name": "very-urgent",
  "color": "#CC0000"
}
```

**Response** (200 OK):
```json
{
  "id": "uuid",
  "name": "very-urgent",
  "color": "#CC0000",
  "task_count": 3,
  "updated_at": "2026-02-11T10:05:00Z"
}
```

---

### DELETE /tags/:id

Delete a tag (removes from all tasks)

**Response** (204 No Content)

---

## 4. Advanced Task Filtering API

### GET /tasks (Extended)

Get tasks with advanced filtering

**Query Parameters**:
- `priority`: string (HIGH/MEDIUM/LOW)
- `status`: string (completed/pending)
- `tags`: string[] (comma-separated tag names)
- `due_date_from`: ISO 8601 date
- `due_date_to`: ISO 8601 date
- `search`: string (searches title and description)
- `sort_by`: string (priority/due_date/created_at/title)
- `sort_order`: string (asc/desc)
- `page`: integer (default: 1)
- `limit`: integer (default: 20, max: 100)

**Example Request**:
```
GET /tasks?priority=HIGH&tags=work,urgent&due_date_from=2026-02-11&sort_by=due_date&sort_order=asc
```

**Response** (200 OK):
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "Daily standup",
      "description": "Team sync meeting",
      "priority": "HIGH",
      "completed": false,
      "due_date": "2026-02-12T09:00:00Z",
      "is_overdue": false,
      "tags": [
        {"id": "uuid", "name": "work", "color": "#FF5733"},
        {"id": "uuid", "name": "urgent", "color": "#C70039"}
      ],
      "reminder": {
        "id": "uuid",
        "remind_at": "2026-02-12T08:00:00Z"
      },
      "created_at": "2026-02-11T10:00:00Z",
      "updated_at": "2026-02-11T10:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 1,
    "total_pages": 1
  },
  "filters_applied": {
    "priority": "HIGH",
    "tags": ["work", "urgent"],
    "due_date_from": "2026-02-11"
  }
}
```

---

## 5. Task Statistics API

### GET /tasks/stats

Get task statistics for the authenticated user

**Response** (200 OK):
```json
{
  "total_tasks": 50,
  "completed_tasks": 30,
  "pending_tasks": 20,
  "overdue_tasks": 5,
  "due_today": 3,
  "due_this_week": 10,
  "recurring_tasks": 8,
  "by_priority": {
    "HIGH": 15,
    "MEDIUM": 20,
    "LOW": 15
  },
  "by_tag": {
    "work": 25,
    "personal": 15,
    "urgent": 10
  },
  "completion_rate": 0.6,
  "average_completion_time_hours": 24.5
}
```

---

## 6. Event Publishing (Internal API)

These endpoints are for internal service-to-service communication via Dapr.

### POST /internal/events/publish

Publish an event to Kafka via Dapr

**Request**:
```json
{
  "topic": "task-events",
  "event_type": "task.created",
  "data": {
    "task_id": "uuid",
    "user_id": "cuid",
    "task_data": {
      "title": "Daily standup",
      "priority": "HIGH"
    }
  }
}
```

**Response** (202 Accepted):
```json
{
  "event_id": "uuid",
  "topic": "task-events",
  "published_at": "2026-02-11T10:00:00Z"
}
```

---

## 7. Notification Preferences API

### GET /users/me/notification-preferences

Get notification preferences for the authenticated user

**Response** (200 OK):
```json
{
  "email_enabled": true,
  "push_enabled": true,
  "email_address": "user@example.com",
  "push_subscription": {
    "endpoint": "https://fcm.googleapis.com/...",
    "keys": {
      "p256dh": "...",
      "auth": "..."
    }
  },
  "quiet_hours": {
    "enabled": true,
    "start": "22:00",
    "end": "08:00",
    "timezone": "UTC"
  }
}
```

---

### PUT /users/me/notification-preferences

Update notification preferences

**Request**:
```json
{
  "email_enabled": true,
  "push_enabled": false,
  "quiet_hours": {
    "enabled": true,
    "start": "23:00",
    "end": "07:00"
  }
}
```

**Response** (200 OK):
```json
{
  "email_enabled": true,
  "push_enabled": false,
  "quiet_hours": {
    "enabled": true,
    "start": "23:00",
    "end": "07:00",
    "timezone": "UTC"
  },
  "updated_at": "2026-02-11T10:00:00Z"
}
```

---

## Error Response Format

All error responses follow this format:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request body",
    "details": [
      {
        "field": "recurrence.frequency",
        "message": "Must be one of: DAILY, WEEKLY, MONTHLY"
      }
    ],
    "request_id": "uuid"
  }
}
```

**Error Codes**:
- `VALIDATION_ERROR`: Request validation failed (400)
- `UNAUTHORIZED`: Authentication required (401)
- `FORBIDDEN`: Insufficient permissions (403)
- `NOT_FOUND`: Resource not found (404)
- `CONFLICT`: Resource conflict (409)
- `INTERNAL_ERROR`: Server error (500)

---

## Rate Limiting

All API endpoints are rate-limited:
- **Authenticated requests**: 1000 requests per hour per user
- **Unauthenticated requests**: 100 requests per hour per IP

Rate limit headers:
```
X-RateLimit-Limit: 1000
X-RateLimit-Remaining: 999
X-RateLimit-Reset: 1644580800
```

---

## Versioning

API version is specified in the URL path: `/api/v1/...`

Breaking changes will result in a new version: `/api/v2/...`

---

## Authentication

All endpoints (except health checks) require JWT authentication:

```
Authorization: Bearer <jwt_token>
```

JWT payload:
```json
{
  "sub": "user_cuid",
  "email": "user@example.com",
  "iat": 1644580800,
  "exp": 1644667200
}
```

---

## Pagination

List endpoints support pagination:
- `page`: Page number (default: 1)
- `limit`: Items per page (default: 20, max: 100)

Response includes pagination metadata:
```json
{
  "data": [...],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100,
    "total_pages": 5,
    "has_next": true,
    "has_prev": false
  }
}
```

---

**API Contract Version**: 1.0.0
**Last Updated**: 2026-02-11
**Status**: Ready for Implementation
