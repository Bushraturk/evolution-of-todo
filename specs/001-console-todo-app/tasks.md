# Tasks: Console Todo App

**Input**: Design documents from `/specs/001-console-todo-app/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/cli-commands.md, research.md, quickstart.md

**Tests**: Tests are included as the constitution recommends demonstrable acceptance tests for all 5 Basic Level features.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Single project**: `src/`, `tests/` at repository root
- Paths assume single project structure per plan.md

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [x] T001 Create project directory structure: src/, src/models/, src/services/, src/cli/, tests/, tests/unit/, tests/integration/
- [x] T002 Create pyproject.toml with project metadata, Python 3.13+ requirement, and pytest dev dependency
- [x] T003 [P] Create src/__init__.py with package docstring
- [x] T004 [P] Create src/models/__init__.py
- [x] T005 [P] Create src/services/__init__.py
- [x] T006 [P] Create src/cli/__init__.py
- [x] T007 [P] Create tests/__init__.py
- [x] T008 [P] Create tests/unit/__init__.py
- [x] T009 [P] Create tests/integration/__init__.py

**Checkpoint**: Project structure ready for implementation

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [x] T010 Create custom exceptions (TaskNotFoundError, ValidationError) in src/services/exceptions.py
- [x] T011 Create Task dataclass with id, title, description, completed, created_at fields in src/models/task.py
- [x] T012 Add title validation (non-empty, max 200 chars) to Task model in src/models/task.py
- [x] T013 Create TaskService class with internal storage (_tasks dict, _next_id counter) in src/services/task_service.py
- [x] T014 [P] Create tests/conftest.py with pytest fixtures for TaskService and sample tasks
- [x] T015 [P] Create tests/unit/test_task.py with Task model unit tests (creation, validation, defaults)

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 3: User Story 1 - Add New Task (Priority: P1)

**Goal**: Users can add new tasks with title and optional description

**Independent Test**: Run `todo add "Test task" -d "Description"` and verify task appears in list with correct ID, title, description, and incomplete status

### Implementation for User Story 1

- [x] T016 [US1] Implement add_task(title, description) method in TaskService in src/services/task_service.py
- [x] T017 [US1] Add ID auto-generation logic in add_task method in src/services/task_service.py
- [x] T018 [US1] Add title validation in add_task (raise ValidationError if empty) in src/services/task_service.py
- [x] T019 [US1] Create argparse CLI structure with subcommands in src/cli/commands.py
- [x] T020 [US1] Implement 'add' subcommand with title argument and --description option in src/cli/commands.py
- [x] T021 [US1] Add success output formatting for add command in src/cli/commands.py
- [x] T022 [US1] Add error handling for validation errors in add command in src/cli/commands.py
- [x] T023 [US1] Create application entry point in src/main.py
- [x] T024 [P] [US1] Create tests/unit/test_task_service.py with add_task tests (success, validation errors)

**Checkpoint**: User Story 1 complete - users can add tasks via CLI

---

## Phase 4: User Story 2 - View Task List (Priority: P1)

**Goal**: Users can view all tasks with ID, title, description, and completion status

**Independent Test**: Add multiple tasks, run `todo list`, verify all tasks displayed with correct format and status indicators

### Implementation for User Story 2

- [x] T025 [US2] Implement get_all_tasks() method in TaskService in src/services/task_service.py
- [x] T026 [US2] Implement 'list' subcommand in src/cli/commands.py
- [x] T027 [US2] Add table formatting for task list display in src/cli/commands.py
- [x] T028 [US2] Add status indicators ([ ] and [x]) for completion status in src/cli/commands.py
- [x] T029 [US2] Add "No tasks found" message for empty list in src/cli/commands.py
- [x] T030 [US2] Add task count summary (total, completed, pending) in src/cli/commands.py
- [x] T031 [P] [US2] Add get_all_tasks tests to tests/unit/test_task_service.py

**Checkpoint**: User Stories 1 AND 2 complete - users can add and view tasks

---

## Phase 5: User Story 3 - Mark Task as Complete (Priority: P1)

**Goal**: Users can toggle task completion status by ID

**Independent Test**: Add a task, run `todo complete 1`, verify status changes to [x], run again to toggle back to [ ]

### Implementation for User Story 3

- [x] T032 [US3] Implement get_task(id) method in TaskService in src/services/task_service.py
- [x] T033 [US3] Implement toggle_complete(id) method in TaskService in src/services/task_service.py
- [x] T034 [US3] Add TaskNotFoundError handling in toggle_complete in src/services/task_service.py
- [x] T035 [US3] Implement 'complete' subcommand with id argument in src/cli/commands.py
- [x] T036 [US3] Add success output for complete/incomplete toggle in src/cli/commands.py
- [x] T037 [US3] Add error handling for not found and invalid ID in src/cli/commands.py
- [x] T038 [P] [US3] Add toggle_complete tests to tests/unit/test_task_service.py

**Checkpoint**: User Stories 1, 2, AND 3 complete - core MVP functionality working

---

## Phase 6: User Story 4 - Update Task Details (Priority: P2)

**Goal**: Users can update task title and/or description by ID

**Independent Test**: Add a task, run `todo update 1 -t "New title"`, verify title changed in list

### Implementation for User Story 4

- [x] T039 [US4] Implement update_task(id, title, description) method in TaskService in src/services/task_service.py
- [x] T040 [US4] Add validation for empty title in update_task in src/services/task_service.py
- [x] T041 [US4] Add "no changes provided" validation in update_task in src/services/task_service.py
- [x] T042 [US4] Implement 'update' subcommand with id, --title, --description options in src/cli/commands.py
- [x] T043 [US4] Add success output formatting for update command in src/cli/commands.py
- [x] T044 [US4] Add error handling for not found, empty title, no changes in src/cli/commands.py
- [x] T045 [P] [US4] Add update_task tests to tests/unit/test_task_service.py

**Checkpoint**: User Stories 1-4 complete - all CRUD except delete working

---

## Phase 7: User Story 5 - Delete Task (Priority: P2)

**Goal**: Users can remove tasks by ID

**Independent Test**: Add a task, run `todo delete 1`, verify task no longer appears in list

### Implementation for User Story 5

- [x] T046 [US5] Implement delete_task(id) method in TaskService in src/services/task_service.py
- [x] T047 [US5] Add TaskNotFoundError handling in delete_task in src/services/task_service.py
- [x] T048 [US5] Implement 'delete' subcommand with id argument in src/cli/commands.py
- [x] T049 [US5] Add success output with deleted task title in src/cli/commands.py
- [x] T050 [US5] Add error handling for not found in src/cli/commands.py
- [x] T051 [P] [US5] Add delete_task tests to tests/unit/test_task_service.py

**Checkpoint**: All 5 user stories complete - full CRUD functionality

---

## Phase 8: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [x] T052 [P] Implement 'help' subcommand with usage examples in src/cli/commands.py
- [x] T053 [P] Add --version flag showing "Todo App v1.0.0 (Phase I)" in src/cli/commands.py
- [x] T054 [P] Add --help flag support to all subcommands in src/cli/commands.py
- [x] T055 Create README.md with installation and usage instructions
- [x] T056 [P] Create tests/integration/test_cli.py with end-to-end CLI tests
- [x] T057 Run all tests and verify 100% pass rate
- [x] T058 Run quickstart.md validation (manual walkthrough of example session)

---

## Dependencies & Execution Order

### Phase Dependencies

```
Phase 1 (Setup)
    │
    ▼
