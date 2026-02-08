# Docker Image Optimization Guide

**Feature**: Local Kubernetes Deployment
**Purpose**: Guidelines for optimizing Docker images for size, security, and performance

## Overview

This guide provides best practices for optimizing Docker images for the Todo Chatbot application. Our target sizes are:
- **Backend**: <500MB
- **Frontend**: <200MB

## Multi-Stage Builds

### Why Multi-Stage Builds?

Multi-stage builds separate the build environment from the runtime environment, significantly reducing final image size.

**Benefits**:
- Smaller images (faster deployment, less storage)
- Improved security (fewer packages = smaller attack surface)
- Better layer caching (faster rebuilds)

### Backend Example

```dockerfile
# Stage 1: Builder (includes build tools)
FROM python:3.13-slim AS builder
WORKDIR /app
RUN apt-get update && apt-get install -y gcc
COPY requirements.txt .
RUN pip install --user --no-cache-dir -r requirements.txt

# Stage 2: Runtime (only runtime dependencies)
FROM python:3.13-slim
WORKDIR /app
RUN useradd -m -u 1000 appuser
COPY --from=builder /root/.local /home/appuser/.local
COPY --chown=appuser:appuser src/ ./src/
USER appuser
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Size Reduction**: ~1GB → ~450MB (55% reduction)

### Frontend Example

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
ENV NODE_ENV=production
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static
USER nextjs
CMD ["node", "server.js"]
```

**Size Reduction**: ~1.2GB → ~180MB (85% reduction)

---

## Base Image Selection

### Python Backend

**Options**:
| Image | Size | Pros | Cons |
|-------|------|------|------|
| `python:3.13` | ~1GB | Full packages | Too large |
| `python:3.13-slim` | ~150MB | Balanced | **Recommended** |
| `python:3.13-alpine` | ~50MB | Smallest | musl libc compatibility issues |

**Recommendation**: Use `python:3.13-slim`
- Includes necessary system libraries
- Compatible with most Python packages
- Good balance of size and functionality

### Node.js Frontend

**Options**:
| Image | Size | Pros | Cons |
|-------|------|------|------|
| `node:20` | ~1GB | Full packages | Too large |
| `node:20-slim` | ~200MB | Balanced | Larger than alpine |
| `node:20-alpine` | ~50MB | Smallest | **Recommended** |

**Recommendation**: Use `node:20-alpine`
- Minimal size (~50MB base)
- Sufficient for Next.js runtime
- No compatibility issues with Node.js

---

## Layer Caching Optimization

### Copy Order Matters

**Bad** (cache invalidated on any code change):
```dockerfile
COPY . .
RUN pip install -r requirements.txt
```

**Good** (dependencies cached separately):
```dockerfile
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
```

### Why This Works

Docker caches each layer. When you change application code:
- **Bad approach**: Reinstalls all dependencies (slow)
- **Good approach**: Reuses cached dependencies (fast)

**Build Time Improvement**: 5 minutes → 30 seconds for code-only changes

---

## Dependency Management

### Python Backend

**Use `--no-cache-dir`**:
```dockerfile
RUN pip install --no-cache-dir -r requirements.txt
```
- Prevents pip from caching downloaded packages
- Saves ~100MB

**Use `--user` flag**:
```dockerfile
RUN pip install --user --no-cache-dir -r requirements.txt
```
- Installs to user directory (easier to copy in multi-stage)
- Better security (no root permissions needed)

### Node.js Frontend

**Use `npm ci` instead of `npm install`**:
```dockerfile
RUN npm ci --only=production
```
- Faster (uses package-lock.json)
- More reliable (exact versions)
- Cleaner (removes node_modules first)

**Use Next.js Standalone Output**:
```javascript
// next.config.js
module.exports = {
  output: 'standalone',
}
```
- Includes only necessary files
- Excludes node_modules (reduces size by ~300MB)

---

## Security Optimization

### Non-Root Users

**Always run as non-root**:

**Backend**:
```dockerfile
RUN useradd -m -u 1000 appuser
USER appuser
```

**Frontend**:
```dockerfile
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs
USER nextjs
```

**Benefits**:
- Principle of least privilege
- Prevents container breakout attacks
- Required by Kubernetes security policies

### Drop Capabilities

In Kubernetes deployment:
```yaml
securityContext:
  runAsNonRoot: true
  runAsUser: 1000
  capabilities:
    drop:
      - ALL
```

---

## .dockerignore Files

### Backend .dockerignore

```
__pycache__/
*.pyc
.venv/
venv/
.env
*.log
tests/
.git/
.vscode/
.idea/
```

