# Data Model: Local Kubernetes Deployment

**Feature**: 005-k8s-local-deployment
**Date**: 2026-02-08
**Purpose**: Define infrastructure entities, relationships, and state management for Kubernetes deployment

## Overview

This data model describes the infrastructure entities involved in deploying the Todo Chatbot to Kubernetes. Unlike application data models (users, tasks, conversations), this focuses on deployment artifacts, their relationships, and lifecycle states.

---

## Entity Definitions

### 1. Docker Image

**Description**: Container image containing application code, dependencies, and runtime environment.

**Attributes**:
- `repository`: String - Image repository name (e.g., "todo-backend", "todo-frontend")
- `tag`: String - Version identifier (e.g., "latest", "v1.0.0", "sha-abc123")
- `digest`: String - SHA256 hash of image content (immutable identifier)
- `size`: Integer - Image size in bytes
- `created`: Timestamp - Image build timestamp
- `layers`: Array[Layer] - Ordered list of filesystem layers
- `platform`: String - Target platform (e.g., "linux/amd64", "linux/arm64")
- `labels`: Map[String, String] - Metadata labels (version, commit, build date)

**Relationships**:
- Built FROM base image (e.g., python:3.13-slim, node:20-alpine)
- Referenced BY Kubernetes Deployment (via image field)
- Stored IN container registry (Docker Hub, Minikube cache, local Docker daemon)

**States**:
- `building`: Image is being built from Dockerfile
- `built`: Image exists in local Docker daemon
- `pushed`: Image pushed to remote registry
- `pulled`: Image pulled to Kubernetes node
- `running`: Container created from image is running

**Validation Rules**:
- Repository name must be lowercase alphanumeric with hyphens
- Tag must not contain spaces or special characters
- Size must be under target limits (500MB backend, 200MB frontend)
- Must include required labels (version, commit, build-date)

**Example**:
```yaml
repository: todo-backend
tag: v1.0.0
digest: sha256:abc123...
size: 450000000  # 450MB
created: 2026-02-08T10:30:00Z
layers:
  - sha256:layer1... (base OS)
  - sha256:layer2... (Python runtime)
  - sha256:layer3... (dependencies)
  - sha256:layer4... (application code)
platform: linux/amd64
labels:
  version: "1.0.0"
  commit: "abc123"
  build-date: "2026-02-08"
```

---

### 2. Helm Chart

**Description**: Package containing Kubernetes manifest templates and configuration values.

**Attributes**:
- `name`: String - Chart name (e.g., "todo-chatbot")
- `version`: String - Chart version (semantic versioning)
- `appVersion`: String - Application version being deployed
- `description`: String - Human-readable description
- `templates`: Array[Template] - Kubernetes manifest templates
- `values`: Map[String, Any] - Default configuration values
- `dependencies`: Array[Dependency] - Required charts (if any)

**Relationships**:
- Contains multiple Kubernetes Resource templates
- References Docker Images via values
- Installed TO Kubernetes namespace
- Managed BY Helm (install, upgrade, rollback)

**States**:
- `created`: Chart files exist locally
- `linted`: Chart passed validation (helm lint)
- `packaged`: Chart archived as .tgz file
- `installed`: Chart deployed to Kubernetes
- `upgraded`: Chart updated to new version
- `rolled-back`: Chart reverted to previous version
- `uninstalled`: Chart removed from Kubernetes

**Validation Rules**:
- Chart.yaml must be valid YAML with required fields
- Templates must render without errors (helm template)
- Values must match schema (if values.schema.json exists)
- All referenced images must exist

**Example**:
```yaml
name: todo-chatbot
version: 1.0.0
appVersion: 1.0.0
description: Todo Chatbot with AI-powered natural language interface
templates:
  - backend-deployment.yaml
  - backend-service.yaml
  - frontend-deployment.yaml
  - frontend-service.yaml
  - configmap.yaml
  - secrets.yaml
values:
  backend:
    image:
      repository: todo-backend
      tag: v1.0.0
    replicas: 1
  frontend:
    image:
      repository: todo-frontend
      tag: v1.0.0
    replicas: 1
```

---

### 3. Kubernetes Deployment

**Description**: Declarative specification for running application pods with desired state management.

