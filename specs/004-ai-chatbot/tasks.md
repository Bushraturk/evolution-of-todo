# Tasks: AI-Powered Todo Chatbot

**Feature**: 004-ai-chatbot
**Input**: Design documents from `/specs/004-ai-chatbot/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅

**Tests**: Not explicitly requested in specification - focusing on implementation tasks only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Backend**: `phase4-chatbot/backend/src/`
- **Frontend**: `phase4-chatbot/frontend/src/`
- **Tests**: `phase4-chatbot/backend/tests/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create phase4-chatbot directory structure with backend/ and frontend/ subdirectories
- [X] T002 Initialize backend Python project with pyproject.toml in phase4-chatbot/backend/
- [X] T003 [P] Create requirements.txt with dependencies (fastapi, openai, mcp, sqlmodel, psycopg2-binary, tenacity) in phase4-chatbot/backend/
- [X] T004 [P] Initialize frontend Next.js project with TypeScript in phase4-chatbot/frontend/
- [X] T005 [P] Create backend .env.example file with required environment variables in phase4-chatbot/backend/
- [X] T006 [P] Create frontend .env.local.example file with required environment variables in phase4-chatbot/frontend/

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Models

- [X] T007 [P] Create Conversation model in phase4-chatbot/backend/src/models/conversation.py
- [X] T008 [P] Create Message model with MessageRole enum in phase4-chatbot/backend/src/models/message.py
- [X] T009 Create database migration script 001_add_chatbot_tables.sql in phase4-chatbot/backend/migrations/
- [X] T010 Create database rollback script 001_rollback_chatbot_tables.sql in phase4-chatbot/backend/migrations/

### MCP Server Infrastructure

- [X] T011 [P] Create MCP server initialization in phase4-chatbot/backend/src/mcp/server.py
- [X] T012 [P] Create MCP tool definitions schema in phase4-chatbot/backend/src/mcp/tools.py
- [X] T013 Create MCP tool handlers base class in phase4-chatbot/backend/src/mcp/handlers.py

### Agent Service

- [X] T014 Create AgentService class with OpenAI Agents SDK integration in phase4-chatbot/backend/src/services/agent_service.py
- [X] T015 Add agent instructions prompt template in phase4-chatbot/backend/src/services/agent_service.py
- [X] T016 Implement retry logic with exponential backoff for OpenAI API calls in phase4-chatbot/backend/src/services/agent_service.py

### Conversation Management (includes US4 - Conversation Continuity)

- [X] T017 Create ConversationService with create_conversation method in phase4-chatbot/backend/src/services/conversation_service.py
- [X] T018 Implement load_conversation_history method (last 50 messages, paginated) in phase4-chatbot/backend/src/services/conversation_service.py
- [X] T019 Implement add_message method in phase4-chatbot/backend/src/services/conversation_service.py
- [X] T020 Implement update_conversation_timestamp method in phase4-chatbot/backend/src/services/conversation_service.py
- [X] T021 Add conversation archival logic (90-day soft delete) in phase4-chatbot/backend/src/services/conversation_service.py

### Chat Endpoint Structure

- [X] T022 Create chat router with POST /api/{user_id}/chat endpoint in phase4-chatbot/backend/src/api/chat.py
- [X] T023 Implement authentication dependency (reuse from Phase III) in phase4-chatbot/backend/src/api/chat.py
- [X] T024 Add request validation (ChatRequest schema) in phase4-chatbot/backend/src/api/chat.py
- [X] T025 Add response formatting (ChatResponse schema) in phase4-chatbot/backend/src/api/chat.py
- [X] T026 Implement error handling (400, 401, 403, 500, 503) in phase4-chatbot/backend/src/api/chat.py

### Application Configuration

- [X] T027 Update FastAPI main.py to register chat router in phase4-chatbot/backend/src/main.py
- [X] T028 Add OpenAI client initialization with dependency injection in phase4-chatbot/backend/src/main.py
- [X] T029 Add MCP server lifecycle management (startup/shutdown events) in phase4-chatbot/backend/src/main.py
- [X] T030 Update CORS configuration to allow frontend origin in phase4-chatbot/backend/src/main.py

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Natural Language Task Creation (Priority: P1) 🎯 MVP

**Goal**: Enable users to create tasks by telling the chatbot in natural language

