# Research: Full-Stack Web Application Todo App

**Feature**: 002-fullstack-webapp
**Date**: 2025-12-28
**Purpose**: Resolve technical unknowns and document best practices

## Technology Research

### 1. FastAPI + SQLModel Integration

**Decision**: Use SQLModel as ORM with FastAPI

**Rationale**:
- SQLModel is created by the same author as FastAPI (Sebastián Ramírez)
- Combines SQLAlchemy ORM with Pydantic validation
- Single model definition serves as database model AND API schema
- Native async support for PostgreSQL
- Reduces code duplication between database and API layers

**Alternatives Considered**:
- SQLAlchemy alone: More verbose, requires separate Pydantic models
- Tortoise-ORM: Less mature, smaller ecosystem
- Peewee: Synchronous only, not ideal for FastAPI

**Best Practices**:
```python
# SQLModel pattern for dual-use models
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4
from datetime import datetime

class TaskBase(SQLModel):
    title: str = Field(max_length=200)
    description: str | None = Field(default=None, max_length=1000)

class Task(TaskBase, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 2. Neon DB (PostgreSQL) Connection

**Decision**: Use Neon DB serverless PostgreSQL with connection pooling

**Rationale**:
- Serverless PostgreSQL with instant scaling
- Free tier sufficient for hackathon
- Native SSL support
- Connection pooling via Neon's proxy

**Connection Pattern**:
```python
from sqlmodel import create_engine, Session
import os

DATABASE_URL = os.getenv("DATABASE_URL")
# Neon requires SSL
engine = create_engine(DATABASE_URL, echo=True)
```

**Best Practices**:
- Always use `?sslmode=require` in connection string
- Use connection pooling for production
- Store DATABASE_URL in environment variables, never in code

### 3. Next.js 14 App Router

**Decision**: Use Next.js 14 with App Router and Server Components

**Rationale**:
- App Router is the recommended approach for new Next.js projects
- Server Components reduce client-side JavaScript
- Built-in TypeScript support
- Excellent developer experience with hot reload

**Alternatives Considered**:
- Pages Router: Legacy approach, less optimal for new projects
- Create React App: No SSR, less optimized
- Vite + React: Requires manual configuration for SSR

**Best Practices**:
- Use client components (`'use client'`) only when needed (interactivity)
- Keep data fetching in server components where possible
- Use TypeScript for type safety

### 4. API Communication Pattern

**Decision**: Use fetch API with typed responses

**Rationale**:
- Built-in to browsers and Next.js
- No additional dependencies
- TypeScript integration for type-safe responses

**Pattern**:
```typescript
// frontend/src/services/api.ts
const API_URL = process.env.NEXT_PUBLIC_API_URL;

export async function getTasks(): Promise<Task[]> {
  const response = await fetch(`${API_URL}/api/tasks`);
  if (!response.ok) throw new Error('Failed to fetch tasks');
  return response.json();
}
```

### 5. CORS Configuration

**Decision**: Configure FastAPI CORS middleware for frontend origin

**Rationale**:
- Frontend (Next.js on port 3000) needs to call backend (FastAPI on port 8000)
- CORS middleware allows cross-origin requests
- Environment-based configuration for different deployments

**Implementation**:
```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### 6. Priority Enum Implementation

**Decision**: Use Python Enum for priorities, stored as string in PostgreSQL

**Rationale**:
- Type-safe in Python code
- Human-readable in database
- Easy to serialize/deserialize with Pydantic

**Implementation**:
```python
from enum import Enum

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

### 7. UUID vs Auto-increment ID

**Decision**: Use UUID for task IDs

**Rationale**:
- Spec requires UUID (Key Entities section)
- No sequential ID guessing
- Works well with distributed systems (future phases)
- SQLModel supports UUID natively with PostgreSQL

**Implementation**:
```python
from uuid import UUID, uuid4
id: UUID = Field(default_factory=uuid4, primary_key=True)
```

### 8. Form Validation Strategy

**Decision**: Client-side validation with server-side enforcement

**Rationale**:
- Immediate feedback to users (better UX)
- Server validation prevents malformed data
- Pydantic schemas enforce constraints

**Validation Rules** (from spec):
- Title: Required, max 200 characters
- Description: Optional, max 1000 characters
- Priority: Enum (High, Medium, Low), default Medium
- Category: Optional string

## Resolved Clarifications

| Item | Resolution |
|------|------------|
| Database connection | Neon DB with SQLModel, SSL required |
| API framework | FastAPI with automatic OpenAPI docs |
| Frontend framework | Next.js 14 App Router with TypeScript |
| Styling | Tailwind CSS for rapid development |
| State management | React hooks (no Redux needed) |
| Testing | pytest (backend), Jest (frontend) |

## Dependencies Summary

### Backend (Python)
```
fastapi>=0.109.0
sqlmodel>=0.0.14
uvicorn[standard]>=0.27.0
python-dotenv>=1.0.0
psycopg2-binary>=2.9.9
pytest>=8.0.0
httpx>=0.26.0  # For testing
```

### Frontend (Node.js)
```
next@14
react@18
react-dom@18
typescript
tailwindcss
@types/react
@types/node
jest
@testing-library/react
```
