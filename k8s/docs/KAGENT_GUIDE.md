# Kagent Guide: AI-Powered Kubernetes Cluster Analysis

**Feature**: AI-Assisted Kubernetes Operations (Phase V)
**Purpose**: Leverage Kagent for intelligent cluster analysis and resource optimization

## Table of Contents

1. [Overview](#overview)
2. [Installation](#installation)
3. [Getting Started](#getting-started)
4. [Cluster Analysis](#cluster-analysis)
5. [Resource Optimization](#resource-optimization)
6. [Cost Analysis](#cost-analysis)
7. [Security Analysis](#security-analysis)
8. [Performance Analysis](#performance-analysis)
9. [Best Practices](#best-practices)
10. [Fallback Commands](#fallback-commands)

---

## Overview

**Kagent** is an AI-powered Kubernetes agent that provides intelligent cluster analysis, optimization recommendations, and automated insights. It helps you understand your cluster's health, identify issues, and optimize resource usage.

**Key Benefits**:
- Automated cluster health analysis
- Resource optimization recommendations
- Cost reduction insights
- Security vulnerability detection
- Performance bottleneck identification
- Proactive issue detection

**How It Works**:
1. Kagent connects to your Kubernetes cluster
2. Analyzes resources, configurations, and metrics
3. Uses AI to identify patterns and issues
4. Provides actionable recommendations
5. Can automatically apply fixes (with approval)

---

## Installation

### Option 1: pip (Recommended)

```bash
# Install Kagent
pip install kagent

# Verify installation
kagent version
```

### Option 2: Docker

```bash
# Run Kagent in Docker
docker run --rm -it \
  -v ~/.kube/config:/root/.kube/config \
  kagent/kagent:latest

# Create alias for convenience
alias kagent='docker run --rm -it -v ~/.kube/config:/root/.kube/config kagent/kagent:latest'
```

### Option 3: From Source

```bash
# Clone repository
git clone https://github.com/kagent-ai/kagent.git
cd kagent

# Install dependencies
pip install -r requirements.txt

# Install Kagent
pip install -e .

# Verify installation
kagent version
```

### Configuration

Kagent requires access to your Kubernetes cluster:

```bash
# Kagent uses your kubectl config
export KUBECONFIG=~/.kube/config

# Or specify context
kagent --context minikube analyze
```

**Optional**: Configure AI provider (OpenAI, Azure, etc.):

```bash
# Set OpenAI API key for enhanced analysis
export OPENAI_API_KEY="sk-..."

# Or use configuration file
cat > ~/.kagent/config.yaml <<EOF
ai_provider: openai
api_key: sk-...
model: gpt-4
EOF
```

---

## Getting Started

### Basic Commands

```bash
# Analyze entire cluster
kagent analyze

# Analyze specific namespace
kagent analyze --namespace default

# Analyze specific resource type
kagent analyze --resource deployments

# Generate report
kagent analyze --output report.html
```

### Interactive Mode

```bash
# Start interactive session
kagent interactive

# Then use natural language:
> What's wrong with my cluster?
> Show me resource usage
> Optimize my deployments
> Check for security issues
```

### Quick Health Check

```bash
# Quick cluster health check
kagent health

# Detailed health report
kagent health --detailed

# Health check with recommendations
kagent health --recommendations
```

---

## Cluster Analysis

### Overall Cluster Health

**Command**:
```bash
kagent analyze --full
```

**Analysis Includes**:
- Node health and capacity
- Pod distribution and status
- Resource utilization (CPU, memory, disk)
- Network connectivity
- Storage health
- Control plane status

**Example Output**:
```
Cluster Health Score: 85/100

✓ Nodes: 1/1 healthy
✓ Pods: 12/12 running
⚠ Resource Usage: CPU 65%, Memory 78% (high)
✓ Network: All services reachable
✓ Storage: 45% used
⚠ Issues Found: 3 warnings, 0 errors

Recommendations:
1. Increase memory limits for backend deployment
2. Add resource requests to 2 pods
3. Enable metrics-server for better monitoring
```

**Fallback** (manual):
```bash
# Check node status
kubectl get nodes

# Check pod status
kubectl get pods --all-namespaces

# Check resource usage
kubectl top nodes
kubectl top pods --all-namespaces

# Check events
kubectl get events --sort-by='.lastTimestamp'
```

---

### Namespace Analysis

**Command**:
```bash
kagent analyze --namespace default
```

**Analysis Includes**:
- Pod health and distribution
- Resource quotas and limits
- Service connectivity
- ConfigMaps and Secrets usage
- Network policies

**Example Output**:
```
Namespace: default
Pods: 2 running, 0 pending, 0 failed
Services: 2 (1 LoadBalancer, 1 ClusterIP)
Resource Usage: 45% CPU, 60% Memory

Issues:
⚠ Backend pod has no resource limits
⚠ Frontend service using LoadBalancer (consider Ingress)
✓ All health checks passing

Recommendations:
1. Add resource limits to backend deployment
2. Consider using Ingress instead of LoadBalancer
3. Enable horizontal pod autoscaling
```

**Fallback** (manual):
```bash
kubectl get all -n default
kubectl describe namespace default
kubectl top pods -n default
```

---

### Deployment Analysis

**Command**:
```bash
kagent analyze --resource deployment --name backend
```

**Analysis Includes**:
- Replica health and distribution
- Resource requests and limits
- Health check configuration
- Update strategy
- Security context
- Image vulnerabilities

**Example Output**:
```
Deployment: backend
Replicas: 1/1 ready
Image: todo-backend:latest (450MB)
Resource Requests: 100m CPU, 256Mi Memory
Resource Limits: 500m CPU, 512Mi Memory

Health Checks:
✓ Liveness probe configured
✓ Readiness probe configured
✓ Startup probe configured

Security:
✓ Running as non-root user
✓ Read-only root filesystem
⚠ No network policy defined

Recommendations:
1. Add network policy to restrict traffic
2. Consider using specific image tag instead of 'latest'
3. Enable pod disruption budget for high availability
```

**Fallback** (manual):
```bash
kubectl describe deployment backend
kubectl get deployment backend -o yaml
```

---

## Resource Optimization

### CPU and Memory Optimization

**Command**:
```bash
kagent optimize --resource cpu,memory
```

**Analysis**:
- Identifies over-provisioned resources
- Detects under-provisioned resources
- Recommends optimal requests and limits
- Calculates potential cost savings

**Example Output**:
```
Resource Optimization Report

Backend Deployment:
Current: 100m CPU request, 500m limit
Actual Usage: 45m CPU (avg), 120m (p95)
Recommendation: 50m request, 200m limit
Savings: 50% CPU, 60% memory

Frontend Deployment:
Current: 50m CPU request, 200m limit
Actual Usage: 35m CPU (avg), 80m (p95)
Recommendation: 40m request, 150m limit
Savings: 20% CPU, 25% memory

Total Cluster Savings: 35% CPU, 42% Memory
Estimated Cost Reduction: $45/month
```

**Apply Recommendations**:
```bash
# Review recommendations
kagent optimize --dry-run

# Apply automatically
kagent optimize --apply

# Apply with confirmation
kagent optimize --apply --confirm
```

**Fallback** (manual):
```bash
# Check current usage
kubectl top pods

# Update resource limits
kubectl set resources deployment backend \
  --requests=cpu=50m,memory=128Mi \
  --limits=cpu=200m,memory=256Mi
```

---

### Image Optimization

**Command**:
```bash
kagent optimize --resource images
```

**Analysis**:
- Identifies large images
- Suggests smaller base images
- Detects unused images
- Recommends image optimization strategies

**Example Output**:
```
Image Optimization Report

todo-backend:latest (450MB)
✓ Size is acceptable (<500MB target)
⚠ Using 'latest' tag (use specific version)
Recommendation: Tag with version (e.g., v1.0.0)

todo-frontend:latest (180MB)
✓ Size is optimal (<200MB target)
✓ Using alpine base
⚠ Using 'latest' tag
Recommendation: Tag with version (e.g., v1.0.0)

Unused Images:
- old-backend:v0.9.0 (650MB) - not used for 30 days
- test-frontend:debug (1.2GB) - not used for 60 days
Recommendation: Remove unused images to free 1.85GB
```

**Fallback** (manual):
```bash
# List images in Minikube
minikube image ls

# Remove unused images
minikube image rm old-backend:v0.9.0
```

---

### Replica Optimization

**Command**:
```bash
kagent optimize --resource replicas
```

**Analysis**:
- Analyzes traffic patterns
- Recommends optimal replica counts
- Suggests autoscaling configuration
- Identifies over/under-scaled deployments

**Example Output**:
```
Replica Optimization Report

Backend Deployment:
Current: 1 replica (static)
Traffic Pattern: Steady (50 req/min avg)
Recommendation: Enable HPA with 1-3 replicas
Trigger: 70% CPU utilization

Frontend Deployment:
Current: 1 replica (static)
Traffic Pattern: Variable (20-100 req/min)
Recommendation: Enable HPA with 1-5 replicas
Trigger: 60% CPU utilization

Benefits:
- Better availability during traffic spikes
- Cost savings during low traffic periods
- Automatic scaling without manual intervention
```

**Apply Recommendations**:
```bash
# Enable autoscaling
kagent optimize --resource replicas --apply
```

**Fallback** (manual):
```bash
# Create HPA
kubectl autoscale deployment backend \
  --min=1 --max=3 --cpu-percent=70

kubectl autoscale deployment frontend \
  --min=1 --max=5 --cpu-percent=60
```

---

## Cost Analysis

### Cluster Cost Analysis

**Command**:
```bash
kagent cost analyze
```

**Analysis**:
- Calculates current resource costs
- Identifies cost optimization opportunities
- Provides cost breakdown by namespace/deployment
- Estimates savings from recommendations

**Example Output**:
```
Cluster Cost Analysis (Monthly)

Current Costs:
- Compute (CPU): $120
- Memory: $80
- Storage: $30
- Network: $20
Total: $250/month

Cost Breakdown by Namespace:
- default: $180 (72%)
- kube-system: $50 (20%)
- monitoring: $20 (8%)

Optimization Opportunities:
1. Right-size backend deployment: Save $35/month
2. Use spot instances for dev workloads: Save $40/month
3. Enable cluster autoscaler: Save $25/month
4. Optimize storage usage: Save $10/month

Total Potential Savings: $110/month (44%)
```

**Fallback** (manual):
```bash
# Calculate resource usage
kubectl top nodes
kubectl top pods --all-namespaces

# Estimate costs manually based on cloud provider pricing
```

---

### Resource Waste Detection

**Command**:
```bash
kagent cost waste
```

**Analysis**:
- Identifies unused resources
- Detects over-provisioned workloads
- Finds idle resources
- Calculates waste costs

**Example Output**:
```
Resource Waste Report

Over-Provisioned Resources:
- backend: Allocated 500m CPU, using 120m (76% waste)
- frontend: Allocated 200m CPU, using 80m (60% waste)
Waste Cost: $45/month

Idle Resources:
- test-deployment: 0 requests in 7 days
- staging-db: 0 connections in 14 days
Waste Cost: $30/month

Unused Persistent Volumes:
- old-data-pvc: 10Gi, not mounted for 30 days
Waste Cost: $5/month

Total Waste: $80/month (32% of total cost)
```

**Fallback** (manual):
```bash
# Find unused PVCs
kubectl get pvc --all-namespaces

# Check pod resource usage
kubectl top pods --all-namespaces
```

---

## Security Analysis

### Security Audit

**Command**:
```bash
kagent security audit
```

**Analysis**:
- Checks for security misconfigurations
- Identifies vulnerable images
- Detects missing security contexts
- Reviews RBAC policies
- Checks network policies

**Example Output**:
```
Security Audit Report

Critical Issues: 0
High Priority: 2
Medium Priority: 5
Low Priority: 3

High Priority Issues:
⚠ Backend deployment missing network policy
  Risk: Unrestricted network access
  Recommendation: Create network policy to restrict traffic

⚠ Frontend service exposed as LoadBalancer
  Risk: Direct internet exposure
  Recommendation: Use Ingress with TLS

Medium Priority Issues:
⚠ 2 pods running as root user
⚠ 3 pods missing security context
⚠ No pod security policies defined
⚠ Secrets not encrypted at rest
⚠ No resource quotas defined

Security Score: 72/100
```

**Apply Fixes**:
```bash
# Apply security recommendations
kagent security fix --apply
```

**Fallback** (manual):
```bash
# Check security contexts
kubectl get pods -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.securityContext}{"\n"}{end}'

# Scan images for vulnerabilities
docker scan todo-backend:latest
```

---

### Vulnerability Scanning

**Command**:
```bash
kagent security scan
```

**Analysis**:
- Scans container images for CVEs
- Checks for outdated dependencies
- Identifies security patches
- Provides remediation steps

**Example Output**:
```
Vulnerability Scan Report

todo-backend:latest
✓ No critical vulnerabilities
⚠ 3 high severity vulnerabilities
⚠ 12 medium severity vulnerabilities
Recommendation: Update base image to python:3.13.1-slim

todo-frontend:latest
✓ No critical vulnerabilities
✓ No high severity vulnerabilities
⚠ 5 medium severity vulnerabilities
Recommendation: Update Node.js to 20.11.0

Action Items:
1. Update backend base image
2. Update frontend Node.js version
3. Rebuild and redeploy images
```

**Fallback** (manual):
```bash
# Scan images with Docker
docker scan todo-backend:latest
docker scan todo-frontend:latest

# Or use Trivy
trivy image todo-backend:latest
```

---

## Performance Analysis

### Performance Profiling

**Command**:
```bash
kagent performance profile
```

**Analysis**:
- Analyzes response times
- Identifies slow endpoints
- Detects resource bottlenecks
- Provides optimization recommendations

**Example Output**:
```
Performance Profile Report

Backend Service:
Average Response Time: 145ms
P95 Response Time: 320ms
P99 Response Time: 580ms
Throughput: 50 req/sec

Bottlenecks Detected:
⚠ Database queries taking 80ms average
⚠ CPU throttling detected (15% of requests)
⚠ Memory pressure causing GC pauses

Recommendations:
1. Add database connection pooling
2. Increase CPU limits to prevent throttling
3. Increase memory limits to reduce GC pressure
4. Add caching layer for frequent queries

Expected Improvement: 40% faster response times
```

**Fallback** (manual):
```bash
# Check pod metrics
kubectl top pods

# View pod logs for performance issues
kubectl logs -l app=backend | grep -i "slow\|timeout"
```

---

### Load Testing Analysis

**Command**:
```bash
kagent performance load-test --duration 5m --rps 100
```

**Analysis**:
- Simulates load on cluster
- Measures performance under stress
- Identifies breaking points
- Recommends scaling strategies

**Example Output**:
```
Load Test Results (5 minutes, 100 RPS)

Success Rate: 98.5%
Failed Requests: 1.5% (timeout)
Average Response Time: 180ms
P95 Response Time: 450ms
P99 Response Time: 850ms

Resource Usage During Test:
- CPU: 85% (peak 95%)
- Memory: 75% (peak 82%)
- Network: 50 Mbps

Recommendations:
1. Scale backend to 3 replicas for 100+ RPS
2. Add connection pooling to reduce latency
3. Enable caching to reduce database load
4. Consider adding CDN for static assets

Estimated Capacity: 120 RPS with current resources
```

**Fallback** (manual):
```bash
# Use kubectl to monitor during load test
watch kubectl top pods

# Use external load testing tool
hey -z 5m -q 100 http://$(minikube ip):$(kubectl get svc frontend -o jsonpath='{.spec.ports[0].nodePort}')
```

---

## Best Practices

### 1. Regular Analysis

Run Kagent analysis regularly:

```bash
# Daily health check
kagent health --schedule daily

# Weekly full analysis
kagent analyze --full --schedule weekly

# Monthly cost review
kagent cost analyze --schedule monthly
```

### 2. Automated Recommendations

Enable automated recommendations:

```bash
# Enable auto-recommendations
kagent config set auto-recommend true

# Set recommendation threshold
kagent config set recommend-threshold medium

# Enable notifications
kagent config set notify-email your@email.com
```

### 3. Gradual Optimization

Apply optimizations gradually:

```bash
# Start with dry-run
kagent optimize --dry-run

# Apply one recommendation at a time
kagent optimize --apply --limit 1

# Monitor impact before applying more
kubectl top pods
```

### 4. Combine with Other Tools

Use Kagent alongside other tools:

```bash
# Use Gordon for Dockerfile optimization
# Use kubectl-ai for operations
# Use Kagent for cluster analysis

# Example workflow:
# 1. Gordon: Optimize Dockerfiles
# 2. kubectl-ai: Deploy optimized images
# 3. Kagent: Analyze cluster performance
# 4. Kagent: Apply resource optimizations
```

### 5. Monitor After Changes

Always monitor after applying recommendations:

```bash
# Apply optimization
kagent optimize --apply

# Monitor for 24 hours
kagent monitor --duration 24h

# Review impact
kagent analyze --compare before,after
```

---

## Fallback Commands

When Kagent is unavailable, use these standard Kubernetes commands:

### Cluster Analysis

```bash
# Node status
kubectl get nodes
kubectl describe nodes

# Pod status
kubectl get pods --all-namespaces
kubectl top pods --all-namespaces

# Resource usage
kubectl top nodes
kubectl top pods

# Events
kubectl get events --sort-by='.lastTimestamp'
```

### Resource Optimization

```bash
# Update resource limits
kubectl set resources deployment <name> \
  --requests=cpu=100m,memory=128Mi \
  --limits=cpu=500m,memory=512Mi

# Scale deployment
kubectl scale deployment <name> --replicas=3

# Enable autoscaling
kubectl autoscale deployment <name> --min=1 --max=5 --cpu-percent=70
```

### Security Analysis

```bash
# Check security contexts
kubectl get pods -o yaml | grep -A 10 securityContext

# Scan images
docker scan <image>
trivy image <image>

# Check RBAC
kubectl get rolebindings,clusterrolebindings --all-namespaces
```

### Performance Analysis

```bash
# Monitor resources
watch kubectl top pods

# Check logs for errors
kubectl logs -l app=backend | grep -i error

# Test connectivity
kubectl exec -it <pod> -- curl http://backend:8000/health
```

---

## Examples from Todo Chatbot

### Initial Cluster Analysis

```bash
# Analyze Todo Chatbot deployment
kagent analyze --namespace default

# Expected findings:
# - 2 pods running (backend, frontend)
# - Resource usage within limits
# - Health checks passing
# - Recommendations for optimization
```

### Resource Optimization

```bash
# Optimize Todo Chatbot resources
kagent optimize --namespace default

# Apply recommendations
kagent optimize --namespace default --apply

# Monitor impact
kagent monitor --namespace default --duration 1h
```

### Security Audit

```bash
# Audit Todo Chatbot security
kagent security audit --namespace default

# Fix security issues
kagent security fix --namespace default --apply

# Verify improvements
kagent security audit --namespace default
```

---

## Comparison: Kagent vs Manual

| Task | Kagent | Manual Analysis | Winner |
|------|--------|-----------------|--------|
| Cluster health check | 30 seconds | 15 minutes | Kagent |
| Resource optimization | 2 minutes | 2 hours | Kagent |
| Security audit | 1 minute | 1 hour | Kagent |
| Cost analysis | 1 minute | 3 hours | Kagent |
| Performance profiling | 5 minutes | 4 hours | Kagent |
| Learning curve | Low | High | Kagent |

**Recommendation**: Use Kagent for comprehensive analysis and optimization, use manual commands for quick checks and specific operations.

---

## Troubleshooting Kagent

### Installation Issues

**Issue**: "pip install kagent" fails

**Solution**:
```bash
# Update pip
pip install --upgrade pip

# Install with verbose output
pip install -v kagent

# Or use Docker
docker pull kagent/kagent:latest
```

### Connection Issues

**Issue**: "Cannot connect to cluster"

**Solution**:
```bash
# Check kubectl config
kubectl config current-context

# Verify cluster access
kubectl get nodes

# Specify context explicitly
kagent --context minikube analyze
```

### API Key Issues

**Issue**: "AI analysis unavailable"

**Solution**:
```bash
# Set API key
export OPENAI_API_KEY="sk-..."

# Or use config file
mkdir -p ~/.kagent
cat > ~/.kagent/config.yaml <<EOF
ai_provider: openai
api_key: sk-...
EOF
```

---

## Additional Resources

- **Kagent Documentation**: https://kagent.ai/docs
- **Kubernetes Best Practices**: https://kubernetes.io/docs/concepts/configuration/overview/
- **Resource Optimization Guide**: https://kubernetes.io/docs/concepts/configuration/manage-resources-containers/
- **Security Best Practices**: https://kubernetes.io/docs/concepts/security/

---

**Last Updated**: 2026-02-08
**Phase**: V - Local Kubernetes Deployment
**Status**: Production Ready