**Attributes**:
- `name`: String - Deployment name (e.g., "backend", "frontend")
- `namespace`: String - Kubernetes namespace (e.g., "default", "todo-chatbot")
- `replicas`: Integer - Desired number of pod instances
- `selector`: Map[String, String] - Label selector for pods
- `template`: PodTemplate - Pod specification
- `strategy`: DeploymentStrategy - Update strategy (RollingUpdate, Recreate)
- `revisionHistoryLimit`: Integer - Number of old ReplicaSets to retain

**Relationships**:
- Creates and manages ReplicaSet
- ReplicaSet creates and manages Pods
- Pods run containers from Docker Images
- Exposed BY Kubernetes Service

**States**:
- `progressing`: Deployment is rolling out
- `available`: Desired replicas are running and ready
- `degraded`: Some replicas are not ready
- `failed`: Deployment failed to progress

**Validation Rules**:
- Replicas must be >= 0
- Selector must match pod template labels
- Container image must exist
- Resource requests must be <= limits

**Example**:
```yaml
name: backend
namespace: default
replicas: 2
selector:
  matchLabels:
    app: todo-chatbot
    component: backend
template:
  metadata:
    labels:
      app: todo-chatbot
      component: backend
  spec:
    containers:
      - name: backend
        image: todo-backend:v1.0.0
        ports:
          - containerPort: 8000
        resources:
          requests:
            cpu: 100m
            memory: 256Mi
          limits:
            cpu: 500m
            memory: 512Mi
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1
    maxUnavailable: 0
```

---

### 4. Kubernetes Service

**Description**: Network abstraction providing stable endpoint for accessing pods.

**Attributes**:
- `name`: String - Service name (e.g., "backend", "frontend")
- `namespace`: String - Kubernetes namespace
- `type`: String - Service type (ClusterIP, NodePort, LoadBalancer)
- `selector`: Map[String, String] - Label selector for target pods
- `ports`: Array[ServicePort] - Port mappings
- `clusterIP`: String - Internal cluster IP (assigned by Kubernetes)
- `externalIP`: String - External IP (for LoadBalancer type)

**Relationships**:
- Routes traffic TO Pods matching selector
- Exposed BY Ingress (if configured)
- Discovered VIA DNS (service-name.namespace.svc.cluster.local)

**States**:
- `pending`: Service created, waiting for endpoint assignment
- `active`: Service has active endpoints
- `no-endpoints`: Service exists but no matching pods

**Validation Rules**:
- Selector must match at least one pod
- Port numbers must be 1-65535
- Type must be valid (ClusterIP, NodePort, LoadBalancer, ExternalName)

**Example**:
```yaml
name: backend
namespace: default
type: ClusterIP
selector:
  app: todo-chatbot
  component: backend
ports:
  - name: http
    port: 8000
    targetPort: 8000
    protocol: TCP
clusterIP: 10.96.100.50
```

---

### 5. Kubernetes ConfigMap

**Description**: Non-sensitive configuration data stored as key-value pairs.

**Attributes**:
- `name`: String - ConfigMap name (e.g., "todo-config")
- `namespace`: String - Kubernetes namespace
- `data`: Map[String, String] - Configuration key-value pairs
- `binaryData`: Map[String, Base64] - Binary configuration data

**Relationships**:
- Mounted AS volume in Pod
- Injected AS environment variables in Container
- Referenced BY Deployment

**States**:
- `created`: ConfigMap exists in cluster
- `mounted`: ConfigMap mounted in running pod
- `updated`: ConfigMap data changed (requires pod restart)

**Validation Rules**:
- Keys must be valid environment variable names (alphanumeric, underscore, hyphen)
- Total size must be < 1MB
- No sensitive data (use Secret instead)

**Example**:
```yaml
name: todo-config
namespace: default
data:
  ENVIRONMENT: "development"
  LOG_LEVEL: "INFO"
  CORS_ORIGINS: "http://localhost:3000"
  MAX_CONVERSATION_HISTORY: "50"
```

---

### 6. Kubernetes Secret

**Description**: Sensitive configuration data stored with base64 encoding.

**Attributes**:
- `name`: String - Secret name (e.g., "todo-secrets")
- `namespace`: String - Kubernetes namespace
- `type`: String - Secret type (Opaque, kubernetes.io/tls, etc.)
- `data`: Map[String, Base64] - Base64-encoded secret values
- `stringData`: Map[String, String] - Plain text (auto-encoded to data)

