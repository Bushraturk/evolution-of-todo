# Data Model: Console Todo App

**Feature**: 001-console-todo-app
**Date**: 2025-12-28
**Status**: Complete

## Entities

### Task

The core entity representing a single todo item.

#### Attributes

| Attribute | Type | Required | Default | Constraints | Description |
|-----------|------|----------|---------|-------------|-------------|
| `id` | `int` | Yes | Auto-generated | Positive integer, unique, immutable | Unique identifier for the task |
| `title` | `str` | Yes | None | 1-200 characters, non-empty | Brief description of what needs to be done |
| `description` | `str` | No | `""` | 0-1000 characters | Detailed information about the task |
| `completed` | `bool` | Yes | `False` | True/False | Whether the task is done |
| `created_at` | `datetime` | Yes | Auto-generated | ISO 8601 format | Timestamp when task was created |

#### Validation Rules

1. **Title Validation**:
   - MUST NOT be empty or whitespace-only
   - MUST NOT exceed 200 characters
   - MUST be stripped of leading/trailing whitespace

2. **Description Validation**:
   - MAY be empty
   - MUST NOT exceed 1000 characters
   - SHOULD be stripped of leading/trailing whitespace

3. **ID Validation**:
   - MUST be auto-generated (not user-provided on create)
   - MUST be positive integer
   - MUST be unique within the task list
   - MUST NOT be reused after deletion

#### State Transitions

```
┌─────────────────┐
│    CREATED      │
│  (completed=    │
│    False)       │
└────────┬────────┘
         │
         │ mark_complete()
         ▼
┌─────────────────┐
│   COMPLETED     │
│  (completed=    │
│    True)        │
└────────┬────────┘
         │
         │ mark_incomplete()
         ▼
┌─────────────────┐
│  INCOMPLETE     │
│  (completed=    │
│    False)       │
└─────────────────┘
```

#### Example Instance

```python
Task(
    id=1,
    title="Buy groceries",
    description="Milk, eggs, bread",
    completed=False,
    created_at=datetime(2025, 12, 28, 10, 30, 0)
)
```

### TaskList (Service Layer)

Collection manager for Task entities. This is not a data model but a service that manages the Task collection.

#### Operations

| Operation | Input | Output | Side Effects |
|-----------|-------|--------|--------------|
| `add_task(title, description?)` | title: str, description: str | Task | Creates new task, increments ID counter |
| `get_all_tasks()` | None | List[Task] | None |
| `get_task(id)` | id: int | Task | None |
| `update_task(id, title?, description?)` | id: int, fields | Task | Modifies existing task |
| `delete_task(id)` | id: int | bool | Removes task from collection |
| `toggle_complete(id)` | id: int | Task | Flips completed status |

#### Error Conditions

| Error | Trigger | Message |
|-------|---------|---------|
| `TaskNotFoundError` | ID doesn't exist | "Task with ID {id} not found." |
| `ValidationError` | Empty title on create/update | "Task title is required." |
| `ValidationError` | Title exceeds 200 chars | "Task title must be 200 characters or less." |

## Data Flow

```
User Input (CLI)
      │
      ▼
┌─────────────────┐
│   CLI Layer     │  Parses arguments, validates input format
│   (cli/main.py) │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Service Layer   │  Business logic, validation, CRUD operations
│ (services/      │
│  task_service)  │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Model Layer    │  Data structure, field definitions
│ (models/task)   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  In-Memory      │  Dict[int, Task] storage
│  Storage        │
└─────────────────┘
```

## Storage Schema

For Phase I, tasks are stored in a Python dictionary:

```python
# Internal storage structure
_tasks: Dict[int, Task] = {}
_next_id: int = 1
```

**Note**: This schema will evolve in Phase II to use SQLModel with Neon DB.

## Display Format

When listing tasks, the following format is used:

```
ID  Status  Title                Description
─────────────────────────────────────────────────
1   [ ]     Buy groceries        Milk, eggs, bread
2   [x]     Call mom
3   [ ]     Write report         Q4 sales analysis
```

- `[ ]` = Incomplete task
- `[x]` = Completed task
- Description truncated if exceeds display width
