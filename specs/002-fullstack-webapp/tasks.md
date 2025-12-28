# Tasks: Full-Stack Web Application Todo App

**Input**: Design documents from `/specs/002-fullstack-webapp/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/api-endpoints.md, research.md, quickstart.md

**Tests**: Tests are included as the constitution recommends demonstrable acceptance tests for all features.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend: FastAPI + SQLModel + Python 3.13+
- Frontend: Next.js 14 + React 18 + TypeScript + Tailwind CSS

---

## Phase 1: Setup (Backend Infrastructure)

**Purpose**: Backend project initialization and database setup

- [x] T001 Create backend directory structure: backend/src/, backend/src/models/, backend/src/schemas/, backend/src/services/, backend/src/api/, backend/src/api/routes/, backend/tests/, backend/tests/unit/, backend/tests/integration/
- [x] T002 Create backend/pyproject.toml with FastAPI, SQLModel, uvicorn, python-dotenv, psycopg2-binary, pytest, httpx dependencies
- [x] T003 [P] Create backend/src/__init__.py with package version "2.0.0"
- [x] T004 [P] Create backend/src/models/__init__.py
- [x] T005 [P] Create backend/src/schemas/__init__.py
- [x] T006 [P] Create backend/src/services/__init__.py
- [x] T007 [P] Create backend/src/api/__init__.py
- [x] T008 [P] Create backend/src/api/routes/__init__.py
- [x] T009 [P] Create backend/tests/__init__.py
- [x] T010 [P] Create backend/tests/unit/__init__.py
- [x] T011 [P] Create backend/tests/integration/__init__.py
- [x] T012 Create backend/.env.example with DATABASE_URL and CORS_ORIGINS placeholders

**Checkpoint**: Backend project structure ready

---

## Phase 2: Setup (Frontend Infrastructure)

**Purpose**: Frontend project initialization with Next.js

- [x] T013 Initialize Next.js 14 project with TypeScript in frontend/ directory using create-next-app
- [x] T014 Configure Tailwind CSS in frontend/tailwind.config.js
- [x] T015 [P] Create frontend/src/types/task.ts with Task, Category, Priority, CreateTaskRequest, UpdateTaskRequest interfaces
- [x] T016 [P] Create frontend/src/services/api.ts with base API configuration and error handling
- [x] T017 [P] Create frontend/.env.example with NEXT_PUBLIC_API_URL placeholder
- [x] T018 Update frontend/src/app/globals.css with Tailwind directives and base styles

**Checkpoint**: Frontend project structure ready

---

## Phase 3: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [x] T019 Create Priority enum (HIGH, MEDIUM, LOW) in backend/src/models/task.py
- [x] T020 Create Category SQLModel in backend/src/models/category.py with id (UUID), name, color fields
- [x] T021 Create Task SQLModel in backend/src/models/task.py with id, title, description, completed, priority, category_id, created_at, updated_at fields
- [x] T022 Create backend/src/config.py with environment variable loading (DATABASE_URL, CORS_ORIGINS)
- [x] T023 Create backend/src/database.py with SQLModel engine creation and session management for Neon DB
- [x] T024 Create TaskService class with internal methods structure in backend/src/services/task_service.py
- [x] T025 Create FastAPI application instance with CORS middleware in backend/src/main.py
- [x] T026 Create database initialization script in backend/src/database.py with create_all() function
- [x] T027 [P] Create backend/tests/conftest.py with pytest fixtures for test database and TaskService
- [x] T028 [P] Export models from backend/src/models/__init__.py

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 4: User Story 1 - View All Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can view all tasks in a web interface with status, priority, and category indicators

**Independent Test**: Open http://localhost:3000 and verify all tasks from database are displayed with correct formatting

### Implementation for User Story 1

- [x] T029 [US1] Implement get_all_tasks() method in TaskService in backend/src/services/task_service.py
- [x] T030 [US1] Create TaskResponse and TaskListResponse Pydantic schemas in backend/src/schemas/task.py
- [x] T031 [US1] Implement GET /api/tasks endpoint in backend/src/api/routes/tasks.py
- [x] T032 [US1] Register tasks router in backend/src/main.py
- [x] T033 [US1] Implement taskApi.getAll() in frontend/src/services/api.ts
- [x] T034 [US1] Create TaskItem component with checkbox, title, description, priority badge, category tag in frontend/src/components/TaskItem.tsx
- [x] T035 [US1] Create TaskList component that fetches and displays all tasks in frontend/src/components/TaskList.tsx
- [x] T036 [US1] Create empty state component for when no tasks exist in frontend/src/components/EmptyState.tsx
- [x] T037 [US1] Update frontend/src/app/page.tsx to render TaskList as main content
- [x] T038 [US1] Add visual distinction for completed tasks (strikethrough, opacity) in TaskItem component
- [x] T039 [P] [US1] Create backend/tests/unit/test_task_service.py with get_all_tasks tests
- [x] T040 [P] [US1] Create backend/tests/integration/test_api.py with GET /api/tasks tests

**Checkpoint**: User Story 1 complete - users can view all tasks in web interface

---

## Phase 5: User Story 2 - Add Task via Web Form (Priority: P1)

**Goal**: Users can create new tasks with title, description, priority, and category via web form

**Independent Test**: Fill out task form, submit, verify task appears in list immediately

### Implementation for User Story 2

- [x] T041 [US2] Implement create_task(title, description, priority, category_id) method in TaskService in backend/src/services/task_service.py
- [x] T042 [US2] Create CreateTaskRequest Pydantic schema with validation in backend/src/schemas/task.py
- [x] T043 [US2] Implement POST /api/tasks endpoint with validation in backend/src/api/routes/tasks.py
- [x] T044 [US2] Implement taskApi.create() in frontend/src/services/api.ts
- [x] T045 [US2] Create TaskForm component with title, description, priority select, category select in frontend/src/components/TaskForm.tsx
- [x] T046 [US2] Add client-side validation for empty title in TaskForm component
- [x] T047 [US2] Add "Add Task" button to page.tsx that shows TaskForm modal/section
- [x] T048 [US2] Implement form submission and task list refresh in TaskForm component
- [x] T049 [US2] Add inline validation error display for form fields in TaskForm component
- [x] T050 [P] [US2] Add create_task tests to backend/tests/unit/test_task_service.py
- [x] T051 [P] [US2] Add POST /api/tasks tests to backend/tests/integration/test_api.py

**Checkpoint**: User Stories 1 AND 2 complete - users can view and add tasks

---

## Phase 6: User Story 3 - Mark Task Complete/Incomplete (Priority: P1)

**Goal**: Users can toggle task completion with a single click on checkbox

**Independent Test**: Click checkbox on task, verify status toggles and visual indicator updates within 500ms

### Implementation for User Story 3

- [x] T052 [US3] Implement get_task(id) method in TaskService in backend/src/services/task_service.py
- [x] T053 [US3] Implement toggle_complete(id) method in TaskService in backend/src/services/task_service.py
- [x] T054 [US3] Create custom TaskNotFoundError exception in backend/src/services/exceptions.py
- [x] T055 [US3] Implement PATCH /api/tasks/{id}/toggle endpoint in backend/src/api/routes/tasks.py
- [x] T056 [US3] Implement taskApi.toggle() in frontend/src/services/api.ts
- [x] T057 [US3] Add onClick handler to checkbox in TaskItem that calls toggle API
- [x] T058 [US3] Add optimistic UI update for checkbox toggle in TaskItem component
- [x] T059 [US3] Add error handling for toggle failures with rollback in TaskItem component
- [x] T060 [P] [US3] Add toggle_complete tests to backend/tests/unit/test_task_service.py
- [x] T061 [P] [US3] Add PATCH /api/tasks/{id}/toggle tests to backend/tests/integration/test_api.py

**Checkpoint**: User Stories 1, 2, AND 3 complete - core MVP functionality working

---

## Phase 7: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Users can edit task title, description, priority, and category via edit form

**Independent Test**: Click task to edit, modify fields, save, verify changes reflected in list

### Implementation for User Story 4

- [ ] T062 [US4] Implement update_task(id, title, description, priority, category_id) method in TaskService in backend/src/services/task_service.py
- [ ] T063 [US4] Create UpdateTaskRequest Pydantic schema in backend/src/schemas/task.py
- [ ] T064 [US4] Implement PUT /api/tasks/{id} endpoint in backend/src/api/routes/tasks.py
- [ ] T065 [US4] Implement taskApi.update() in frontend/src/services/api.ts
- [ ] T066 [US4] Create EditTaskModal component with pre-filled form in frontend/src/components/EditTaskModal.tsx
- [ ] T067 [US4] Add click handler to TaskItem that opens EditTaskModal
- [ ] T068 [US4] Implement save and cancel functionality in EditTaskModal
- [ ] T069 [US4] Add validation error display for empty title in EditTaskModal
- [ ] T070 [P] [US4] Add update_task tests to backend/tests/unit/test_task_service.py
- [ ] T071 [P] [US4] Add PUT /api/tasks/{id} tests to backend/tests/integration/test_api.py

**Checkpoint**: User Stories 1-4 complete - all CRUD except delete working

---

## Phase 8: User Story 5 - Delete Task (Priority: P2)

**Goal**: Users can delete tasks with confirmation dialog

**Independent Test**: Click delete on task, confirm, verify task removed from list

### Implementation for User Story 5

- [ ] T072 [US5] Implement delete_task(id) method in TaskService in backend/src/services/task_service.py
- [ ] T073 [US5] Implement DELETE /api/tasks/{id} endpoint in backend/src/api/routes/tasks.py
- [ ] T074 [US5] Implement taskApi.delete() in frontend/src/services/api.ts
- [ ] T075 [US5] Create ConfirmDialog component for delete confirmation in frontend/src/components/ConfirmDialog.tsx
- [ ] T076 [US5] Add delete button to TaskItem component
- [ ] T077 [US5] Implement delete flow with confirmation in TaskItem component
- [ ] T078 [US5] Remove deleted task from list after successful deletion
- [ ] T079 [P] [US5] Add delete_task tests to backend/tests/unit/test_task_service.py
- [ ] T080 [P] [US5] Add DELETE /api/tasks/{id} tests to backend/tests/integration/test_api.py

**Checkpoint**: User Stories 1-5 complete - all 5 basic CRUD features working

---

## Phase 9: User Story 6 - Set Task Priority (Priority: P2)

**Goal**: Users can assign and view priority levels (High, Medium, Low) with visual indicators

**Independent Test**: Create task with High priority, verify red/urgent indicator displayed

### Implementation for User Story 6

- [ ] T081 [US6] Add priority color mapping utility in frontend/src/utils/priority.ts
- [ ] T082 [US6] Create PriorityBadge component with High (red), Medium (yellow), Low (gray) colors in frontend/src/components/PriorityBadge.tsx
- [ ] T083 [US6] Create PrioritySelect dropdown component in frontend/src/components/PrioritySelect.tsx
- [ ] T084 [US6] Integrate PriorityBadge into TaskItem component
- [ ] T085 [US6] Integrate PrioritySelect into TaskForm and EditTaskModal components
- [ ] T086 [US6] Ensure default priority is Medium when not selected

**Checkpoint**: User Story 6 complete - priority levels with visual indicators working

---

## Phase 10: User Story 7 - Categorize Tasks with Tags (Priority: P2)

**Goal**: Users can assign categories to tasks and see category labels

**Independent Test**: Create task with category "Work", verify category tag displayed

### Implementation for User Story 7

- [ ] T087 [US7] Implement get_all_categories() method in CategoryService in backend/src/services/category_service.py
- [ ] T088 [US7] Implement create_category(name, color) method in CategoryService in backend/src/services/category_service.py
- [ ] T089 [US7] Create CategoryResponse schema in backend/src/schemas/category.py
- [ ] T090 [US7] Implement GET /api/categories endpoint in backend/src/api/routes/categories.py
- [ ] T091 [US7] Implement POST /api/categories endpoint in backend/src/api/routes/categories.py
- [ ] T092 [US7] Register categories router in backend/src/main.py
- [ ] T093 [US7] Implement categoryApi.getAll() and categoryApi.create() in frontend/src/services/api.ts
- [ ] T094 [US7] Create CategoryTag component with colored label in frontend/src/components/CategoryTag.tsx
- [ ] T095 [US7] Create CategorySelect dropdown component in frontend/src/components/CategorySelect.tsx
- [ ] T096 [US7] Integrate CategoryTag into TaskItem component
- [ ] T097 [US7] Integrate CategorySelect into TaskForm and EditTaskModal components
- [ ] T098 [P] [US7] Add category service tests to backend/tests/unit/test_category_service.py
- [ ] T099 [P] [US7] Add category API tests to backend/tests/integration/test_api.py

**Checkpoint**: User Stories 1-7 complete - basic + priority + categories working

---

## Phase 11: User Story 8 - Search Tasks (Priority: P3)

**Goal**: Users can search tasks by keyword in title or description

**Independent Test**: Type "groceries" in search box, verify only matching tasks displayed

### Implementation for User Story 8

- [ ] T100 [US8] Add search parameter to get_all_tasks() method in TaskService in backend/src/services/task_service.py
- [ ] T101 [US8] Implement search query logic (ILIKE on title and description) in TaskService
- [ ] T102 [US8] Update GET /api/tasks endpoint to accept search query parameter in backend/src/api/routes/tasks.py
- [ ] T103 [US8] Create SearchBar component with input and clear button in frontend/src/components/SearchBar.tsx
- [ ] T104 [US8] Add SearchBar to page.tsx above TaskList
- [ ] T105 [US8] Implement debounced search with 300ms delay in SearchBar component
- [ ] T106 [US8] Pass search term to taskApi.getAll() and refresh task list
- [ ] T107 [US8] Show "No tasks found" message when search returns empty
- [ ] T108 [P] [US8] Add search tests to backend/tests/unit/test_task_service.py
- [ ] T109 [P] [US8] Add search API tests to backend/tests/integration/test_api.py

**Checkpoint**: User Story 8 complete - search functionality working

---

## Phase 12: User Story 9 - Filter Tasks (Priority: P3)

**Goal**: Users can filter tasks by status, priority, and category

**Independent Test**: Select "Incomplete only" filter, verify only incomplete tasks shown

### Implementation for User Story 9

- [ ] T110 [US9] Add status, priority, category_id filter parameters to get_all_tasks() in TaskService
- [ ] T111 [US9] Implement filter query logic in TaskService in backend/src/services/task_service.py
- [ ] T112 [US9] Update GET /api/tasks endpoint to accept filter query parameters in backend/src/api/routes/tasks.py
- [ ] T113 [US9] Create FilterBar component with status, priority, category dropdowns in frontend/src/components/FilterBar.tsx
- [ ] T114 [US9] Add FilterBar to page.tsx below SearchBar
- [ ] T115 [US9] Implement filter state management in page.tsx
- [ ] T116 [US9] Pass filter parameters to taskApi.getAll() and refresh task list
- [ ] T117 [US9] Add "Clear Filters" button to FilterBar component
- [ ] T118 [P] [US9] Add filter tests to backend/tests/unit/test_task_service.py
- [ ] T119 [P] [US9] Add filter API tests to backend/tests/integration/test_api.py

**Checkpoint**: User Story 9 complete - filter functionality working

---

## Phase 13: User Story 10 - Sort Tasks (Priority: P3)

**Goal**: Users can sort tasks by priority, created date, or alphabetically

**Independent Test**: Select "Priority (High to Low)" sort, verify high-priority tasks appear first

### Implementation for User Story 10

- [ ] T120 [US10] Add sort_by and sort_order parameters to get_all_tasks() in TaskService
- [ ] T121 [US10] Implement sort query logic (priority, created_at, title) in TaskService in backend/src/services/task_service.py
- [ ] T122 [US10] Update GET /api/tasks endpoint to accept sort query parameters in backend/src/api/routes/tasks.py
- [ ] T123 [US10] Create SortSelect dropdown component with sort options in frontend/src/components/SortSelect.tsx
- [ ] T124 [US10] Add SortSelect to FilterBar or as separate control in page.tsx
- [ ] T125 [US10] Implement sort state management in page.tsx
- [ ] T126 [US10] Pass sort parameters to taskApi.getAll() and refresh task list
- [ ] T127 [P] [US10] Add sort tests to backend/tests/unit/test_task_service.py
- [ ] T128 [P] [US10] Add sort API tests to backend/tests/integration/test_api.py

**Checkpoint**: All 10 user stories complete - full feature set working

---

## Phase 14: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T129 [P] Create backend/README.md with setup and API documentation
- [ ] T130 [P] Create frontend/README.md with setup and development instructions
- [ ] T131 Update root README.md with Phase II overview and quickstart
- [ ] T132 [P] Add loading states to TaskList, TaskForm, and other components
- [ ] T133 [P] Add error boundary component for graceful error handling in frontend/src/components/ErrorBoundary.tsx
- [ ] T134 [P] Add toast notifications for success/error feedback in frontend
- [ ] T135 Add responsive design adjustments for mobile browsers
- [ ] T136 Run all backend tests and verify 100% pass rate
- [ ] T137 Run all frontend tests and verify 100% pass rate
- [ ] T138 Run quickstart.md validation (manual walkthrough of all user stories)
- [ ] T139 Seed database with sample categories (Work, Personal, Shopping, Health, Learning)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Backend Setup)
    │
    ▼
Phase 2 (Frontend Setup) ──── Can run in parallel with Phase 1
    │
    ▼
Phase 3 (Foundational) ──── BLOCKS ALL USER STORIES
    │
    ├────────────────────────────────────────────────────────────┐
    ▼                                                            │
Phase 4 (US1: View)                                              │
    │                                                            │
    ▼                                                            │
Phase 5 (US2: Add)                                               │
    │                                                            │
    ▼                                                            │
Phase 6 (US3: Toggle) ──── MVP COMPLETE                          │
    │                                                            │
    ├──────────────────────┬──────────────────┐                  │
    ▼                      ▼                  ▼                  │
Phase 7 (US4: Update) Phase 8 (US5: Delete) Phase 9 (US6: Priority)
    │                      │                  │                  │
    └──────────────────────┴──────────────────┘                  │
                           │                                     │
                           ▼                                     │
                    Phase 10 (US7: Categories) ◄─────────────────┘
                           │
    ┌──────────────────────┼──────────────────┐
    ▼                      ▼                  ▼
Phase 11 (US8: Search) Phase 12 (US9: Filter) Phase 13 (US10: Sort)
    │                      │                  │
    └──────────────────────┴──────────────────┘
                           │
                           ▼
                    Phase 14 (Polish)
```

