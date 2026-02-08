# Deployment Guide: Todo Chatbot on Minikube

**Feature**: Local Kubernetes Deployment (Phase V)
**Purpose**: Complete guide for deploying Todo Chatbot to local Minikube cluster

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Quick Start](#quick-start)
3. [Detailed Deployment Steps](#detailed-deployment-steps)
4. [Verification](#verification)
5. [Accessing the Application](#accessing-the-application)
6. [Common Operations](#common-operations)
7. [Troubleshooting](#troubleshooting)
8. [Cleanup](#cleanup)

---

## Prerequisites

### Required Software

| Software | Version | Installation |
|----------|---------|--------------|
| Docker Desktop | 4.53+ | https://www.docker.com/products/docker-desktop |
| Minikube | 1.30+ | https://minikube.sigs.k8s.io/docs/start/ |
| kubectl | 1.28+ | https://kubernetes.io/docs/tasks/tools/ |
| Helm | 3.12+ | https://helm.sh/docs/intro/install/ |

### Optional AI Tools

| Tool | Purpose | Installation |
|------|---------|--------------|
| Gordon (Docker AI) | AI-assisted Docker operations | Docker Desktop 4.53+ Beta features |
| kubectl-ai | AI-assisted Kubernetes operations | `brew install kubectl-ai` or `pip install kubectl-ai` |
| Kagent | Cluster analysis and optimization | `pip install kagent` |

### System Requirements

**Minimum**:
- CPU: 2 cores
- RAM: 4GB
- Disk: 20GB free space

**Recommended**:
- CPU: 4 cores
- RAM: 8GB
- Disk: 40GB free space

### Prerequisites Checklist

Before starting, verify:

- [ ] Docker Desktop is installed and running
- [ ] Minikube is installed
- [ ] kubectl is installed
- [ ] Helm is installed
- [ ] You have access to the Phase IV application code
- [ ] You have database credentials (Neon PostgreSQL)
- [ ] You have Groq API key (from https://console.groq.com/keys)
- [ ] You have JWT secret (generate a random 32+ character string)

---

## Quick Start

For experienced users, use the automated deployment script:

```bash
# Navigate to project root
cd evolution-of-todo

# Run automated deployment
./k8s/scripts/deploy-minikube.sh
```

This script will:
1. Check prerequisites
2. Start Minikube
3. Build Docker images
4. Load images to Minikube
5. Create Kubernetes secrets
6. Deploy with Helm
7. Verify deployment
8. Provide access instructions

**Estimated Time**: 10-15 minutes

---

## Detailed Deployment Steps

### Step 1: Start Minikube

Start a local Kubernetes cluster with sufficient resources:

```bash
# Start Minikube with 4GB RAM and 2 CPUs
minikube start --memory=4096 --cpus=2 --driver=docker

# Verify Minikube is running
minikube status
```

**Expected Output**:
```
minikube
type: Control Plane
host: Running
kubelet: Running
apiserver: Running
kubeconfig: Configured
```

**Troubleshooting**:
- If Minikube fails to start: `minikube delete && minikube start`
- On Windows: Ensure Docker Desktop is running
- On macOS: Ensure Docker Desktop has sufficient resources in Settings

---

### Step 2: Build Docker Images

Build optimized Docker images for backend and frontend:

```bash
# Build both images
./k8s/scripts/build-images.sh

# Or build individually
docker build -t todo-backend:latest \
  -f k8s/dockerfiles/backend.Dockerfile \
  phase4-chatbot/backend/

docker build -t todo-frontend:latest \
  -f k8s/dockerfiles/frontend.Dockerfile \
  phase4-chatbot/frontend/
```

**Expected Output**:
```
Backend:  todo-backend:latest (450MB)
Frontend: todo-frontend:latest (180MB)
✓ All images built successfully
```

**Verification**:
```bash
# Check image sizes
docker images | grep todo
```

**Target Sizes**:
- Backend: <500MB
- Frontend: <200MB

---

### Step 3: Load Images to Minikube

Load built images into Minikube's Docker environment:

```bash
# Load both images
./k8s/scripts/load-images.sh

# Or load individually
minikube image load todo-backend:latest
minikube image load todo-frontend:latest
```

**Verification**:
```bash
# List images in Minikube
minikube image ls | grep todo
```

**Alternative Method** (use Minikube's Docker daemon):
```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Rebuild images (they'll be in Minikube automatically)
./k8s/scripts/build-images.sh

# Reset Docker CLI to host daemon
eval $(minikube docker-env -u)
```

---

### Step 4: Create Kubernetes Secrets

Create secrets for sensitive configuration:

#### Option A: Using .env File (Recommended)

1. Copy the example file:
   ```bash
   cp k8s/.env.example k8s/.env
   ```

2. Edit `k8s/.env` with your actual values:
   ```bash
   DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/todo_db
   GROQ_API_KEY=gsk_xxx
   JWT_SECRET=your-secret-key-min-32-chars
   GROQ_BASE_URL=https://api.groq.com/openai/v1
   GROQ_MODEL=llama-3.3-70b-versatile
   ```

3. Create secrets:
   ```bash
   ./k8s/scripts/create-secrets.sh
   ```

#### Option B: Manual Creation

```bash
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@host/db" \
  --from-literal=GROQ_API_KEY="gsk_xxx" \
  --from-literal=JWT_SECRET="your-secret-key" \
  --from-literal=GROQ_BASE_URL="https://api.groq.com/openai/v1" \
  --from-literal=GROQ_MODEL="llama-3.3-70b-versatile"
```

**Verification**:
```bash
# Check secret exists
kubectl get secrets

# View secret keys (not values)
kubectl describe secret todo-secrets
```

**Security Note**: Never commit `.env` file to version control. It's already in `.gitignore`.

---

### Step 5: Validate Helm Chart

Before deploying, validate the Helm chart:

```bash
# Run validation script
./k8s/scripts/validate-chart.sh

# Or manually
helm lint k8s/helm-charts/todo-chatbot/
helm template todo-chatbot k8s/helm-charts/todo-chatbot/ --debug
```

**Expected Output**:
```
✓ Helm lint passed
✓ Template rendering successful
✓ All required templates present
✓ Chart validation complete
```

---

### Step 6: Deploy with Helm

Install the Helm chart:

```bash
# Install with default values
helm install todo-chatbot k8s/helm-charts/todo-chatbot/

# Or with development values
helm install todo-chatbot k8s/helm-charts/todo-chatbot/ \
  -f k8s/helm-charts/todo-chatbot/values-dev.yaml
```

**Expected Output**:
```
NAME: todo-chatbot
LAST DEPLOYED: [timestamp]
NAMESPACE: default
STATUS: deployed
REVISION: 1
```

**Verification**:
```bash
# Check Helm release
helm list

# Check deployment status
kubectl get all -l app.kubernetes.io/name=todo-chatbot
```

---

### Step 7: Verify Deployment

Wait for pods to be ready and verify deployment:

```bash
# Run verification script
./k8s/scripts/verify-deployment.sh

# Or manually
kubectl get pods
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-chatbot --timeout=180s
```

**Expected Output**:
```
NAME                        READY   STATUS    RESTARTS   AGE
backend-7d8f9c5b-xk2p9      1/1     Running   0          2m
frontend-6c9d8f4a-zx7k3     1/1     Running   0          2m
```

**Check Logs**:
```bash
# Backend logs
kubectl logs -l app.kubernetes.io/component=backend

# Frontend logs
kubectl logs -l app.kubernetes.io/component=frontend
```

---

## Accessing the Application

### Option 1: Minikube Tunnel (Recommended)

1. Start Minikube tunnel in a separate terminal:
   ```bash
   minikube tunnel
   ```
   (Requires admin/sudo password)

2. Access the application:
   ```
   http://localhost
   or
   http://127.0.0.1
   ```

### Option 2: NodePort

```bash
# Get NodePort and Minikube IP
export NODE_PORT=$(kubectl get service frontend -o jsonpath='{.spec.ports[0].nodePort}')
export MINIKUBE_IP=$(minikube ip)

# Access application
echo "http://${MINIKUBE_IP}:${NODE_PORT}"
```

### Option 3: Port Forwarding

```bash
# Forward local port to frontend service
kubectl port-forward service/frontend 3000:80

# Access application
open http://localhost:3000
```

---

## Common Operations

### Scaling

```bash
# Scale backend to 3 replicas
kubectl scale deployment backend --replicas=3

# Scale frontend to 2 replicas
kubectl scale deployment frontend --replicas=2

# Verify scaling
kubectl get pods
```

### Rolling Update

```bash
# Rebuild images with new tag
TAG=v1.0.1 ./k8s/scripts/build-images.sh
minikube image load todo-backend:v1.0.1
minikube image load todo-frontend:v1.0.1

# Update deployment
helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
  --set backend.image.tag=v1.0.1 \
  --set frontend.image.tag=v1.0.1

# Watch rollout
kubectl rollout status deployment/backend
kubectl rollout status deployment/frontend
```

### Rollback

```bash
# Rollback to previous version
helm rollback todo-chatbot

# Or rollback to specific revision
helm rollback todo-chatbot 1

# Verify rollback
helm history todo-chatbot
```

### View Logs

```bash
# Follow backend logs
kubectl logs -f deployment/backend

# Follow frontend logs
kubectl logs -f deployment/frontend

# View logs from all pods
kubectl logs -l app.kubernetes.io/name=todo-chatbot --all-containers=true
```

### Resource Usage

```bash
# Enable metrics-server (if not already enabled)
minikube addons enable metrics-server

# View resource usage
kubectl top nodes
kubectl top pods
```

---

## Troubleshooting

### Pods Stuck in Pending

**Cause**: Insufficient cluster resources

**Solution**:
```bash
# Check node resources
kubectl describe nodes

# Restart Minikube with more resources
minikube stop
minikube start --memory=8192 --cpus=4
```

### ImagePullBackOff

**Cause**: Images not loaded to Minikube

**Solution**:
```bash
# Verify images in Minikube
minikube image ls | grep todo

# Reload images
./k8s/scripts/load-images.sh
```

### CrashLoopBackOff

**Cause**: Application error or missing configuration

**Solution**:
```bash
# Check pod logs
kubectl logs <pod-name>

# Check pod events
kubectl describe pod <pod-name>

# Verify secrets
kubectl get secrets
kubectl describe secret todo-secrets
```

### Cannot Access Application

**Cause**: Service not exposed or tunnel not running

**Solution**:
```bash
# Check service status
kubectl get services

# Ensure tunnel is running
minikube tunnel

# Or use port forwarding
kubectl port-forward service/frontend 3000:80
```

### Database Connection Failed

**Cause**: Invalid DATABASE_URL or network issue

**Solution**:
```bash
# Test database connectivity from pod
kubectl exec -it deployment/backend -- \
  python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"

# Verify secret value
kubectl get secret todo-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

### Health Checks Failing

**Cause**: Application not ready or health endpoint not responding

**Solution**:
```bash
# Check health endpoint manually
kubectl exec -it deployment/backend -- curl http://localhost:8000/health
kubectl exec -it deployment/frontend -- curl http://localhost:3000/api/health

# Check pod events
kubectl describe pod <pod-name>
```

---

## Cleanup

### Uninstall Application

```bash
# Uninstall Helm release
helm uninstall todo-chatbot

# Delete secrets
kubectl delete secret todo-secrets

# Verify cleanup
kubectl get all -l app.kubernetes.io/name=todo-chatbot
```

### Stop Minikube

```bash
# Stop Minikube (preserves cluster state)
minikube stop

# Delete Minikube cluster (removes all data)
minikube delete
```

### Remove Docker Images

```bash
# Remove local images
docker rmi todo-backend:latest todo-frontend:latest

# Remove images from Minikube
minikube image rm todo-backend:latest todo-frontend:latest
```

---

## Next Steps

After successful deployment:

1. **Test Application**: Verify all Todo Chatbot features work
2. **Explore AI Tools**: Try Gordon, kubectl-ai, Kagent (see [AI_TOOLS_GUIDE.md](AI_TOOLS_GUIDE.md))
3. **Monitor Resources**: Enable metrics-server and monitor pod usage
4. **Practice Operations**: Try scaling, updates, and rollbacks
5. **Prepare for Phase VI**: Document lessons learned for cloud deployment

---

## Additional Resources

- **Troubleshooting Guide**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **AI Tools Guide**: [AI_TOOLS_GUIDE.md](AI_TOOLS_GUIDE.md)
- **Image Optimization**: [IMAGE_OPTIMIZATION.md](IMAGE_OPTIMIZATION.md)
- **Lifecycle Management**: [LIFECYCLE_MANAGEMENT.md](LIFECYCLE_MANAGEMENT.md)
- **Production Readiness**: [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md)

---

**Deployment Time**: 10-15 minutes (first time), 5 minutes (subsequent deployments)
**Difficulty**: Intermediate
**Prerequisites**: Docker, Minikube, kubectl, Helm
**Support**: See [TROUBLESHOOTING.md](TROUBLESHOOTING.md) for common issues

---

**Last Updated**: 2026-02-08
**Phase**: V - Local Kubernetes Deployment
**Status**: Production Ready
