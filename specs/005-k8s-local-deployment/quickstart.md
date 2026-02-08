# Quickstart: Local Kubernetes Deployment

**Feature**: 005-k8s-local-deployment
**Date**: 2026-02-08
**Purpose**: Step-by-step guide to deploy Todo Chatbot to local Minikube cluster

## Overview

This guide walks you through deploying the Todo Chatbot application to a local Kubernetes cluster using Minikube, Docker, and Helm. The entire process takes approximately 30-45 minutes for first-time setup.

**What You'll Deploy**:
- Backend API (FastAPI) - 1 pod
- Frontend UI (Next.js) - 1 pod
- External PostgreSQL database (Neon)

**Prerequisites Time**: 15-20 minutes (one-time setup)
**Build Time**: 5-10 minutes
**Deploy Time**: 3-5 minutes

---

## Prerequisites

### Required Software

1. **Docker Desktop 4.53+**
   - Download: https://www.docker.com/products/docker-desktop
   - Verify: `docker --version`
   - Enable Gordon (optional): Settings → Beta features → Docker AI

2. **Minikube 1.30+**
   - Install: `brew install minikube` (macOS) or download from https://minikube.sigs.k8s.io/
   - Verify: `minikube version`

3. **kubectl 1.28+**
   - Install: `brew install kubectl` (macOS) or download from https://kubernetes.io/
   - Verify: `kubectl version --client`

4. **Helm 3.12+**
   - Install: `brew install helm` (macOS) or download from https://helm.sh/
   - Verify: `helm version`

### Optional AI Tools

5. **kubectl-ai** (optional, enhances productivity)
   - Install: `brew install kubectl-ai` or `pip install kubectl-ai`
   - Verify: `kubectl-ai --version`

6. **Kagent** (optional, cluster analysis)
   - Install: `pip install kagent` or download binary
   - Verify: `kagent --version`

### System Requirements

- **CPU**: 2 cores minimum (4 cores recommended)
- **RAM**: 4GB minimum (8GB recommended)
- **Disk**: 20GB free space
- **OS**: Windows 10+, macOS 11+, or Linux

---

## Step 1: Start Minikube

Start a local Kubernetes cluster with sufficient resources:

```bash
# Start Minikube with 4GB RAM and 2 CPUs
minikube start --memory=4096 --cpus=2 --driver=docker

# Verify cluster is running
minikube status

# Expected output:
# minikube
# type: Control Plane
# host: Running
# kubelet: Running
# apiserver: Running
# kubeconfig: Configured
```

**Troubleshooting**:
- If Minikube fails to start, try: `minikube delete && minikube start`
- On Windows, ensure Docker Desktop is running
- On macOS, ensure Docker Desktop has sufficient resources in Settings

---

## Step 2: Build Docker Images

Navigate to the project root and build both images:

### Option A: Using Gordon (Docker AI)

```bash
# Ask Gordon to build optimized images
docker ai "Build a multi-stage Docker image for a Python FastAPI backend from phase4-chatbot/backend/"
docker ai "Build a multi-stage Docker image for a Next.js frontend from phase4-chatbot/frontend/"
```

### Option B: Standard Docker Commands

```bash
# Build backend image
docker build \
  -t todo-backend:v1.0.0 \
  -f k8s/dockerfiles/backend.Dockerfile \
  phase4-chatbot/backend/

# Build frontend image
docker build \
  -t todo-frontend:v1.0.0 \
  -f k8s/dockerfiles/frontend.Dockerfile \
  phase4-chatbot/frontend/

# Verify images
docker images | grep todo
```

**Expected Output**:
```
todo-backend   v1.0.0   abc123   2 minutes ago   450MB
todo-frontend  v1.0.0   def456   1 minute ago    180MB
```

**Troubleshooting**:
- If build fails, check Dockerfile paths are correct
- Ensure you're in the project root directory
- Check Docker daemon is running: `docker ps`

---

## Step 3: Load Images to Minikube

Minikube runs in its own Docker environment, so we need to load images:

```bash
# Load backend image
minikube image load todo-backend:v1.0.0

# Load frontend image
minikube image load todo-frontend:v1.0.0

# Verify images in Minikube
minikube image ls | grep todo
```

**Alternative**: Use Minikube's Docker daemon directly:

```bash
# Point Docker CLI to Minikube's Docker daemon
eval $(minikube docker-env)

# Now rebuild images (they'll be in Minikube automatically)
docker build -t todo-backend:v1.0.0 -f k8s/dockerfiles/backend.Dockerfile phase4-chatbot/backend/
docker build -t todo-frontend:v1.0.0 -f k8s/dockerfiles/frontend.Dockerfile phase4-chatbot/frontend/

# Reset Docker CLI to host daemon
eval $(minikube docker-env -u)
```