**Independent Test**: Send message "Add a task to buy groceries" and verify task is created with correct title

### Implementation for User Story 1

- [X] T031 [US1] Implement add_task MCP tool handler in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T032 [US1] Register add_task tool with MCP server in phase4-chatbot/backend/src/mcp/server.py
- [X] T033 [US1] Add add_task tool to agent's tool registry in phase4-chatbot/backend/src/services/agent_service.py
- [X] T034 [US1] Integrate add_task handler with existing TaskService from Phase II in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T035 [US1] Add validation for task title (1-200 chars) and description (max 1000 chars) in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T036 [US1] Implement error handling for task creation failures in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T037 [US1] Add logging for add_task tool invocations in phase4-chatbot/backend/src/mcp/handlers.py

**Checkpoint**: At this point, User Story 1 should be fully functional - users can create tasks via natural language

---

## Phase 4: User Story 2 - Task List Viewing and Filtering (Priority: P1)

**Goal**: Enable users to view their tasks with natural language queries

**Independent Test**: Send message "Show me all my tasks" and verify correct task list is returned

### Implementation for User Story 2

- [X] T038 [US2] Implement list_tasks MCP tool handler in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T039 [US2] Register list_tasks tool with MCP server in phase4-chatbot/backend/src/mcp/server.py
- [X] T040 [US2] Add list_tasks tool to agent's tool registry in phase4-chatbot/backend/src/services/agent_service.py
- [X] T041 [US2] Integrate list_tasks handler with existing TaskService from Phase II in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T042 [US2] Implement status filtering (all, pending, completed) in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T043 [US2] Format task list output for natural language response in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T044 [US2] Add logging for list_tasks tool invocations in phase4-chatbot/backend/src/mcp/handlers.py

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently - users can create and view tasks

---

## Phase 5: User Story 3 - Task Completion (Priority: P2)

**Goal**: Enable users to mark tasks as complete through conversation

**Independent Test**: Send message "Mark task {id} as complete" and verify task status changes

### Implementation for User Story 3

- [X] T045 [US3] Implement complete_task MCP tool handler in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T046 [US3] Register complete_task tool with MCP server in phase4-chatbot/backend/src/mcp/server.py
- [X] T047 [US3] Add complete_task tool to agent's tool registry in phase4-chatbot/backend/src/services/agent_service.py
- [X] T048 [US3] Integrate complete_task handler with existing TaskService from Phase II in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T049 [US3] Add validation for task existence and ownership in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T050 [US3] Implement error handling for non-existent tasks in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T051 [US3] Add logging for complete_task tool invocations in phase4-chatbot/backend/src/mcp/handlers.py

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently - full task lifecycle via chat

---

## Phase 6: User Story 5 - Task Modification (Priority: P3)

**Goal**: Enable users to update task details through conversation

**Independent Test**: Send message "Change task {id} to 'New title'" and verify task title updates

### Implementation for User Story 5

- [X] T052 [US5] Implement update_task MCP tool handler in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T053 [US5] Register update_task tool with MCP server in phase4-chatbot/backend/src/mcp/server.py
- [X] T054 [US5] Add update_task tool to agent's tool registry in phase4-chatbot/backend/src/services/agent_service.py
- [X] T055 [US5] Integrate update_task handler with existing TaskService from Phase II in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T056 [US5] Add validation for task title and description updates in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T057 [US5] Implement error handling for invalid updates in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T058 [US5] Add logging for update_task tool invocations in phase4-chatbot/backend/src/mcp/handlers.py

**Checkpoint**: At this point, users can create, view, complete, and update tasks via chat

---

## Phase 7: User Story 6 - Task Deletion (Priority: P3)

**Goal**: Enable users to remove tasks through conversation

**Independent Test**: Send message "Delete task {id}" and verify task is removed

### Implementation for User Story 6

- [X] T059 [US6] Implement delete_task MCP tool handler in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T060 [US6] Register delete_task tool with MCP server in phase4-chatbot/backend/src/mcp/server.py
- [X] T061 [US6] Add delete_task tool to agent's tool registry in phase4-chatbot/backend/src/services/agent_service.py
- [X] T062 [US6] Integrate delete_task handler with existing TaskService from Phase II in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T063 [US6] Add validation for task existence and ownership in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T064 [US6] Implement error handling for non-existent tasks in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T065 [US6] Add logging for delete_task tool invocations in phase4-chatbot/backend/src/mcp/handlers.py