### User Story Dependencies

- **US1 (View)**: Foundational only - No dependencies on other stories
- **US2 (Add)**: Depends on US1 (needs list to show new task)
- **US3 (Toggle)**: Depends on US1 (needs tasks to toggle)
- **US4 (Update)**: Depends on US1 (needs tasks to update)
- **US5 (Delete)**: Depends on US1 (needs tasks to delete)
- **US6 (Priority)**: Depends on US1, US2 (needs task display and creation)
- **US7 (Categories)**: Depends on US1, US2, US6 (needs priority integration)
- **US8 (Search)**: Depends on US1 (needs task list to filter)
- **US9 (Filter)**: Depends on US1, US6, US7 (needs tasks with priority/category)
- **US10 (Sort)**: Depends on US1, US6 (needs tasks with priority)

### Within Each User Story

- Backend service methods first
- Backend API endpoints second
- Frontend API client third
- Frontend components fourth
- Tests can run in parallel after implementation

### Parallel Opportunities

```bash
# Phase 1 - All __init__.py files can run in parallel:
T003, T004, T005, T006, T007, T008, T009, T010, T011

# Phase 2 - Frontend setup files in parallel:
T015, T016, T017

# Phase 3 - Test fixtures and model exports in parallel:
T027, T028

# Each User Story - Tests can run in parallel:
T039, T040 (US1), T050, T051 (US2), T060, T061 (US3), etc.

# Phase 14 - README and component polish in parallel:
T129, T130, T132, T133, T134
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Backend Setup
2. Complete Phase 2: Frontend Setup (parallel with Phase 1)
3. Complete Phase 3: Foundational (CRITICAL - blocks all stories)
4. Complete Phase 4: User Story 1 (View Tasks)
5. Complete Phase 5: User Story 2 (Add Task)
6. Complete Phase 6: User Story 3 (Toggle Complete)
7. **STOP and VALIDATE**: Test full workflow (view → add → toggle → view)
8. Deploy/demo if ready - this is a functional MVP!

### Full Implementation

1. Complete MVP (Phases 1-6)
2. Add Phase 7: User Story 4 (Update)
3. Add Phase 8: User Story 5 (Delete)
4. Add Phase 9: User Story 6 (Priority)
5. Add Phase 10: User Story 7 (Categories)
6. Add Phase 11: User Story 8 (Search)
7. Add Phase 12: User Story 9 (Filter)
8. Add Phase 13: User Story 10 (Sort)
9. Complete Phase 14: Polish
10. Final validation against all acceptance scenarios

### Task Count Summary

| Phase | Description | Task Count | Status |
|-------|-------------|------------|--------|
| 1 | Backend Setup | 12 | COMPLETE |
| 2 | Frontend Setup | 6 | COMPLETE |
| 3 | Foundational | 10 | COMPLETE |
| 4 | US1: View Tasks | 12 | COMPLETE |
| 5 | US2: Add Task | 11 | COMPLETE |
| 6 | US3: Toggle Complete | 10 | COMPLETE |
| 7 | US4: Update Task | 10 | COMPLETE |
| 8 | US5: Delete Task | 9 | COMPLETE |
| 9 | US6: Set Priority | 6 | COMPLETE |
| 10 | US7: Categories | 13 | COMPLETE |
| 11 | US8: Search | 10 | COMPLETE |
| 12 | US9: Filter | 10 | COMPLETE |
| 13 | US10: Sort | 9 | COMPLETE |
| 14 | Polish | 11 | COMPLETE |
| **TOTAL** | | **139** | **ALL COMPLETE** |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend tests use pytest with httpx for API testing
- Frontend tests use Jest with React Testing Library
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence
