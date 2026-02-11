# Research: Advanced Cloud Deployment Technologies

**Feature**: 006-advanced-cloud-deployment
**Date**: 2026-02-11
**Purpose**: Technology evaluation and decision-making for Phase VI implementation

## 1. Message Streaming Platform Selection

### Options Evaluated

#### Option A: Redpanda Cloud (Serverless) ⭐ RECOMMENDED

**Decision**: Use Redpanda Cloud for message streaming

**Rationale**:
- Kafka-compatible API (drop-in replacement for existing Kafka clients)
- Free serverless tier: 10GB storage, 10MB/s throughput (sufficient for hackathon/learning)
- No ZooKeeper dependency (simpler architecture, fewer moving parts)
- Better performance than Kafka (C++ implementation vs JVM)
- Built-in schema registry
- Simple setup (managed service, no operational overhead)

**Alternatives Considered**:
- **Confluent Cloud**: $400 credits provide 3-4 months, excellent ecosystem, but more expensive after credits expire
- **Self-hosted Strimzi**: Complete control and free, but high operational overhead (3-6GB RAM minimum, complex troubleshooting)

**Implementation Guidance**:
- Use standard Kafka client libraries (kafka-python, aiokafka for Python)
- Configure bootstrap servers with Redpanda Cloud endpoint
- Use SASL_SSL for authentication
- Topics: `task-events`, `reminders`, `task-updates`

---

## 2. Distributed Application Runtime (Dapr)

### Decision: Use Dapr for Infrastructure Abstraction

**Rationale**:
- Language-agnostic HTTP/gRPC APIs (no vendor lock-in)
- Abstracts infrastructure complexity (swap Redis for PostgreSQL without code changes)
- Built-in observability (distributed tracing, metrics)
- Kubernetes-native deployment (sidecar pattern)
- Supports all required building blocks:
  - Pub/sub for Kafka abstraction
  - State management for conversation/session state
  - Service invocation with retries and circuit breaking
  - Bindings for cron triggers (recurring tasks)
  - Secrets management

**Trade-offs**:
- Additional sidecar overhead (50-100MB per pod)
- Learning curve for new concepts
- Debugging complexity (need to understand sidecar communication)

**Alternatives Considered**:
- **Direct Kafka clients**: Simpler initially but tightly couples code to Kafka
- **Custom abstraction layer**: More control but reinventing the wheel

**Implementation Guidance**:

**Sidecar Injection** (Kubernetes annotations):
```yaml
annotations:
  dapr.io/enabled: "true"
  dapr.io/app-id: "todo-api"
  dapr.io/app-port: "8000"
  dapr.io/log-level: "info"
```

**Pub/Sub Component** (Kafka):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.kafka
  metadata:
  - name: brokers
    value: "redpanda-cloud-endpoint:9092"
  - name: consumerGroup
    value: "todo-service"
  - name: authType
    value: "password"
```

**State Store Component** (Redis):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  metadata:
  - name: redisHost
    value: "redis:6379"
```

**Cron Binding** (Recurring tasks safety net):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: recurring-task-cron
spec:
  type: bindings.cron
  metadata:
  - name: schedule
    value: "@every 5m"
```

---

## 3. Recurring Tasks Implementation Pattern

### Decision: Hybrid Event-Driven + Cron Safety Net

**Rationale**:
- **Primary**: Event-driven approach for immediate response to user actions
- **Safety Net**: Cron job checks for missed occurrences every 5 minutes
- Provides best of both worlds: responsiveness + reliability

**Pattern A: Event-Driven (Primary)**:
```
User completes task → task.completed event published →
Consumer receives event → Calculate next occurrence →
Create new task with future due date
```

**Pros**:
- Immediate response (no polling delay)
- Natural audit trail (all events logged)
- Scales horizontally (multiple consumers)
- Aligns with event-driven architecture goal

**Cons**:
- Requires message broker
- Need idempotency checks (handle duplicate events)
- More complex error handling

**Pattern B: Cron Safety Net (Backup)**:
```
Cron runs every 5 minutes → Query tasks with nextOccurrence < now →
Create missing tasks → Update nextOccurrence timestamp
```

**Pros**:
- Catches missed events (broker downtime, consumer failures)
- Simple to understand and debug
- No message broker dependency

**Cons**:
- Polling overhead
- Delayed task creation (up to 5 minutes)

**Implementation Approach**:
1. Store `recurrence_pattern` (daily/weekly/monthly) and `next_occurrence_date` in task table
2. On task completion, publish `task.completed` event with recurrence metadata
3. Recurring Task Service consumes events and creates next occurrence
4. Cron job runs every 5 minutes to catch any missed occurrences
5. Use database unique constraint on (parent_task_id, next_occurrence_date) to prevent duplicates

**Edge Cases Handled**:
- **Deletion during creation**: Check parent task status before creating occurrence
- **Timezone issues**: Store all dates in UTC, convert on display
- **DST transitions**: Use `python-dateutil` for timezone-aware calculations
- **Concurrent creation**: Database unique constraint prevents duplicates
- **Clock skew**: Cron safety net catches missed occurrences

---

## 4. Reminder/Notification System

### Decision: Scheduled Notification Pattern with Multiple Delivery Channels

**Architecture**:
```
[Task Service] → [Kafka: reminders topic] → [Notification Scheduler] →
[Scheduled Notifications Table] → [Cron Job] → [Kafka: notification.send] →
[Delivery Workers] → [Email/Push]
```

**Rationale**:
- Decoupled from task service (separate concern)
- Supports multiple delivery channels (email, push, future: SMS)
- Retry logic for failed deliveries
- Audit trail of all notifications

**Email Delivery: Resend (Recommended)**

**Decision**: Use Resend for email notifications

**Rationale**:
- Free tier: 3,000 emails/month (sufficient for hackathon)
- Modern API with excellent developer experience
- Good deliverability rates
- Simple setup (API key only)

**Alternatives Considered**:
- **SendGrid**: 100 emails/day (too limited)
- **AWS SES**: 62,000/month but requires AWS account and sandbox approval
- **SMTP (Gmail)**: 500/day but spam issues and rate limits

**Implementation**:
```python
import resend

