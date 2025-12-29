# Tasks: User Authentication & Multi-User Support

**Input**: Design documents from `/specs/003-user-authentication/`
**Prerequisites**: plan.md (required), spec.md (required), data-model.md, contracts/api-endpoints.md, research.md, quickstart.md

**Tests**: Tests are included as the constitution recommends demonstrable acceptance tests for auth features.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- Backend: FastAPI + SQLModel + Python 3.13+
- Frontend: Next.js 14 + React 18 + TypeScript + Better Auth

---

## Phase 1: Setup (Backend Auth Infrastructure)

**Purpose**: Backend project auth module setup and dependencies

- [X] T001 Add python-jose[cryptography] and httpx dependencies to backend/pyproject.toml
- [X] T002 Create backend/src/auth/__init__.py with module exports
- [X] T003 [P] Create backend/src/auth/config.py with JWKS_URL, JWT_ISSUER environment variables
- [X] T004 [P] Update backend/.env.example with JWKS_URL and JWT_ISSUER placeholders

**Checkpoint**: Backend auth module structure ready

---

## Phase 2: Setup (Frontend Auth Infrastructure)

**Purpose**: Frontend Better Auth setup and dependencies

- [X] T005 Install Better Auth dependencies: npm install better-auth @better-auth/pg in frontend/
- [X] T006 [P] Update frontend/.env.example with BETTER_AUTH_SECRET and BETTER_AUTH_URL placeholders
- [X] T007 Create frontend/src/lib/auth.ts with Better Auth server configuration and JWT plugin
- [X] T008 Create frontend/src/lib/auth-client.ts with Better Auth client configuration and jwtClient plugin
- [X] T009 Create frontend/src/app/api/auth/[...all]/route.ts with Better Auth handler using toNextJsHandler

**Checkpoint**: Frontend auth infrastructure ready

---

## Phase 3: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

- [X] T010 Create backend/src/auth/dependencies.py with get_current_user JWT verification dependency
- [X] T011 Add user_id field (TEXT, nullable initially) to Task model in backend/src/models/task.py
- [ ] T012 Run database migration to add user_id column to task table
- [ ] T013 Delete existing tasks from database (clean slate for multi-user)
- [X] T014 Make user_id column NOT NULL after data cleanup in backend/src/models/task.py
- [ ] T015 Create index idx_task_user_id on task.user_id in database
- [ ] T016 Run Better Auth CLI migrations to create user, session, account tables: npx @better-auth/cli migrate
- [X] T017 Update TaskService.get_all_tasks() to accept user_id parameter in backend/src/services/task_service.py
- [X] T018 Update TaskService.create_task() to require user_id parameter in backend/src/services/task_service.py
- [X] T019 Update TaskService.get_task() to filter by user_id in backend/src/services/task_service.py
- [X] T020 Update TaskService.update_task() to verify user_id ownership in backend/src/services/task_service.py
- [X] T021 Update TaskService.delete_task() to verify user_id ownership in backend/src/services/task_service.py
- [X] T022 Update TaskService.toggle_complete() to verify user_id ownership in backend/src/services/task_service.py
- [X] T023 [P] Create backend/tests/conftest.py fixture for mock JWT token and user

**Checkpoint**: Foundation ready - user story implementation can now begin

---

## Phase 4: User Story 1 - User Registration (Priority: P1) 🎯 MVP

**Goal**: Users can create accounts with email and password

**Independent Test**: Navigate to /register, fill form with valid email/password, verify account created and redirected to dashboard

### Implementation for User Story 1

- [X] T024 [US1] Create frontend/src/components/AuthForm.tsx with email, password, name fields and validation
- [X] T025 [US1] Add client-side validation for email format and password length (min 8 chars) in AuthForm.tsx
- [X] T026 [US1] Create frontend/src/app/register/page.tsx with registration form using AuthForm component
- [X] T027 [US1] Implement signUp.email() call using authClient in register page
- [X] T028 [US1] Add error display for "Email already in use" and validation errors in register page
- [X] T029 [US1] Implement redirect to dashboard after successful registration
- [ ] T030 [P] [US1] Create backend/tests/integration/test_auth_api.py with registration flow tests

**Checkpoint**: User Story 1 complete - users can register accounts

---

## Phase 5: User Story 2 - User Login (Priority: P1)

**Goal**: Registered users can log in and access their tasks

**Independent Test**: Navigate to /login, enter valid credentials, verify redirected to dashboard with tasks visible

### Implementation for User Story 2