**Size Reduction**: ~50MB (excludes unnecessary files)

### Frontend .dockerignore

```
node_modules/
.next/
.env.local
*.log
.git/
.vscode/
.idea/
coverage/
```

**Size Reduction**: ~200MB (excludes node_modules and build artifacts)

---

## Health Checks

### Backend Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1
```

### Frontend Health Check

```dockerfile
HEALTHCHECK --interval=30s --timeout=3s --start-period=10s --retries=3 \
    CMD node -e "require('http').get('http://localhost:3000/api/health', (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})" || exit 1
```

**Benefits**:
- Docker can detect unhealthy containers
- Kubernetes uses for liveness probes
- Automatic restart of failed containers

---

## Build Performance

### Parallel Builds

Build both images simultaneously:
```bash
docker build -t todo-backend:latest -f k8s/dockerfiles/backend.Dockerfile phase4-chatbot/backend/ &
docker build -t todo-frontend:latest -f k8s/dockerfiles/frontend.Dockerfile phase4-chatbot/frontend/ &
wait
```

**Time Reduction**: 10 minutes → 5 minutes

### BuildKit

Enable Docker BuildKit for faster builds:
```bash
export DOCKER_BUILDKIT=1
docker build ...
```

**Benefits**:
- Parallel layer building
- Better caching
- Faster dependency resolution

---

## Size Verification

### Check Image Sizes

```bash
docker images | grep todo
```

Expected output:
```
todo-backend   latest   abc123   2 minutes ago   450MB
todo-frontend  latest   def456   1 minute ago    180MB
```

### Analyze Image Layers

```bash
docker history todo-backend:latest
```

Identify large layers and optimize them.

### Use dive Tool

```bash
# Install dive
brew install dive  # macOS
# or download from https://github.com/wagoodman/dive

# Analyze image
dive todo-backend:latest
```

**Benefits**:
- Visual layer analysis
- Identify wasted space
- Optimize layer efficiency

---

## Optimization Checklist

### Backend

- [x] Use `python:3.13-slim` base image
- [x] Multi-stage build (builder + runtime)
- [x] Copy requirements.txt before source code
- [x] Use `--no-cache-dir` with pip
- [x] Create non-root user (appuser)
- [x] Add health check
- [x] Use .dockerignore file
- [x] Target size: <500MB

### Frontend

- [x] Use `node:20-alpine` base image
- [x] Multi-stage build (deps + builder + runner)
- [x] Copy package files before source code
- [x] Use `npm ci --only=production`
- [x] Enable Next.js standalone output
- [x] Create non-root user (nextjs)
- [x] Add health check
- [x] Use .dockerignore file
- [x] Target size: <200MB

---

## Common Issues and Solutions

### Issue: Image Too Large

**Diagnosis**:
```bash
docker history todo-backend:latest --no-trunc
```

**Solutions**:
1. Use smaller base image (slim or alpine)
2. Remove unnecessary packages
3. Use multi-stage builds
4. Add .dockerignore file
5. Use `--no-cache-dir` with pip

### Issue: Slow Builds

**Diagnosis**: Check layer caching

**Solutions**:
1. Copy dependency files before source code
2. Enable BuildKit
3. Use parallel builds
4. Optimize layer order

### Issue: Security Vulnerabilities

**Diagnosis**:
```bash
docker scan todo-backend:latest
```

**Solutions**:
1. Use official base images
2. Keep base images updated
3. Run as non-root user
4. Drop unnecessary capabilities
5. Use minimal base images (slim/alpine)

---

## Best Practices Summary

1. **Use multi-stage builds** - Separate build and runtime
2. **Choose minimal base images** - slim or alpine variants
3. **Optimize layer caching** - Copy dependencies before code
4. **Run as non-root** - Create dedicated users
5. **Add health checks** - Enable automatic recovery
6. **Use .dockerignore** - Exclude unnecessary files
7. **Verify sizes** - Check against targets (<500MB, <200MB)
8. **Scan for vulnerabilities** - Use docker scan regularly

---

## Resources

- [Docker Best Practices](https://docs.docker.com/develop/dev-best-practices/)
- [Multi-Stage Builds](https://docs.docker.com/build/building/multi-stage/)
- [Dockerfile Reference](https://docs.docker.com/engine/reference/builder/)
- [dive - Image Analysis Tool](https://github.com/wagoodman/dive)
- [Docker BuildKit](https://docs.docker.com/build/buildkit/)

---

**Last Updated**: 2026-02-08
**Maintained By**: DevOps Team
