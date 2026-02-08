# Lifecycle Management Guide: Todo Chatbot on Kubernetes

**Feature**: Deployment Lifecycle Management (Phase V)
**Purpose**: Comprehensive guide for managing the complete lifecycle of Todo Chatbot deployments

## Table of Contents

1. [Overview](#overview)
2. [Rolling Updates](#rolling-updates)
3. [Rollback Procedures](#rollback-procedures)
4. [Scaling Operations](#scaling-operations)
5. [Image Updates](#image-updates)
6. [Configuration Updates](#configuration-updates)
7. [Zero Downtime Deployments](#zero-downtime-deployments)
8. [Health Check Management](#health-check-management)
9. [Monitoring and Observability](#monitoring-and-observability)
10. [Best Practices](#best-practices)

---

## Overview

This guide covers the complete lifecycle management of Todo Chatbot deployments on Kubernetes, including:

- **Rolling Updates**: Zero-downtime updates to new versions
- **Rollbacks**: Reverting to previous working versions
- **Scaling**: Horizontal scaling (manual and automatic)
- **Image Updates**: Deploying new container images
- **Configuration Updates**: Changing environment variables and settings
- **Health Checks**: Managing liveness, readiness, and startup probes

**Key Principles**:
- Zero downtime for all operations
- Gradual rollout with validation
- Easy rollback to previous versions
- Automated health checks
- Comprehensive monitoring

---

## Rolling Updates

### Overview

Rolling updates allow you to update deployments with zero downtime by gradually replacing old pods with new ones.

**How It Works**:
1. New pods are created with updated configuration
2. New pods pass health checks
3. Old pods are terminated
4. Process repeats until all pods are updated

**Strategy Configuration**:
```yaml
strategy:
  type: RollingUpdate
  rollingUpdate:
    maxSurge: 1        # Max new pods above desired count
    maxUnavailable: 0  # Max old pods that can be unavailable
```

### Performing Rolling Updates

#### Option 1: Using Automated Script

```bash
# Update backend to new version
./k8s/scripts/update-deployment.sh --component backend --tag v1.0.1 --wait

# Update frontend to new version
./k8s/scripts/update-deployment.sh --component frontend --tag v1.0.2 --wait

# Update all components
./k8s/scripts/update-deployment.sh --component all --tag v1.0.1 --wait
```

**Script Features**:
- Validates Helm release exists
- Performs Helm upgrade with new image tag
- Optionally waits for rollout completion
- Shows deployment status

#### Option 2: Using Helm

```bash
# Update with Helm
helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
  --set backend.image.tag=v1.0.1 \
  --set frontend.image.tag=v1.0.2 \
  --namespace default

# Watch rollout status
kubectl rollout status deployment/backend -n default
kubectl rollout status deployment/frontend -n default
```

#### Option 3: Using kubectl

```bash
# Update image directly
kubectl set image deployment/backend backend=todo-backend:v1.0.1 -n default

# Watch rollout
kubectl rollout status deployment/backend -n default --watch
```

### Monitoring Rolling Updates

```bash
# Watch pod changes in real-time
kubectl get pods -n default -w

# Check rollout status
kubectl rollout status deployment/backend -n default

# View rollout history
kubectl rollout history deployment/backend -n default

# Describe deployment for details
kubectl describe deployment backend -n default
```

### Rolling Update Best Practices

1. **Always Use Tags**: Never use `latest` tag in production
   ```bash
   # Good
   --set backend.image.tag=v1.0.1

   # Bad
   --set backend.image.tag=latest
   ```

2. **Test Before Production**: Test updates in dev environment first
   ```bash
   # Deploy to dev
   helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
     -f k8s/helm-charts/todo-chatbot/values-dev.yaml \
     --set backend.image.tag=v1.0.1
   ```

3. **Monitor During Rollout**: Watch logs and metrics
   ```bash
   # Follow logs during update
   kubectl logs -f deployment/backend -n default

   # Check resource usage
   kubectl top pods -n default
   ```

4. **Validate Health Checks**: Ensure new pods are healthy
   ```bash
   # Check pod status
   kubectl get pods -n default

   # Test health endpoint
   kubectl exec -it <pod-name> -- curl http://localhost:8000/health
   ```

---

## Rollback Procedures

### Overview

Rollbacks allow you to quickly revert to a previous working version when issues are detected.

**When to Rollback**:
- New version has critical bugs
- Performance degradation detected
- Health checks failing
- User-reported issues
- Failed deployment

### Performing Rollbacks

#### Option 1: Using Automated Script

```bash
# Rollback backend to previous version
./k8s/scripts/rollback-deployment.sh --component backend --wait

# Rollback to specific revision
./k8s/scripts/rollback-deployment.sh --component backend --revision 2 --wait

# Rollback all components
./k8s/scripts/rollback-deployment.sh --component all --wait
```

**Script Features**:
- Shows rollout history before rollback
- Confirms before proceeding
- Supports rollback to specific revision
- Waits for rollback completion

#### Option 2: Using kubectl

```bash
# Rollback to previous version
kubectl rollout undo deployment/backend -n default

# Rollback to specific revision
kubectl rollout undo deployment/backend -n default --to-revision=2

# Watch rollback progress
kubectl rollout status deployment/backend -n default
```

#### Option 3: Using Helm

```bash
# View Helm release history
helm history todo-chatbot -n default

# Rollback to previous release
helm rollback todo-chatbot -n default

# Rollback to specific revision
helm rollback todo-chatbot 2 -n default
```

### Viewing Version History

```bash
# Kubernetes deployment history
kubectl rollout history deployment/backend -n default

# Detailed revision info
kubectl rollout history deployment/backend -n default --revision=3

# Helm release history
helm history todo-chatbot -n default
```

**Example Output**:
```
REVISION  UPDATED                   STATUS      CHART               DESCRIPTION
1         Mon Feb 08 10:00:00 2026  superseded  todo-chatbot-1.0.0  Install complete
2         Mon Feb 08 11:00:00 2026  superseded  todo-chatbot-1.0.0  Upgrade complete
3         Mon Feb 08 12:00:00 2026  deployed    todo-chatbot-1.0.0  Upgrade complete
```

### Rollback Best Practices

1. **Verify Issue First**: Confirm the problem before rolling back
   ```bash
   # Check logs
   kubectl logs deployment/backend -n default --tail=100

   # Check metrics
   kubectl top pods -n default

   # Test endpoints
   curl http://<service-url>/health
   ```

2. **Document Rollback Reason**: Keep track of why rollback was needed
   ```bash
   # Add annotation
   kubectl annotate deployment backend \
     rollback-reason="Critical bug in v1.0.1" \
     -n default
   ```

3. **Test After Rollback**: Verify system is working
   ```bash
   # Check pod status
   kubectl get pods -n default

   # Test application
   ./k8s/scripts/access-application.sh
   ```

4. **Investigate Root Cause**: Understand what went wrong
   ```bash
   # Review logs from failed version
   kubectl logs <old-pod-name> -n default --previous
   ```

---

## Scaling Operations

### Overview

Scaling adjusts the number of pod replicas to handle varying load.

**Types of Scaling**:
- **Manual Scaling**: Explicitly set replica count
- **Horizontal Pod Autoscaling (HPA)**: Automatic scaling based on metrics

### Manual Scaling

#### Using Automated Script

```bash
# Scale backend to 3 replicas
./k8s/scripts/scale-deployment.sh --component backend --replicas 3 --wait

# Scale frontend to 5 replicas
./k8s/scripts/scale-deployment.sh --component frontend --replicas 5 --wait

# Scale all components to 2 replicas
./k8s/scripts/scale-deployment.sh --component all --replicas 2 --wait
```

#### Using kubectl

```bash
# Scale deployment
kubectl scale deployment backend --replicas=3 -n default

# Verify scaling
kubectl get deployment backend -n default
kubectl get pods -n default -l app.kubernetes.io/component=backend
```

#### Using Helm

```bash
# Update replica count via Helm
helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
  --set backend.replicaCount=3 \
  --set frontend.replicaCount=2 \
  --namespace default
```

### Horizontal Pod Autoscaling (HPA)

#### Enable Autoscaling

```bash
# Enable autoscaling with script
./k8s/scripts/scale-deployment.sh \
  --component backend \
  --autoscale \
  --min 2 \
  --max 10 \
  --cpu 70

# Or use kubectl
kubectl autoscale deployment backend \
  --min=2 \
  --max=10 \
  --cpu-percent=70 \
  -n default
```

#### Monitor Autoscaling

```bash
# View HPA status
kubectl get hpa -n default

# Watch HPA in real-time
kubectl get hpa -n default -w

# Describe HPA for details
kubectl describe hpa backend -n default
```

**Example HPA Status**:
```
NAME      REFERENCE            TARGETS   MINPODS   MAXPODS   REPLICAS   AGE
backend   Deployment/backend   45%/70%   2         10        3          5m
```

#### Disable Autoscaling

```bash
# Delete HPA
kubectl delete hpa backend -n default

# Set fixed replica count
kubectl scale deployment backend --replicas=2 -n default
```

### Scaling Best Practices

1. **Start Conservative**: Begin with lower replica counts
   ```bash
   # Start with 2 replicas
   kubectl scale deployment backend --replicas=2
   ```

2. **Monitor Resource Usage**: Check if scaling is needed
   ```bash
   # Check current usage
   kubectl top pods -n default

   # Check node capacity
   kubectl top nodes
   ```

3. **Use HPA for Variable Load**: Enable autoscaling for traffic spikes
   ```bash
   # Enable HPA for production
   kubectl autoscale deployment backend --min=2 --max=10 --cpu-percent=70
   ```

4. **Set Resource Requests**: Required for HPA to work
   ```yaml
   resources:
     requests:
       cpu: 100m
       memory: 256Mi
     limits:
       cpu: 500m
       memory: 512Mi
   ```

5. **Test Scaling**: Verify pods scale correctly
   ```bash
   # Generate load
   hey -z 5m -q 100 http://<service-url>

   # Watch HPA scale up
   kubectl get hpa -w
   ```

---

## Image Updates

### Overview

Image updates deploy new container images with code changes, bug fixes, or security patches.

### Update Workflow

#### Step 1: Build New Images

```bash
# Build with new tag
TAG=v1.0.1 ./k8s/scripts/build-images.sh

# Or build individually
docker build -t todo-backend:v1.0.1 \
  -f k8s/dockerfiles/backend.Dockerfile \
  phase4-chatbot/backend/

docker build -t todo-frontend:v1.0.1 \
  -f k8s/dockerfiles/frontend.Dockerfile \
  phase4-chatbot/frontend/
```

#### Step 2: Load Images to Minikube

```bash
# Load new images
minikube image load todo-backend:v1.0.1
minikube image load todo-frontend:v1.0.1

# Verify images loaded
minikube image ls | grep todo
```

#### Step 3: Deploy New Images

```bash
# Update deployment
./k8s/scripts/update-deployment.sh \
  --component backend \
  --tag v1.0.1 \
  --wait

# Or use Helm
helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
  --set backend.image.tag=v1.0.1 \
  --namespace default
```

#### Step 4: Verify Update

```bash
# Check pod images
kubectl get pods -n default -o jsonpath='{range .items[*]}{.metadata.name}{"\t"}{.spec.containers[*].image}{"\n"}{end}'

# Test application
./k8s/scripts/access-application.sh
```

### Image Update Best Practices

1. **Use Semantic Versioning**: Tag images with version numbers
   ```bash
   # Good
   todo-backend:v1.0.1
   todo-backend:v1.1.0
   todo-backend:v2.0.0

   # Bad
   todo-backend:latest
   todo-backend:new
   ```

2. **Test Images Locally**: Verify before deploying
   ```bash
   # Test image locally
   docker run --rm -p 8000:8000 todo-backend:v1.0.1

   # Check health
   curl http://localhost:8000/health
   ```

3. **Keep Old Images**: Don't delete until rollback window passes
   ```bash
   # List images
   minikube image ls | grep todo

   # Keep last 3 versions for rollback
   ```

4. **Document Changes**: Tag images with commit SHA or build number
   ```bash
   # Build with commit SHA
   GIT_SHA=$(git rev-parse --short HEAD)
   docker build -t todo-backend:v1.0.1-${GIT_SHA} .
   ```

---

## Configuration Updates

### Overview

Configuration updates change environment variables, secrets, or ConfigMaps without rebuilding images.

### Update Environment Variables

#### Via Helm Values

```bash
# Update values file
cat > custom-values.yaml <<EOF
backend:
  env:
    LOG_LEVEL: DEBUG
    MAX_CONVERSATION_HISTORY: 100
EOF

# Apply update
helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
  -f custom-values.yaml \
  --namespace default
```

#### Via kubectl

```bash
# Update environment variable
kubectl set env deployment/backend LOG_LEVEL=DEBUG -n default

# Verify update
kubectl describe deployment backend -n default | grep -A 10 Environment
```

### Update Secrets

```bash
# Update secret value
kubectl create secret generic todo-secrets \
  --from-literal=GROQ_API_KEY="new-key" \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new secret
kubectl rollout restart deployment/backend -n default
```

### Update ConfigMaps

```bash
# Update ConfigMap
kubectl create configmap app-config \
  --from-file=config.yaml \
  --dry-run=client -o yaml | kubectl apply -f -

# Restart pods to pick up new config
kubectl rollout restart deployment/backend -n default
```

### Configuration Update Best Practices

1. **Test Configuration**: Validate before applying
   ```bash
   # Dry-run to check syntax
   helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
     -f custom-values.yaml \
     --dry-run --debug
   ```

2. **Restart Pods**: Some changes require pod restart
   ```bash
   # Restart deployment
   kubectl rollout restart deployment/backend -n default
   ```

3. **Use ConfigMaps for Non-Sensitive Data**: Keep secrets separate
   ```yaml
   # ConfigMap for app config
   # Secret for credentials
   ```

4. **Version Configuration**: Track changes in git
   ```bash
   git add k8s/helm-charts/todo-chatbot/values-prod.yaml
   git commit -m "Update production configuration"
   ```

---

## Zero Downtime Deployments

### Overview

Zero downtime deployments ensure the application remains available during updates.

### Requirements for Zero Downtime

1. **Multiple Replicas**: At least 2 replicas
   ```yaml
   replicaCount: 2
   ```

2. **Proper Health Checks**: Liveness and readiness probes
   ```yaml
   livenessProbe:
     httpGet:
       path: /health
       port: 8000
     initialDelaySeconds: 10

   readinessProbe:
     httpGet:
       path: /health
       port: 8000
     initialDelaySeconds: 5
   ```

3. **Rolling Update Strategy**: maxUnavailable: 0
   ```yaml
   strategy:
     type: RollingUpdate
     rollingUpdate:
       maxSurge: 1
       maxUnavailable: 0
   ```

4. **Graceful Shutdown**: Handle SIGTERM properly
   ```yaml
   lifecycle:
     preStop:
       exec:
         command: ["/bin/sh", "-c", "sleep 5"]
   ```

### Testing Zero Downtime

```bash
# Run zero downtime test
./k8s/scripts/test-rolling-update.sh \
  --component backend \
  --tag v1.0.1 \
  --duration 60

# Test monitors requests during update
# Reports success rate and downtime
```

**Expected Output**:
```
Total Requests: 60
Successful Requests: 60
Failed Requests: 0
Success Rate: 100.00%

✓ ZERO DOWNTIME ACHIEVED
All requests succeeded during rolling update
```

### Zero Downtime Best Practices

1. **Always Use Multiple Replicas**: Minimum 2 for production
2. **Configure Health Checks**: Ensure pods are ready before traffic
3. **Set maxUnavailable to 0**: Keep all old pods until new ones ready
4. **Add Graceful Shutdown**: Give pods time to finish requests
5. **Test Regularly**: Verify zero downtime with automated tests

---

## Health Check Management

### Overview

Health checks ensure pods are healthy and ready to serve traffic.

### Types of Health Checks

1. **Liveness Probe**: Detects if pod is alive
   - Restarts pod if check fails
   - Use for detecting deadlocks

2. **Readiness Probe**: Detects if pod is ready for traffic
   - Removes pod from service if check fails
   - Use for startup and temporary issues

3. **Startup Probe**: Detects if application has started
   - Delays liveness/readiness checks
   - Use for slow-starting applications

### Configuring Health Checks

```yaml
# Backend health checks
livenessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 10
  periodSeconds: 10
  timeoutSeconds: 3
  failureThreshold: 3

readinessProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 5
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 3

startupProbe:
  httpGet:
    path: /health
    port: 8000
  initialDelaySeconds: 0
  periodSeconds: 5
  timeoutSeconds: 3
  failureThreshold: 30
```

### Testing Health Checks

```bash
# Test health endpoint manually
kubectl exec -it <pod-name> -- curl http://localhost:8000/health

# Check probe status
kubectl describe pod <pod-name> | grep -A 10 "Liveness\|Readiness"

# View probe failures
kubectl get events --field-selector involvedObject.name=<pod-name>
```

### Health Check Best Practices

1. **Use Appropriate Delays**: Allow time for startup
   ```yaml
   initialDelaySeconds: 10  # Adjust based on startup time
   ```

2. **Set Reasonable Timeouts**: Don't fail too quickly
   ```yaml
   timeoutSeconds: 3
   failureThreshold: 3  # 3 failures before restart
   ```

3. **Implement Health Endpoints**: Return proper status codes
   ```python
   @app.get("/health")
   async def health():
       # Check database connection
       # Check external dependencies
       return {"status": "healthy"}
   ```

4. **Monitor Probe Failures**: Alert on repeated failures
   ```bash
   kubectl get events --watch | grep "Unhealthy"
   ```

---

## Monitoring and Observability

### Metrics

```bash
# Enable metrics-server
minikube addons enable metrics-server

# View resource usage
kubectl top nodes
kubectl top pods -n default

# View specific deployment
kubectl top pods -n default -l app.kubernetes.io/component=backend
```

### Logs

```bash
# View logs
kubectl logs deployment/backend -n default

# Follow logs
kubectl logs -f deployment/backend -n default

# View logs from all replicas
kubectl logs -l app.kubernetes.io/component=backend -n default --all-containers=true

# View previous pod logs (after crash)
kubectl logs <pod-name> -n default --previous
```

### Events

```bash
# View all events
kubectl get events -n default --sort-by='.lastTimestamp'

# Watch events in real-time
kubectl get events -n default --watch

# Filter events by type
kubectl get events -n default --field-selector type=Warning
```

### Monitoring Best Practices

1. **Enable Metrics Server**: Required for HPA and monitoring
2. **Centralize Logs**: Use logging solution (ELK, Loki, etc.)
3. **Set Up Alerts**: Monitor critical metrics
4. **Track Deployment History**: Keep audit trail
5. **Monitor Resource Usage**: Prevent resource exhaustion

---

## Best Practices

### General Best Practices

1. **Always Use Version Tags**: Never use `latest` in production
2. **Test in Dev First**: Validate changes before production
3. **Monitor During Changes**: Watch logs and metrics
4. **Keep Rollback Ready**: Maintain previous versions
5. **Document Changes**: Track what changed and why
6. **Automate Operations**: Use scripts for consistency
7. **Validate Health**: Check health endpoints after changes
8. **Use Gradual Rollouts**: Update one component at a time
9. **Set Resource Limits**: Prevent resource exhaustion
10. **Enable Autoscaling**: Handle variable load automatically

### Deployment Checklist

Before deploying:
- [ ] Code changes tested locally
- [ ] Docker images built and tagged
- [ ] Images loaded to cluster
- [ ] Health checks configured
- [ ] Resource limits set
- [ ] Secrets updated (if needed)
- [ ] Backup/rollback plan ready

During deployment:
- [ ] Monitor pod status
- [ ] Check logs for errors
- [ ] Verify health checks passing
- [ ] Test application endpoints
- [ ] Monitor resource usage

After deployment:
- [ ] Verify all pods running
- [ ] Test application functionality
- [ ] Check metrics and logs
- [ ] Document deployment
- [ ] Update version tracking

---

## Quick Reference

### Common Commands

```bash
# Rolling update
./k8s/scripts/update-deployment.sh --component backend --tag v1.0.1 --wait

# Rollback
./k8s/scripts/rollback-deployment.sh --component backend --wait

# Scale
./k8s/scripts/scale-deployment.sh --component backend --replicas 3 --wait

# Enable autoscaling
./k8s/scripts/scale-deployment.sh --component backend --autoscale --min 2 --max 10

# Test zero downtime
./k8s/scripts/test-rolling-update.sh --component backend --tag v1.0.1

# View status
kubectl get all -n default
kubectl get pods -n default -w
kubectl top pods -n default

# View logs
kubectl logs -f deployment/backend -n default

# View history
kubectl rollout history deployment/backend -n default
helm history todo-chatbot -n default
```

---

## Additional Resources

- **Deployment Guide**: [DEPLOYMENT.md](DEPLOYMENT.md)
- **Troubleshooting Guide**: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **AI Tools Guide**: [AI_TOOLS_GUIDE.md](AI_TOOLS_GUIDE.md)
- **Production Readiness**: [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md)

---

**Last Updated**: 2026-02-08
**Phase**: V - Local Kubernetes Deployment
**Status**: Production Ready