**Relationships**:
- Mounted AS volume in Pod
- Injected AS environment variables in Container
- Referenced BY Deployment

**States**:
- `created`: Secret exists in cluster
- `mounted`: Secret mounted in running pod
- `rotated`: Secret values updated (requires pod restart)

**Validation Rules**:
- Keys must be valid environment variable names
- Total size must be < 1MB
- Never commit to version control
- Use stringData in Helm templates (auto-base64 encoding)

**Example**:
```yaml
name: todo-secrets
namespace: default
type: Opaque
stringData:
  DATABASE_URL: "postgresql://user:pass@neon.tech/db"
  GROQ_API_KEY: "gsk_xxx"
  JWT_SECRET: "secret-key-xxx"
```

---

### 7. Kubernetes Pod

**Description**: Smallest deployable unit containing one or more containers.

**Attributes**:
- `name`: String - Pod name (generated with random suffix)
- `namespace`: String - Kubernetes namespace
- `phase`: String - Pod lifecycle phase (Pending, Running, Succeeded, Failed, Unknown)
- `conditions`: Array[Condition] - Pod conditions (Ready, Initialized, ContainersReady)
- `containers`: Array[Container] - Container specifications
- `restartPolicy`: String - Restart policy (Always, OnFailure, Never)
- `nodeName`: String - Node where pod is scheduled

**Relationships**:
- Created BY ReplicaSet (managed by Deployment)
- Runs ON Kubernetes Node
- Exposes ports TO Service
- Mounts ConfigMaps and Secrets

**States**:
- `Pending`: Pod accepted but not yet scheduled
- `Running`: Pod bound to node, containers running
- `Succeeded`: All containers terminated successfully
- `Failed`: All containers terminated, at least one failed
- `Unknown`: Pod state cannot be determined

**Validation Rules**:
- At least one container must be defined
- Container image must exist
- Resource requests must fit on available nodes
- Health probes must be properly configured

**Example**:
```yaml
name: backend-7d8f9c5b-xk2p9
namespace: default
phase: Running
conditions:
  - type: Ready
    status: "True"
  - type: ContainersReady
    status: "True"
containers:
  - name: backend
    image: todo-backend:v1.0.0
    state: running
    ready: true
restartPolicy: Always
nodeName: minikube
```

---

### 8. PersistentVolume (Optional)

**Description**: Storage resource for persisting data beyond pod lifecycle.

**Attributes**:
- `name`: String - PV name
- `capacity`: Map[String, Quantity] - Storage capacity (e.g., "10Gi")
- `accessModes`: Array[String] - Access modes (ReadWriteOnce, ReadOnlyMany, ReadWriteMany)
- `storageClassName`: String - Storage class (e.g., "local-path", "standard")
- `persistentVolumeReclaimPolicy`: String - Reclaim policy (Retain, Delete, Recycle)

**Relationships**:
- Claimed BY PersistentVolumeClaim
- Mounted IN Pod
- Backed BY storage provider (local disk, NFS, cloud storage)

**States**:
- `Available`: PV is available for claim
- `Bound`: PV is bound to PVC
- `Released`: PVC deleted but PV not yet reclaimed
- `Failed`: PV reclamation failed

**Note**: For Phase V, using external Neon PostgreSQL, so PersistentVolumes are optional. May be used for local PostgreSQL in future.

---

## Entity Relationships Diagram

