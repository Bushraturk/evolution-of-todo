# Architecture: Todo Chatbot Kubernetes Deployment

**Feature**: Local Kubernetes Deployment (Phase V)
**Purpose**: Detailed architecture documentation for Kubernetes deployment

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Network Architecture](#network-architecture)
4. [Data Flow](#data-flow)
5. [Security Architecture](#security-architecture)
6. [Deployment Architecture](#deployment-architecture)
7. [Scaling Architecture](#scaling-architecture)
8. [Design Decisions](#design-decisions)

---

## System Overview

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         User Browser                             │
└────────────────────────────┬────────────────────────────────────┘
                             │ HTTPS (future)
                             │ HTTP (current)
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                      Minikube Cluster                            │
│                                                                  │
│  ┌────────────────────────────────────────────────────────┐   │
│  │              LoadBalancer Service                       │   │
│  │              (frontend-service)                         │   │
│  │              Port: 80 → 3000                            │   │
│  └────────────────────────┬───────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────▼───────────────────────────────┐   │
│  │           Frontend Deployment (Next.js)                 │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │  Pod 1   │  │  Pod 2   │  │  Pod N   │            │   │
│  │  │ (1-5x)   │  │          │  │          │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘            │   │
│  │  - Next.js 14                                          │   │
│  │  - Node 20 Alpine                                      │   │
│  │  - Health: /api/health                                 │   │
│  │  - Resources: 50m CPU, 128Mi RAM                       │   │
│  └────────────────────────┬───────────────────────────────┘   │
│                           │ HTTP (internal)                     │
│                           │ http://backend:8000                 │
│  ┌────────────────────────▼───────────────────────────────┐   │
│  │              ClusterIP Service                          │   │
│  │              (backend-service)                          │   │
│  │              Port: 8000                                 │   │
│  └────────────────────────┬───────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────▼───────────────────────────────┐   │
│  │           Backend Deployment (FastAPI)                  │   │
│  │  ┌──────────┐  ┌──────────┐  ┌──────────┐            │   │
│  │  │  Pod 1   │  │  Pod 2   │  │  Pod N   │            │   │
│  │  │ (1-10x)  │  │          │  │          │            │   │
│  │  └──────────┘  └──────────┘  └──────────┘            │   │
│  │  - FastAPI                                             │   │
│  │  - Python 3.13                                         │   │
│  │  - Health: /health                                     │   │
│  │  - Resources: 100m CPU, 256Mi RAM                      │   │
│  └────────────────────────┬───────────────────────────────┘   │
│                           │                                     │
│  ┌────────────────────────▼───────────────────────────────┐   │
│  │              Secrets & ConfigMaps                       │   │
│  │  - DATABASE_URL (secret)                               │   │
│  │  - GROQ_API_KEY (secret)                               │   │
│  │  - JWT_SECRET (secret)                                 │   │
│  │  - App configuration (configmap)                       │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                  │
└──────────────────────────┬───────────────────────────────────────┘
                           │ PostgreSQL
                           │ (external)
                           ▼
                ┌──────────────────────┐
                │  Neon PostgreSQL     │
                │  (Managed Service)   │
                │  - User data         │
                │  - Todo items        │
                │  - Conversations     │
                └──────────────────────┘
                           │
                           │ HTTPS
                           ▼
                ┌──────────────────────┐
                │  Groq API            │
                │  (External Service)  │
                │  - LLM inference     │
                │  - Function calling  │
                └──────────────────────┘
```

### Component Summary

| Component | Technology | Purpose | Replicas |
|-----------|-----------|---------|----------|
| **Frontend** | Next.js 14, Node 20 | User interface, SSR | 1-5 (autoscaling) |
| **Backend** | FastAPI, Python 3.13 | API server, business logic | 1-10 (autoscaling) |
| **Database** | PostgreSQL (Neon) | Data persistence | 1 (managed) |
| **LLM** | Groq API | AI inference | N/A (external) |

---

## Component Architecture

### Frontend (Next.js)

**Purpose**: Server-side rendered React application with AI chat interface

**Technology Stack**:
- Next.js 14 (App Router)
- React 18
- TypeScript
- Tailwind CSS
- Node.js 20 Alpine

**Container Specifications**:
```yaml
Image: todo-frontend:latest
Base: node:20-alpine
Size: ~180MB
Port: 3000
User: nextjs (UID 1001)
```

**Resource Configuration**:
```yaml
Requests:
  CPU: 50m
  Memory: 128Mi
Limits:
  CPU: 200m
  Memory: 256Mi
```

**Health Checks**:
```yaml
Liveness Probe:
  Path: /api/health
  Port: 3000
  Initial Delay: 10s
  Period: 10s

Readiness Probe:
  Path: /api/health
  Port: 3000
  Initial Delay: 5s
  Period: 5s
```

**Key Features**:
- Server-side rendering for SEO
- API routes for backend communication
- Real-time chat interface
- Responsive design
- Standalone output for minimal size

---

### Backend (FastAPI)

**Purpose**: RESTful API server with AI-powered natural language processing

**Technology Stack**:
- FastAPI
- Python 3.13
- SQLAlchemy (ORM)
- Pydantic (validation)
- Uvicorn (ASGI server)

**Container Specifications**:
```yaml
Image: todo-backend:latest
Base: python:3.13-slim
Size: ~450MB
Port: 8000
User: appuser (UID 1000)
```

**Resource Configuration**:
```yaml
Requests:
  CPU: 100m
  Memory: 256Mi
Limits:
  CPU: 500m
  Memory: 512Mi
```

**Health Checks**:
```yaml
Liveness Probe:
  Path: /health
  Port: 8000
  Initial Delay: 10s
  Period: 10s

Readiness Probe:
  Path: /health
  Port: 8000
  Initial Delay: 5s
  Period: 5s

Startup Probe:
  Path: /health
  Port: 8000
  Initial Delay: 0s
  Period: 5s
  Failure Threshold: 30
```

**Key Features**:
- RESTful API endpoints
- JWT authentication
- Natural language processing
- Function calling for todo operations
- Database connection pooling
- Structured logging

---

### Database (PostgreSQL)

**Purpose**: Persistent data storage

**Technology**: Neon PostgreSQL (managed service)

**Schema**:
```sql
-- Users table
users (
  id UUID PRIMARY KEY,
  email VARCHAR UNIQUE,
  hashed_password VARCHAR,
  created_at TIMESTAMP
)

-- Todos table
todos (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  title VARCHAR,
  description TEXT,
  completed BOOLEAN,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)

-- Conversations table
conversations (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES users(id),
  messages JSONB,
  created_at TIMESTAMP,
  updated_at TIMESTAMP
)
```

**Connection**:
- Connection string stored in Kubernetes Secret
- SSL/TLS encryption
- Connection pooling in backend

---

## Network Architecture

### Service Types

#### Frontend Service (LoadBalancer)

```yaml
Type: LoadBalancer
Port: 80 (external) → 3000 (container)
Selector: app.kubernetes.io/component=frontend
```

**Purpose**: Expose frontend to external traffic

**Access Methods**:
1. **Minikube Tunnel**: `minikube tunnel` → http://localhost
2. **NodePort**: http://$(minikube ip):$(nodePort)
3. **Port Forward**: `kubectl port-forward service/frontend 3000:80`

#### Backend Service (ClusterIP)

```yaml
Type: ClusterIP
Port: 8000 (internal only)
Selector: app.kubernetes.io/component=backend
```

**Purpose**: Internal service for frontend-to-backend communication

**Access**: Only accessible within cluster at `http://backend:8000`

### Network Policies (Future)

```yaml
# Frontend → Backend only
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: backend-ingress
spec:
  podSelector:
    matchLabels:
      app.kubernetes.io/component: backend
  ingress:
  - from:
    - podSelector:
        matchLabels:
          app.kubernetes.io/component: frontend
    ports:
    - protocol: TCP
      port: 8000
```

---

## Data Flow

### User Request Flow

```
1. User → Browser
   ↓
2. Browser → Frontend Service (LoadBalancer)
   HTTP GET /
   ↓
3. Frontend Pod → SSR
   Render React components
   ↓
4. Frontend → Backend Service (ClusterIP)
   HTTP GET /api/todos
   Headers: Authorization: Bearer <JWT>
   ↓
5. Backend Pod → Validate JWT
   ↓
6. Backend → Database (Neon PostgreSQL)
   SQL: SELECT * FROM todos WHERE user_id = ?
   ↓
7. Database → Backend
   Return todo items
   ↓
8. Backend → Frontend
   JSON: { todos: [...] }
   ↓
9. Frontend → Browser
   HTML with rendered todos
   ↓
10. Browser → User
    Display page
```

### AI Chat Flow

```
1. User types message in chat
   ↓
2. Frontend → Backend
   POST /api/chat
   Body: { message: "add task buy milk" }
   ↓
3. Backend → Groq API
   POST /chat/completions
   Body: {
     model: "llama-3.3-70b-versatile",
     messages: [...],
     tools: [add_todo, list_todos, ...]
   }
   ↓
4. Groq API → Backend
   Response: {
     tool_calls: [{
       function: "add_todo",
       arguments: { title: "buy milk" }
     }]
   }
   ↓
5. Backend → Execute function
   INSERT INTO todos (title, ...) VALUES (...)
   ↓
6. Backend → Groq API
   Send function result
   ↓
7. Groq API → Backend
   Final response: "I've added 'buy milk' to your list"
   ↓
8. Backend → Frontend
   JSON: { response: "...", todos: [...] }
   ↓
9. Frontend → User
   Display AI response and updated todo list
```

---

## Security Architecture

### Pod Security

**Security Context**:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000 (backend) / 1001 (frontend)
  fsGroup: 1000 / 1001
  allowPrivilegeEscalation: false
  readOnlyRootFilesystem: true (where possible)
  capabilities:
    drop:
      - ALL
```

**Image Security**:
- Multi-stage builds (separate build and runtime)
- Minimal base images (alpine, slim)
- No root user
- Regular vulnerability scanning
- Specific version tags (no `latest`)

### Secrets Management

**Kubernetes Secrets**:
```yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
type: Opaque
data:
  DATABASE_URL: <base64-encoded>
  GROQ_API_KEY: <base64-encoded>
  JWT_SECRET: <base64-encoded>
```

**Best Practices**:
- Never commit secrets to git
- Use `.env` file locally (gitignored)
- Rotate secrets regularly
- Encrypt secrets at rest (cloud provider feature)
- Use RBAC to restrict secret access

### Network Security

**Current**:
- ClusterIP for internal services
- LoadBalancer for external access
- No network policies (permissive)

**Future (Production)**:
- Network policies to restrict traffic
- TLS/SSL for all external endpoints
- mTLS for internal service communication
- Ingress controller with TLS termination

---

## Deployment Architecture

### Helm Chart Structure

```
helm-charts/todo-chatbot/
├── Chart.yaml              # Chart metadata
├── values.yaml             # Default values
├── values-dev.yaml         # Development overrides
├── values-prod.yaml        # Production overrides
└── templates/
    ├── _helpers.tpl        # Template helpers
    ├── backend-deployment.yaml
    ├── frontend-deployment.yaml
    ├── backend-service.yaml
    ├── frontend-service.yaml
    ├── configmap.yaml
    ├── secrets.yaml
    └── NOTES.txt           # Post-install instructions
```

### Deployment Strategy

**Rolling Update**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # Max new pods above desired
    maxUnavailable: 0  # Keep all old pods until new ready
```

**Benefits**:
- Zero downtime deployments
- Gradual rollout
- Easy rollback
- Health check validation

**Process**:
1. Create new pod with updated image
2. Wait for health checks to pass
3. Add new pod to service endpoints
4. Remove old pod from service endpoints
5. Terminate old pod
6. Repeat for remaining pods

---

## Scaling Architecture

### Horizontal Pod Autoscaling (HPA)

**Backend HPA**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: backend
  minReplicas: 2
  maxReplicas: 10
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
```

**Frontend HPA**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: frontend
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: frontend
  minReplicas: 1
  maxReplicas: 5
  metrics:
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 60
```

**Scaling Behavior**:
- Scale up: When CPU > threshold for 3 minutes
- Scale down: When CPU < threshold for 5 minutes
- Cooldown: 3 minutes between scale operations

### Load Distribution

**Service Load Balancing**:
- Round-robin by default
- Session affinity: None (stateless)
- Health check-based routing

---

## Design Decisions

### 1. Why Minikube for Local Development?

**Decision**: Use Minikube instead of kind, k3s, or Docker Desktop Kubernetes

**Rationale**:
- Easy to install and use
- Good documentation
- Supports LoadBalancer via `minikube tunnel`
- Addons for metrics-server, dashboard, etc.
- Similar to production Kubernetes

**Trade-offs**:
- Requires separate VM (more resource usage)
- Slower startup than kind
- Single-node only (no multi-node testing)

### 2. Why Helm for Deployment?

**Decision**: Use Helm instead of raw Kubernetes manifests or Kustomize

**Rationale**:
- Templating for environment-specific values
- Package management (versioning, rollback)
- Widely adopted in industry
- Good for learning production practices

**Trade-offs**:
- Additional tool to learn
- Template syntax can be complex
- Overkill for simple deployments

### 3. Why Multi-Stage Docker Builds?

**Decision**: Use multi-stage builds instead of single-stage

**Rationale**:
- Smaller final images (exclude build tools)
- Better security (minimal attack surface)
- Faster deployment (smaller images)
- Industry best practice

**Trade-offs**:
- More complex Dockerfiles
- Longer build times (multiple stages)

### 4. Why ClusterIP for Backend?

**Decision**: Use ClusterIP instead of LoadBalancer for backend

**Rationale**:
- Backend should not be directly accessible externally
- Frontend acts as API gateway
- Better security (defense in depth)
- Simpler network topology

**Trade-offs**:
- Cannot access backend directly from outside cluster
- Need port-forward for debugging

### 5. Why Horizontal Pod Autoscaling?

**Decision**: Use HPA instead of fixed replica counts

**Rationale**:
- Handles variable load automatically
- Cost-effective (scale down when idle)
- Better resource utilization
- Production-ready practice

**Trade-offs**:
- Requires metrics-server
- More complex to configure
- Can cause instability if misconfigured

### 6. Why External Database (Neon)?

**Decision**: Use external managed database instead of in-cluster PostgreSQL

**Rationale**:
- Managed service (no maintenance)
- Better reliability and backups
- Easier to scale
- Persistent across cluster recreations

**Trade-offs**:
- External dependency
- Network latency
- Cost (vs free in-cluster)

---

## Future Enhancements

### Phase VI: Cloud Deployment

1. **Managed Kubernetes**: EKS, GKE, or AKS
2. **Ingress Controller**: NGINX or Traefik with TLS
3. **Network Policies**: Restrict pod-to-pod traffic
4. **Service Mesh**: Istio or Linkerd for mTLS
5. **Monitoring**: Prometheus + Grafana
6. **Logging**: ELK or Loki stack
7. **CI/CD**: GitHub Actions or GitLab CI
8. **Multi-region**: Active-active or active-passive

### Observability

1. **Metrics**: Prometheus metrics from applications
2. **Tracing**: OpenTelemetry for distributed tracing
3. **Logging**: Structured JSON logs to centralized system
4. **Dashboards**: Grafana dashboards for key metrics
5. **Alerting**: PagerDuty or Opsgenie integration

### Security Enhancements

1. **Pod Security Standards**: Enforce restricted profile
2. **Network Policies**: Default deny, explicit allow
3. **Service Mesh**: mTLS for all internal traffic
4. **Secrets Management**: External secrets operator (AWS Secrets Manager, etc.)
5. **Image Scanning**: Automated vulnerability scanning in CI/CD
6. **RBAC**: Fine-grained access control

---

## References

- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Helm Documentation**: https://helm.sh/docs/
- **Docker Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **12-Factor App**: https://12factor.net/
- **CNCF Landscape**: https://landscape.cncf.io/

---

**Last Updated**: 2026-02-08
**Phase**: V - Local Kubernetes Deployment
**Status**: Production Ready
**Next Phase**: VI - Cloud Deployment (AWS/GCP/Azure)