**Checkpoint**: All user stories should now be independently functional - complete task management via chat

---

## Phase 8: Frontend Integration

**Purpose**: Build chat interface using OpenAI ChatKit

### Frontend Components

- [X] T066 [P] Install OpenAI ChatKit dependency in phase4-chatbot/frontend/package.json
- [X] T067 [P] Create ChatInterface component wrapper in phase4-chatbot/frontend/src/components/ChatInterface.tsx
- [X] T068 [P] Create chat API client with JWT authentication in phase4-chatbot/frontend/src/services/chatApi.ts
- [X] T069 [P] Create TypeScript interfaces for chat types in phase4-chatbot/frontend/src/types/chat.ts
- [X] T070 Create chat page with ChatInterface in phase4-chatbot/frontend/src/app/chat/page.tsx
- [X] T071 Add navigation link to chat page in existing dashboard in phase4-chatbot/frontend/src/components/UserNav.tsx
- [X] T072 Implement conversation state management (localStorage for conversation_id) in phase4-chatbot/frontend/src/services/chatApi.ts
- [X] T073 Add error handling and user feedback for API failures in phase4-chatbot/frontend/src/components/ChatInterface.tsx

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

### Backend Polish

- [X] T074 [P] Add comprehensive logging for all MCP tool invocations in phase4-chatbot/backend/src/mcp/handlers.py
- [X] T075 [P] Implement request/response logging middleware in phase4-chatbot/backend/src/main.py
- [X] T076 [P] Add health check endpoint in phase4-chatbot/backend/src/api/health.py
- [X] T077 Create Dockerfile for backend deployment in phase4-chatbot/backend/Dockerfile
- [X] T078 Update backend README.md with setup instructions in phase4-chatbot/backend/README.md

### Frontend Polish

- [X] T079 [P] Add loading states for chat messages in phase4-chatbot/frontend/src/components/ChatInterface.tsx
- [X] T080 [P] Add error boundary for graceful error handling in phase4-chatbot/frontend/src/app/chat/page.tsx
- [X] T081 Update frontend README.md with setup instructions in phase4-chatbot/frontend/README.md

### Database & Deployment

- [ ] T082 Run database migrations on development database
- [ ] T083 Verify all database indexes are created correctly
- [ ] T084 Test conversation archival background job logic
- [ ] T085 Deploy backend to Hugging Face Spaces with environment variables
- [ ] T086 Deploy frontend to Vercel with environment variables
- [ ] T087 Configure OpenAI domain allowlist with Vercel URL
- [ ] T088 Add NEXT_PUBLIC_OPENAI_DOMAIN_KEY to Vercel environment variables

### Documentation & Validation

- [X] T089 [P] Validate all user stories against acceptance criteria from spec.md
- [X] T090 [P] Run through quickstart.md testing scenarios
- [X] T091 [P] Update main project README.md with Phase IV information
- [X] T092 Create deployment documentation in phase4-chatbot/DEPLOYMENT.md

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-7)**: All depend on Foundational phase completion
  - User stories can then proceed in parallel (if staffed)
  - Or sequentially in priority order (US1 → US2 → US3 → US5 → US6)
- **Frontend (Phase 8)**: Can start after US1 is complete (MVP), but benefits from all user stories being done
- **Polish (Phase 9)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational (Phase 2) - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational (Phase 2) - Independent of US1
- **User Story 3 (P2)**: Can start after Foundational (Phase 2) - Independent of US1/US2
- **User Story 4 (P2)**: Built into Foundational phase (conversation management)
- **User Story 5 (P3)**: Can start after Foundational (Phase 2) - Independent of other stories
- **User Story 6 (P3)**: Can start after Foundational (Phase 2) - Independent of other stories

### Within Each User Story

- MCP tool handler implementation first
- Tool registration with MCP server second
- Tool added to agent registry third
- Integration with existing services fourth
- Validation and error handling fifth
- Logging last

### Parallel Opportunities