resend.api_key = os.environ["RESEND_API_KEY"]

resend.Emails.send({
    "from": "noreply@todoapp.com",
    "to": user.email,
    "subject": "Task Reminder: {task.title}",
    "html": f"<p>Your task '{task.title}' is due at {task.due_date}</p>"
})
```

**Push Notifications: Web Push API**

**Decision**: Use Web Push API for browser notifications

**Rationale**:
- Native browser support (no third-party service needed)
- Free (no API costs)
- Works offline (service workers)
- Good for web applications

**Implementation**:
```javascript
// Service worker registration
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.register('/sw.js');

  // Request notification permission
  const permission = await Notification.requestPermission();

  // Subscribe to push notifications
  const subscription = await registration.pushManager.subscribe({
    userVisibleOnly: true,
    applicationServerKey: PUBLIC_VAPID_KEY
  });
}
```

**Retry and Failure Handling**:
- Store notification status: pending, queued, sent, failed
- Retry failed notifications up to 3 times with exponential backoff
- Log all failures for debugging
- Provide user preference for notification channels

---

## 5. Cloud Provider Selection

### Decision: Oracle Cloud OKE (Always Free Tier) ⭐ RECOMMENDED

**Rationale**:
- **Always free tier**: 4 OCPUs, 24GB RAM (no time limit, no credit card charge)
- Sufficient resources for learning and hackathon projects
- Managed Kubernetes service (OKE)
- No pressure to complete within trial period
- Good for long-term learning

**Alternatives Considered**:
- **Azure AKS**: $200 credits for 30 days (good but time-limited)
- **Google Cloud GKE**: $300 credits for 90 days (generous but expires)

**Implementation Guidance**:
1. Sign up at https://www.oracle.com/cloud/free/
2. Create OKE cluster (1 node pool, 2 nodes, 2 OCPUs each)
3. Configure kubectl: `oci ce cluster create-kubeconfig`
4. Deploy using Helm charts from Phase V
5. Configure ingress for external access

**Fallback Options**:
- If Oracle Cloud signup issues, use Google Cloud GKE (90-day trial)
- If budget allows, Azure AKS provides excellent developer experience

---

## 6. CI/CD Pipeline (GitHub Actions)

### Decision: GitHub Actions for CI/CD Automation

**Rationale**:
- Native GitHub integration (no external service needed)
- Free for public repositories (2,000 minutes/month for private)
- Excellent Kubernetes and Docker support
- Large marketplace of pre-built actions
- Simple YAML configuration

**Pipeline Stages**:

**1. Test Stage** (on push to any branch):
```yaml
- Run unit tests (pytest, jest)
- Run integration tests
- Run linting (ruff, eslint)
- Generate coverage reports
```

**2. Build Stage** (on push to main or release branches):
```yaml
- Build Docker images (backend, frontend)
- Tag with commit SHA and branch name
- Push to container registry (GitHub Container Registry)
```

**3. Deploy Stage** (on push to main):
```yaml
- Deploy to staging environment (automatic)
- Run smoke tests
- Wait for manual approval
- Deploy to production (manual trigger)
```

**Implementation**:
```yaml
name: CI/CD Pipeline

on:
  push:
    branches: [main, develop]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          cd backend && pytest
          cd frontend && npm test

  build:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Build and push Docker images
        run: |
          docker build -t ghcr.io/${{ github.repository }}/backend:${{ github.sha }} ./backend
          docker push ghcr.io/${{ github.repository }}/backend:${{ github.sha }}

  deploy:
    needs: build
    runs-on: ubuntu-latest
    if: github.ref == 'refs/heads/main'
    steps:
      - name: Deploy to Kubernetes
        run: |
          helm upgrade --install todo-app ./helm-charts/todo-chatbot \
            --set backend.image.tag=${{ github.sha }} \
            --set frontend.image.tag=${{ github.sha }}
