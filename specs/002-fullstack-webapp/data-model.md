# Data Model: Full-Stack Web Application Todo App

**Feature**: 002-fullstack-webapp
**Date**: 2025-12-28
**Source**: spec.md Key Entities section

## Entities

### Task

Primary entity representing a todo item.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | UUID | Primary Key, Auto-generated | uuid4() | Unique identifier |
| title | String | Required, Max 200 chars | - | Brief description of task |
| description | String | Optional, Max 1000 chars | None | Detailed information |
| completed | Boolean | Required | False | Completion status |
| priority | Enum | HIGH, MEDIUM, LOW | MEDIUM | Importance level |
| category_id | UUID | Foreign Key, Optional | None | Reference to Category |
| created_at | DateTime | Auto-generated | now() | Creation timestamp |
| updated_at | DateTime | Auto-updated | now() | Last modification timestamp |

**Validation Rules**:
- Title cannot be empty or whitespace-only
- Title must be ≤200 characters
- Description must be ≤1000 characters if provided
- Priority must be one of: HIGH, MEDIUM, LOW
- Completed must be boolean

**State Transitions**:
```
[Created] → completed=false
    ↓
[Toggle Complete] → completed=true
    ↓
[Toggle Complete] → completed=false
    ↓
[Deleted] → removed from database
```

### Category

Entity for organizing tasks by context.

| Field | Type | Constraints | Default | Description |
|-------|------|-------------|---------|-------------|
| id | UUID | Primary Key, Auto-generated | uuid4() | Unique identifier |
| name | String | Required, Unique, Max 50 chars | - | Category name (e.g., "Work") |
| color | String | Optional, Hex format | #808080 | Visual color code |

**Predefined Categories** (optional seeding):
- Work (#3B82F6 - blue)
- Personal (#10B981 - green)
- Shopping (#F59E0B - amber)
- Health (#EF4444 - red)
- Learning (#8B5CF6 - purple)

## Relationships

```
┌──────────────┐       ┌──────────────┐
│    Task      │ N:1   │   Category   │
├──────────────┤       ├──────────────┤
│ id (PK)      │       │ id (PK)      │
│ title        │       │ name         │
│ description  │       │ color        │
│ completed    │       └──────────────┘
│ priority     │              ▲
│ category_id  │──────────────┘
│ created_at   │       (Optional FK)
│ updated_at   │
└──────────────┘
```

- **Task → Category**: Many-to-One (optional)
  - A task can have zero or one category
  - A category can have many tasks
  - Deleting a category sets task.category_id to NULL (ON DELETE SET NULL)

## SQLModel Definitions

### Priority Enum
```python
from enum import Enum

class Priority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
```

### Category Model
```python
from sqlmodel import SQLModel, Field
from uuid import UUID, uuid4

class Category(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    name: str = Field(max_length=50, unique=True)
    color: str = Field(default="#808080", max_length=7)
```

### Task Model
```python
from sqlmodel import SQLModel, Field, Relationship
from uuid import UUID, uuid4
from datetime import datetime
from typing import Optional

class Task(SQLModel, table=True):
    id: UUID = Field(default_factory=uuid4, primary_key=True)
    title: str = Field(max_length=200)
    description: Optional[str] = Field(default=None, max_length=1000)
    completed: bool = Field(default=False)
    priority: Priority = Field(default=Priority.MEDIUM)
    category_id: Optional[UUID] = Field(default=None, foreign_key="category.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship
    category: Optional[Category] = Relationship()
```

## TypeScript Interfaces

```typescript
// frontend/src/types/task.ts

export type Priority = 'high' | 'medium' | 'low';

export interface Category {
  id: string;
  name: string;
  color: string;
}

export interface Task {
  id: string;
  title: string;
  description: string | null;
  completed: boolean;
  priority: Priority;
  category_id: string | null;
  category: Category | null;
  created_at: string;
  updated_at: string;
}

export interface CreateTaskRequest {
  title: string;
  description?: string;
  priority?: Priority;
  category_id?: string;
}

export interface UpdateTaskRequest {
  title?: string;
  description?: string;
  priority?: Priority;
  category_id?: string;
}
```

## Database Indexes

| Table | Index | Columns | Purpose |
|-------|-------|---------|---------|
| task | pk_task | id | Primary key |
| task | ix_task_completed | completed | Filter by status |
| task | ix_task_priority | priority | Filter by priority |
| task | ix_task_category_id | category_id | Join with category |
| task | ix_task_created_at | created_at | Sort by date |
| task | ix_task_title_search | title | Text search (optional) |
| category | pk_category | id | Primary key |
| category | uq_category_name | name | Unique constraint |

## Migration Strategy

For Phase II, use SQLModel's `create_all()` for initial schema creation:

```python
from sqlmodel import SQLModel, create_engine

def init_db():
    engine = create_engine(DATABASE_URL)
    SQLModel.metadata.create_all(engine)
```

Future phases may use Alembic for migrations.
