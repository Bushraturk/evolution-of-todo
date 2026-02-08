# Research: Local Kubernetes Deployment

**Feature**: 005-k8s-local-deployment
**Date**: 2026-02-08
**Purpose**: Resolve technical unknowns and establish best practices for containerization and Kubernetes deployment

## Research Areas & Decisions

### 1. Docker Multi-Stage Builds

#### Backend (Python FastAPI)

**Decision**: Use `python:3.13-slim` with multi-stage build

**Rationale**:
- `python:3.13-slim` provides Python runtime with minimal system packages (~150MB base)
- Multi-stage build separates build dependencies from runtime dependencies
- Reduces final image size by excluding build tools (gcc, make, etc.)
- Security benefit: fewer packages = smaller attack surface

**Build Strategy**:
```dockerfile
# Stage 1: Builder (install dependencies)
FROM python:3.13-slim as builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime (copy only installed packages)
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY src/ ./src/
ENV PATH=/root/.local/bin:$PATH
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Alternatives Considered**:
- `python:3.13-alpine`: Rejected due to musl libc compatibility issues with some Python packages (psycopg2, numpy)
- `python:3.13` (full): Rejected due to large size (~1GB) with unnecessary packages
- Distroless images: Rejected due to debugging complexity in local development

**Expected Size**: 400-500MB (base 150MB + dependencies 250-350MB)

#### Frontend (Next.js)

**Decision**: Use `node:20-alpine` with multi-stage build for SSR

**Rationale**:
- Next.js requires Node.js runtime for Server-Side Rendering (SSR)
- Alpine variant provides minimal base (~50MB) with necessary libraries
- Multi-stage build separates build artifacts from runtime
- SSR needed for authentication and dynamic content

**Build Strategy**:
```dockerfile
# Stage 1: Dependencies
FROM node:20-alpine AS deps
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci --only=production

# Stage 2: Builder
FROM node:20-alpine AS builder
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

# Stage 3: Runner
FROM node:20-alpine AS runner
WORKDIR /app
ENV NODE_ENV production
COPY --from=builder /app/public ./public
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
EXPOSE 3000
CMD ["node", "server.js"]
```

**Alternatives Considered**:
- Static export with nginx: Rejected because SSR is required for authentication flows and dynamic content
- `node:20-slim`: Rejected because Alpine is smaller and sufficient for Next.js
- Standalone output: Selected (Next.js 13+ feature reduces size by excluding node_modules)

**Expected Size**: 150-200MB (base 50MB + Next.js runtime 100-150MB)

---

### 2. Helm Chart Best Practices

#### Chart Structure

**Decision**: Single chart with separate templates for backend and frontend

**Rationale**:
- Atomic deployments: Both services deploy together
- Shared configuration: Common values (database URL, secrets) defined once
- Simplified management: Single `helm install/upgrade/rollback` command
- Dependency management: Frontend depends on backend being available

**Chart Organization**:
```
todo-chatbot/
├── Chart.yaml          # Metadata (name, version, description)
├── values.yaml         # Default values (dev-friendly)
├── values-dev.yaml     # Development overrides
├── values-prod.yaml    # Production overrides
└── templates/
    ├── _helpers.tpl            # Reusable template functions
    ├── backend-deployment.yaml # Backend Deployment
    ├── backend-service.yaml    # Backend Service (ClusterIP)
    ├── frontend-deployment.yaml# Frontend Deployment
    ├── frontend-service.yaml   # Frontend Service (LoadBalancer)
    ├── configmap.yaml          # Non-sensitive config
    ├── secrets.yaml            # Sensitive data template
    └── NOTES.txt               # Post-install instructions
```

**Alternatives Considered**:
- Separate charts for backend/frontend: Rejected due to increased complexity and coordination overhead
- Umbrella chart with subcharts: Rejected as overkill for 2 services
- Kustomize instead of Helm: Rejected because Helm provides better templating and rollback capabilities

#### Values.yaml Organization

**Decision**: Hierarchical structure with environment-specific overrides

**Structure**:
```yaml
# Global settings
global:
  environment: development
  domain: localhost

# Backend configuration
backend:
  image:
    repository: todo-backend
    tag: latest
    pullPolicy: IfNotPresent
  replicas: 1
  resources:
    requests:
      cpu: 100m
      memory: 256Mi
    limits:
      cpu: 500m
      memory: 512Mi
  env:
    DATABASE_URL: ""  # Override in secrets
    GROQ_API_KEY: ""  # Override in secrets

# Frontend configuration
frontend:
  image:
    repository: todo-frontend
    tag: latest
    pullPolicy: IfNotPresent
  replicas: 1
  resources:
    requests:
      cpu: 50m
      memory: 128Mi
    limits:
      cpu: 200m
      memory: 256Mi
  env:
    NEXT_PUBLIC_API_URL: http://backend:8000
