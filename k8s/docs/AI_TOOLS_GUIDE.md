# AI Tools Guide: Integrated Kubernetes Workflow

**Feature**: AI-Assisted Kubernetes Operations (Phase V)
**Purpose**: Comprehensive guide for using Gordon, kubectl-ai, and Kagent together for enhanced productivity

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Tool Comparison](#tool-comparison)
4. [Integrated Workflows](#integrated-workflows)
5. [Development Workflow](#development-workflow)
6. [Deployment Workflow](#deployment-workflow)
7. [Operations Workflow](#operations-workflow)
8. [Troubleshooting Workflow](#troubleshooting-workflow)
9. [Optimization Workflow](#optimization-workflow)
10. [Best Practices](#best-practices)
11. [Fallback Commands](#fallback-commands)

---

## Overview

This guide demonstrates how to use three AI-powered tools together to streamline Kubernetes development and operations:

| Tool | Purpose | Primary Use Cases |
|------|---------|-------------------|
| **Gordon** | Docker AI Assistant | Dockerfile generation, image optimization, Docker troubleshooting |
| **kubectl-ai** | Kubernetes Operations | Natural language kubectl commands, deployment management, cluster operations |
| **Kagent** | Cluster Analysis | Resource optimization, cost analysis, security audits, performance profiling |

**Why Use AI Tools?**
- **Faster Development**: Generate Dockerfiles and Kubernetes manifests in seconds
- **Better Optimization**: AI-powered recommendations for resource usage and costs
- **Easier Troubleshooting**: Natural language queries for complex debugging
- **Reduced Learning Curve**: Less need to memorize complex syntax
- **Proactive Insights**: Automated detection of issues before they become problems

---

## Installation

### Prerequisites

- Docker Desktop 4.53+ (for Gordon)
- kubectl 1.28+ (for kubectl-ai and Kagent)
- Python 3.8+ (for kubectl-ai and Kagent)
- Kubernetes cluster (Minikube, kind, or cloud provider)

### Install All Tools

```bash
# 1. Gordon (Docker AI) - Enable in Docker Desktop
# Open Docker Desktop → Settings → Features in development → Enable "Docker AI (Gordon)"

# 2. kubectl-ai - Install via pip
pip install kubectl-ai

# Set OpenAI API key
export OPENAI_API_KEY="sk-..."
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc

# 3. Kagent - Install via pip
pip install kagent

# Verify installations
docker version  # Check Docker Desktop version (4.53+)
kubectl ai version
kagent version
```

### Alternative Installation Methods

#### Homebrew (macOS/Linux)

```bash
# kubectl-ai
brew install kubectl-ai

# Kagent (if available)
brew install kagent
```

#### Docker (Isolated Environment)

```bash
# kubectl-ai in Docker
docker run --rm -it \
  -v ~/.kube/config:/root/.kube/config \
  -e OPENAI_API_KEY="$OPENAI_API_KEY" \
  kubectl-ai/kubectl-ai:latest

# Kagent in Docker
docker run --rm -it \
  -v ~/.kube/config:/root/.kube/config \
  kagent/kagent:latest
```

### Configuration

```bash
# Create configuration directory
mkdir -p ~/.kube ~/.kagent

# Set up kubectl context
kubectl config use-context minikube

# Configure API keys
cat > ~/.bashrc <<EOF
export OPENAI_API_KEY="sk-..."
export KUBECONFIG=~/.kube/config
EOF

source ~/.bashrc

# Verify setup
kubectl get nodes
kubectl ai "show me all pods"
kagent health
```

---

## Tool Comparison

### When to Use Each Tool

| Scenario | Best Tool | Why |
|----------|-----------|-----|
| Create Dockerfile | Gordon | Specialized for Docker, generates optimized Dockerfiles |
| Optimize image size | Gordon | Analyzes layers, suggests base image alternatives |
| Deploy to Kubernetes | kubectl-ai | Natural language kubectl commands |
| Scale deployment | kubectl-ai | Quick scaling with natural language |
| Debug pod issues | kubectl-ai | Easy log access and troubleshooting |
| Analyze cluster health | Kagent | Comprehensive cluster analysis |
| Optimize resources | Kagent | AI-powered resource recommendations |
| Security audit | Kagent | Automated security scanning |
| Cost analysis | Kagent | Detailed cost breakdown and savings |
| Performance profiling | Kagent | Load testing and bottleneck detection |

### Tool Strengths

**Gordon**:
- ✅ Best for Dockerfile generation
- ✅ Excellent image optimization
- ✅ Integrated with Docker Desktop
- ❌ Limited to Docker operations
- ❌ No Kubernetes integration

**kubectl-ai**:
- ✅ Natural language kubectl interface
- ✅ Fast for simple operations
- ✅ Great for learning kubectl
- ❌ Requires API key
- ❌ Limited analysis capabilities

**Kagent**:
- ✅ Comprehensive cluster analysis
- ✅ Proactive recommendations
- ✅ Cost and security insights
- ❌ Requires setup
- ❌ Overkill for simple tasks

---

## Integrated Workflows

### Complete Application Lifecycle

```
1. Development (Gordon)
   ↓
2. Build & Test (Gordon + Docker)
   ↓
3. Deploy (kubectl-ai)
   ↓
4. Monitor (Kagent)
   ↓
5. Optimize (Kagent + kubectl-ai)
   ↓
6. Scale (kubectl-ai)
   ↓
7. Troubleshoot (kubectl-ai + Kagent)
```

---

## Development Workflow

### Step 1: Create Dockerfiles with Gordon

**Scenario**: Building a new microservice

```bash
# 1. Open Docker Desktop and access Gordon
# 2. Describe your application

Gordon Prompt:
"Create a production-ready Dockerfile for a Python FastAPI application with:
- Python 3.13 slim base
- Multi-stage build
- Non-root user
- Health check on port 8000
- Target size under 500MB"

# 3. Gordon generates Dockerfile
# 4. Save to k8s/dockerfiles/myservice.Dockerfile
```

**Fallback** (manual):
```bash
# Use existing template
cp k8s/dockerfiles/backend.Dockerfile k8s/dockerfiles/myservice.Dockerfile

# Edit manually
vim k8s/dockerfiles/myservice.Dockerfile
```

### Step 2: Optimize Dockerfile with Gordon

```bash
Gordon Prompt:
"Optimize this Dockerfile for smaller size and faster builds:
[paste Dockerfile]"

# Gordon suggests:
# - Use alpine base (if applicable)
# - Combine RUN commands
# - Add .dockerignore
# - Remove build tools from runtime
```

**Fallback** (manual):
```bash
# Analyze image layers
docker history myservice:latest --human

# Use dive for detailed analysis
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive:latest myservice:latest
```

### Step 3: Build and Test Images

```bash
# Build image
docker build -t myservice:latest -f k8s/dockerfiles/myservice.Dockerfile .

# Test locally
docker run --rm -p 8000:8000 myservice:latest

# Check size
docker images myservice:latest

# Scan for vulnerabilities
docker scan myservice:latest
```

---

## Deployment Workflow

### Step 1: Deploy with kubectl-ai

**Scenario**: Deploying Todo Chatbot to Minikube

```bash
# Start Minikube
minikube start --memory=4096 --cpus=2

# Load images
minikube image load todo-backend:latest
minikube image load todo-frontend:latest

# Create secrets
kubectl create secret generic todo-secrets \
  --from-literal=DATABASE_URL="postgresql://..." \
  --from-literal=GROQ_API_KEY="gsk_..." \
  --from-literal=JWT_SECRET="..."

# Deploy with Helm
helm install todo-chatbot k8s/helm-charts/todo-chatbot/

# Verify with kubectl-ai
kubectl ai "show me the status of todo-chatbot pods"
kubectl ai "are all pods running?"
```

**Fallback** (manual):
```bash
kubectl get pods -l app.kubernetes.io/name=todo-chatbot
kubectl wait --for=condition=ready pod -l app.kubernetes.io/name=todo-chatbot --timeout=180s
```

### Step 2: Verify Deployment with kubectl-ai

```bash
# Check pod status
kubectl ai "show me all pods and their status"

# Check services
kubectl ai "list all services with their endpoints"

# Check logs
kubectl ai "show me backend logs from the last 5 minutes"

# Test connectivity
kubectl ai "test if frontend can reach backend service"
```

**Fallback** (manual):
```bash
kubectl get pods
kubectl get services
kubectl logs -l app.kubernetes.io/component=backend --tail=50
kubectl exec -it <frontend-pod> -- curl http://backend:8000/health
```

### Step 3: Analyze with Kagent

```bash
# Initial health check
kagent health

# Full cluster analysis
kagent analyze --namespace default

# Check for issues
kagent analyze --full

# Review recommendations
kagent optimize --dry-run
```

**Fallback** (manual):
```bash
kubectl get all -n default
kubectl top pods -n default
kubectl describe pods -n default
kubectl get events --sort-by='.lastTimestamp'
```

---

## Operations Workflow

### Daily Operations

```bash
# Morning health check (Kagent)
kagent health --detailed

# Check resource usage (kubectl-ai)
kubectl ai "show me pods using the most CPU and memory"

# Review logs for errors (kubectl-ai)
kubectl ai "show me logs with errors from the last hour"

# Check for security issues (Kagent)
kagent security audit --quick
```

### Scaling Operations

```bash
# Scale based on traffic (kubectl-ai)
kubectl ai "scale backend to 3 replicas"

# Verify scaling (kubectl-ai)
kubectl ai "check if all backend replicas are ready"

# Enable autoscaling (kubectl-ai)
kubectl ai "create horizontal pod autoscaler for backend with min 2 max 10 replicas at 80% CPU"

# Monitor autoscaling (Kagent)
kagent monitor --resource hpa --duration 1h
```

**Fallback** (manual):
```bash
kubectl scale deployment backend --replicas=3
kubectl get pods -l app.kubernetes.io/component=backend
kubectl autoscale deployment backend --min=2 --max=10 --cpu-percent=80
kubectl get hpa
```

### Rolling Updates

```bash
# Update image (kubectl-ai)
kubectl ai "update backend deployment to use image todo-backend:v1.0.1"

# Watch rollout (kubectl-ai)
kubectl ai "watch the rollout status of backend deployment"

# Verify update (Kagent)
kagent analyze --resource deployment --name backend

# Rollback if needed (kubectl-ai)
kubectl ai "rollback backend deployment to previous version"
```

**Fallback** (manual):
```bash
kubectl set image deployment/backend backend=todo-backend:v1.0.1
kubectl rollout status deployment/backend
kubectl rollout undo deployment/backend
```

---

## Troubleshooting Workflow

### Pod Crashes

```bash
# 1. Identify issue (kubectl-ai)
kubectl ai "why is my backend pod crashing?"

# 2. Check logs (kubectl-ai)
kubectl ai "show me backend logs including previous crashes"

# 3. Describe pod (kubectl-ai)
kubectl ai "describe the backend pod and show events"

# 4. Analyze with Kagent
kagent analyze --resource pod --name <pod-name>

# 5. Get recommendations (Kagent)
kagent troubleshoot --issue crashloop
```

**Fallback** (manual):
```bash
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl logs <pod-name> --previous
kubectl get events --field-selector involvedObject.name=<pod-name>
```

### Performance Issues

```bash
# 1. Check resource usage (kubectl-ai)
kubectl ai "show me pods that are using too much CPU or memory"

# 2. Profile performance (Kagent)
kagent performance profile --namespace default

# 3. Identify bottlenecks (Kagent)
kagent analyze --focus performance

# 4. Get optimization recommendations (Kagent)
kagent optimize --resource cpu,memory --dry-run

# 5. Apply fixes (kubectl-ai)
kubectl ai "increase backend CPU limit to 500m and memory limit to 512Mi"
```

**Fallback** (manual):
```bash
kubectl top pods
kubectl describe pod <pod-name>
kubectl set resources deployment backend --limits=cpu=500m,memory=512Mi
```

### Network Issues

```bash
# 1. Check service connectivity (kubectl-ai)
kubectl ai "test if frontend can reach backend service"

# 2. Check service endpoints (kubectl-ai)
kubectl ai "show me endpoints for backend service"

# 3. Analyze network (Kagent)
kagent analyze --focus network

# 4. Test DNS (kubectl-ai)
kubectl ai "check DNS resolution for backend service from frontend pod"
```

**Fallback** (manual):
```bash
kubectl get services
kubectl get endpoints
kubectl exec -it <frontend-pod> -- curl http://backend:8000/health
kubectl exec -it <frontend-pod> -- nslookup backend
```

---

## Optimization Workflow

### Resource Optimization

```bash
# 1. Analyze current usage (Kagent)
kagent analyze --full

# 2. Get optimization recommendations (Kagent)
kagent optimize --resource cpu,memory,replicas

# 3. Review recommendations
kagent optimize --dry-run --output report.html

# 4. Apply optimizations gradually (kubectl-ai)
kubectl ai "set backend CPU request to 50m and limit to 200m"

# 5. Monitor impact (Kagent)
kagent monitor --duration 24h --compare before,after

# 6. Adjust if needed (kubectl-ai)
kubectl ai "scale backend to 2 replicas if CPU usage is high"
```

**Fallback** (manual):
```bash
kubectl top pods
kubectl set resources deployment backend --requests=cpu=50m,memory=128Mi --limits=cpu=200m,memory=256Mi
watch kubectl top pods
```

### Cost Optimization

```bash
# 1. Analyze costs (Kagent)
kagent cost analyze

# 2. Identify waste (Kagent)
kagent cost waste

# 3. Get savings recommendations (Kagent)
kagent cost optimize --dry-run

# 4. Apply cost-saving measures (kubectl-ai + Kagent)
kagent cost optimize --apply --confirm

# 5. Verify savings (Kagent)
kagent cost analyze --compare before,after
```

**Fallback** (manual):
```bash
kubectl top nodes
kubectl top pods --all-namespaces
kubectl get pods --all-namespaces -o json | jq '.items[] | select(.spec.containers[].resources.requests == null)'
```

### Security Optimization

```bash
# 1. Security audit (Kagent)
kagent security audit

# 2. Scan for vulnerabilities (Kagent)
kagent security scan

# 3. Get security recommendations (Kagent)
kagent security fix --dry-run

# 4. Apply security fixes (Kagent + kubectl-ai)
kagent security fix --apply

# 5. Verify improvements (Kagent)
kagent security audit --compare before,after
```

**Fallback** (manual):
```bash
kubectl get pods -o yaml | grep -A 10 securityContext
docker scan todo-backend:latest
kubectl get networkpolicies
```

---

## Best Practices

### 1. Use the Right Tool for the Job

```bash
# Docker operations → Gordon
Gordon: "Optimize this Dockerfile"

# Kubernetes operations → kubectl-ai
kubectl ai "scale backend to 3 replicas"

# Analysis and optimization → Kagent
kagent optimize --resource cpu,memory
```

### 2. Combine Tools in Workflows

```bash
# Example: Deploy and optimize new service

# Step 1: Create Dockerfile (Gordon)
Gordon: "Create Dockerfile for Node.js app"

# Step 2: Build and load (Docker + Minikube)
docker build -t myapp:latest .
minikube image load myapp:latest

# Step 3: Deploy (kubectl-ai)
kubectl ai "create deployment myapp with image myapp:latest and 2 replicas"

# Step 4: Analyze (Kagent)
kagent analyze --resource deployment --name myapp

# Step 5: Optimize (Kagent + kubectl-ai)
kagent optimize --resource myapp --apply
```

### 3. Verify AI Recommendations

Always review before applying:

```bash
# Use dry-run mode
kagent optimize --dry-run
kubectl ai --dry-run "delete all pods"

# Review generated commands
# Apply only if correct
```

### 4. Monitor After Changes

```bash
# After any change, monitor impact
kagent monitor --duration 1h

# Check for issues
kubectl ai "show me pods that are not running"

# Review logs
kubectl ai "show me logs with errors from the last 10 minutes"
```

### 5. Keep Fallback Commands Ready

Always know the manual alternative:

```bash
# AI tool fails? Use standard commands
kubectl get pods
kubectl describe pod <pod-name>
kubectl logs <pod-name>
docker build -t myapp:latest .
```

---

## Fallback Commands

### When AI Tools Are Unavailable

#### Docker Operations (Gordon Fallback)

```bash
# Build images
docker build -t myapp:latest -f Dockerfile .

# Optimize images
docker history myapp:latest --human
docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock wagoodman/dive:latest myapp:latest

# Test images
docker run --rm -p 8000:8000 myapp:latest

# Scan images
docker scan myapp:latest
```

#### Kubernetes Operations (kubectl-ai Fallback)

```bash
# View resources
kubectl get pods
kubectl get services
kubectl get deployments

# Describe resources
kubectl describe pod <pod-name>
kubectl describe service <service-name>

# View logs
kubectl logs <pod-name>
kubectl logs -f <pod-name>
kubectl logs --tail=50 <pod-name>

# Scale deployments
kubectl scale deployment <name> --replicas=3

# Update deployments
kubectl set image deployment/<name> <container>=<image>

# Rollback deployments
kubectl rollout undo deployment/<name>
```

#### Cluster Analysis (Kagent Fallback)

```bash
# Check cluster health
kubectl get nodes
kubectl get pods --all-namespaces
kubectl top nodes
kubectl top pods --all-namespaces

# Resource usage
kubectl describe nodes
kubectl describe pod <pod-name>

# Security checks
kubectl get pods -o yaml | grep -A 10 securityContext
docker scan <image>

# Cost analysis
kubectl top pods --all-namespaces
# Calculate costs manually based on cloud provider pricing
```

---

## Complete Example: Todo Chatbot Deployment

### Phase 1: Development (Gordon)

```bash
# Already done - Dockerfiles created with Gordon's help
# See: k8s/dockerfiles/backend.Dockerfile
# See: k8s/dockerfiles/frontend.Dockerfile
```

### Phase 2: Build and Load (Docker + Minikube)

```bash
# Build images
./k8s/scripts/build-images.sh

# Start Minikube
minikube start --memory=4096 --cpus=2

# Load images
./k8s/scripts/load-images.sh
```

### Phase 3: Deploy (kubectl-ai)

```bash
# Create secrets
./k8s/scripts/create-secrets.sh

# Deploy with Helm
helm install todo-chatbot k8s/helm-charts/todo-chatbot/

# Verify with kubectl-ai
kubectl ai "show me all todo-chatbot pods and their status"
kubectl ai "are all pods running and healthy?"
```

### Phase 4: Analyze (Kagent)

```bash
# Initial health check
kagent health

# Full analysis
kagent analyze --namespace default

# Check for issues
kagent analyze --full
```

### Phase 5: Optimize (Kagent + kubectl-ai)

```bash
# Get optimization recommendations
kagent optimize --dry-run

# Apply resource optimizations
kagent optimize --apply --confirm

# Verify with kubectl-ai
kubectl ai "show me resource usage for todo-chatbot pods"
```

### Phase 6: Monitor (All Tools)

```bash
# Daily health check (Kagent)
kagent health --detailed

# Check logs (kubectl-ai)
kubectl ai "show me logs from the last hour"

# Resource usage (kubectl-ai)
kubectl ai "show me pods using the most resources"

# Security audit (Kagent)
kagent security audit
```

---

## Troubleshooting AI Tools

### Gordon Not Available

**Issue**: Gordon icon not showing in Docker Desktop

**Solution**:
1. Update Docker Desktop to 4.53+ Beta
2. Enable in Settings → Features in development → Docker AI
3. Restart Docker Desktop

**Fallback**: Use manual Dockerfile creation and optimization

### kubectl-ai Not Working

**Issue**: "OpenAI API key not found"

**Solution**:
```bash
export OPENAI_API_KEY="sk-..."
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
source ~/.bashrc
```

**Fallback**: Use standard kubectl commands

### Kagent Connection Issues

**Issue**: "Cannot connect to cluster"

**Solution**:
```bash
kubectl config current-context
kubectl get nodes
kagent --context minikube analyze
```

**Fallback**: Use kubectl top, describe, and manual analysis

---

## Additional Resources

### Tool-Specific Guides

- **Gordon Guide**: [GORDON_GUIDE.md](GORDON_GUIDE.md)
- **kubectl-ai Guide**: [KUBECTL_AI_GUIDE.md](KUBECTL_AI_GUIDE.md)
- **Kagent Guide**: [KAGENT_GUIDE.md](KAGENT_GUIDE.md)

### Kubernetes Resources

- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Troubleshooting Guide**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Image Optimization**: [IMAGE_OPTIMIZATION.md](IMAGE_OPTIMIZATION.md)
- **Lifecycle Management**: [LIFECYCLE_MANAGEMENT.md](LIFECYCLE_MANAGEMENT.md)

### External Resources

- **Docker Documentation**: https://docs.docker.com/
- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **kubectl Cheat Sheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- **Helm Documentation**: https://helm.sh/docs/

---

## Quick Reference

### Common Commands

```bash
# Gordon (Docker Desktop UI)
# Access via AI assistant icon or Cmd+K / Ctrl+K

# kubectl-ai
kubectl ai "your natural language request"
kubectl ai --dry-run "your request"  # Preview command

# Kagent
kagent health                         # Quick health check
kagent analyze                        # Full cluster analysis
kagent optimize --dry-run             # Get recommendations
kagent optimize --apply               # Apply optimizations
kagent security audit                 # Security check
kagent cost analyze                   # Cost analysis
```

### Workflow Shortcuts

```bash
# Quick deployment check
kubectl ai "show me all pods" && kagent health

# Quick optimization
kagent optimize --dry-run && kubectl ai "show me resource usage"

# Quick troubleshooting
kubectl ai "why is my pod crashing?" && kagent analyze --resource pod

# Quick security check
kagent security audit && kubectl ai "show me pods running as root"
```

---

**Last Updated**: 2026-02-08
**Phase**: V - Local Kubernetes Deployment
**Status**: Production Ready

**Summary**: This guide demonstrates how to use Gordon, kubectl-ai, and Kagent together for efficient Kubernetes development and operations. Each tool has its strengths, and combining them creates a powerful workflow for building, deploying, and managing containerized applications.