---

## Step 4: Create Kubernetes Secrets

Create secrets for sensitive configuration:

```bash
# Create secrets from environment variables
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://user:pass@ep-xxx.neon.tech/todo_db" \
  --from-literal=GROQ_API_KEY="gsk_xxx" \
  --from-literal=JWT_SECRET="your-secret-key-min-32-chars" \
  --from-literal=GROQ_BASE_URL="https://api.groq.com/openai/v1" \
  --from-literal=GROQ_MODEL="llama-3.3-70b-versatile"

# Verify secret created
kubectl get secrets
```

**Security Note**: Never commit these values to Git. Use `.env` file locally:

```bash
# Create .env file (gitignored)
cat > .env <<EOF
DATABASE_URL=postgresql://user:pass@ep-xxx.neon.tech/todo_db
GROQ_API_KEY=gsk_xxx
JWT_SECRET=your-secret-key-min-32-chars
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.3-70b-versatile
EOF

# Create secret from file
kubectl create secret generic todo-secrets --from-env-file=.env
```

---

## Step 5: Install Helm Chart

Deploy the application using Helm:

### Option A: Using kubectl-ai

```bash
# Ask kubectl-ai to deploy
kubectl-ai "deploy the todo-chatbot helm chart from k8s/helm-charts/todo-chatbot/"
```

### Option B: Standard Helm Commands

```bash
# Validate chart first
helm lint k8s/helm-charts/todo-chatbot/

# Dry-run to see what will be created
helm install todo-chatbot k8s/helm-charts/todo-chatbot/ --dry-run --debug

# Install chart
helm install todo-chatbot k8s/helm-charts/todo-chatbot/

# Verify installation
helm list
```

**Expected Output**:
```
NAME            NAMESPACE   REVISION    UPDATED                                 STATUS      CHART
todo-chatbot    default     1           2026-02-08 10:30:00.000000 +0000 UTC    deployed    todo-chatbot-1.0.0
```

---

## Step 6: Verify Deployment

Check that all pods are running:

```bash
# Watch pods start up
kubectl get pods -w

# Expected output (after 1-2 minutes):
# NAME                        READY   STATUS    RESTARTS   AGE
# backend-7d8f9c5b-xk2p9      1/1     Running   0          2m
# frontend-6c9d8f4a-zx7k3     1/1     Running   0          2m

# Check pod logs
kubectl logs -l app=todo-chatbot,component=backend
kubectl logs -l app=todo-chatbot,component=frontend

# Check services
kubectl get services
```

**Troubleshooting**:
- If pods are in `Pending` state: Check Minikube resources with `kubectl describe pod <pod-name>`
- If pods are in `CrashLoopBackOff`: Check logs with `kubectl logs <pod-name>`
- If pods are in `ImagePullBackOff`: Verify images are loaded with `minikube image ls`

---

## Step 7: Access the Application

### Option A: Using Minikube Tunnel (Recommended)

```bash
# Start tunnel (requires admin/sudo password)
minikube tunnel

# In another terminal, get the external IP
kubectl get service frontend

# Expected output:
# NAME       TYPE           CLUSTER-IP      EXTERNAL-IP   PORT(S)        AGE
# frontend   LoadBalancer   10.96.100.50    127.0.0.1     80:30000/TCP   5m

# Access application
open http://127.0.0.1
# Or visit http://localhost in your browser
```

### Option B: Using NodePort

```bash
# Get the NodePort
kubectl get service frontend -o jsonpath='{.spec.ports[0].nodePort}'

# Get Minikube IP
minikube ip

# Access application
open http://$(minikube ip):$(kubectl get service frontend -o jsonpath='{.spec.ports[0].nodePort}')
```

### Option C: Using Port Forwarding

```bash
# Forward local port to frontend service
kubectl port-forward service/frontend 3000:80

# Access application
open http://localhost:3000
```

---

## Step 8: Test the Application