```

**Rationale**:
- Clear separation between backend and frontend config
- Resource requests/limits prevent resource starvation
- Environment variables templated for flexibility
- Secrets separated from values (security best practice)

#### Health Check Configuration

**Decision**: Implement liveness, readiness, and startup probes for both services

**Backend Probes**:
```yaml
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 2

startupProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 0
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 12  # 60 seconds max startup time
```

**Frontend Probes**:
```yaml
livenessProbe:
  httpGet:
    path: /api/health
    port: 3000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 2
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /api/health
    port: 3000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 2
  failureThreshold: 2
```

**Rationale**:
- Startup probe prevents premature liveness checks during slow startup
- Readiness probe ensures traffic only goes to ready pods
- Liveness probe restarts unhealthy pods
- Aggressive timeouts (2s) ensure fast failure detection

---

### 3. Minikube Networking

#### Service Exposure Strategy

**Backend Service**:
- **Type**: ClusterIP (internal only)
- **Port**: 8000
- **Rationale**: Backend should not be directly accessible from outside cluster, only via frontend

**Frontend Service**:
- **Type**: LoadBalancer (with Minikube tunnel)
- **Port**: 80 → 3000
- **Rationale**: Enables external access for testing, mimics cloud LoadBalancer behavior

**Access Methods**:
1. **Minikube tunnel**: `minikube tunnel` (requires admin/sudo)
2. **NodePort**: Fallback if tunnel unavailable
3. **Port forwarding**: `kubectl port-forward` for debugging

**DNS Resolution**:
- Services accessible via DNS: `<service-name>.<namespace>.svc.cluster.local`
- Frontend → Backend: `http://backend:8000` (short name within same namespace)

#### External Database Connectivity

**Decision**: Use external Neon PostgreSQL with connection string in Secret

**Configuration**:
```yaml
# In secrets.yaml
apiVersion: v1
kind: Secret
metadata:
  name: todo-secrets
type: Opaque
stringData:
  DATABASE_URL: postgresql://user:pass@ep-xxx.neon.tech/todo_db
  GROQ_API_KEY: gsk_xxx
  JWT_SECRET: xxx
```

**Rationale**:
- Reuses existing Phase IV database (no data migration)
- Neon PostgreSQL accessible from anywhere (public endpoint)
- Avoids complexity of running PostgreSQL in Kubernetes for local dev
- Secrets stored in Kubernetes Secret (not in values.yaml)

**Alternatives Considered**:
- Local PostgreSQL in Kubernetes: Deferred to Phase VI (adds complexity, requires PersistentVolume setup)
- PostgreSQL StatefulSet: Overkill for local development

---

### 4. AI DevOps Tools

#### Gordon (Docker AI)

**Capabilities**:
- Dockerfile generation from natural language
- Optimization suggestions (layer caching, multi-stage builds)
- Security recommendations (non-root users, minimal base images)
- Troubleshooting build errors

**Usage Examples**:
```bash
# Generate Dockerfile
docker ai "Create a Dockerfile for a Python FastAPI app with multi-stage build"

# Optimize existing Dockerfile
docker ai "Optimize this Dockerfile for size and security" < Dockerfile

# Troubleshoot build error
docker ai "Why is my Docker build failing with 'package not found'?"
```

**Availability**: Docker Desktop 4.53+ with Beta features enabled
**Fallback**: Standard Docker commands with manual Dockerfile creation

#### kubectl-ai

**Capabilities**:
- Natural language to kubectl commands
- Deployment troubleshooting
- Resource scaling and management
- Log analysis and debugging

**Usage Examples**:
```bash
# Deploy application
kubectl-ai "deploy the todo frontend with 2 replicas"

# Scale deployment
kubectl-ai "scale the backend to handle more load"

# Troubleshoot
kubectl-ai "check why the pods are failing"
kubectl-ai "show me logs for the backend pod"

# Resource management
kubectl-ai "increase memory limit for frontend to 512Mi"
```

**Installation**: `brew install kubectl-ai` or `pip install kubectl-ai`
**Fallback**: Standard kubectl commands with documentation

#### Kagent

**Capabilities**:
- Cluster health analysis
- Resource optimization recommendations
- Performance bottleneck identification
- Cost optimization suggestions

**Usage Examples**:
```bash
# Analyze cluster health
kagent "analyze the cluster health"

# Optimize resources
kagent "optimize resource allocation for todo-chatbot"

# Identify issues
kagent "why is my cluster slow?"
kagent "find pods using too much memory"
```

**Installation**: `pip install kagent` or download binary
**Fallback**: Manual kubectl commands for resource inspection

**Integration Strategy**:
- Document AI-assisted workflows in `AI_TOOLS_GUIDE.md`
- Provide fallback commands for each AI tool operation
- Include both AI and manual approaches in deployment guide
- Optional: Use AI tools to generate initial artifacts, then refine manually

---

### 5. Kubernetes Security

#### Non-Root Container Users

**Decision**: Run all containers as non-root users

