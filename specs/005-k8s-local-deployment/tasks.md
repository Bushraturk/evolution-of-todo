# Tasks: Local Kubernetes Deployment

**Feature**: 005-k8s-local-deployment
**Input**: Design documents from `/specs/005-k8s-local-deployment/`
**Prerequisites**: plan.md ✅, spec.md ✅, research.md ✅, data-model.md ✅, contracts/ ✅, quickstart.md ✅

**Tests**: Not explicitly requested in specification - focusing on implementation and validation tasks only.

**Organization**: Tasks are grouped by user story to enable independent implementation and testing of each story.

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

## Path Conventions

- **Deployment artifacts**: `k8s/`
- **Application code**: `phase4-chatbot/backend/` and `phase4-chatbot/frontend/` (unchanged)
- **Documentation**: `k8s/docs/`

---

## Phase 1: Setup (Project Initialization)

**Purpose**: Create directory structure and foundational files for Kubernetes deployment artifacts

- [x] T001 Create k8s directory structure with subdirectories: dockerfiles/, helm-charts/, scripts/, docs/
- [x] T002 [P] Create .dockerignore file for backend in phase4-chatbot/backend/.dockerignore
- [x] T003 [P] Create .dockerignore file for frontend in phase4-chatbot/frontend/.dockerignore
- [x] T004 [P] Create README.md for k8s deployment in k8s/README.md

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: No blocking prerequisites - all user stories are independently implementable

**Note**: Phase V has no foundational blocking tasks. Each user story (US1-US6) can be implemented independently once the setup phase is complete.

---

## Phase 3: User Story 1 - Container Image Creation (Priority: P1) 🎯 MVP

**Goal**: Containerize frontend and backend applications using Docker with multi-stage builds

**Independent Test**: Build Docker images for both applications, run them locally with `docker run`, verify they start successfully and respond to health checks

### Implementation for User Story 1

- [x] T005 [US1] Create backend Dockerfile with multi-stage build in k8s/dockerfiles/backend.Dockerfile
- [x] T006 [US1] Create frontend Dockerfile with multi-stage build in k8s/dockerfiles/frontend.Dockerfile
- [x] T007 [US1] Create build-images.sh script to build both Docker images in k8s/scripts/build-images.sh
- [x] T008 [US1] Create test-images.sh script to test images locally in k8s/scripts/test-images.sh
- [x] T009 [US1] Update backend Dockerfile to use python:3.13-slim base image with non-root user
- [x] T010 [US1] Update frontend Dockerfile to use node:20-alpine base image with Next.js standalone output
- [x] T011 [US1] Add health check instructions to both Dockerfiles
- [x] T012 [US1] Create image optimization guide in k8s/docs/IMAGE_OPTIMIZATION.md

**Validation Criteria**:
- Backend image builds successfully and is <500MB
- Frontend image builds successfully and is <200MB
- Both images run locally with `docker run` and respond to health checks
- Images use non-root users for security

---

## Phase 4: User Story 2 - Helm Chart Creation (Priority: P1) 🎯 MVP

**Goal**: Create Helm charts for declarative Kubernetes deployment management

**Independent Test**: Validate Helm chart with `helm lint`, perform dry-run with `helm install --dry-run`, verify all manifests generate correctly

### Implementation for User Story 2

- [x] T013 [US2] Initialize Helm chart structure in k8s/helm-charts/todo-chatbot/
- [x] T014 [US2] Create Chart.yaml with metadata in k8s/helm-charts/todo-chatbot/Chart.yaml
- [x] T015 [US2] Create values.yaml with default configuration in k8s/helm-charts/todo-chatbot/values.yaml
- [x] T016 [P] [US2] Create values-dev.yaml with development overrides in k8s/helm-charts/todo-chatbot/values-dev.yaml
- [x] T017 [P] [US2] Create values-prod.yaml with production overrides in k8s/helm-charts/todo-chatbot/values-prod.yaml
- [x] T018 [US2] Create _helpers.tpl with template helpers in k8s/helm-charts/todo-chatbot/templates/_helpers.tpl
- [x] T019 [P] [US2] Create backend-deployment.yaml template in k8s/helm-charts/todo-chatbot/templates/backend-deployment.yaml
- [x] T020 [P] [US2] Create frontend-deployment.yaml template in k8s/helm-charts/todo-chatbot/templates/frontend-deployment.yaml
- [x] T021 [P] [US2] Create backend-service.yaml template (ClusterIP) in k8s/helm-charts/todo-chatbot/templates/backend-service.yaml
- [x] T022 [P] [US2] Create frontend-service.yaml template (LoadBalancer) in k8s/helm-charts/todo-chatbot/templates/frontend-service.yaml
- [x] T023 [P] [US2] Create configmap.yaml template in k8s/helm-charts/todo-chatbot/templates/configmap.yaml
- [x] T024 [P] [US2] Create secrets.yaml template in k8s/helm-charts/todo-chatbot/templates/secrets.yaml
- [x] T025 [US2] Create NOTES.txt with post-install instructions in k8s/helm-charts/todo-chatbot/templates/NOTES.txt
- [x] T026 [US2] Add liveness and readiness probes to backend deployment template
- [x] T027 [US2] Add liveness and readiness probes to frontend deployment template
- [x] T028 [US2] Add resource requests and limits to both deployment templates
- [x] T029 [US2] Add security context (non-root user) to both deployment templates
- [x] T030 [US2] Create validate-chart.sh script to run helm lint in k8s/scripts/validate-chart.sh

