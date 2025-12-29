# API Contracts: User Authentication & Multi-User Support

**Feature**: 003-user-authentication
**Date**: 2025-12-28

## Overview

This document defines the API contracts for authentication and updated task endpoints with user isolation.

## Authentication Flow

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│   Browser   │     │  Next.js    │     │   FastAPI   │
│   Client    │     │  Frontend   │     │   Backend   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       │  1. Login Form    │                   │
       │──────────────────>│                   │
       │                   │                   │
       │  2. Better Auth   │                   │
       │  POST /api/auth/* │                   │
       │<─────────────────>│                   │
       │                   │                   │
       │  3. Get JWT Token │                   │
       │  authClient.token()                   │
       │<──────────────────│                   │
       │                   │                   │
       │  4. API Request with Bearer Token     │
       │─────────────────────────────────────>│
       │                   │  Authorization:   │
       │                   │  Bearer <jwt>     │
       │                   │                   │
       │  5. Verify JWT via JWKS              │
       │                   │<─────────────────│
       │                   │  GET /api/auth/jwks
       │                   │─────────────────>│
       │                   │                   │
       │  6. Return User's Data Only          │
       │<─────────────────────────────────────│
       │                   │                   │
```

## Base URLs

- **Frontend Auth API**: `http://localhost:3000/api/auth/*` (Better Auth)
- **Backend API**: `http://localhost:8000/api/*` (FastAPI)
- **JWKS Endpoint**: `http://localhost:3000/api/auth/jwks`

---

## Authentication Endpoints (Better Auth - Frontend)

Better Auth automatically provides these endpoints at `/api/auth/*`:

### POST /api/auth/sign-up/email

Create a new user account.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123",
  "name": "John Doe"
}
```

**Response (200)**:
```json
{
  "user": {
    "id": "clx1234567890",
    "email": "user@example.com",
    "name": "John Doe",
    "emailVerified": false,
    "createdAt": "2025-12-28T10:00:00.000Z"
  },
  "session": {
    "id": "sess_1234567890",
    "userId": "clx1234567890",
    "expiresAt": "2026-01-04T10:00:00.000Z"
  }
}
```

**Response (400)** - Validation Error:
```json
{
  "error": "Email already in use"
}
```

---

### POST /api/auth/sign-in/email

Authenticate existing user.

**Request**:
```json
{
  "email": "user@example.com",
  "password": "securepassword123"
}
```

**Response (200)**:
```json
{
  "user": {
    "id": "clx1234567890",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "session": {
    "id": "sess_1234567890",
    "userId": "clx1234567890",
    "expiresAt": "2026-01-04T10:00:00.000Z"
  }
}
```

**Response (401)**:
```json
{
  "error": "Invalid email or password"
}
```

---

### POST /api/auth/sign-out

End current session.

**Headers**:
```
Cookie: better-auth.session_token=...
```

**Response (200)**:
```json
{
  "success": true
}
```

---

### GET /api/auth/session

Get current session info.

**Headers**:
```
Cookie: better-auth.session_token=...
```

**Response (200)**:
```json
{
  "user": {
    "id": "clx1234567890",
    "email": "user@example.com",
    "name": "John Doe"
  },
  "session": {
    "id": "sess_1234567890",
    "expiresAt": "2026-01-04T10:00:00.000Z"
  }
}
```

**Response (401)**:
```json
{
  "error": "Not authenticated"
}
```

---

### GET /api/auth/token

Get JWT token for API authentication.

**Headers**:
```
Cookie: better-auth.session_token=...
```

**Response (200)**:
```json
{
  "token": "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCIsImtpZCI6ImM1Yzc5OTVkLTAwMzctNDU1My04YWVlLWI1YjYyMGI4OWIyMyJ9..."
}
```

**JWT Payload** (decoded):
```json
{
  "sub": "clx1234567890",
  "email": "user@example.com",
  "name": "John Doe",
  "iat": 1703764800,
  "exp": 1703765700,
  "iss": "http://localhost:3000"
}
```

---

### GET /api/auth/jwks

Public keys for JWT verification.

**Response (200)**:
```json
{
  "keys": [
    {
      "kty": "OKP",
      "crv": "Ed25519",
      "x": "bDHiLTt7u-VIU7rfmcltcFhaHKLVvWFy-_csKZARUEU",
      "kid": "c5c7995d-0037-4553-8aee-b5b620b89b23"
    }
  ]
}
```

---

## Backend API Endpoints (FastAPI)

All backend endpoints now require JWT authentication.

### Common Headers (All Requests)

```
Authorization: Bearer <jwt_token>
Content-Type: application/json
```

### Common Error Responses

**401 Unauthorized** - Missing or invalid token:
```json
{
  "detail": "Not authenticated"
}
```

**403 Forbidden** - Valid token but no access to resource:
```json
{
  "detail": "Access denied"
}
```

---

## Task Endpoints (Updated)

### GET /api/tasks

List authenticated user's tasks.

**Query Parameters**:
| Parameter | Type | Description |
|-----------|------|-------------|
| search | string | Search in title/description |
| status | string | "all", "completed", "incomplete" |
| priority | string | "high", "medium", "low" |
| category_id | UUID | Filter by category |
| sort_by | string | "created_at", "priority", "title" |
| sort_order | string | "asc", "desc" |

**Response (200)**:
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "user_id": "clx1234567890",
      "title": "Buy groceries",
      "description": "Milk, eggs, bread",
      "completed": false,
      "priority": "high",
      "category_id": "550e8400-e29b-41d4-a716-446655440001",
      "category": {
        "id": "550e8400-e29b-41d4-a716-446655440001",
        "name": "Shopping",
        "color": "#10b981"
      },
      "created_at": "2025-12-28T10:00:00.000Z",
      "updated_at": "2025-12-28T10:00:00.000Z"
    }
  ],
  "count": 1
}
```

**Note**: Only returns tasks where `user_id` matches JWT's `sub` claim.

---

### POST /api/tasks

Create a new task for authenticated user.

**Request**:
```json
{
  "title": "Buy groceries",
  "description": "Milk, eggs, bread",
  "priority": "high",
  "category_id": "550e8400-e29b-41d4-a716-446655440001"
}
```

**Response (201)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "clx1234567890",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "priority": "high",
    "category_id": "550e8400-e29b-41d4-a716-446655440001",
    "created_at": "2025-12-28T10:00:00.000Z",
    "updated_at": "2025-12-28T10:00:00.000Z"
  },
  "message": "Task created successfully"
}
```

**Note**: `user_id` is automatically set from JWT's `sub` claim.

---

### GET /api/tasks/{task_id}

Get a specific task (must belong to authenticated user).

**Response (200)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "clx1234567890",
    "title": "Buy groceries",
    "description": "Milk, eggs, bread",
    "completed": false,
    "priority": "high",
    "category_id": "550e8400-e29b-41d4-a716-446655440001",
    "created_at": "2025-12-28T10:00:00.000Z",
    "updated_at": "2025-12-28T10:00:00.000Z"
  }
}
```

**Response (404)** - Task not found or belongs to another user:
```json
{
  "detail": "Task not found"
}
```

---

### PUT /api/tasks/{task_id}

Update a task (must belong to authenticated user).

**Request**:
```json
{
  "title": "Buy groceries (updated)",
  "description": "Milk, eggs, bread, cheese",
  "priority": "medium",
  "category_id": null
}
```

**Response (200)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "user_id": "clx1234567890",
    "title": "Buy groceries (updated)",
    "description": "Milk, eggs, bread, cheese",
    "completed": false,
    "priority": "medium",
    "category_id": null,
    "created_at": "2025-12-28T10:00:00.000Z",
    "updated_at": "2025-12-28T11:00:00.000Z"
  },
  "message": "Task updated successfully"
}
```

---

### DELETE /api/tasks/{task_id}

Delete a task (must belong to authenticated user).

**Response (200)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "title": "Buy groceries"
  },
  "message": "Task deleted successfully"
}
```

---

### PATCH /api/tasks/{task_id}/toggle

Toggle task completion (must belong to authenticated user).

**Response (200)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "completed": true,
    "updated_at": "2025-12-28T11:00:00.000Z"
  },
  "message": "Task marked as complete"
}
```

---

## Category Endpoints (Updated)

Categories remain global but now require authentication.

### GET /api/categories

List all categories (requires authentication).

**Response (200)**:
```json
{
  "data": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440001",
      "name": "Shopping",
      "color": "#10b981"
    },
    {
      "id": "550e8400-e29b-41d4-a716-446655440002",
      "name": "Work",
      "color": "#6366f1"
    }
  ],
  "count": 2
}
```

### POST /api/categories

Create a new category (requires authentication).

**Request**:
```json
{
  "name": "Personal",
  "color": "#f59e0b"
}
```

**Response (201)**:
```json
{
  "data": {
    "id": "550e8400-e29b-41d4-a716-446655440003",
    "name": "Personal",
    "color": "#f59e0b"
  },
  "message": "Category created successfully"
}
```

---

## JWT Verification (Backend Implementation)

### FastAPI Dependency

```python
# backend/src/auth/dependencies.py
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
import httpx

security = HTTPBearer()

JWKS_URL = "http://localhost:3000/api/auth/jwks"
JWT_ISSUER = "http://localhost:3000"

# Cache JWKS keys
_jwks_cache = None

async def get_jwks():
    global _jwks_cache
    if _jwks_cache is None:
        async with httpx.AsyncClient() as client:
            response = await client.get(JWKS_URL)
            _jwks_cache = response.json()
    return _jwks_cache

async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> dict:
    token = credentials.credentials
    try:
        jwks = await get_jwks()
        payload = jwt.decode(
            token,
            jwks,
            algorithms=["EdDSA", "RS256"],
            issuer=JWT_ISSUER
        )
        user_id = payload.get("sub")
        if user_id is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )
        return {
            "id": user_id,
            "email": payload.get("email"),
            "name": payload.get("name")
        }
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token"
        )
```

### Usage in Routes

```python
# backend/src/api/routes/tasks.py
from ..auth.dependencies import get_current_user

@router.get("")
async def get_tasks(
    current_user: dict = Depends(get_current_user),
    service: TaskService = Depends(get_task_service)
):
    # Filter by current user
    tasks = service.get_all_tasks(user_id=current_user["id"])
    return TaskListResponse(data=tasks, count=len(tasks))
```

---

## Error Codes Summary

| Code | Meaning | When |
|------|---------|------|
| 200 | Success | Request completed |
| 201 | Created | Resource created |
| 400 | Bad Request | Invalid input data |
| 401 | Unauthorized | Missing/invalid token |
| 403 | Forbidden | Valid token, no permission |
| 404 | Not Found | Resource doesn't exist |
| 500 | Server Error | Internal error |
