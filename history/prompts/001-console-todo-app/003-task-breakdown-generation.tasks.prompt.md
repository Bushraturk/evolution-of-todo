---
id: 003
title: Task Breakdown for Console Todo App
stage: tasks
date: 2025-12-28
surface: agent
model: claude-sonnet-4-5-20250929
feature: 001-console-todo-app
branch: 001-console-todo-app
user: Bushraturk
command: /sp.tasks
labels: ["tasks", "phase-1", "implementation", "breakdown"]
links:
  spec: specs/001-console-todo-app/spec.md
  ticket: null
  adr: null
  pr: null
files:
  - specs/001-console-todo-app/tasks.md
tests:
  - null
---

## Prompt

/sp.tasks

Generate task breakdown for Console Todo App based on spec.md (5 user stories), plan.md (project structure), data-model.md (Task entity), and contracts/cli-commands.md (6 CLI commands).

## Response snapshot

Generated comprehensive tasks.md with 58 tasks across 8 phases:

**Phase Structure**:
| Phase | Description | Tasks |
|-------|-------------|-------|
| 1 | Setup | 9 |
| 2 | Foundational | 6 |
| 3 | US1: Add Task (P1) | 9 |
| 4 | US2: View Tasks (P1) | 7 |
| 5 | US3: Mark Complete (P1) | 7 |
| 6 | US4: Update Task (P2) | 7 |
| 7 | US5: Delete Task (P2) | 6 |
| 8 | Polish | 7 |

**User Story Mapping**:
- US1 (Add): T016-T024 - add_task service, argparse CLI, add command
- US2 (View): T025-T031 - get_all_tasks service, list command, formatting
- US3 (Complete): T032-T038 - toggle_complete service, complete command
- US4 (Update): T039-T045 - update_task service, update command
- US5 (Delete): T046-T051 - delete_task service, delete command

**Key Features**:
- All tasks follow checklist format: `- [ ] [ID] [P?] [Story?] Description with path`
- Parallel opportunities identified (7 __init__.py files, test files)
- Dependencies mapped (Foundational blocks all stories)
- MVP scope defined (Phases 1-5 = 38 tasks)
- Independent test criteria for each user story

**File Paths**:
- src/models/task.py - Task dataclass
- src/services/task_service.py - CRUD operations
- src/services/exceptions.py - Custom exceptions
- src/cli/commands.py - argparse CLI
- src/main.py - Entry point
- tests/unit/test_*.py - Unit tests
- tests/integration/test_cli.py - E2E tests

## Outcome

- Impact: Complete implementation roadmap with 58 executable tasks
- Tests: Test tasks included (T015, T024, T031, T038, T045, T051, T056)
- Files: specs/001-console-todo-app/tasks.md
- Next prompts: /sp.implement to execute tasks via Claude Code
- Reflection: Tasks are specific with exact file paths, immediately executable by LLM

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All tasks follow checklist format, dependencies clear
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Proceed with /sp.implement
