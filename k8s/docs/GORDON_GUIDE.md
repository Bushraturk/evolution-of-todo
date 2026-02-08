# Gordon Guide: Docker AI Assistant

**Feature**: AI-Assisted Docker Operations (Phase V)
**Purpose**: Leverage Docker's built-in AI assistant for Dockerfile generation and optimization

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Getting Started](#getting-started)
4. [Common Use Cases](#common-use-cases)
5. [Dockerfile Generation](#dockerfile-generation)
6. [Dockerfile Optimization](#dockerfile-optimization)
7. [Image Analysis](#image-analysis)
8. [Best Practices](#best-practices)
9. [Fallback Commands](#fallback-commands)

---

## Overview

**Gordon** is Docker's AI assistant, integrated into Docker Desktop 4.53+ Beta. It provides natural language interaction for Docker operations, making it easier to:

- Generate Dockerfiles from descriptions
- Optimize existing Dockerfiles
- Analyze image sizes and layers
- Get recommendations for security and performance
- Troubleshoot Docker issues

**Key Benefits**:
- Faster Dockerfile creation
- Best practices automatically applied
- Interactive optimization suggestions
- Context-aware recommendations

---

## Prerequisites

### Required Software

| Software | Version | Installation |
|----------|---------|--------------|
| Docker Desktop | 4.53+ Beta | https://www.docker.com/products/docker-desktop |

### Enable Gordon

1. Open Docker Desktop
2. Go to **Settings** → **Features in development**
3. Enable **Docker AI (Gordon)**
4. Restart Docker Desktop

### Verify Installation

```bash
# Check Docker Desktop version
docker version

# Gordon is accessed through Docker Desktop UI
# Look for the AI assistant icon in the Docker Desktop interface
```

---

## Getting Started

### Accessing Gordon

Gordon is available through:

1. **Docker Desktop UI**: Click the AI assistant icon (💬) in the toolbar
2. **Command Palette**: Press `Cmd+K` (macOS) or `Ctrl+K` (Windows/Linux)
3. **Context Menu**: Right-click on containers, images, or files

### Basic Interaction

Gordon uses natural language. Simply describe what you want:

```
"Create a Dockerfile for a Python FastAPI application"
"Optimize this Dockerfile for production"
"Why is my image so large?"
"How can I reduce build time?"
```

---

## Common Use Cases

### 1. Generate Dockerfile from Scratch

**Prompt**:
```
Create a Dockerfile for a Python 3.13 FastAPI application with:
- Multi-stage build
- Non-root user
- Health check on port 8000
- Optimized for production
```

**Gordon Output** (example):
```dockerfile
# Builder stage
FROM python:3.13-slim AS builder
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# Runtime stage
FROM python:3.13-slim
WORKDIR /app
COPY --from=builder /root/.local /root/.local
COPY . .
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser
ENV PATH=/root/.local/bin:$PATH
EXPOSE 8000
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:8000/health || exit 1
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Fallback** (manual):
```bash
# Use our existing backend Dockerfile as template
cat k8s/dockerfiles/backend.Dockerfile
```

---

### 2. Optimize Existing Dockerfile

**Prompt**:
```
Optimize this Dockerfile for smaller image size and faster builds:
[paste your Dockerfile]
```

**Gordon Suggestions** (example):
- Use alpine base images
- Combine RUN commands to reduce layers
- Add .dockerignore file
- Use multi-stage builds
- Remove unnecessary dependencies
- Use --no-cache-dir for pip

**Fallback** (manual):
```bash
# Analyze image layers
docker history todo-backend:latest

# Check image size
docker images todo-backend:latest

# See our optimization guide
cat k8s/docs/IMAGE_OPTIMIZATION.md
```

---

### 3. Analyze Image Size

**Prompt**:
```
Why is my todo-backend:latest image 800MB? How can I reduce it?
```

**Gordon Analysis** (example):
- Identifies large layers
- Suggests base image alternatives
- Recommends removing build tools from runtime
- Points out cached files

**Fallback** (manual):
```bash
# Analyze image layers and sizes
docker history todo-backend:latest --human --no-trunc

# Use dive for detailed analysis
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive:latest todo-backend:latest
```

---

## Dockerfile Generation

### Backend Application (Python FastAPI)

**Prompt**:
```
Generate a production-ready Dockerfile for:
- Python 3.13 FastAPI application
- Dependencies in requirements.txt
- Run on port 8000
- Non-root user
- Multi-stage build
- Target size under 500MB
```

**Expected Features**:
- Builder stage with gcc for compiled dependencies
- Runtime stage with minimal dependencies
- Security best practices (non-root, dropped capabilities)
- Health check configuration
- Proper layer caching

**Fallback**:
```bash
# Use our template
cp k8s/dockerfiles/backend.Dockerfile my-backend.Dockerfile
```

---

### Frontend Application (Next.js)

**Prompt**:
```
Generate a production-ready Dockerfile for:
- Next.js 14 application
- Node 20 Alpine base
- Standalone output
- Run on port 3000
- Non-root user
- Target size under 200MB
```

**Expected Features**:
- Three-stage build (deps, builder, runner)
- Next.js standalone output for minimal size
- Alpine base for small footprint
- Security best practices

**Fallback**:
```bash
# Use our template
cp k8s/dockerfiles/frontend.Dockerfile my-frontend.Dockerfile
```

---

## Dockerfile Optimization

### Size Optimization

**Prompt**:
```
My Docker image is 1.2GB. Help me reduce it to under 500MB.
Current Dockerfile:
[paste Dockerfile]
```

**Gordon Recommendations**:
1. **Base Image**: Switch from `python:3.13` to `python:3.13-slim` (-400MB)
2. **Multi-stage**: Separate build and runtime stages (-200MB)
3. **.dockerignore**: Exclude unnecessary files (-50MB)
4. **Dependencies**: Remove build tools from runtime (-100MB)
5. **Layer Optimization**: Combine RUN commands (-50MB)

**Fallback**:
```bash
# Compare base image sizes
docker images | grep python

# Analyze what's in your image
docker run --rm -it todo-backend:latest du -sh /*
```

---

### Build Time Optimization

**Prompt**:
```
My Docker build takes 10 minutes. How can I speed it up?
```

**Gordon Recommendations**:
1. **Layer Caching**: Order commands from least to most frequently changed
2. **BuildKit**: Enable Docker BuildKit for parallel builds
3. **Dependencies**: Copy requirements.txt before source code
4. **.dockerignore**: Exclude large directories (node_modules, .git)
5. **Multi-stage**: Build dependencies once, reuse across stages

**Fallback**:
```bash
# Enable BuildKit for faster builds
export DOCKER_BUILDKIT=1

# Build with cache
docker build --cache-from todo-backend:latest -t todo-backend:latest .

# Build with progress output
docker build --progress=plain -t todo-backend:latest .
```

---

### Security Optimization

**Prompt**:
```
Make this Dockerfile more secure for production deployment.
```

**Gordon Recommendations**:
1. **Non-root User**: Create and use non-root user
2. **Capabilities**: Drop unnecessary Linux capabilities
3. **Read-only**: Use read-only root filesystem where possible
4. **Secrets**: Never include secrets in image layers
5. **Scanning**: Scan for vulnerabilities

**Fallback**:
```bash
# Scan image for vulnerabilities
docker scan todo-backend:latest

# Check for secrets in image
docker history todo-backend:latest --no-trunc | grep -i "secret\|password\|key"

# Run container with security options
docker run --rm \
  --read-only \
  --cap-drop=ALL \
  --security-opt=no-new-privileges \
  todo-backend:latest
```

---

## Image Analysis

### Layer Analysis

**Prompt**:
```
Show me what's in each layer of my todo-backend:latest image.
```

**Gordon Output**:
- Layer-by-layer breakdown
- Size contribution of each layer
- Commands that created each layer
- Recommendations for optimization

**Fallback**:
```bash
# Show layer history
docker history todo-backend:latest --human

# Detailed layer analysis with dive
docker run --rm -it \
  -v /var/run/docker.sock:/var/run/docker.sock \
  wagoodman/dive:latest todo-backend:latest
```

---

### Dependency Analysis

**Prompt**:
```
What dependencies are installed in my image and how much space do they take?
```

**Gordon Analysis**:
- Lists installed packages
- Shows size of each package
- Identifies unused dependencies
- Suggests removals

**Fallback**:
```bash
# List installed packages (Debian/Ubuntu)
docker run --rm todo-backend:latest dpkg -l

# Check package sizes
docker run --rm todo-backend:latest \
  dpkg-query -Wf '${Installed-Size}\t${Package}\n' | sort -n

# List Python packages
docker run --rm todo-backend:latest pip list
```

---

## Best Practices

### 1. Iterative Optimization

Start with Gordon's generated Dockerfile, then iteratively optimize:

```
1. "Generate a Dockerfile for [description]"
2. Build and test
3. "Optimize this Dockerfile for size"
4. Build and compare
5. "Make this Dockerfile more secure"
6. Final build and validation
```

### 2. Context-Aware Prompts

Provide context for better results:

**Good Prompt**:
```
Create a Dockerfile for a Python FastAPI app that:
- Connects to PostgreSQL database
- Uses Groq API for LLM
- Runs on port 8000
- Needs psycopg2 (requires gcc to build)
- Target production deployment on Kubernetes
```

**Poor Prompt**:
```
Make a Python Dockerfile
```

### 3. Validate Gordon's Output

Always validate generated Dockerfiles:

```bash
# Build the image
docker build -t test:latest -f Dockerfile.gordon .

# Test the container
docker run --rm -p 8000:8000 test:latest

# Check image size
docker images test:latest

# Scan for vulnerabilities
docker scan test:latest
```

### 4. Combine with Manual Expertise

Use Gordon for:
- Initial Dockerfile generation
- Optimization suggestions
- Best practices recommendations

Use manual commands for:
- Fine-tuning specific configurations
- Project-specific requirements
- Advanced optimization techniques

---

## Fallback Commands

When Gordon is unavailable, use these standard Docker commands:

### Build Images

```bash
# Build with tag
docker build -t todo-backend:latest -f k8s/dockerfiles/backend.Dockerfile phase4-chatbot/backend/

# Build with BuildKit (faster)
DOCKER_BUILDKIT=1 docker build -t todo-backend:latest -f k8s/dockerfiles/backend.Dockerfile phase4-chatbot/backend/

# Build with no cache
docker build --no-cache -t todo-backend:latest -f k8s/dockerfiles/backend.Dockerfile phase4-chatbot/backend/
```

### Analyze Images

```bash
# Show image history
docker history todo-backend:latest --human --no-trunc

# Inspect image
docker inspect todo-backend:latest

# Check image size
docker images todo-backend:latest

# Use dive for detailed analysis
docker run --rm -it -v /var/run/docker.sock:/var/run/docker.sock wagoodman/dive:latest todo-backend:latest
```

### Test Images

```bash
# Run container
docker run --rm -p 8000:8000 todo-backend:latest

# Run with environment variables
docker run --rm -p 8000:8000 -e DATABASE_URL="postgresql://..." todo-backend:latest

# Run interactively
docker run --rm -it todo-backend:latest /bin/bash

# Check health
docker run --rm todo-backend:latest curl -f http://localhost:8000/health
```

### Optimize Images

```bash
# Use slim base images
FROM python:3.13-slim

# Use alpine for smaller size
FROM node:20-alpine

# Multi-stage build
FROM python:3.13-slim AS builder
# ... build stage
FROM python:3.13-slim AS runtime
# ... runtime stage

# Combine RUN commands
RUN apt-get update && \
    apt-get install -y --no-install-recommends gcc && \
    pip install --no-cache-dir -r requirements.txt && \
    apt-get purge -y gcc && \
    apt-get autoremove -y && \
    rm -rf /var/lib/apt/lists/*
```

---

## Comparison: Gordon vs Manual

| Task | Gordon | Manual | Winner |
|------|--------|--------|--------|
| Generate Dockerfile | 30 seconds | 15 minutes | Gordon |
| Optimize for size | 1 minute | 30 minutes | Gordon |
| Security hardening | 2 minutes | 20 minutes | Gordon |
| Custom requirements | 5 minutes | 10 minutes | Manual |
| Fine-tuning | 10 minutes | 5 minutes | Manual |
| Learning | High | Medium | Gordon |

**Recommendation**: Use Gordon for initial generation and optimization, then fine-tune manually for project-specific needs.

---

## Troubleshooting

### Gordon Not Available

**Issue**: Gordon icon not showing in Docker Desktop

**Solution**:
1. Update to Docker Desktop 4.53+ Beta
2. Enable in Settings → Features in development
3. Restart Docker Desktop
4. Check Docker Desktop logs for errors

### Generated Dockerfile Fails to Build

**Issue**: Gordon's Dockerfile has build errors

**Solution**:
1. Copy error message
2. Ask Gordon: "Fix this build error: [paste error]"
3. Or manually debug with `docker build --progress=plain`
4. Use our templates as fallback

### Image Size Still Too Large

**Issue**: Optimized image still exceeds target size

**Solution**:
1. Ask Gordon: "My image is still [size]. What else can I remove?"
2. Use dive to analyze layers: `dive todo-backend:latest`
3. Check our IMAGE_OPTIMIZATION.md guide
4. Consider different base image (alpine, distroless)

---

## Additional Resources

- **Docker AI Documentation**: https://docs.docker.com/desktop/features/ai/
- **Dockerfile Best Practices**: https://docs.docker.com/develop/dev-best-practices/
- **Image Optimization Guide**: [IMAGE_OPTIMIZATION.md](IMAGE_OPTIMIZATION.md)
- **Multi-stage Builds**: https://docs.docker.com/build/building/multi-stage/

---

## Examples from Todo Chatbot

### Backend Dockerfile (Generated with Gordon)

See: `k8s/dockerfiles/backend.Dockerfile`

**Features**:
- Multi-stage build (builder + runtime)
- Python 3.13-slim base
- Non-root user (appuser, uid 1000)
- Health check on /health endpoint
- Size: ~450MB (under 500MB target)

### Frontend Dockerfile (Generated with Gordon)

See: `k8s/dockerfiles/frontend.Dockerfile`

**Features**:
- Three-stage build (deps + builder + runner)
- Node 20-alpine base
- Next.js standalone output
- Non-root user (nextjs, uid 1001)
- Size: ~180MB (under 200MB target)

---

**Last Updated**: 2026-02-08
**Phase**: V - Local Kubernetes Deployment
**Status**: Production Ready