- [X] T031 [US2] Create frontend/src/app/login/page.tsx with login form using AuthForm component
- [X] T032 [US2] Implement signIn.email() call using authClient in login page
- [X] T033 [US2] Add error display for "Invalid email or password" in login page
- [X] T034 [US2] Implement redirect to dashboard after successful login
- [X] T035 [US2] Add "Don't have an account? Register" link in login page
- [X] T036 [US2] Add "Already have an account? Login" link in register page
- [ ] T037 [P] [US2] Add login flow tests to backend/tests/integration/test_auth_api.py

**Checkpoint**: User Stories 1 AND 2 complete - users can register and login

---

## Phase 6: User Story 3 - User Logout (Priority: P1)

**Goal**: Users can securely end their sessions

**Independent Test**: While logged in, click logout button, verify redirected to login and cannot access protected routes

### Implementation for User Story 3

- [X] T038 [US3] Create frontend/src/components/UserNav.tsx with user email display and logout button
- [X] T039 [US3] Implement signOut() call using authClient in UserNav component
- [X] T040 [US3] Add UserNav component to frontend/src/app/page.tsx (dashboard header)
- [X] T041 [US3] Implement redirect to /login after successful logout
- [ ] T042 [P] [US3] Add logout flow tests to backend/tests/integration/test_auth_api.py

**Checkpoint**: User Stories 1, 2, AND 3 complete - full auth flow working

---

## Phase 7: User Story 4 - Task Isolation (Priority: P1)

**Goal**: Each user sees only their own tasks, cannot access other users' data

**Independent Test**: Create tasks as User A, logout, login as User B, verify User A's tasks not visible

### Implementation for User Story 4

- [X] T043 [US4] Update GET /api/tasks endpoint to require auth and filter by user_id in backend/src/api/routes/tasks.py
- [X] T044 [US4] Update POST /api/tasks endpoint to set user_id from JWT in backend/src/api/routes/tasks.py
- [X] T045 [US4] Update GET /api/tasks/{id} endpoint to verify user_id ownership in backend/src/api/routes/tasks.py
- [X] T046 [US4] Update PUT /api/tasks/{id} endpoint to verify user_id ownership in backend/src/api/routes/tasks.py
- [X] T047 [US4] Update DELETE /api/tasks/{id} endpoint to verify user_id ownership in backend/src/api/routes/tasks.py
- [X] T048 [US4] Update PATCH /api/tasks/{id}/toggle endpoint to verify user_id ownership in backend/src/api/routes/tasks.py
- [X] T049 [US4] Update frontend/src/services/api.ts to include JWT token in Authorization header
- [X] T050 [US4] Add getToken() function to fetch JWT from authClient.token() in api.ts
- [X] T051 [US4] Update all taskApi methods to call getToken() and include Bearer token
- [ ] T052 [P] [US4] Add task isolation tests to backend/tests/integration/test_auth_api.py
- [ ] T053 [P] [US4] Add cross-user access denial tests to backend/tests/integration/test_auth_api.py

**Checkpoint**: User Stories 1-4 complete - core multi-user functionality working

---

## Phase 8: User Story 5 - Protected Routes (Priority: P2)

**Goal**: All task pages and APIs require authentication, unauthenticated users redirected to login

**Independent Test**: Without logging in, try to access dashboard and API endpoints, verify all return 401 or redirect to login

### Implementation for User Story 5

- [X] T054 [US5] Create frontend/middleware.ts with auth check using Better Auth
- [X] T055 [US5] Configure middleware matcher to protect / (dashboard) route
- [X] T056 [US5] Add redirect to /login for unauthenticated requests in middleware
- [X] T057 [US5] Update GET /api/categories endpoint to require auth in backend/src/api/routes/categories.py
- [X] T058 [US5] Update POST /api/categories endpoint to require auth in backend/src/api/routes/categories.py
- [X] T059 [US5] Add session expiry handling - redirect to /login with message in frontend
- [ ] T060 [P] [US5] Add protected route tests to backend/tests/integration/test_auth_api.py
- [ ] T061 [P] [US5] Add 401 response tests for unauthenticated API requests

**Checkpoint**: User Stories 1-5 complete - all routes and APIs protected

---

## Phase 9: User Story 6 - User Profile Display (Priority: P3)

**Goal**: User can see their email/name in navigation and access logout

**Independent Test**: Log in, verify user email displayed in header, click profile dropdown to see logout option

### Implementation for User Story 6

- [X] T062 [US6] Update UserNav.tsx to display user email from session
- [X] T063 [US6] Add dropdown menu to UserNav with user profile info
- [X] T064 [US6] Style UserNav dropdown with purple/violet theme matching existing UI
- [X] T065 [US6] Add user avatar placeholder (first letter of email) in UserNav
- [X] T066 [US6] Ensure logout option is prominently displayed in dropdown