**Implementation**:
```dockerfile
# Backend Dockerfile
FROM python:3.13-slim
RUN useradd -m -u 1000 appuser
USER appuser
WORKDIR /home/appuser/app
```

```yaml
# Deployment security context
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  fsGroup: 1000
  capabilities:
    drop:
      - ALL
  readOnlyRootFilesystem: false  # Next.js needs write access for cache
```

**Rationale**:
- Principle of least privilege
- Prevents container breakout attacks
- Required by many Kubernetes security policies (PSP, PSA)

#### Secret Management

**Decision**: Use Kubernetes Secrets with base64 encoding

**Strategy**:
1. Create Secret from environment variables:
   ```bash
   kubectl create secret generic todo-secrets \
     --from-literal=DATABASE_URL=$DATABASE_URL \
     --from-literal=GROQ_API_KEY=$GROQ_API_KEY \
     --from-literal=JWT_SECRET=$JWT_SECRET
   ```

2. Reference in Deployment:
   ```yaml
   env:
     - name: DATABASE_URL
       valueFrom:
         secretKeyRef:
           name: todo-secrets
           key: DATABASE_URL
   ```

**Alternatives Considered**:
- External secret managers (Vault, AWS Secrets Manager): Overkill for local development
- Sealed Secrets: Adds complexity, not needed for local Minikube
- ConfigMaps: Rejected because secrets should not be in plain text

**Security Practices**:
- Never commit secrets to Git
- Use `.env.example` with placeholder values
- Document secret creation in deployment guide
- Use `stringData` in Helm templates (auto-base64 encoding)

#### Network Policies

**Decision**: Defer to Phase VI (optional for local development)

**Rationale**:
- Minikube doesn't enforce network policies by default
- Adds complexity without security benefit in local environment
- Will be critical for cloud deployment (Phase VI)

---

### 6. Performance Optimization

#### Image Layer Caching

**Strategy**:
1. Copy dependency files first (package.json, requirements.txt)
2. Install dependencies (cached if files unchanged)
3. Copy application code last (changes frequently)

**Example (Backend)**:
```dockerfile
# Good: Dependencies cached separately
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/

# Bad: Everything copied together (cache invalidated on any change)
COPY . .
RUN pip install -r requirements.txt
```

**Benefits**:
- Faster rebuilds (only changed layers rebuilt)
- Reduced CI/CD time
- Lower bandwidth usage

#### Resource Request/Limit Tuning

**Decision**: Conservative requests, generous limits

**Backend**:
- Requests: 100m CPU, 256Mi memory (guaranteed minimum)
- Limits: 500m CPU, 512Mi memory (burst capacity)

**Frontend**:
- Requests: 50m CPU, 128Mi memory (guaranteed minimum)
- Limits: 200m CPU, 256Mi memory (burst capacity)

**Rationale**:
- Requests ensure pod scheduling (Kubernetes reserves resources)
- Limits prevent resource starvation (one pod can't consume all resources)
- Conservative requests allow more pods on limited Minikube resources
- Generous limits allow burst traffic handling

**Tuning Process**:
1. Deploy with initial estimates
2. Monitor actual usage: `kubectl top pods`
3. Adjust based on observed patterns
4. Document final values in values.yaml

#### Horizontal Pod Autoscaler (HPA)

**Decision**: Manual scaling for Phase V, HPA for Phase VI

**Rationale**:
- Minikube metrics-server required for HPA (additional setup)
- Local development doesn't need autoscaling
- Manual scaling sufficient for testing: `kubectl scale deployment backend --replicas=3`

**Future Enhancement (Phase VI)**:
```yaml
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: backend-hpa
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

---

## Summary of Key Decisions

| Area | Decision | Rationale |
|------|----------|-----------|
| Backend Base Image | python:3.13-slim | Balance of size and compatibility |
| Frontend Base Image | node:20-alpine | Minimal size, SSR support |
| Helm Chart Structure | Single chart, separate templates | Atomic deployments, shared config |
| Backend Service Type | ClusterIP | Internal only, not externally accessible |
| Frontend Service Type | LoadBalancer | External access for testing |
| Database Strategy | External Neon PostgreSQL | Reuse Phase IV, avoid migration |
| Secret Management | Kubernetes Secrets | Standard approach, sufficient for local dev |
| Container Security | Non-root users, dropped capabilities | Security best practices |
| AI Tools | Gordon, kubectl-ai, Kagent with fallbacks | Enhanced productivity, optional |
| Resource Limits | Conservative requests, generous limits | Efficient scheduling, burst capacity |

---

## Unresolved Questions

**None** - All technical decisions resolved with reasonable defaults and documented alternatives.

---

## Next Steps

1. Generate `data-model.md` with infrastructure entities
2. Generate `contracts/` with Dockerfile templates and Helm values schema
3. Generate `quickstart.md` with step-by-step deployment guide
4. Proceed to `/sp.tasks` for task breakdown
