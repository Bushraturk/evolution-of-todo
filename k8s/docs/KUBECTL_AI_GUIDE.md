# kubectl-ai Guide: AI-Assisted Kubernetes Operations

**Feature**: AI-Assisted Kubernetes Operations (Phase V)
**Purpose**: Leverage kubectl-ai for natural language Kubernetes cluster management

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Common Use Cases](#common-use-cases)
5. [Deployment Operations](#deployment-operations)
6. [Scaling Operations](#scaling-operations)
7. [Troubleshooting](#troubleshooting)
8. [Resource Management](#resource-management)
9. [Best Practices](#best-practices)
10. [Fallback Commands](#fallback-commands)

---

## Overview

**kubectl-ai** is an AI-powered kubectl plugin that translates natural language into Kubernetes commands. It simplifies cluster operations by allowing you to describe what you want instead of remembering complex kubectl syntax.

**Key Benefits**:
- Natural language interface for kubectl
- Automatic command generation
- Context-aware suggestions
- Reduced learning curve for Kubernetes
- Faster operations with less syntax errors

**How It Works**:
1. You describe what you want in plain English
2. kubectl-ai generates the appropriate kubectl command
3. You review and approve the command
4. kubectl-ai executes it

---

## Installation

### Option 1: Homebrew (macOS/Linux)

```bash
# Install kubectl-ai
brew install kubectl-ai

# Verify installation
kubectl ai version
```

### Option 2: pip (All Platforms)

```bash
# Install via pip
pip install kubectl-ai

# Verify installation
kubectl ai version
```

### Option 3: Manual Installation

```bash
# Download binary from GitHub
curl -LO https://github.com/sozercan/kubectl-ai/releases/latest/download/kubectl-ai-$(uname -s)-$(uname -m)

# Make executable
chmod +x kubectl-ai-*

# Move to PATH
sudo mv kubectl-ai-* /usr/local/bin/kubectl-ai

# Verify installation
kubectl ai version
```

### Configuration

kubectl-ai requires an OpenAI API key:

```bash
# Set OpenAI API key
export OPENAI_API_KEY="sk-..."

# Or add to your shell profile
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
source ~/.bashrc
```

**Alternative**: Use Azure OpenAI or other compatible endpoints:

```bash
export OPENAI_API_BASE="https://your-endpoint.openai.azure.com/"
export OPENAI_API_KEY="your-azure-key"
```

---

## Getting Started

### Basic Syntax

```bash
kubectl ai "your natural language request"
```

### Interactive Mode

```bash
# Start interactive session
kubectl ai

# Then type requests:
> show me all pods
> scale backend to 3 replicas
> get logs from frontend
```

### Dry Run Mode

```bash
# Generate command without executing
kubectl ai --dry-run "show me all pods"
```

### Examples

```bash
# Simple query
kubectl ai "list all pods"

# Complex operation
kubectl ai "scale the backend deployment to 3 replicas and wait for them to be ready"

# Troubleshooting
kubectl ai "why is my frontend pod crashing?"
```

---

## Common Use Cases

### 1. Viewing Resources

**Natural Language**:
```bash
kubectl ai "show me all pods in the default namespace"
kubectl ai "list all services"
kubectl ai "get all deployments with their replica counts"
kubectl ai "show me pods that are not running"
```

**Generated Commands**:
```bash
kubectl get pods -n default
kubectl get services
kubectl get deployments -o wide
kubectl get pods --field-selector=status.phase!=Running
```

**Fallback** (manual):
```bash
kubectl get pods
kubectl get services
kubectl get deployments
kubectl get all
```

---

### 2. Describing Resources

**Natural Language**:
```bash
kubectl ai "describe the backend pod"
kubectl ai "show me details of the frontend service"
kubectl ai "what's the configuration of the backend deployment?"
```

**Generated Commands**:
```bash
kubectl describe pod -l app.kubernetes.io/component=backend
kubectl describe service frontend
kubectl describe deployment backend
```

**Fallback** (manual):
```bash
kubectl describe pod <pod-name>
kubectl describe service <service-name>
kubectl describe deployment <deployment-name>
```

---

### 3. Viewing Logs

**Natural Language**:
```bash
kubectl ai "show me logs from the backend pod"
kubectl ai "tail logs from frontend with timestamps"
kubectl ai "show me the last 50 lines of backend logs"
kubectl ai "follow logs from all pods with label app=todo-chatbot"
```

**Generated Commands**:
```bash
kubectl logs -l app.kubernetes.io/component=backend
kubectl logs -l app.kubernetes.io/component=frontend --timestamps --follow
kubectl logs -l app.kubernetes.io/component=backend --tail=50
kubectl logs -l app.kubernetes.io/name=todo-chatbot --all-containers --follow
```

**Fallback** (manual):
```bash
kubectl logs <pod-name>
kubectl logs -f <pod-name>
kubectl logs --tail=50 <pod-name>
kubectl logs -l app=backend
```

---

## Deployment Operations

### Creating Deployments

**Natural Language**:
```bash
kubectl ai "create a deployment named test-app with nginx image and 2 replicas"
kubectl ai "deploy redis with 1 replica and expose port 6379"
```

**Generated Commands**:
```bash
kubectl create deployment test-app --image=nginx --replicas=2
kubectl create deployment redis --image=redis --port=6379
kubectl expose deployment redis --port=6379
```

**Fallback** (manual):
```bash
kubectl create deployment <name> --image=<image>
kubectl expose deployment <name> --port=<port>
```

---

### Updating Deployments

**Natural Language**:
```bash
kubectl ai "update backend deployment to use image todo-backend:v1.0.1"
kubectl ai "change the frontend image tag to latest"
kubectl ai "set environment variable API_URL to http://backend:8000 in frontend deployment"
```

**Generated Commands**:
```bash
kubectl set image deployment/backend backend=todo-backend:v1.0.1
kubectl set image deployment/frontend frontend=todo-frontend:latest
kubectl set env deployment/frontend API_URL=http://backend:8000
```

**Fallback** (manual):
```bash
kubectl set image deployment/<name> <container>=<image>
kubectl set env deployment/<name> KEY=VALUE
kubectl edit deployment <name>
```

---

### Rolling Updates

**Natural Language**:
```bash
kubectl ai "perform a rolling update of backend to version v1.0.1"
kubectl ai "update frontend image and watch the rollout"
kubectl ai "check the rollout status of backend deployment"
```

**Generated Commands**:
```bash
kubectl set image deployment/backend backend=todo-backend:v1.0.1
kubectl rollout status deployment/backend --watch
kubectl rollout status deployment/backend
```

**Fallback** (manual):
```bash
kubectl set image deployment/<name> <container>=<image>
kubectl rollout status deployment/<name>
kubectl rollout history deployment/<name>
```

---

### Rollbacks

**Natural Language**:
```bash
kubectl ai "rollback the backend deployment to the previous version"
kubectl ai "undo the last deployment of frontend"
kubectl ai "rollback backend to revision 2"
```

**Generated Commands**:
```bash
kubectl rollout undo deployment/backend
kubectl rollout undo deployment/frontend
kubectl rollout undo deployment/backend --to-revision=2
```

**Fallback** (manual):
```bash
kubectl rollout undo deployment/<name>
kubectl rollout undo deployment/<name> --to-revision=<number>
kubectl rollout history deployment/<name>
```

---

## Scaling Operations

### Manual Scaling

**Natural Language**:
```bash
kubectl ai "scale backend to 3 replicas"
kubectl ai "increase frontend replicas to 5"
kubectl ai "scale down backend to 1 replica"
```

**Generated Commands**:
```bash
kubectl scale deployment backend --replicas=3
kubectl scale deployment frontend --replicas=5
kubectl scale deployment backend --replicas=1
```

**Fallback** (manual):
```bash
kubectl scale deployment <name> --replicas=<count>
```

---

### Autoscaling

**Natural Language**:
```bash
kubectl ai "create horizontal pod autoscaler for backend with min 2 max 10 replicas at 80% CPU"
kubectl ai "enable autoscaling for frontend between 1 and 5 replicas"
kubectl ai "show me the autoscaler status for backend"
```

**Generated Commands**:
```bash
kubectl autoscale deployment backend --min=2 --max=10 --cpu-percent=80
kubectl autoscale deployment frontend --min=1 --max=5
kubectl get hpa backend
```

**Fallback** (manual):
```bash
kubectl autoscale deployment <name> --min=<min> --max=<max> --cpu-percent=<percent>
kubectl get hpa
kubectl describe hpa <name>
```

---

### Verifying Scaling

**Natural Language**:
```bash
kubectl ai "check if all backend replicas are ready"
kubectl ai "show me the current replica count for all deployments"
kubectl ai "wait for backend to have 3 ready replicas"
```

**Generated Commands**:
```bash
kubectl get deployment backend -o jsonpath='{.status.readyReplicas}'
kubectl get deployments -o wide
kubectl wait --for=condition=available --timeout=60s deployment/backend
```

**Fallback** (manual):
```bash
kubectl get deployments
kubectl get pods -l app=backend
kubectl wait --for=condition=available deployment/<name>
```

---

## Troubleshooting

### Pod Issues

**Natural Language**:
```bash
kubectl ai "why is my backend pod crashing?"
kubectl ai "show me events for the frontend pod"
kubectl ai "what's wrong with pods that are not running?"
kubectl ai "debug the backend pod"
```

**Generated Commands**:
```bash
kubectl describe pod -l app.kubernetes.io/component=backend
kubectl get events --field-selector involvedObject.name=<frontend-pod>
kubectl get pods --field-selector=status.phase!=Running
kubectl logs -l app.kubernetes.io/component=backend --previous
```

**Fallback** (manual):
```bash
kubectl describe pod <pod-name>
kubectl logs <pod-name>
kubectl logs <pod-name> --previous
kubectl get events --sort-by='.lastTimestamp'
```

---

### Service Issues

**Natural Language**:
```bash
kubectl ai "why can't I access the frontend service?"
kubectl ai "show me the endpoints for backend service"
kubectl ai "test connectivity to backend service from frontend pod"
```

**Generated Commands**:
```bash
kubectl describe service frontend
kubectl get endpoints backend
kubectl exec -it <frontend-pod> -- curl http://backend:8000/health
```

**Fallback** (manual):
```bash
kubectl describe service <service-name>
kubectl get endpoints <service-name>
kubectl exec -it <pod-name> -- curl <service-url>
```

---

### Resource Issues

**Natural Language**:
```bash
kubectl ai "show me pods that are using too much memory"
kubectl ai "which pods are being throttled?"
kubectl ai "show me resource usage for all pods"
```

**Generated Commands**:
```bash
kubectl top pods --sort-by=memory
kubectl describe pods | grep -i throttl
kubectl top pods
```

**Fallback** (manual):
```bash
kubectl top pods
kubectl top nodes
kubectl describe pod <pod-name> | grep -A 5 "Limits\|Requests"
```

---

### Network Issues

**Natural Language**:
```bash
kubectl ai "test if backend can reach the database"
kubectl ai "show me network policies affecting frontend"
kubectl ai "check DNS resolution in backend pod"
```

**Generated Commands**:
```bash
kubectl exec -it <backend-pod> -- nc -zv <db-host> 5432
kubectl get networkpolicies
kubectl exec -it <backend-pod> -- nslookup backend
```

**Fallback** (manual):
```bash
kubectl exec -it <pod-name> -- curl <url>
kubectl exec -it <pod-name> -- ping <host>
kubectl exec -it <pod-name> -- nslookup <service>
```

---

## Resource Management

### ConfigMaps and Secrets

**Natural Language**:
```bash
kubectl ai "create a configmap named app-config from file config.yaml"
kubectl ai "show me the contents of todo-secrets"
kubectl ai "update the DATABASE_URL in todo-secrets"
```

**Generated Commands**:
```bash
kubectl create configmap app-config --from-file=config.yaml
kubectl get secret todo-secrets -o yaml
kubectl edit secret todo-secrets
```

**Fallback** (manual):
```bash
kubectl create configmap <name> --from-file=<file>
kubectl create secret generic <name> --from-literal=KEY=VALUE
kubectl get secret <name> -o jsonpath='{.data.KEY}' | base64 -d
```

---

### Resource Quotas and Limits

**Natural Language**:
```bash
kubectl ai "show me resource limits for backend pod"
kubectl ai "what's the resource quota for default namespace?"
kubectl ai "check if any pods are hitting resource limits"
```

**Generated Commands**:
```bash
kubectl describe pod -l app.kubernetes.io/component=backend | grep -A 5 "Limits\|Requests"
kubectl get resourcequota -n default
kubectl top pods
```

**Fallback** (manual):
```bash
kubectl describe pod <pod-name>
kubectl get resourcequota
kubectl describe resourcequota <name>
```

---

### Persistent Volumes

**Natural Language**:
```bash
kubectl ai "show me all persistent volumes"
kubectl ai "which persistent volume claims are bound?"
kubectl ai "create a persistent volume claim for 10Gi storage"
```

**Generated Commands**:
```bash
kubectl get pv
kubectl get pvc --field-selector=status.phase=Bound
kubectl create -f - <<EOF
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: my-pvc
spec:
  accessModes:
    - ReadWriteOnce
  resources:
    requests:
      storage: 10Gi
EOF
```

**Fallback** (manual):
```bash
kubectl get pv
kubectl get pvc
kubectl describe pv <name>
kubectl describe pvc <name>
```

---

## Best Practices

### 1. Review Before Executing

Always review generated commands before execution:

```bash
# Use dry-run mode first
kubectl ai --dry-run "scale backend to 10 replicas"

# Review the command
# If correct, execute without --dry-run
kubectl ai "scale backend to 10 replicas"
```

### 2. Be Specific

Provide clear, specific requests:

**Good**:
```bash
kubectl ai "scale the backend deployment in default namespace to 3 replicas"
```

**Poor**:
```bash
kubectl ai "scale backend"
```

### 3. Use Context

kubectl-ai respects your current kubectl context:

```bash
# Set context first
kubectl config use-context minikube

# Then use kubectl-ai
kubectl ai "show me all pods"
```

### 4. Combine with Standard kubectl

Use kubectl-ai for complex operations, standard kubectl for simple ones:

```bash
# Simple: use standard kubectl
kubectl get pods

# Complex: use kubectl-ai
kubectl ai "show me pods that are crashing and their logs from the last 5 minutes"
```

### 5. Learn from Generated Commands

Use kubectl-ai as a learning tool:

```bash
# See what command is generated
kubectl ai --dry-run "create a deployment with 3 replicas"

# Learn the kubectl syntax
# Use it directly next time
```

---

## Fallback Commands

When kubectl-ai is unavailable, use these standard kubectl commands:

### Viewing Resources

```bash
# List resources
kubectl get pods
kubectl get services
kubectl get deployments
kubectl get all

# Describe resources
kubectl describe pod <pod-name>
kubectl describe service <service-name>

# View logs
kubectl logs <pod-name>
kubectl logs -f <pod-name>
kubectl logs --tail=50 <pod-name>
```

### Managing Deployments

```bash
# Create deployment
kubectl create deployment <name> --image=<image>

# Update image
kubectl set image deployment/<name> <container>=<image>

# Scale
kubectl scale deployment <name> --replicas=<count>

# Rollout
kubectl rollout status deployment/<name>
kubectl rollout undo deployment/<name>
```

### Troubleshooting

```bash
# Check pod status
kubectl get pods -o wide

# View events
kubectl get events --sort-by='.lastTimestamp'

# Execute commands in pod
kubectl exec -it <pod-name> -- /bin/bash

# Port forward
kubectl port-forward <pod-name> 8080:8080
```

### Resource Management

```bash
# ConfigMaps
kubectl create configmap <name> --from-file=<file>
kubectl get configmap <name> -o yaml

# Secrets
kubectl create secret generic <name> --from-literal=KEY=VALUE
kubectl get secret <name> -o jsonpath='{.data.KEY}' | base64 -d

# Resource usage
kubectl top pods
kubectl top nodes
```

---

## Examples from Todo Chatbot

### Deployment

```bash
# Check deployment status
kubectl ai "show me the status of todo-chatbot deployments"

# Scale backend
kubectl ai "scale backend to 3 replicas for load testing"

# Update image
kubectl ai "update backend deployment to use todo-backend:v1.0.1"
```

### Troubleshooting

```bash
# Debug pod issues
kubectl ai "why is the backend pod in CrashLoopBackOff?"

# Check connectivity
kubectl ai "test if frontend can reach backend service"

# View logs
kubectl ai "show me backend logs from the last 10 minutes with errors"
```

### Monitoring

```bash
# Resource usage
kubectl ai "show me which pods are using the most CPU"

# Health checks
kubectl ai "check if all health probes are passing"

# Events
kubectl ai "show me recent events for todo-chatbot"
```

---

## Comparison: kubectl-ai vs Manual

| Task | kubectl-ai | Manual kubectl | Winner |
|------|-----------|----------------|--------|
| Simple queries | 5 seconds | 2 seconds | Manual |
| Complex queries | 10 seconds | 60 seconds | kubectl-ai |
| Troubleshooting | 15 seconds | 120 seconds | kubectl-ai |
| Learning curve | Low | High | kubectl-ai |
| Precision | Medium | High | Manual |
| Speed (expert) | Medium | High | Manual |

**Recommendation**: Use kubectl-ai for complex operations and learning, use manual kubectl for simple, repetitive tasks.

---

## Troubleshooting kubectl-ai

### API Key Issues

**Issue**: "OpenAI API key not found"

**Solution**:
```bash
export OPENAI_API_KEY="sk-..."
echo 'export OPENAI_API_KEY="sk-..."' >> ~/.bashrc
```

### Command Not Found

**Issue**: "kubectl: 'ai' is not a kubectl command"

**Solution**:
```bash
# Reinstall kubectl-ai
pip install --upgrade kubectl-ai

# Or use direct binary
kubectl-ai "your request"
```

### Incorrect Commands Generated

**Issue**: kubectl-ai generates wrong command

**Solution**:
1. Be more specific in your request
2. Use --dry-run to review first
3. Provide more context (namespace, labels, etc.)
4. Fall back to manual kubectl

---

## Additional Resources

- **kubectl-ai GitHub**: https://github.com/sozercan/kubectl-ai
- **kubectl Documentation**: https://kubernetes.io/docs/reference/kubectl/
- **Kubernetes Cheat Sheet**: https://kubernetes.io/docs/reference/kubectl/cheatsheet/
- **Troubleshooting Guide**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

**Last Updated**: 2026-02-08
**Phase**: V - Local Kubernetes Deployment
**Status**: Production Ready