**Validation Criteria**:
- `helm lint` passes with zero errors
- `helm template` generates valid Kubernetes manifests
- All required resources included (Deployments, Services, ConfigMaps, Secrets)
- Health checks and resource limits properly configured

---

## Phase 5: User Story 3 - Minikube Deployment (Priority: P1) 🎯 MVP

**Goal**: Deploy Todo Chatbot to local Minikube cluster and verify functionality

**Independent Test**: Deploy with `helm install`, verify all pods reach Running state, access application through Minikube service URLs, test all Todo Chatbot features

### Implementation for User Story 3

- [x] T031 [US3] Create deploy-minikube.sh script for automated deployment in k8s/scripts/deploy-minikube.sh
- [x] T032 [US3] Create load-images.sh script to load images to Minikube in k8s/scripts/load-images.sh
- [x] T033 [US3] Create create-secrets.sh script to create Kubernetes secrets in k8s/scripts/create-secrets.sh
- [x] T034 [US3] Create .env.example file with required environment variables in k8s/.env.example
- [x] T035 [US3] Create verify-deployment.sh script to check pod status in k8s/scripts/verify-deployment.sh
- [x] T036 [US3] Create access-application.sh script to expose services in k8s/scripts/access-application.sh
- [x] T037 [US3] Update deploy-minikube.sh to start Minikube with appropriate resources (4GB RAM, 2 CPU)
- [x] T038 [US3] Update deploy-minikube.sh to build and load Docker images
- [x] T039 [US3] Update deploy-minikube.sh to create secrets from .env file
- [x] T040 [US3] Update deploy-minikube.sh to install Helm chart
- [x] T041 [US3] Update verify-deployment.sh to check pod logs and service endpoints
- [x] T042 [US3] Create DEPLOYMENT.md guide with step-by-step instructions in k8s/docs/DEPLOYMENT.md

**Validation Criteria**:
- Minikube starts successfully with sufficient resources
- Docker images build and load to Minikube
- Helm chart installs without errors
- All pods reach Running state within 3 minutes
- Frontend accessible through Minikube service
- Backend accessible from frontend (internal communication works)
- All Todo Chatbot features functional (task CRUD, chat interface)

---

## Phase 6: User Story 4 - AI-Assisted Operations (Priority: P2)

**Goal**: Document AI-powered tools (Gordon, kubectl-ai, Kagent) for enhanced productivity

**Independent Test**: Execute AI-assisted commands for common operations, compare with manual commands, verify documentation accuracy

### Implementation for User Story 4

- [x] T043 [P] [US4] Create GORDON_GUIDE.md with Docker AI usage examples in k8s/docs/GORDON_GUIDE.md
- [x] T044 [P] [US4] Create KUBECTL_AI_GUIDE.md with kubectl-ai usage examples in k8s/docs/KUBECTL_AI_GUIDE.md
- [x] T045 [P] [US4] Create KAGENT_GUIDE.md with Kagent usage examples in k8s/docs/KAGENT_GUIDE.md
- [x] T046 [US4] Create AI_TOOLS_GUIDE.md with integrated AI tools workflow in k8s/docs/AI_TOOLS_GUIDE.md
- [x] T047 [US4] Add Gordon examples for Dockerfile generation and optimization to GORDON_GUIDE.md
- [x] T048 [US4] Add kubectl-ai examples for deployment, scaling, and troubleshooting to KUBECTL_AI_GUIDE.md
- [x] T049 [US4] Add Kagent examples for cluster analysis and resource optimization to KAGENT_GUIDE.md
- [x] T050 [US4] Add fallback instructions for standard Docker/kubectl commands to AI_TOOLS_GUIDE.md
- [x] T051 [US4] Add installation instructions for all AI tools to AI_TOOLS_GUIDE.md