```

**Secrets Management**:
- Store cloud credentials in GitHub Secrets
- Use OIDC for keyless authentication (recommended)
- Rotate secrets regularly

---

## 7. Additional Technology Decisions

### Database Schema Extensions

**Decision**: Extend existing PostgreSQL schema with new tables

**New Tables**:
- `recurring_tasks`: Stores recurrence patterns and next occurrence dates
- `reminders`: Stores scheduled reminder notifications
- `task_events`: Audit log of all task operations (optional, can use Kafka retention)
- `scheduled_notifications`: Queue of pending notifications

**Rationale**:
- Reuse existing Neon PostgreSQL database (no new infrastructure)
- Maintain data consistency with existing tasks
- Enable complex queries (e.g., "show all overdue tasks with reminders")

### Frontend Enhancements

**Decision**: Extend existing Next.js frontend with new components

**New Components**:
- `RecurrenceSelector`: UI for selecting daily/weekly/monthly recurrence
- `DateTimePicker`: UI for setting due dates and reminder times
- `NotificationPreferences`: UI for managing notification channels
- `TaskFilters`: Enhanced filtering by priority, tags, due date range

**Rationale**:
- Reuse existing component library and styling
- Maintain consistent user experience
- Progressive enhancement (new features don't break existing functionality)

### Monitoring and Observability

**Decision**: Use Prometheus + Grafana for monitoring

**Rationale**:
- Kubernetes-native (easy to deploy with Helm)
- Free and open-source
- Excellent Dapr integration (built-in metrics)
- Large community and pre-built dashboards

**Key Metrics to Track**:
- Task operation rates (create, update, complete, delete)
- Event publishing latency
- Consumer lag (Kafka)
- Notification delivery success rate
- API response times (p50, p95, p99)
- Error rates by service

---

## Summary of Technology Stack

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| Message Streaming | Redpanda Cloud | Free tier, Kafka-compatible, simple setup |
| Distributed Runtime | Dapr | Infrastructure abstraction, Kubernetes-native |
| Recurring Tasks | Event-driven + Cron | Responsive + reliable |
| Email Notifications | Resend | 3,000/month free, modern API |
| Push Notifications | Web Push API | Native browser support, free |
| Cloud Provider | Oracle Cloud OKE | Always free tier, no time pressure |
| CI/CD | GitHub Actions | Native integration, free for public repos |
| Monitoring | Prometheus + Grafana | Kubernetes-native, free, excellent Dapr support |
| Database | PostgreSQL (Neon) | Reuse existing, extend schema |
| Frontend | Next.js (existing) | Extend with new components |
| Backend | FastAPI (existing) | Add new services and event handlers |

---

## Implementation Risks and Mitigations

### Risk 1: Message Broker Complexity
**Impact**: Developers unfamiliar with event-driven architecture may struggle
**Mitigation**:
- Provide clear documentation and examples
- Use Dapr abstraction to simplify Kafka interaction
- Start with simple pub/sub, add complexity gradually

### Risk 2: Dapr Learning Curve
**Impact**: New concepts (sidecars, components) may slow development
**Mitigation**:
- Provide reference implementations
- Start with one building block (pub/sub), add others incrementally
- Use Dapr dashboard for debugging

### Risk 3: Cloud Cost Overruns
**Impact**: Free tier limits may be exceeded
**Mitigation**:
- Use Oracle Cloud always-free tier (no expiration)
- Monitor resource usage closely
- Set up billing alerts
- Document cost optimization tips

### Risk 4: Timezone Complexity
**Impact**: Single timezone assumption may not work for global users
**Mitigation**:
- Store all timestamps in UTC
- Document limitation clearly
- Plan for multi-timezone support in future phase

### Risk 5: Event Ordering Issues
**Impact**: Lack of strict ordering may cause race conditions
**Mitigation**:
- Use idempotent event processing
- Include sequence numbers in events
- Use database constraints to prevent duplicates
- Document eventual consistency model

---

## Next Steps

1. **Phase 1: Design & Contracts**
   - Create data-model.md with extended schema
   - Generate API contracts for new endpoints
   - Create quickstart.md for local development

2. **Phase 2: Tasks**
   - Break down implementation into testable tasks
   - Prioritize MVP features (recurring tasks, due dates, event publishing)
   - Define acceptance criteria for each task

3. **Phase 3: Implementation**
   - Implement backend services (Recurring Task Service, Notification Service)
   - Extend frontend with new components
   - Deploy Dapr to Kubernetes
   - Configure Redpanda Cloud
   - Set up CI/CD pipeline

4. **Phase 4: Testing & Validation**
   - Test event-driven flows end-to-end
   - Validate recurring task creation accuracy
   - Test notification delivery
   - Load test with 1,000 concurrent users
   - Validate cloud deployment

---

**Research Completed**: 2026-02-11
**Reviewed By**: Claude Sonnet 4.5
**Status**: Ready for Phase 1 (Design & Contracts)