**Checkpoint**: All 6 user stories complete - full feature set working

---

## Phase 10: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [X] T067 [P] Update frontend/src/app/page.tsx to show loading state while checking auth
- [X] T068 [P] Add error boundary for auth errors in frontend
- [X] T069 [P] Style login and register pages with purple/violet theme
- [ ] T070 [P] Add "Remember me" checkbox to login form (optional)
- [ ] T071 Run all backend tests and verify 100% pass rate: cd backend && pytest -v
- [ ] T072 Run frontend build and verify no TypeScript errors: cd frontend && npm run build
- [ ] T073 Run quickstart.md validation (manual walkthrough of all user stories)
- [X] T074 Update root README.md with authentication feature overview

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
Phase 4 (US1: Registration)                                      │
    │                                                            │
    ▼                                                            │
Phase 5 (US2: Login)                                             │
    │                                                            │
    ▼                                                            │
Phase 6 (US3: Logout) ──── MVP AUTH COMPLETE                     │
    │                                                            │
    ▼                                                            │
Phase 7 (US4: Task Isolation) ──── CORE SECURITY                 │
    │                                                            │
    ▼                                                            │
Phase 8 (US5: Protected Routes)                                  │
    │                                                            │
    ▼                                                            │
Phase 9 (US6: Profile Display)                                   │
    │                                                            │
    ▼                                                            │
Phase 10 (Polish)                                                │
```

### User Story Dependencies

- **US1 (Registration)**: Foundational only - entry point for new users
- **US2 (Login)**: Depends on US1 (need registered users to log in)
- **US3 (Logout)**: Depends on US2 (need logged-in users to log out)
- **US4 (Task Isolation)**: Depends on US2 (need auth to filter tasks)
- **US5 (Protected Routes)**: Depends on US2 (need auth middleware)
- **US6 (Profile Display)**: Depends on US2 (need session to display user info)

### Within Each User Story

- Frontend components first (visible progress)
- API integration second
- Tests can run in parallel after implementation

### Parallel Opportunities

```bash
# Phase 1 & 2 - Setup can run in parallel:
Phase 1 (Backend Setup) || Phase 2 (Frontend Setup)

# Phase 3 - Config tasks can run in parallel:
T003, T004 (config files)
T017-T022 (TaskService updates)

# Each User Story - Tests can run in parallel with other tests:
T030 || T037 || T042 (test files)

# Phase 10 - Polish tasks can run in parallel:
T067, T068, T069, T070 (independent improvements)
```

---

## Implementation Strategy

### MVP First (User Stories 1-3 Only)

1. Complete Phase 1: Backend Setup
2. Complete Phase 2: Frontend Setup (parallel with Phase 1)
3. Complete Phase 3: Foundational (CRITICAL - blocks all stories)
4. Complete Phase 4: User Story 1 (Registration)
5. Complete Phase 5: User Story 2 (Login)
6. Complete Phase 6: User Story 3 (Logout)
7. **STOP and VALIDATE**: Test full auth flow (register → login → logout)
8. Deploy/demo if ready - this is a functional auth MVP!

### Full Implementation

1. Complete MVP (Phases 1-6)
2. Add Phase 7: User Story 4 (Task Isolation) - CRITICAL for security
3. Add Phase 8: User Story 5 (Protected Routes)
4. Add Phase 9: User Story 6 (Profile Display)
5. Complete Phase 10: Polish
6. Final validation against all acceptance scenarios

### Task Count Summary

| Phase | Description | Task Count | Status |
|-------|-------------|------------|--------|
| 1 | Backend Setup | 4 | PENDING |
| 2 | Frontend Setup | 5 | PENDING |
| 3 | Foundational | 14 | PENDING |
| 4 | US1: Registration | 7 | PENDING |
| 5 | US2: Login | 7 | PENDING |
| 6 | US3: Logout | 5 | PENDING |
| 7 | US4: Task Isolation | 11 | PENDING |
| 8 | US5: Protected Routes | 8 | PENDING |
| 9 | US6: Profile Display | 5 | PENDING |
| 10 | Polish | 8 | PENDING |
| **TOTAL** | | **74** | **PENDING** |

---

## Notes

- [P] tasks = different files, no dependencies on incomplete tasks
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Backend tests use pytest with httpx for API testing
- Frontend uses Better Auth's built-in session management
- JWT verification uses JWKS endpoint (no shared secret)
- User ID is TEXT type to match Better Auth's CUID format
