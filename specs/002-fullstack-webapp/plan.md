# Implementation Plan: Full-Stack Web Application Todo App

**Branch**: `002-fullstack-webapp` | **Date**: 2025-12-28 | **Spec**: [spec.md](./spec.md)
**Input**: Feature specification from `/specs/002-fullstack-webapp/spec.md`

## Summary

Build a full-stack web application todo app with Next.js frontend and FastAPI backend using SQLModel ORM with Neon DB (PostgreSQL). Implements all 5 basic CRUD features plus intermediate features (priorities, categories, search, filter, sort). Monorepo structure with `backend/` and `frontend/` directories.

## Technical Context

**Language/Version**: Python 3.13+ (backend), TypeScript/JavaScript (frontend)
**Primary Dependencies**:
- Backend: FastAPI, SQLModel, uvicorn, python-dotenv
- Frontend: Next.js 14+, React 18+, TypeScript, Tailwind CSS
**Storage**: Neon DB (PostgreSQL) via SQLModel ORM
**Testing**: pytest (backend), Jest + React Testing Library (frontend)
**Target Platform**: Web browsers (Chrome 90+, Firefox 88+, Safari 14+, Edge 90+)
**Project Type**: Web application (monorepo with backend/ and frontend/)
**Performance Goals**:
- Task list load <3 seconds
- Search results <1 second
- Toggle completion feedback <500ms
- Support 1000 tasks without degradation
**Constraints**:
- Single-user operation (no authentication for Phase II)
- No offline support
- Internet connectivity required
**Scale/Scope**: 1000+ tasks, single user, web interface

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

| Principle | Status | Notes |
|-----------|--------|-------|
| I. Spec-Driven Development | ✅ PASS | spec.md created with 10 user stories, 16 FRs |
| II. No Manual Code | ✅ PASS | All code will be generated via Claude Code |
| III. Clean Python Architecture | ✅ PASS | Monorepo with backend/frontend separation |
| IV. Test-First Development | ✅ PASS | pytest + Jest testing planned |
| V. Progressive Enhancement | ✅ PASS | Basic (5) + Intermediate (5) features |
| VI. Agentic Dev Stack Workflow | ✅ PASS | Following /sp.plan workflow |

**Gate Status**: PASSED - Proceed to Phase 0

## Project Structure

### Documentation (this feature)

```text
specs/002-fullstack-webapp/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
│   └── api-endpoints.md # REST API contract
└── tasks.md             # Phase 2 output (/sp.tasks command)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and environment
│   ├── database.py          # Database connection (Neon DB)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── task.py          # Task SQLModel
│   │   └── category.py      # Category SQLModel
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── task.py          # Pydantic request/response schemas
│   ├── services/
│   │   ├── __init__.py
│   │   └── task_service.py  # Business logic
│   └── api/
│       ├── __init__.py
│       └── routes/
│           ├── __init__.py
│           └── tasks.py     # Task endpoints
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── unit/
│   │   └── test_task_service.py
│   └── integration/
│       └── test_api.py
├── pyproject.toml
├── .env.example
└── README.md

frontend/
├── src/
│   ├── app/
│   │   ├── layout.tsx       # Root layout
│   │   ├── page.tsx         # Home page (task list)
│   │   └── globals.css      # Global styles
│   ├── components/
│   │   ├── TaskList.tsx     # Task list component
│   │   ├── TaskItem.tsx     # Single task component
│   │   ├── TaskForm.tsx     # Add/Edit task form
│   │   ├── SearchBar.tsx    # Search component
│   │   ├── FilterBar.tsx    # Filter component
│   │   └── SortSelect.tsx   # Sort dropdown
│   ├── services/
│   │   └── api.ts           # API client
│   └── types/
│       └── task.ts          # TypeScript interfaces
├── tests/
│   └── components/
│       └── TaskList.test.tsx
├── package.json
├── tsconfig.json
├── tailwind.config.js
├── next.config.js
└── README.md
```

**Structure Decision**: Monorepo with `backend/` (FastAPI + SQLModel) and `frontend/` (Next.js + React) directories per constitution Phase II requirements.

## Complexity Tracking

> No violations requiring justification. Architecture follows constitution guidelines.

## Technical Decisions

### Backend Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | FastAPI | Constitution mandates FastAPI for Phase II |
| ORM | SQLModel | Constitution mandates SQLModel; combines Pydantic + SQLAlchemy |
| Database | Neon DB (PostgreSQL) | Constitution mandates Neon DB for Phase II |
| API Style | REST | Spec requires RESTful API (FR-014) |
| UUID Generation | Python uuid4 | Spec requires UUID for task IDs |

### Frontend Architecture

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | Next.js 14+ (App Router) | Constitution mandates Next.js |
| Styling | Tailwind CSS | Modern, utility-first, fast development |
| State Management | React useState/useEffect | Simple state; no Redux needed for single-user |
| HTTP Client | fetch API | Built-in, no additional dependencies |
| Form Handling | Controlled components | Simple validation, clear data flow |

### Database Schema

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Primary Key | UUID | Spec requires UUID for task IDs |
| Priority | Enum (High, Medium, Low) | FR-009 specifies three levels |
| Category | Separate table | Allows reusability and color association |
| Timestamps | created_at, updated_at | Spec requires for sorting and audit |

## API Design Summary

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/api/tasks` | GET | List all tasks (with query params for filter/sort/search) |
| `/api/tasks` | POST | Create new task |
| `/api/tasks/{id}` | GET | Get single task |
| `/api/tasks/{id}` | PUT | Update task |
| `/api/tasks/{id}` | DELETE | Delete task |
| `/api/tasks/{id}/toggle` | PATCH | Toggle completion status |
| `/api/categories` | GET | List all categories |
| `/api/categories` | POST | Create new category |

## Environment Variables

### Backend (.env)
```
DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
CORS_ORIGINS=http://localhost:3000
```

### Frontend (.env.local)
```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## Development Workflow

1. **Backend First**: Set up FastAPI with SQLModel models and database connection
2. **API Endpoints**: Implement REST endpoints with proper validation
3. **Frontend Setup**: Initialize Next.js with TypeScript and Tailwind
4. **UI Components**: Build task list, form, and filter components
5. **Integration**: Connect frontend to backend API
6. **Testing**: Unit tests (backend) + component tests (frontend)

## Risk Mitigation

| Risk | Mitigation |
|------|------------|
| Neon DB connection issues | Environment variable configuration, connection pooling |
| CORS errors | Proper FastAPI CORS middleware configuration |
| Type mismatches | Shared types between Pydantic schemas and TypeScript interfaces |
| Performance with 1000 tasks | Pagination ready (optional), efficient queries |