Phase 2 (Foundational) ──── BLOCKS ALL USER STORIES
    │
    ├──────────────────────────────────────┐
    ▼                                      ▼
Phase 3 (US1: Add)                    Phase 4 (US2: View)
    │                                      │
    └──────────────┬───────────────────────┘
                   ▼
           Phase 5 (US3: Complete)
                   │
    ┌──────────────┴──────────────┐
    ▼                             ▼
Phase 6 (US4: Update)      Phase 7 (US5: Delete)
    │                             │
    └──────────────┬──────────────┘
                   ▼
           Phase 8 (Polish)
```

### User Story Dependencies

- **User Story 1 (Add)**: Depends on Phase 2 - No dependencies on other stories
- **User Story 2 (View)**: Depends on Phase 2 - Independent, but best tested with US1
- **User Story 3 (Complete)**: Depends on US1 (needs tasks to complete) and US2 (to verify)
- **User Story 4 (Update)**: Depends on US1 (needs tasks to update)
- **User Story 5 (Delete)**: Depends on US1 (needs tasks to delete)

### Within Each User Story

- Service methods before CLI commands
- Core implementation before error handling
- Implementation before tests (tests validate implementation)

### Parallel Opportunities

```bash
# Phase 1 - All __init__.py files can run in parallel:
T003, T004, T005, T006, T007, T008, T009

# Phase 2 - Conftest and model tests in parallel:
T014, T015

# Each User Story - Tests can run in parallel with next story prep:
T024 (US1 tests), T031 (US2 tests), T038 (US3 tests), T045 (US4 tests), T051 (US5 tests)

# Phase 8 - Help, version, and CLI tests in parallel:
T052, T053, T054, T056
```

---

## Parallel Example: Phase 1 Setup

```bash
# Launch all __init__.py files together:
Task T003: "Create src/__init__.py with package docstring"
Task T004: "Create src/models/__init__.py"
Task T005: "Create src/services/__init__.py"
Task T006: "Create src/cli/__init__.py"
Task T007: "Create tests/__init__.py"
Task T008: "Create tests/unit/__init__.py"
Task T009: "Create tests/integration/__init__.py"
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Add Task)
4. Complete Phase 4: User Story 2 (View Tasks)
5. Complete Phase 5: User Story 3 (Mark Complete)
6. **STOP and VALIDATE**: Test full workflow (add → view → complete → view)
7. Deploy/demo if ready - this is a functional MVP!

### Full Implementation

1. Complete MVP (Phases 1-5)
2. Add Phase 6: User Story 4 (Update)
3. Add Phase 7: User Story 5 (Delete)
4. Complete Phase 8: Polish (help, version, README, integration tests)
5. Final validation against all acceptance scenarios

### Task Count Summary

| Phase | Description | Task Count | Status |
|-------|-------------|------------|--------|
| 1 | Setup | 9 | COMPLETE |
| 2 | Foundational | 6 | COMPLETE |
| 3 | US1: Add Task | 9 | COMPLETE |
| 4 | US2: View Tasks | 7 | COMPLETE |
| 5 | US3: Mark Complete | 7 | COMPLETE |
| 6 | US4: Update Task | 7 | COMPLETE |
| 7 | US5: Delete Task | 6 | COMPLETE |
| 8 | Polish | 7 | COMPLETE |
| **TOTAL** | | **58** | **ALL COMPLETE** |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Avoid: vague tasks, same file conflicts, cross-story dependencies that break independence

## Implementation Results

**Date**: 2025-12-28
**Tests**: 62 passed, 0 failed
**Coverage**: All 5 user stories implemented and tested