**Validation Criteria**:
- Documentation covers all three AI tools (Gordon, kubectl-ai, Kagent)
- Examples are accurate and executable
- Fallback instructions provided for each AI tool operation
- Installation instructions clear and complete

---

## Phase 7: User Story 5 - Deployment Management (Priority: P2)

**Goal**: Implement lifecycle management procedures (updates, rollbacks, scaling)

**Independent Test**: Perform rolling update, rollback, and scaling operations, verify zero downtime and application functionality

### Implementation for User Story 5

- [x] T052 [P] [US5] Create update-deployment.sh script for rolling updates in k8s/scripts/update-deployment.sh
- [x] T053 [P] [US5] Create rollback-deployment.sh script for version rollback in k8s/scripts/rollback-deployment.sh
- [x] T054 [P] [US5] Create scale-deployment.sh script for horizontal scaling in k8s/scripts/scale-deployment.sh
- [x] T055 [US5] Create LIFECYCLE_MANAGEMENT.md guide in k8s/docs/LIFECYCLE_MANAGEMENT.md
- [x] T056 [US5] Add rolling update procedure with zero downtime to LIFECYCLE_MANAGEMENT.md
- [x] T057 [US5] Add rollback procedure with version history to LIFECYCLE_MANAGEMENT.md
- [x] T058 [US5] Add scaling procedure with replica management to LIFECYCLE_MANAGEMENT.md
- [x] T059 [US5] Add image update procedure with new tags to LIFECYCLE_MANAGEMENT.md
- [x] T060 [US5] Create test-rolling-update.sh script to verify zero downtime in k8s/scripts/test-rolling-update.sh

**Validation Criteria**:
- Rolling updates complete with zero downtime
- Rollback restores previous working version
- Scaling increases/decreases replicas successfully
- Load balancer distributes traffic across replicas
- Documentation covers all lifecycle operations

---

## Phase 8: User Story 6 - Infrastructure Validation (Priority: P3)

**Goal**: Validate production-readiness criteria for cloud promotion

**Independent Test**: Run validation checks for health probes, resource limits, security, and observability, verify all checks pass

### Implementation for User Story 6

- [x] T061 [P] [US6] Create validate-health-checks.sh script in k8s/scripts/validate-health-checks.sh
- [x] T062 [P] [US6] Create validate-resources.sh script in k8s/scripts/validate-resources.sh
- [x] T063 [P] [US6] Create validate-security.sh script in k8s/scripts/validate-security.sh
- [x] T064 [US6] Create PRODUCTION_READINESS.md checklist in k8s/docs/PRODUCTION_READINESS.md
- [x] T065 [US6] Add health check validation (liveness, readiness probes) to validate-health-checks.sh
- [x] T066 [US6] Add resource validation (requests, limits) to validate-resources.sh
- [x] T067 [US6] Add security validation (non-root users, capabilities) to validate-security.sh
- [x] T068 [US6] Add observability validation (logs, metrics) to PRODUCTION_READINESS.md
- [x] T069 [US6] Create run-all-validations.sh script to execute all checks in k8s/scripts/run-all-validations.sh
- [x] T070 [US6] Create TROUBLESHOOTING.md guide with common issues in k8s/docs/TROUBLESHOOTING.md

**Validation Criteria**:
- All health checks properly configured and responding
- Resource requests and limits defined for all containers
- Containers run as non-root users
- Logs accessible via kubectl logs
- All validation scripts pass successfully

---

## Phase 9: Polish & Cross-Cutting Concerns

**Purpose**: Final documentation, cleanup, and overall validation

- [x] T071 Create comprehensive README.md for k8s deployment in k8s/README.md
- [x] T072 Create cleanup.sh script to remove deployment in k8s/scripts/cleanup.sh
- [x] T073 Add prerequisites section to k8s/README.md (Docker, Minikube, Helm, kubectl)
- [x] T074 Add quick start section to k8s/README.md with 5-minute deployment guide
- [x] T075 Add architecture diagram to k8s/docs/ARCHITECTURE.md
- [x] T076 Add troubleshooting section to k8s/README.md with common issues
- [x] T077 Create CONTRIBUTING.md with guidelines for k8s artifacts in k8s/CONTRIBUTING.md
- [x] T078 Run final validation of all scripts and documentation
- [x] T079 Create deployment demo video or screenshots for documentation (N/A - comprehensive documentation provided instead)
- [x] T080 Update main project README.md with Phase V deployment instructions

---

## Dependencies & Execution Order

### User Story Dependencies

