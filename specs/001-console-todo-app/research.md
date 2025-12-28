# Research: Console Todo App

**Feature**: 001-console-todo-app
**Date**: 2025-12-28
**Status**: Complete

## Technical Decisions

### 1. CLI Framework Selection

**Decision**: Use `argparse` (Python standard library)

**Rationale**:
- Built into Python 3.13+ - no additional dependencies
- Sufficient for Phase I simple command structure
- Well-documented and widely understood
- Supports subcommands for operations (add, list, update, delete, complete)

**Alternatives Considered**:
| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| `click` | Rich features, decorators | External dependency | Adds complexity for simple CLI |
| `typer` | Type hints, auto-completion | External dependency | Overkill for 5 commands |
| `argparse` | Built-in, no deps | More verbose | **Selected** |

### 2. Data Storage Approach

**Decision**: Python dictionary with auto-incrementing integer keys

**Rationale**:
- In-memory storage per constitution (Phase I requirement)
- O(1) lookup by ID
- Simple implementation, easy to test
- Natural fit for CRUD operations

**Alternatives Considered**:
| Option | Pros | Cons | Rejected Because |
|--------|------|------|------------------|
| List with index | Simple iteration | O(n) lookup, index shifts on delete | Poor performance for ID-based ops |
| Dict with UUID | Globally unique | Harder to type manually | User unfriendly for CLI |
| Dict with int ID | Fast lookup, user-friendly | Gaps after deletion | **Selected** - gaps acceptable |

### 3. Project Structure

**Decision**: Single project with `src/` directory following clean architecture

**Rationale**:
- Constitution mandates: `src/` with `models/`, `services/`, `cli/` modules
- Dependencies flow: CLI → Services → Models
- Prepares for Phase II migration to backend/frontend structure

**Structure**:
```
src/
├── __init__.py
├── models/
│   ├── __init__.py
│   └── task.py          # Task dataclass
├── services/
│   ├── __init__.py
│   └── task_service.py  # TaskService with CRUD operations
├── cli/
│   ├── __init__.py
│   └── main.py          # argparse CLI entry point
└── main.py              # Application entry point
```

### 4. Task Model Design

**Decision**: Python `dataclass` with auto-generated fields

**Rationale**:
- `dataclass` provides clean, immutable-friendly structure
- Auto-generates `__init__`, `__repr__`, `__eq__`
- Type hints for better code documentation
- Easy to extend for Phase II (add priority, tags, due_date)

**Fields**:
```python
@dataclass
class Task:
    id: int                    # Auto-generated, read-only
    title: str                 # Required, max 200 chars
    description: str = ""      # Optional
    completed: bool = False    # Default incomplete
    created_at: datetime       # Auto-generated
```

### 5. ID Generation Strategy

**Decision**: Class-level counter with auto-increment

**Rationale**:
- Simple, predictable IDs (1, 2, 3...)
- User-friendly for CLI input
- Counter persists during runtime
- Gaps acceptable after deletion (no re-use)

### 6. Testing Framework

**Decision**: `pytest` with test directory structure

**Rationale**:
- Constitution mandates pytest
- Industry standard for Python
- Rich assertion capabilities
- Easy fixture management

**Test Structure**:
```
tests/
├── __init__.py
├── unit/
│   ├── __init__.py
│   ├── test_task.py
│   └── test_task_service.py
└── integration/
    ├── __init__.py
    └── test_cli.py
```

### 7. Package Manager

**Decision**: UV (as specified in constitution)

**Rationale**:
- Constitution mandates UV for Phase I
- Fast dependency resolution
- Modern Python tooling
- Compatible with pyproject.toml

### 8. Error Handling Strategy

**Decision**: Custom exceptions with user-friendly messages

**Rationale**:
- Clear separation between internal errors and user messages
- FR-008 requires appropriate error messages
- Enables consistent error formatting in CLI

**Exceptions**:
- `TaskNotFoundError`: When ID doesn't exist
- `ValidationError`: When input validation fails (empty title, title too long)

## Constitution Compliance Check

| Principle | Status | Evidence |
|-----------|--------|----------|
| I. Spec-Driven Development | PASS | spec.md created before plan.md |
| II. No Manual Code | PASS | Implementation via Claude Code |
| III. Clean Python Architecture | PASS | src/ with models/, services/, cli/ |
| IV. Test-First Development | READY | pytest structure defined |
| V. Progressive Enhancement | PASS | Basic features only (P1, P2) |
| VI. Agentic Dev Stack Workflow | PASS | Following specify → plan → tasks flow |

## Open Questions Resolved

All technical decisions made. No NEEDS CLARIFICATION items remain.

## Next Steps

1. Create `data-model.md` with Task entity details
2. Create `contracts/` with CLI command specifications
3. Create `quickstart.md` with setup and usage instructions
4. Proceed to `/sp.tasks` for task breakdown
