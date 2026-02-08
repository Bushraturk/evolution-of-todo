# Troubleshooting Guide: Todo Chatbot on Kubernetes

**Feature**: Local Kubernetes Deployment (Phase V)
**Purpose**: Comprehensive troubleshooting guide for common issues and their solutions

## Table of Contents

1. [Quick Diagnostics](#quick-diagnostics)
2. [Pod Issues](#pod-issues)
3. [Image Issues](#image-issues)
4. [Network Issues](#network-issues)
5. [Resource Issues](#resource-issues)
6. [Configuration Issues](#configuration-issues)
7. [Performance Issues](#performance-issues)
8. [Minikube Issues](#minikube-issues)
9. [Helm Issues](#helm-issues)
10. [Common Error Messages](#common-error-messages)

---

## Quick Diagnostics

### First Steps for Any Issue

```bash
# 1. Check pod status
kubectl get pods -n default

# 2. Check events
kubectl get events -n default --sort-by='.lastTimestamp' | tail -20

# 3. Check logs
kubectl logs -l app.kubernetes.io/name=todo-chatbot -n default --tail=50

# 4. Check resource usage
kubectl top pods -n default

# 5. Check deployment status
kubectl get deployments -n default
```

### Quick Health Check

```bash
# Run verification script
./k8s/scripts/verify-deployment.sh

# Check all resources
kubectl get all -n default

# Check secrets
kubectl get secrets -n default
```

---

## Pod Issues

### Issue: Pods Stuck in Pending

**Symptoms**:
```
NAME                        READY   STATUS    RESTARTS   AGE
backend-7d8f9c5b-xk2p9      0/1     Pending   0          2m
```

**Causes**:
1. Insufficient cluster resources
2. Node selector/affinity not matching
3. Persistent volume not available

**Diagnosis**:
```bash
# Check pod events
kubectl describe pod <pod-name> -n default

# Check node resources
kubectl describe nodes

# Check resource requests
kubectl describe deployment backend -n default | grep -A 5 "Requests"
```

**Solutions**:

1. **Increase Minikube resources**:
   ```bash
   minikube stop
   minikube start --memory=8192 --cpus=4
   ```

2. **Reduce resource requests**:
   ```bash
   helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
     --set backend.resources.requests.memory=128Mi \
     --set backend.resources.requests.cpu=50m
   ```

3. **Check node capacity**:
   ```bash
   kubectl top nodes
   kubectl describe nodes | grep -A 5 "Allocated resources"
   ```

---

### Issue: Pods in CrashLoopBackOff

**Symptoms**:
```
NAME                        READY   STATUS             RESTARTS   AGE
backend-7d8f9c5b-xk2p9      0/1     CrashLoopBackOff   5          5m
```

**Causes**:
1. Application error on startup
2. Missing environment variables
3. Database connection failure
4. Health check failing immediately

**Diagnosis**:
```bash
# Check current logs
kubectl logs <pod-name> -n default

# Check previous logs (from crashed container)
kubectl logs <pod-name> -n default --previous

# Check pod events
kubectl describe pod <pod-name> -n default

# Check environment variables
kubectl exec <pod-name> -n default -- env
```

**Solutions**:

1. **Check application logs**:
   ```bash
   kubectl logs <pod-name> -n default --previous | tail -50
   ```

2. **Verify secrets exist**:
   ```bash
   kubectl get secret todo-secrets -n default
   kubectl describe secret todo-secrets -n default
   ```

3. **Test database connection**:
   ```bash
   # Get DATABASE_URL
   kubectl get secret todo-secrets -n default -o jsonpath='{.data.DATABASE_URL}' | base64 -d

   # Test connection from pod
   kubectl exec -it <pod-name> -n default -- python -c "import psycopg2; psycopg2.connect('$DATABASE_URL')"
   ```

4. **Increase health check delays**:
   ```bash
   helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
     --set backend.livenessProbe.initialDelaySeconds=30 \
     --set backend.readinessProbe.initialDelaySeconds=20
   ```

---

### Issue: Pods in ImagePullBackOff

**Symptoms**:
```
NAME                        READY   STATUS             RESTARTS   AGE
backend-7d8f9c5b-xk2p9      0/1     ImagePullBackOff   0          2m
```

**Causes**:
1. Image not loaded to Minikube
2. Image name/tag incorrect
3. Image pull policy issues

**Diagnosis**:
```bash
# Check pod events
kubectl describe pod <pod-name> -n default | grep -A 10 "Events"

# List images in Minikube
minikube image ls | grep todo

# Check deployment image
kubectl get deployment backend -n default -o jsonpath='{.spec.template.spec.containers[0].image}'
```

**Solutions**:

1. **Load images to Minikube**:
   ```bash
   ./k8s/scripts/load-images.sh

   # Or manually
   minikube image load todo-backend:latest
   minikube image load todo-frontend:latest
   ```

2. **Verify image exists locally**:
   ```bash
   docker images | grep todo
   ```

3. **Rebuild and reload images**:
   ```bash
   ./k8s/scripts/build-images.sh
   ./k8s/scripts/load-images.sh
   ```

4. **Set imagePullPolicy to IfNotPresent**:
   ```bash
   helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
     --set backend.image.pullPolicy=IfNotPresent \
     --set frontend.image.pullPolicy=IfNotPresent
   ```

---

### Issue: Pods Restarting Frequently

**Symptoms**:
```
NAME                        READY   STATUS    RESTARTS   AGE
backend-7d8f9c5b-xk2p9      1/1     Running   15         10m
```

**Causes**:
1. Health checks failing
2. Memory limit exceeded (OOMKilled)
3. Application crashes
4. Resource constraints

**Diagnosis**:
```bash
# Check restart reason
kubectl describe pod <pod-name> -n default | grep -A 10 "Last State"

# Check for OOMKilled
kubectl describe pod <pod-name> -n default | grep -i "oom"

# Check resource usage
kubectl top pod <pod-name> -n default

# Check logs for errors
kubectl logs <pod-name> -n default | grep -i "error\|exception\|fatal"
```

**Solutions**:

1. **If OOMKilled, increase memory limit**:
   ```bash
   helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
     --set backend.resources.limits.memory=1Gi
   ```

2. **If health checks failing, adjust timing**:
   ```bash
   helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
     --set backend.livenessProbe.failureThreshold=5 \
     --set backend.livenessProbe.periodSeconds=15
   ```

3. **Check for memory leaks**:
   ```bash
   # Monitor memory usage over time
   watch kubectl top pod <pod-name> -n default
   ```

---

## Image Issues

### Issue: Image Build Fails

**Symptoms**:
```
ERROR: failed to solve: failed to compute cache key
```

**Causes**:
1. Missing files in build context
2. Dockerfile syntax errors
3. Base image not available
4. Network issues

**Diagnosis**:
```bash
# Build with verbose output
docker build --progress=plain -t todo-backend:latest -f k8s/dockerfiles/backend.Dockerfile phase4-chatbot/backend/

# Check Dockerfile syntax
docker build --check -f k8s/dockerfiles/backend.Dockerfile phase4-chatbot/backend/
```

**Solutions**:

1. **Check .dockerignore**:
   ```bash
   cat phase4-chatbot/backend/.dockerignore
   # Ensure required files are not ignored
   ```

2. **Verify build context**:
   ```bash
   ls -la phase4-chatbot/backend/
   # Ensure requirements.txt, main.py, etc. exist
   ```

3. **Pull base image manually**:
   ```bash
   docker pull python:3.13-slim
   docker pull node:20-alpine
   ```

4. **Use build script**:
   ```bash
   ./k8s/scripts/build-images.sh
   ```

---

### Issue: Image Too Large

**Symptoms**:
```
todo-backend:latest   850MB
```

**Causes**:
1. Not using multi-stage builds
2. Including unnecessary files
3. Not cleaning up build artifacts
4. Using large base images

**Diagnosis**:
```bash
# Analyze image layers
docker history todo-backend:latest --human

# Use dive for detailed analysis
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive:latest todo-backend:latest
```

**Solutions**:

1. **Use slim base images**:
   ```dockerfile
   FROM python:3.13-slim  # Instead of python:3.13
   FROM node:20-alpine    # Instead of node:20
   ```

2. **Add .dockerignore**:
   ```bash
   # Backend
   echo "__pycache__" >> phase4-chatbot/backend/.dockerignore
   echo "*.pyc" >> phase4-chatbot/backend/.dockerignore
   echo ".pytest_cache" >> phase4-chatbot/backend/.dockerignore

   # Frontend
   echo "node_modules" >> phase4-chatbot/frontend/.dockerignore
   echo ".next" >> phase4-chatbot/frontend/.dockerignore
   ```

3. **Use multi-stage builds**:
   - See `k8s/dockerfiles/backend.Dockerfile` for example
   - Separate builder and runtime stages

4. **Review optimization guide**:
   ```bash
   cat k8s/docs/IMAGE_OPTIMIZATION.md
   ```

---

## Network Issues

### Issue: Cannot Access Application

**Symptoms**:
- Browser shows "Connection refused"
- `curl` fails to connect

**Causes**:
1. Service not exposed
2. Minikube tunnel not running
3. Wrong port or IP
4. Firewall blocking connection

**Diagnosis**:
```bash
# Check service status
kubectl get services -n default

# Check service type
kubectl get service frontend -n default -o jsonpath='{.spec.type}'

# Check endpoints
kubectl get endpoints frontend -n default

# Check if pods are ready
kubectl get pods -n default -l app.kubernetes.io/component=frontend
```

**Solutions**:

1. **Start Minikube tunnel** (for LoadBalancer):
   ```bash
   # In separate terminal
   minikube tunnel
   ```

2. **Use NodePort**:
   ```bash
   export NODE_PORT=$(kubectl get service frontend -n default -o jsonpath='{.spec.ports[0].nodePort}')
   export MINIKUBE_IP=$(minikube ip)
   echo "http://${MINIKUBE_IP}:${NODE_PORT}"
   ```

3. **Use port forwarding**:
   ```bash
   kubectl port-forward service/frontend 3000:80 -n default
   # Access at http://localhost:3000
   ```

4. **Run access script**:
   ```bash
   ./k8s/scripts/access-application.sh
   ```

---

### Issue: Frontend Cannot Reach Backend

**Symptoms**:
- Frontend loads but API calls fail
- 502 Bad Gateway errors
- Connection timeout errors

**Causes**:
1. Backend service not running
2. Wrong backend URL in frontend
3. Network policy blocking traffic
4. Backend pods not ready

**Diagnosis**:
```bash
# Check backend service
kubectl get service backend -n default

# Check backend pods
kubectl get pods -n default -l app.kubernetes.io/component=backend

# Test connectivity from frontend pod
FRONTEND_POD=$(kubectl get pods -n default -l app.kubernetes.io/component=frontend -o jsonpath='{.items[0].metadata.name}')
kubectl exec -it $FRONTEND_POD -n default -- curl http://backend:8000/health

# Check frontend environment variables
kubectl exec -it $FRONTEND_POD -n default -- env | grep API
```

**Solutions**:

1. **Verify backend is running**:
   ```bash
   kubectl get pods -n default -l app.kubernetes.io/component=backend
   kubectl logs -l app.kubernetes.io/component=backend -n default
   ```

2. **Check backend service**:
   ```bash
   kubectl get service backend -n default
   kubectl describe service backend -n default
   ```

3. **Verify frontend configuration**:
   ```bash
   # Should be http://backend:8000 for internal communication
   kubectl get deployment frontend -n default -o jsonpath='{.spec.template.spec.containers[0].env[?(@.name=="NEXT_PUBLIC_API_URL")].value}'
   ```

4. **Test backend health**:
   ```bash
   kubectl exec -it <frontend-pod> -n default -- curl -v http://backend:8000/health
   ```

---

## Resource Issues

### Issue: Out of Memory (OOMKilled)

**Symptoms**:
```
Last State:     Terminated
  Reason:       OOMKilled
  Exit Code:    137
```

**Causes**:
1. Memory limit too low
2. Memory leak in application
3. Unexpected memory usage spike

**Diagnosis**:
```bash
# Check memory limit
kubectl describe pod <pod-name> -n default | grep -A 5 "Limits"

# Check memory usage
kubectl top pod <pod-name> -n default

# Check for memory leak
watch kubectl top pod <pod-name> -n default
```

**Solutions**:

1. **Increase memory limit**:
   ```bash
   helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
     --set backend.resources.limits.memory=1Gi
   ```

2. **Increase memory request**:
   ```bash
   helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
     --set backend.resources.requests.memory=512Mi
   ```

3. **Investigate memory leak**:
   ```bash
   # Check application logs for memory issues
   kubectl logs <pod-name> -n default | grep -i "memory\|heap"
   ```

---

### Issue: CPU Throttling

**Symptoms**:
- Slow response times
- High CPU usage
- Requests timing out

**Causes**:
1. CPU limit too low
2. Inefficient code
3. High traffic load

**Diagnosis**:
```bash
# Check CPU usage
kubectl top pod <pod-name> -n default

# Check CPU limit
kubectl describe pod <pod-name> -n default | grep -A 5 "Limits"

# Check for throttling
kubectl describe pod <pod-name> -n default | grep -i "throttl"
```

**Solutions**:

1. **Increase CPU limit**:
   ```bash
   helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
     --set backend.resources.limits.cpu=1000m
   ```

2. **Scale horizontally**:
   ```bash
   ./k8s/scripts/scale-deployment.sh --component backend --replicas 3
   ```

3. **Enable autoscaling**:
   ```bash
   ./k8s/scripts/scale-deployment.sh --component backend --autoscale --min 2 --max 10 --cpu 70
   ```

---

## Configuration Issues

### Issue: Missing Environment Variables

**Symptoms**:
- Application fails to start
- Errors about missing configuration
- Database connection fails

**Causes**:
1. Secrets not created
2. Environment variables not configured
3. Wrong secret name

**Diagnosis**:
```bash
# Check if secrets exist
kubectl get secrets -n default

# Check secret contents (keys only)
kubectl describe secret todo-secrets -n default

# Check pod environment variables
kubectl exec <pod-name> -n default -- env
```

**Solutions**:

1. **Create secrets**:
   ```bash
   ./k8s/scripts/create-secrets.sh

   # Or manually
   kubectl create secret generic todo-secrets \
     --from-literal=DATABASE_URL="postgresql://..." \
     --from-literal=GROQ_API_KEY="gsk_..." \
     --from-literal=JWT_SECRET="..." \
     -n default
   ```

2. **Verify secret values**:
   ```bash
   kubectl get secret todo-secrets -n default -o jsonpath='{.data.DATABASE_URL}' | base64 -d
   ```

3. **Restart pods to pick up new secrets**:
   ```bash
   kubectl rollout restart deployment/backend -n default
   ```

---

### Issue: Wrong Configuration Values

**Symptoms**:
- Application behaves incorrectly
- Features not working as expected
- Wrong API endpoints

**Causes**:
1. Wrong Helm values
2. Environment-specific configuration not applied
3. ConfigMap not updated

**Diagnosis**:
```bash
# Check current Helm values
helm get values todo-chatbot -n default

# Check deployment environment variables
kubectl describe deployment backend -n default | grep -A 20 "Environment"

# Check ConfigMap
kubectl get configmap -n default
kubectl describe configmap <configmap-name> -n default
```

**Solutions**:

1. **Update Helm values**:
   ```bash
   helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
     -f k8s/helm-charts/todo-chatbot/values-dev.yaml \
     --set backend.env.LOG_LEVEL=DEBUG
   ```

2. **Update ConfigMap**:
   ```bash
   kubectl create configmap app-config \
     --from-file=config.yaml \
     --dry-run=client -o yaml | kubectl apply -f -

   # Restart pods
   kubectl rollout restart deployment/backend -n default
   ```

---

## Performance Issues

### Issue: Slow Response Times

**Symptoms**:
- API requests take > 1 second
- Frontend loads slowly
- Timeouts

**Causes**:
1. Database queries slow
2. Insufficient resources
3. Network latency
4. No caching

**Diagnosis**:
```bash
# Check resource usage
kubectl top pods -n default

# Check logs for slow queries
kubectl logs -l app.kubernetes.io/component=backend -n default | grep -i "slow\|timeout"

# Test response time
time curl http://<service-url>/health

# Check pod events
kubectl get events -n default --sort-by='.lastTimestamp'
```

**Solutions**:

1. **Increase resources**:
   ```bash
   helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
     --set backend.resources.requests.cpu=200m \
     --set backend.resources.requests.memory=512Mi
   ```

2. **Scale horizontally**:
   ```bash
   ./k8s/scripts/scale-deployment.sh --component backend --replicas 3
   ```

3. **Check database performance**:
   - Add indexes
   - Optimize queries
   - Enable connection pooling

4. **Enable caching**:
   - Add Redis for caching
   - Cache frequent queries
   - Cache API responses

---

## Minikube Issues

### Issue: Minikube Won't Start

**Symptoms**:
```
Error: Failed to start minikube
```

**Causes**:
1. Docker not running
2. Insufficient system resources
3. Corrupted Minikube state
4. Port conflicts

**Diagnosis**:
```bash
# Check Docker status
docker ps

# Check Minikube status
minikube status

# Check Minikube logs
minikube logs
```

**Solutions**:

1. **Start Docker Desktop**:
   - Ensure Docker Desktop is running
   - Check Docker settings for sufficient resources

2. **Delete and recreate Minikube**:
   ```bash
   minikube delete
   minikube start --memory=4096 --cpus=2
   ```

3. **Increase resources**:
   ```bash
   minikube start --memory=8192 --cpus=4
   ```

4. **Use different driver**:
   ```bash
   minikube start --driver=virtualbox
   # or
   minikube start --driver=hyperkit
   ```

---

### Issue: Minikube Tunnel Requires Password

**Symptoms**:
- Minikube tunnel prompts for password repeatedly
- Cannot access LoadBalancer services

**Causes**:
- Minikube tunnel requires elevated privileges
- Password caching not working

**Solutions**:

1. **Use NodePort instead**:
   ```bash
   export NODE_PORT=$(kubectl get service frontend -n default -o jsonpath='{.spec.ports[0].nodePort}')
   export MINIKUBE_IP=$(minikube ip)
   echo "http://${MINIKUBE_IP}:${NODE_PORT}"
   ```

2. **Use port forwarding**:
   ```bash
   kubectl port-forward service/frontend 3000:80 -n default
   ```

3. **Configure passwordless sudo** (macOS/Linux):
   ```bash
   # Add to /etc/sudoers (use visudo)
   %admin ALL=(ALL) NOPASSWD: /usr/local/bin/minikube tunnel
   ```

---

## Helm Issues

### Issue: Helm Install/Upgrade Fails

**Symptoms**:
```
Error: UPGRADE FAILED: failed to create resource
```

**Causes**:
1. Invalid Helm chart
2. Missing required values
3. Resource conflicts
4. Insufficient permissions

**Diagnosis**:
```bash
# Validate chart
helm lint k8s/helm-charts/todo-chatbot/

# Dry-run install
helm install todo-chatbot k8s/helm-charts/todo-chatbot/ --dry-run --debug

# Check Helm history
helm history todo-chatbot -n default

# Check Helm status
helm status todo-chatbot -n default
```

**Solutions**:

1. **Validate chart**:
   ```bash
   ./k8s/scripts/validate-chart.sh
   ```

2. **Uninstall and reinstall**:
   ```bash
   helm uninstall todo-chatbot -n default
   helm install todo-chatbot k8s/helm-charts/todo-chatbot/ -n default
   ```

3. **Check for resource conflicts**:
   ```bash
   kubectl get all -n default
   # Delete conflicting resources
   kubectl delete deployment <name> -n default
   ```

---

## Common Error Messages

### "Error: ImagePullBackOff"

**Solution**: Load images to Minikube
```bash
./k8s/scripts/load-images.sh
```

### "Error: CrashLoopBackOff"

**Solution**: Check logs and fix application error
```bash
kubectl logs <pod-name> -n default --previous
```

### "Error: Pending"

**Solution**: Increase Minikube resources
```bash
minikube stop
minikube start --memory=8192 --cpus=4
```

### "Error: OOMKilled"

**Solution**: Increase memory limit
```bash
helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
  --set backend.resources.limits.memory=1Gi
```

### "Error: Connection refused"

**Solution**: Start Minikube tunnel or use port forwarding
```bash
minikube tunnel
# or
kubectl port-forward service/frontend 3000:80
```

### "Error: Unhealthy"

**Solution**: Adjust health check timing
```bash
helm upgrade todo-chatbot k8s/helm-charts/todo-chatbot/ \
  --set backend.livenessProbe.initialDelaySeconds=30
```

---

## Getting Help

### Self-Service Resources

1. **Run verification script**:
   ```bash
   ./k8s/scripts/verify-deployment.sh
   ```

2. **Check documentation**:
   - [DEPLOYMENT.md](DEPLOYMENT.md)
   - [LIFECYCLE_MANAGEMENT.md](LIFECYCLE_MANAGEMENT.md)
   - [PRODUCTION_READINESS.md](PRODUCTION_READINESS.md)

3. **Use AI tools**:
   - kubectl-ai: `kubectl ai "why is my pod crashing?"`
   - Kagent: `kagent analyze --namespace default`

### Community Resources

- **Kubernetes Documentation**: https://kubernetes.io/docs/
- **Minikube Documentation**: https://minikube.sigs.k8s.io/docs/
- **Helm Documentation**: https://helm.sh/docs/
- **Stack Overflow**: Tag questions with `kubernetes`, `minikube`, `helm`

---

**Last Updated**: 2026-02-08
**Phase**: V - Local Kubernetes Deployment
**Status**: Production Ready
