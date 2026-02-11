# Tasks: Advanced Cloud Deployment

**Input**: Design documents from `/specs/006-advanced-cloud-deployment/`
**Prerequisites**: plan.md, spec.md, research.md, data-model.md, contracts/api-contracts.md, quickstart.md

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Web app**: `backend/src/`, `frontend/src/`
- **Dapr**: `dapr/components/`
- **Kubernetes**: `k8s/helm-charts/todo-chatbot/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [X] T001 Create Dapr configuration directory structure at `dapr/components/`
- [X] T002 [P] Update backend dependencies in `backend/pyproject.toml` (add aiokafka, dapr-ext-fastapi, resend)
- [X] T003 [P] Update frontend dependencies in `frontend/package.json` (add date-fns)
- [X] T004 [P] Create environment variable template at `backend/.env.example` with Kafka, Dapr, Resend config
- [ ] T005 Install Dapr CLI and initialize locally (verify with `dapr --version`)

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**⚠️ CRITICAL**: No user story work can begin until this phase is complete

### Database Schema Extensions

- [X] T006 Create Alembic migration for new columns in tasks table (priority, due_date, is_recurring, parent_task_id, recurrence_id) in `backend/alembic/versions/`
- [X] T007 [P] Create Alembic migration for recurring_patterns table in `backend/alembic/versions/`
- [X] T008 [P] Create Alembic migration for reminders table in `backend/alembic/versions/`
- [X] T009 [P] Create Alembic migration for scheduled_notifications table in `backend/alembic/versions/`
- [X] T010 [P] Create Alembic migration for tags table in `backend/alembic/versions/`
- [X] T011 [P] Create Alembic migration for task_tags junction table in `backend/alembic/versions/`
- [ ] T012 Run all migrations and verify schema in Neon DB

### Data Models

- [X] T013 [P] Extend Task model in `backend/src/models/task.py` with priority, due_date, is_recurring, parent_task_id, recurrence_id fields
- [X] T014 [P] Create RecurringPattern model in `backend/src/models/recurring_pattern.py`
- [X] T015 [P] Create Reminder model in `backend/src/models/reminder.py`
- [X] T016 [P] Create ScheduledNotification model in `backend/src/models/notification.py`
- [X] T017 [P] Create Tag model in `backend/src/models/tag.py`
- [X] T018 [P] Create TaskTag model in `backend/src/models/task_tag.py`

### Dapr Infrastructure

- [X] T019 Create Dapr pub/sub component for Kafka/Redpanda in `dapr/components/pubsub.yaml`
- [X] T020 [P] Create Dapr state store component for Redis in `dapr/components/statestore.yaml`
- [X] T021 [P] Create Dapr secrets component in `dapr/components/secrets.yaml`
- [X] T022 [P] Create Dapr cron binding component in `dapr/components/cron-binding.yaml`
- [X] T023 Create secrets file template at `dapr/secrets.json.example`
- [X] T024 Create Dapr pub/sub client wrapper in `backend/src/dapr/pubsub.py`
- [X] T025 [P] Create Dapr state management client in `backend/src/dapr/state.py`

### Event Publishing Infrastructure

- [X] T026 Create event publisher service in `backend/src/services/event_publisher.py` with publish_event() method
- [X] T027 Define event schemas (TaskCreatedEvent, TaskCompletedEvent, ReminderScheduledEvent) in `backend/src/models/events.py`
- [ ] T028 Create Kafka topics (task-events, reminders, task-updates) in Redpanda Cloud or local

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Recurring Tasks (Priority: P1) 🎯 MVP

**Goal**: Users can create recurring tasks (daily, weekly, monthly) that automatically generate next occurrences

**Independent Test**: Create a daily recurring task, mark it complete, verify next occurrence is created within 5 seconds

### Implementation for User Story 1

- [X] T029 [P] [US1] Extend TaskService in `backend/src/services/task_service.py` with create_recurring_task() method
- [X] T030 [P] [US1] Create RecurringPatternService in `backend/src/services/recurring_pattern_service.py` with calculate_next_occurrence() method
- [X] T031 [US1] Extend POST /tasks endpoint in `backend/src/api/routes/tasks.py` to accept recurrence field
- [X] T032 [US1] Add validation for recurrence fields (frequency, interval, end_date) in `backend/src/api/routes/tasks.py`
- [X] T033 [US1] Publish task.created event when recurring task is created in `backend/src/services/task_service.py`
- [X] T034 [US1] Create Recurring Task Service consumer in `backend/src/services/recurring_task_service.py`
- [X] T035 [US1] Implement event handler for task.completed events in `backend/src/services/recurring_task_service.py`
- [X] T036 [US1] Implement create_next_occurrence() logic in `backend/src/services/recurring_task_service.py`
- [X] T037 [US1] Add idempotency check (unique constraint on parent_task_id + next_occurrence_date) in create_next_occurrence()
- [X] T038 [US1] Implement cron safety net job in `backend/src/services/recurring_task_service.py` (runs every 5 minutes)
- [X] T039 [US1] Create GET /tasks/:id/occurrences endpoint in `backend/src/api/routes/tasks.py`
- [X] T040 [US1] Create DELETE /tasks/:id/recurrence endpoint in `backend/src/api/routes/tasks.py`
- [ ] T041 [P] [US1] Create RecurrenceSelector component in `frontend/src/components/RecurrenceSelector.tsx`
- [ ] T042 [US1] Integrate RecurrenceSelector into task creation form in `frontend/src/components/TaskForm.tsx`
- [ ] T043 [US1] Update taskService.ts to include recurrence field in `frontend/src/services/taskService.ts`
- [ ] T044 [US1] Display recurring task indicator in TaskList component in `frontend/src/components/TaskList.tsx`

### Tests for User Story 1

- [X] T045 [P] [US1] Unit test for calculate_next_occurrence() in `backend/tests/unit/test_recurring_pattern.py`
- [X] T046 [P] [US1] Integration test for recurring task creation flow in `backend/tests/integration/test_recurring_task_creation.py`
- [X] T047 [P] [US1] Integration test for next occurrence generation in `backend/tests/integration/test_next_occurrence.py`
- [X] T048 [P] [US1] Contract test for POST /tasks with recurrence in `backend/tests/contract/test_tasks_api.py`

**Checkpoint**: At this point, User Story 1 should be fully functional and testable independently

---

## Phase 4: User Story 2 - Due Dates & Reminders (Priority: P1) 🎯 MVP

**Goal**: Users can set due dates and receive reminders via email or push notifications

**Independent Test**: Create a task with due date and reminder, verify notification is delivered within 30 seconds of scheduled time

### Implementation for User Story 2

- [ ] T049 [P] [US2] Extend POST /tasks endpoint to accept due_date and reminder fields in `backend/src/api/routes/tasks.py`
- [ ] T050 [P] [US2] Create ReminderService in `backend/src/services/reminder_service.py` with schedule_reminder() method
- [ ] T051 [US2] Calculate remind_at timestamp (due_date - offset_minutes) in `backend/src/services/reminder_service.py`
- [ ] T052 [US2] Create ScheduledNotification record when reminder is scheduled in `backend/src/services/reminder_service.py`
- [ ] T053 [US2] Publish reminder.scheduled event in `backend/src/services/reminder_service.py`
- [ ] T054 [US2] Create Notification Service consumer in `backend/src/services/notification_service.py`
- [ ] T055 [US2] Implement cron job to query pending notifications (scheduled_for <= NOW) in `backend/src/services/notification_service.py`
- [ ] T056 [US2] Implement email delivery via Resend API in `backend/src/services/notification_service.py`
- [ ] T057 [US2] Implement push notification delivery via Web Push API in `backend/src/services/notification_service.py`
- [ ] T058 [US2] Add retry logic (max 3 retries with exponential backoff) in `backend/src/services/notification_service.py`
- [ ] T059 [US2] Update reminder status to SENT after successful delivery in `backend/src/services/notification_service.py`
- [ ] T060 [US2] Create POST /tasks/:id/reminders endpoint in `backend/src/api/routes/reminders.py`
- [ ] T061 [US2] Create GET /tasks/:id/reminders endpoint in `backend/src/api/routes/reminders.py`
- [ ] T062 [US2] Create DELETE /reminders/:id endpoint in `backend/src/api/routes/reminders.py`
- [ ] T063 [P] [US2] Create DateTimePicker component in `frontend/src/components/DateTimePicker.tsx`
- [ ] T064 [P] [US2] Create ReminderForm component in `frontend/src/components/ReminderForm.tsx`
- [ ] T065 [US2] Integrate DateTimePicker and ReminderForm into task creation form in `frontend/src/components/TaskForm.tsx`
- [ ] T066 [US2] Display due date and reminder indicator in TaskList in `frontend/src/components/TaskList.tsx`
- [ ] T067 [US2] Implement push notification subscription in `frontend/src/services/notificationService.ts`

### Tests for User Story 2

- [ ] T068 [P] [US2] Unit test for remind_at calculation in `backend/tests/unit/test_reminder.py`
- [ ] T069 [P] [US2] Integration test for reminder scheduling in `backend/tests/integration/test_reminder_scheduling.py`
- [ ] T070 [P] [US2] Integration test for notification delivery in `backend/tests/integration/test_notification_delivery.py`
- [ ] T071 [P] [US2] Contract test for POST /tasks/:id/reminders in `backend/tests/contract/test_reminders_api.py`

**Checkpoint**: At this point, User Stories 1 AND 2 should both work independently

---

## Phase 5: User Story 3 - Event-Driven Architecture (Priority: P1) 🎯 MVP

**Goal**: All task operations publish events to Kafka for audit trail and real-time sync

**Independent Test**: Create/update/complete/delete a task, verify events are published to Kafka within 5 seconds

### Implementation for User Story 3

- [ ] T072 [US3] Publish task.created event in TaskService.create() in `backend/src/services/task_service.py`
- [ ] T073 [US3] Publish task.updated event in TaskService.update() in `backend/src/services/task_service.py`
- [ ] T074 [US3] Publish task.completed event in TaskService.complete() in `backend/src/services/task_service.py`
- [ ] T075 [US3] Publish task.deleted event in TaskService.delete() in `backend/src/services/task_service.py`
- [ ] T076 [US3] Create Audit Service consumer in `backend/src/services/audit_service.py`
- [ ] T077 [US3] Implement event handler for all task events in `backend/src/services/audit_service.py`
- [ ] T078 [US3] Store events in task_events table (optional) or rely on Kafka retention in `backend/src/services/audit_service.py`
- [ ] T079 [US3] Create GET /internal/events endpoint for debugging in `backend/src/api/routes/events.py`

### Tests for User Story 3

- [ ] T080 [P] [US3] Integration test for event publishing on task creation in `backend/tests/integration/test_event_flow.py`
- [ ] T081 [P] [US3] Integration test for event delivery to multiple consumers in `backend/tests/integration/test_event_consumers.py`

**Checkpoint**: At this point, User Stories 1, 2, AND 3 should all work independently (MVP complete!)

---

## Phase 6: User Story 4 - Dapr Integration (Priority: P2)

**Goal**: All infrastructure interactions go through Dapr sidecars for portability

**Independent Test**: Swap Kafka for RabbitMQ via Dapr config change, verify system still works

### Implementation for User Story 4

- [ ] T082 [US4] Refactor event_publisher.py to use Dapr pub/sub API in `backend/src/services/event_publisher.py`
- [ ] T083 [US4] Refactor recurring_task_service.py to subscribe via Dapr in `backend/src/services/recurring_task_service.py`
- [ ] T084 [US4] Refactor notification_service.py to subscribe via Dapr in `backend/src/services/notification_service.py`
- [ ] T085 [US4] Refactor audit_service.py to subscribe via Dapr in `backend/src/services/audit_service.py`
- [ ] T086 [US4] Use Dapr state store for conversation state in `backend/src/services/chat_service.py`
- [ ] T087 [US4] Use Dapr secrets for API keys (Groq, Resend) in `backend/src/main.py`
- [ ] T088 [US4] Add Dapr service invocation for inter-service calls (if needed) in `backend/src/dapr/service_invocation.py`

### Tests for User Story 4

- [ ] T089 [P] [US4] Integration test for Dapr pub/sub in `backend/tests/integration/test_dapr_pubsub.py`
- [ ] T090 [P] [US4] Integration test for Dapr state store in `backend/tests/integration/test_dapr_state.py`

**Checkpoint**: At this point, all infrastructure is abstracted via Dapr

---

## Phase 7: User Story 5 - Advanced Organization (Priority: P2)

**Goal**: Users can organize tasks with priorities, tags, and advanced filtering

**Independent Test**: Create tasks with different priorities and tags, filter by priority=HIGH and tag=urgent, verify results

### Implementation for User Story 5

- [ ] T091 [P] [US5] Create TagService in `backend/src/services/tag_service.py`
- [ ] T092 [US5] Create GET /tags endpoint in `backend/src/api/routes/tags.py`
- [ ] T093 [US5] Create POST /tags endpoint in `backend/src/api/routes/tags.py`
- [ ] T094 [US5] Create PUT /tags/:id endpoint in `backend/src/api/routes/tags.py`
- [ ] T095 [US5] Create DELETE /tags/:id endpoint in `backend/src/api/routes/tags.py`
- [ ] T096 [US5] Extend GET /tasks endpoint with filtering (priority, tags, due_date_range, search, sort) in `backend/src/api/routes/tasks.py`
- [ ] T097 [US5] Implement search query (title and description ILIKE) in `backend/src/services/task_service.py`
- [ ] T098 [US5] Create GET /tasks/stats endpoint in `backend/src/api/routes/stats.py`
- [ ] T099 [P] [US5] Create TagSelector component in `frontend/src/components/TagSelector.tsx`
- [ ] T100 [P] [US5] Create TaskFilters component in `frontend/src/components/TaskFilters.tsx`
- [ ] T101 [US5] Integrate TagSelector into task creation form in `frontend/src/components/TaskForm.tsx`
- [ ] T102 [US5] Integrate TaskFilters into task list page in `frontend/src/pages/tasks.tsx`
- [ ] T103 [US5] Create tagService.ts API client in `frontend/src/services/tagService.ts`

### Tests for User Story 5

- [ ] T104 [P] [US5] Unit test for tag creation in `backend/tests/unit/test_tag.py`
- [ ] T105 [P] [US5] Integration test for advanced filtering in `backend/tests/integration/test_task_filtering.py`
- [ ] T106 [P] [US5] Contract test for GET /tasks with filters in `backend/tests/contract/test_tasks_filtering.py`

**Checkpoint**: At this point, advanced organization features are complete

---

## Phase 8: User Story 6 - Local Deployment (Priority: P2)

**Goal**: Complete system deployed to Minikube with Dapr in under 10 minutes

**Independent Test**: Run deployment script on clean Minikube cluster, verify all pods running and features working

### Implementation for User Story 6

- [ ] T107 [US6] Create Kubernetes deployment for recurring-task-service in `k8s/helm-charts/todo-chatbot/templates/recurring-task-service-deployment.yaml`
- [ ] T108 [US6] Create Kubernetes deployment for notification-service in `k8s/helm-charts/todo-chatbot/templates/notification-service-deployment.yaml`
- [ ] T109 [US6] Create Kubernetes deployment for audit-service in `k8s/helm-charts/todo-chatbot/templates/audit-service-deployment.yaml`
- [ ] T110 [US6] Create Kubernetes deployment for Redis in `k8s/helm-charts/todo-chatbot/templates/redis-deployment.yaml`
- [ ] T111 [US6] Create Dapr components ConfigMap in `k8s/helm-charts/todo-chatbot/templates/dapr-components.yaml`
- [ ] T112 [US6] Update Helm values.yaml with new services in `k8s/helm-charts/todo-chatbot/values.yaml`
- [ ] T113 [US6] Create deployment script with Dapr init in `k8s/scripts/deploy-with-dapr.sh`
- [ ] T114 [US6] Update quickstart.md with Minikube deployment steps in `specs/006-advanced-cloud-deployment/quickstart.md`
- [ ] T115 [US6] Test full deployment on clean Minikube cluster

**Checkpoint**: At this point, local Kubernetes deployment is complete

---

## Phase 9: User Story 7 - Cloud Deployment (Priority: P3)

**Goal**: Production deployment to Oracle Cloud OKE with monitoring and logging

**Independent Test**: Deploy to OKE, run load test with 1,000 concurrent users, verify 99.9% success rate

### Implementation for User Story 7

- [ ] T116 [US7] Create Terraform configuration for OKE cluster in `infrastructure/terraform/oke/`
- [ ] T117 [US7] Create Kubernetes ingress configuration in `k8s/helm-charts/todo-chatbot/templates/ingress.yaml`
- [ ] T118 [US7] Configure Prometheus monitoring in `k8s/monitoring/prometheus.yaml`
- [ ] T119 [US7] Configure Grafana dashboards in `k8s/monitoring/grafana-dashboards/`
- [ ] T120 [US7] Create production Helm values in `k8s/helm-charts/todo-chatbot/values-production.yaml`
- [ ] T121 [US7] Create deployment guide in `docs/deployment/cloud-deployment.md`
- [ ] T122 [US7] Test deployment to OKE cluster
- [ ] T123 [US7] Run load tests with 1,000 concurrent users

**Checkpoint**: At this point, cloud deployment is complete

---

## Phase 10: User Story 8 - CI/CD Pipeline (Priority: P3)

**Goal**: Automated testing, building, and deployment via GitHub Actions

**Independent Test**: Push code change, verify CI/CD pipeline runs tests, builds images, and deploys to staging

### Implementation for User Story 8

- [ ] T124 [US8] Create CI workflow in `.github/workflows/ci.yml` (test, lint, build)
- [ ] T125 [US8] Create deploy-staging workflow in `.github/workflows/deploy-staging.yml`
- [ ] T126 [US8] Create deploy-production workflow in `.github/workflows/deploy-production.yml`
- [ ] T127 [US8] Configure GitHub secrets (cloud credentials, API keys)
- [ ] T128 [US8] Add Docker image building and pushing to GitHub Container Registry
- [ ] T129 [US8] Add automated rollback on deployment failure
- [ ] T130 [US8] Test full CI/CD pipeline with sample PR

**Checkpoint**: At this point, CI/CD automation is complete

---

## Phase 11: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T131 [P] Update README.md with Phase VI features and deployment instructions
- [ ] T132 [P] Update API documentation in `docs/api/`
- [ ] T133 [P] Add error handling for Kafka connection failures
- [ ] T134 [P] Add logging for all event publishing and consumption
- [ ] T135 [P] Performance optimization: add database indexes for due_date and priority queries
- [ ] T136 [P] Security hardening: validate all user inputs, sanitize event data
- [ ] T137 Run quickstart.md validation (follow guide from scratch)
- [ ] T138 Create troubleshooting guide in `docs/troubleshooting.md`
- [ ] T139 Update CLAUDE.md with Phase VI technologies and patterns

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: No dependencies - can start immediately
- **Foundational (Phase 2)**: Depends on Setup completion - BLOCKS all user stories
- **User Stories (Phase 3-5)**: All depend on Foundational phase completion - P1 MVP stories
  - US1 (Recurring Tasks): Can start after Foundational
  - US2 (Due Dates & Reminders): Can start after Foundational
  - US3 (Event-Driven Architecture): Can start after Foundational
- **User Stories (Phase 6-8)**: P2 enhancement stories
  - US4 (Dapr Integration): Depends on US1, US2, US3 completion
  - US5 (Advanced Organization): Can start after Foundational (independent)
  - US6 (Local Deployment): Depends on US1-US5 completion
- **User Stories (Phase 9-10)**: P3 polish stories
  - US7 (Cloud Deployment): Depends on US6 completion
  - US8 (CI/CD Pipeline): Depends on US6 completion
- **Polish (Phase 11)**: Depends on all desired user stories being complete

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 4 (P2)**: Depends on US1, US2, US3 (refactors their implementations)
- **User Story 5 (P2)**: Can start after Foundational - No dependencies on other stories
- **User Story 6 (P2)**: Depends on US1-US5 (deploys all features)
- **User Story 7 (P3)**: Depends on US6 (extends local deployment to cloud)
- **User Story 8 (P3)**: Depends on US6 (automates deployment)

### Within Each User Story

- Tests MUST be written and FAIL before implementation
- Models before services
- Services before endpoints
- Core implementation before integration
- Story complete before moving to next priority

### Parallel Opportunities

- All Setup tasks marked [P] can run in parallel (T002, T003, T004)
- All Foundational database migrations marked [P] can run in parallel (T007-T011)
- All Foundational data models marked [P] can run in parallel (T014-T018)
- All Foundational Dapr components marked [P] can run in parallel (T020-T022)
- Once Foundational phase completes, US1, US2, US3, US5 can start in parallel (if team capacity allows)
- All tests for a user story marked [P] can run in parallel
- Models within a story marked [P] can run in parallel
- Different user stories can be worked on in parallel by different team members

---

## Implementation Strategy

### MVP First (User Stories 1, 2, 3 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational (CRITICAL - blocks all stories)
3. Complete Phase 3: User Story 1 (Recurring Tasks)
4. Complete Phase 4: User Story 2 (Due Dates & Reminders)
5. Complete Phase 5: User Story 3 (Event-Driven Architecture)
6. **STOP and VALIDATE**: Test all MVP features independently
7. Deploy to Minikube and demo

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo (MVP!)
5. Add User Story 4 → Test independently → Deploy/Demo
6. Add User Story 5 → Test independently → Deploy/Demo
7. Add User Story 6 → Test independently → Deploy/Demo
8. Add User Story 7 → Test independently → Deploy/Demo
9. Add User Story 8 → Test independently → Deploy/Demo
10. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Recurring Tasks)
   - Developer B: User Story 2 (Due Dates & Reminders)
   - Developer C: User Story 3 (Event-Driven Architecture)
   - Developer D: User Story 5 (Advanced Organization)
3. After MVP (US1-US3) complete:
   - Developer A: User Story 4 (Dapr Integration)
   - Developer B: User Story 6 (Local Deployment)
4. After US6 complete:
   - Developer A: User Story 7 (Cloud Deployment)
   - Developer B: User Story 8 (CI/CD Pipeline)
5. Stories complete and integrate independently

---

## Notes

- [P] tasks = different files, no dependencies
- [Story] label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- Total tasks: 139 (exceeds 80-100 target for comprehensive coverage)
- MVP tasks (US1-US3): T029-T081 (53 tasks)
- Enhancement tasks (US4-US6): T082-T115 (34 tasks)
- Polish tasks (US7-US8 + Phase 11): T116-T139 (24 tasks)