- **Setup Phase**: T003, T004, T005, T006 can run in parallel (different files)
- **Foundational Phase**: T007-T008 (models), T011-T012 (MCP), can run in parallel
- **User Stories**: Once Foundational completes, all user stories (US1-US6) can be worked on in parallel by different team members
- **Frontend Phase**: T066, T067, T068, T069 can run in parallel (different files)
- **Polish Phase**: T074, T075, T076, T079, T080, T089, T090, T091 can run in parallel

---

## Parallel Example: Foundational Phase

```bash
# Launch all model creation tasks together:
Task T007: "Create Conversation model in phase4-chatbot/backend/src/models/conversation.py"
Task T008: "Create Message model with MessageRole enum in phase4-chatbot/backend/src/models/message.py"

# Launch all MCP infrastructure tasks together:
Task T011: "Create MCP server initialization in phase4-chatbot/backend/src/mcp/server.py"
Task T012: "Create MCP tool definitions schema in phase4-chatbot/backend/src/mcp/tools.py"
```

---

## Parallel Example: User Stories (After Foundational Complete)

```bash
# Different team members can work on different user stories simultaneously:
Developer A: Phase 3 (US1 - Task Creation) - Tasks T031-T037
Developer B: Phase 4 (US2 - Task Viewing) - Tasks T038-T044
Developer C: Phase 5 (US3 - Task Completion) - Tasks T045-T051
```

---

## Implementation Strategy

### MVP First (User Story 1 + User Story 2 Only)

1. Complete Phase 1: Setup (T001-T006)
2. Complete Phase 2: Foundational (T007-T030) - CRITICAL - blocks all stories
3. Complete Phase 3: User Story 1 (T031-T037) - Task creation
4. Complete Phase 4: User Story 2 (T038-T044) - Task viewing
5. **STOP and VALIDATE**: Test US1 and US2 independently
6. Complete Phase 8: Frontend Integration (T066-T073)
7. Deploy/demo MVP

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (can create tasks!)
3. Add User Story 2 → Test independently → Deploy/Demo (can view tasks!)
4. Add User Story 3 → Test independently → Deploy/Demo (can complete tasks!)
5. Add User Story 5 → Test independently → Deploy/Demo (can update tasks!)
6. Add User Story 6 → Test independently → Deploy/Demo (full CRUD via chat!)
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together (T001-T030)
2. Once Foundational is done:
   - Developer A: User Story 1 (T031-T037)
   - Developer B: User Story 2 (T038-T044)
   - Developer C: User Story 3 (T045-T051)
   - Developer D: User Story 5 (T052-T058)
   - Developer E: User Story 6 (T059-T065)
3. Stories complete and integrate independently
4. Team completes Frontend + Polish together

---

## Task Summary

**Total Tasks**: 92

**Tasks by Phase**:
- Phase 1 (Setup): 6 tasks
- Phase 2 (Foundational): 24 tasks (CRITICAL - blocks all user stories)
- Phase 3 (US1 - Task Creation): 7 tasks
- Phase 4 (US2 - Task Viewing): 7 tasks
- Phase 5 (US3 - Task Completion): 7 tasks
- Phase 6 (US5 - Task Modification): 7 tasks
- Phase 7 (US6 - Task Deletion): 7 tasks
- Phase 8 (Frontend): 8 tasks
- Phase 9 (Polish): 19 tasks

**Parallel Opportunities**: 23 tasks marked [P] can run in parallel

**MVP Scope** (Recommended):
- Phase 1: Setup (6 tasks)
- Phase 2: Foundational (24 tasks)
- Phase 3: US1 - Task Creation (7 tasks)
- Phase 4: US2 - Task Viewing (7 tasks)
- Phase 8: Frontend Integration (8 tasks)
- **Total MVP**: 52 tasks

**Independent Test Criteria**:
- US1: Send "Add a task to buy groceries" → Task created
- US2: Send "Show me all my tasks" → Task list returned
- US3: Send "Mark task {id} as complete" → Task status updated
- US4: Multi-turn conversation maintains context (built into foundational)
- US5: Send "Change task {id} to 'New title'" → Task title updated
- US6: Send "Delete task {id}" → Task removed

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Tests not included as they were not explicitly requested in spec.md
- Conversation continuity (US4) is built into foundational conversation management
- All MCP tools delegate to existing TaskService from Phase II (no duplication)
- Frontend uses existing authentication from Phase III (JWT tokens)
- Database migrations must be run before backend deployment