1. **Open the application** in your browser (http://localhost or http://127.0.0.1)

2. **Login** with your existing credentials from Phase IV

3. **Test basic features**:
   - Create a new task
   - View task list
   - Mark task as complete
   - Update task details
   - Delete task

4. **Test chatbot** (click purple robot icon 🤖):
   - "Add a task to buy groceries"
   - "Show me all my tasks"
   - "Mark task 1 as complete"

5. **Verify health checks**:
   ```bash
   # Backend health
   kubectl exec -it deployment/backend -- curl http://localhost:8000/health

   # Frontend health
   kubectl exec -it deployment/frontend -- curl http://localhost:3000/api/health
   ```

---

## Step 9: Scale the Application (Optional)

Test horizontal scaling:

### Option A: Using kubectl-ai

```bash
# Scale backend to 3 replicas
kubectl-ai "scale the backend to 3 replicas"

# Scale frontend to 2 replicas
kubectl-ai "scale the frontend to 2 replicas"
```

### Option B: Standard kubectl Commands

```bash
# Scale backend
kubectl scale deployment backend --replicas=3

# Scale frontend
kubectl scale deployment frontend --replicas=2

# Verify scaling
kubectl get pods
```

**Expected Output**:
```
NAME                        READY   STATUS    RESTARTS   AGE
backend-7d8f9c5b-xk2p9      1/1     Running   0          10m
backend-7d8f9c5b-abc123     1/1     Running   0          30s
backend-7d8f9c5b-def456     1/1     Running   0          30s
frontend-6c9d8f4a-zx7k3     1/1     Running   0          10m
frontend-6c9d8f4a-ghi789    1/1     Running   0          30s
```

---

## Step 10: Update the Application (Optional)

Test rolling updates:

```bash
# Rebuild images with new tag
docker build -t todo-backend:v1.0.1 -f k8s/dockerfiles/backend.Dockerfile phase4-chatbot/backend/
minikube image load todo-backend:v1.0.1

# Update Helm values
helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
  --set backend.image.tag=v1.0.1

# Watch rolling update
kubectl rollout status deployment/backend

# Verify new version
kubectl get pods -l component=backend -o jsonpath='{.items[0].spec.containers[0].image}'
```

**Rollback if needed**:
```bash
# Rollback to previous version
helm rollback todo-chatbot

# Or using kubectl
kubectl rollout undo deployment/backend
```

---

## Cleanup

When you're done testing:

```bash
# Uninstall Helm chart
helm uninstall todo-chatbot

# Delete secrets
kubectl delete secret todo-secrets

# Stop Minikube
minikube stop

# Delete Minikube cluster (optional, removes all data)
minikube delete
```

---

## Common Issues and Solutions

### Issue: Pods stuck in Pending

**Cause**: Insufficient Minikube resources

**Solution**:
```bash
# Check resource usage
kubectl top nodes

# Restart Minikube with more resources
minikube stop
minikube start --memory=8192 --cpus=4
```

### Issue: ImagePullBackOff

**Cause**: Images not loaded to Minikube

**Solution**:
```bash
# Verify images in Minikube
minikube image ls | grep todo

# Reload images
minikube image load todo-backend:v1.0.0
minikube image load todo-frontend:v1.0.0
```

### Issue: CrashLoopBackOff

**Cause**: Application error or missing configuration

**Solution**:
```bash
# Check pod logs
kubectl logs <pod-name>

# Check pod events
kubectl describe pod <pod-name>

# Verify secrets exist
kubectl get secrets
kubectl describe secret todo-secrets
```

### Issue: Cannot access application

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

### Issue: Database connection failed

**Cause**: Invalid DATABASE_URL or network issue

**Solution**:
```bash
# Test database connectivity from pod
kubectl exec -it deployment/backend -- python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"

# Verify secret value
kubectl get secret todo-secrets -o jsonpath='{.data.DATABASE_URL}' | base64 -d
```

---

## Next Steps

After successful deployment:

1. **Explore AI Tools**:
   - Try Gordon for Dockerfile optimization
   - Use kubectl-ai for cluster operations
   - Run Kagent for cluster analysis

2. **Monitor Resources**:
   ```bash
   # Install metrics-server
   minikube addons enable metrics-server

   # View resource usage
   kubectl top pods
   kubectl top nodes
   ```

3. **Test Production Scenarios**:
   - Simulate pod failures: `kubectl delete pod <pod-name>`
   - Test rolling updates with zero downtime
   - Verify health checks restart unhealthy pods

4. **Prepare for Phase VI**:
   - Document lessons learned
   - Identify configuration changes needed for cloud
   - Plan for production-grade monitoring and logging

---

## Summary

You've successfully deployed the Todo Chatbot to a local Kubernetes cluster! 🎉

**What You Accomplished**:
- ✅ Built optimized Docker images (<500MB backend, <200MB frontend)
- ✅ Created Helm chart for declarative deployment
- ✅ Deployed to Minikube with proper health checks
- ✅ Exposed application for external access
- ✅ Tested scaling and updates

**Deployment Time**: ~30-45 minutes (first time), ~10 minutes (subsequent deployments)

**Next Command**: `/sp.tasks` to break down implementation into executable tasks