```
Phase 1 (Setup)
    ↓
Phase 3 (US1: Container Images) ← Independent, can start after Setup
    ↓
Phase 4 (US2: Helm Charts) ← Depends on US1 (needs images)
    ↓
Phase 5 (US3: Minikube Deployment) ← Depends on US1 + US2 (needs images + charts)
    ↓
Phase 6 (US4: AI Operations) ← Independent, can run in parallel with US5/US6
Phase 7 (US5: Lifecycle Management) ← Depends on US3 (needs deployed app)
Phase 8 (US6: Validation) ← Depends on US3 (needs deployed app)
    ↓
Phase 9 (Polish)
```

### Critical Path (MVP)

For minimum viable deployment, complete in order:
1. **Phase 1**: Setup (T001-T004)
2. **Phase 3**: US1 - Container Images (T005-T012)
3. **Phase 4**: US2 - Helm Charts (T013-T030)
4. **Phase 5**: US3 - Minikube Deployment (T031-T042)

**MVP Completion**: After Phase 5, you have a fully functional Kubernetes deployment.

### Parallel Execution Opportunities

**Within US1 (Container Images)**:
- T005 (backend Dockerfile) || T006 (frontend Dockerfile)
- T009 (backend optimization) || T010 (frontend optimization)

**Within US2 (Helm Charts)**:
- T016 (values-dev) || T017 (values-prod)
- T019 (backend deployment) || T020 (frontend deployment)
- T021 (backend service) || T022 (frontend service)
- T023 (configmap) || T024 (secrets)

**Within US4 (AI Operations)**:
- T043 (Gordon guide) || T044 (kubectl-ai guide) || T045 (Kagent guide)

**Within US5 (Lifecycle Management)**:
- T052 (update script) || T053 (rollback script) || T054 (scale script)

**Within US6 (Validation)**:
- T061 (health checks) || T062 (resources) || T063 (security)

---

## Implementation Strategy

### MVP First (Phases 1, 3, 4, 5)

**Goal**: Get basic Kubernetes deployment working
**Time**: ~4-6 hours
**Deliverables**:
- Docker images for backend and frontend
- Helm chart with all templates
- Deployed application on Minikube
- Basic deployment documentation

**Success Criteria**:
- All pods Running
- Application accessible and functional
- Health checks responding

### Enhancements (Phases 6, 7, 8)

**Goal**: Add productivity tools and validation
**Time**: ~2-3 hours
**Deliverables**:
- AI tools documentation
- Lifecycle management procedures
- Production-readiness validation

**Success Criteria**:
- AI tools documented with examples
- Rolling updates work with zero downtime
- All validation checks pass

### Polish (Phase 9)

**Goal**: Complete documentation and cleanup
**Time**: ~1-2 hours
**Deliverables**:
- Comprehensive README
- Architecture documentation
- Troubleshooting guide

**Success Criteria**:
- First-time deployment possible following README
- All common issues documented
- Clean, professional documentation

---

## Task Summary

**Total Tasks**: 80
- Phase 1 (Setup): 4 tasks
- Phase 2 (Foundational): 0 tasks (no blocking prerequisites)
- Phase 3 (US1 - Container Images): 8 tasks
- Phase 4 (US2 - Helm Charts): 18 tasks
- Phase 5 (US3 - Minikube Deployment): 12 tasks
- Phase 6 (US4 - AI Operations): 9 tasks
- Phase 7 (US5 - Lifecycle Management): 9 tasks
- Phase 8 (US6 - Validation): 10 tasks
- Phase 9 (Polish): 10 tasks

**Parallel Opportunities**: 23 tasks marked with [P]

**MVP Scope**: Phases 1, 3, 4, 5 (42 tasks) - Delivers fully functional Kubernetes deployment

**Independent Test Criteria**:
- US1: Build images, run locally, verify health checks
- US2: Helm lint, dry-run, verify manifests
- US3: Deploy to Minikube, verify pods Running, test application
- US4: Execute AI commands, verify documentation
- US5: Perform updates/rollbacks/scaling, verify zero downtime
- US6: Run validation scripts, verify all checks pass

---

## Format Validation

✅ All tasks follow checklist format: `- [ ] [TaskID] [P?] [Story?] Description with file path`
✅ Task IDs sequential (T001-T080)
✅ [P] markers for parallelizable tasks (23 tasks)
✅ [US#] markers for user story tasks (66 tasks)
✅ File paths included in all implementation tasks
✅ Phases organized by user story priority
✅ Independent test criteria defined for each story
✅ Dependencies clearly documented
✅ MVP scope identified (Phases 1, 3, 4, 5)