```
┌─────────────────┐
│  Docker Image   │
│  (Backend/      │
│   Frontend)     │
└────────┬────────┘
         │ referenced by
         ▼
┌─────────────────┐      contains      ┌──────────────────┐
│   Helm Chart    │◄──────────────────►│  K8s Resources   │
│  (todo-chatbot) │                    │  (templates)     │
└────────┬────────┘                    └──────────────────┘
         │ installs to
         ▼
┌─────────────────────────────────────────────────────────┐
│              Kubernetes Cluster (Minikube)              │
│                                                          │
│  ┌──────────────┐         ┌──────────────┐             │
│  │  Deployment  │ creates │  ReplicaSet  │             │
│  │  (Backend)   │────────►│              │             │
│  └──────────────┘         └──────┬───────┘             │
│                                   │ creates             │
│                                   ▼                     │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Service    │ routes  │     Pod      │             │
│  │  (Backend)   │────────►│  (Backend)   │             │
│  │  ClusterIP   │         └──────┬───────┘             │
│  └──────────────┘                │ mounts              │
│         ▲                         ▼                     │
│         │                 ┌──────────────┐             │
│         │                 │  ConfigMap   │             │
│         │                 │   Secret     │             │
│         │                 └──────────────┘             │
│         │                                               │
│  ┌──────────────┐         ┌──────────────┐             │
│  │  Deployment  │ creates │  ReplicaSet  │             │
│  │  (Frontend)  │────────►│              │             │
│  └──────────────┘         └──────┬───────┘             │
│                                   │ creates             │
│                                   ▼                     │
│  ┌──────────────┐         ┌──────────────┐             │
│  │   Service    │ routes  │     Pod      │             │
│  │  (Frontend)  │────────►│  (Frontend)  │             │
│  │ LoadBalancer │         └──────────────┘             │
│  └──────┬───────┘                                       │
│         │                                               │
└─────────┼───────────────────────────────────────────────┘
          │ exposes
          ▼
    ┌──────────────┐
    │   External   │
    │    Access    │
    │ (localhost)  │
    └──────────────┘
```

---

## State Transitions

### Deployment Lifecycle

```
[Created] → [Progressing] → [Available]
                ↓               ↓
            [Degraded] ←────────┘
                ↓
            [Failed]
```

**Transitions**:
1. `Created → Progressing`: Deployment created, rolling out pods
2. `Progressing → Available`: All replicas running and ready
3. `Available → Degraded`: Some replicas become unhealthy
4. `Degraded → Available`: Unhealthy replicas recovered
5. `Progressing → Failed`: Deployment failed to progress (image pull error, crash loop)

### Pod Lifecycle

```
[Pending] → [Running] → [Succeeded]
              ↓
          [Failed]
```

**Transitions**:
1. `Pending → Running`: Pod scheduled, containers started
2. `Running → Succeeded`: All containers exited successfully (for Jobs)
3. `Running → Failed`: Container crashed or health check failed
4. `Failed → Running`: Pod restarted by restart policy

---

## Validation Rules Summary

| Entity | Key Validation Rules |
|--------|---------------------|
| Docker Image | Size limits, valid tags, required labels |
| Helm Chart | Valid YAML, templates render, values match schema |
| Deployment | Replicas >= 0, selector matches labels, resources defined |
| Service | Valid type, selector matches pods, valid port range |
| ConfigMap | Valid keys, size < 1MB, no sensitive data |
| Secret | Valid keys, size < 1MB, never in version control |
| Pod | At least one container, image exists, health probes configured |

---

## Data Flow

### Deployment Flow

1. **Build Phase**:
   - Dockerfile → Docker Image (local daemon)
   - Docker Image → Minikube cache (minikube image load)

2. **Package Phase**:
   - Helm templates + values → Helm Chart
   - Helm Chart → Kubernetes manifests (helm template)

3. **Deploy Phase**:
   - Helm Chart → Kubernetes API (helm install)
   - Kubernetes API → Deployment → ReplicaSet → Pods
   - Pods pull images from Minikube cache
   - Pods mount ConfigMaps and Secrets

4. **Runtime Phase**:
   - Service routes traffic to Pods
   - Pods serve requests
   - Health probes monitor pod health
   - Kubernetes restarts unhealthy pods

### Update Flow

1. **Image Update**:
   - Build new Docker Image with new tag
   - Load image to Minikube
   - Update Helm values with new tag
   - Run `helm upgrade` (triggers rolling update)

2. **Configuration Update**:
   - Update ConfigMap or Secret
   - Restart pods to pick up new config
   - Or use `kubectl rollout restart deployment`

---

## Summary

This data model defines 8 core infrastructure entities for Kubernetes deployment:
1. **Docker Image**: Container images with application code
2. **Helm Chart**: Deployment package with templates and values
3. **Deployment**: Declarative pod management
4. **Service**: Network abstraction for pod access
5. **ConfigMap**: Non-sensitive configuration
6. **Secret**: Sensitive configuration
7. **Pod**: Running container instances
8. **PersistentVolume**: Optional persistent storage

These entities work together to deploy, manage, and expose the Todo Chatbot application in a Kubernetes environment.
