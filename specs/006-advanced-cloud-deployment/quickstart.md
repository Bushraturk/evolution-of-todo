# Quick Start Guide: Advanced Cloud Deployment

**Feature**: 006-advanced-cloud-deployment
**Date**: 2026-02-11
**Estimated Setup Time**: 30 minutes

## Prerequisites

Before starting, ensure you have:

- ✅ Phase V (Local Kubernetes Deployment) completed
- ✅ Docker Desktop installed and running
- ✅ Minikube installed (v1.30+)
- ✅ kubectl installed (v1.28+)
- ✅ Helm installed (v3.12+)
- ✅ Python 3.13+ with UV package manager
- ✅ Node.js 20+ with npm
- ✅ Git configured

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                    Kubernetes Cluster (Minikube)                 │
│                                                                   │
│  ┌──────────────┐   ┌──────────────┐   ┌──────────────┐        │
│  │   Frontend   │   │   Backend    │   │  Recurring   │        │
│  │   (Next.js)  │──▶│   (FastAPI)  │   │Task Service  │        │
│  │  + Dapr      │   │   + Dapr     │   │  + Dapr      │        │
│  └──────────────┘   └──────┬───────┘   └──────┬───────┘        │
│                             │                   │                 │
│                             ▼                   ▼                 │
│                    ┌─────────────────────────────┐               │
│                    │   Redpanda Cloud (Kafka)    │               │
│                    │  Topics: task-events,       │               │
│                    │  reminders, task-updates    │               │
│                    └─────────────────────────────┘               │
│                             │                                     │
│                             ▼                                     │
│                    ┌──────────────┐   ┌──────────────┐          │
│                    │Notification  │   │ Audit Log    │          │
│                    │   Service    │   │   Service    │          │
│                    │  + Dapr      │   │  + Dapr      │          │
│                    └──────────────┘   └──────────────┘          │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌──────────────┐
                    │  Neon DB     │
                    │ (PostgreSQL) │
                    └──────────────┘
```

## Step 1: Clone and Setup Repository

```bash
# Navigate to project root
cd evolution-of-todo

# Checkout Phase VI branch
git checkout 006-advanced-cloud-deployment

# Verify you're on the correct branch
git branch --show-current
# Should output: 006-advanced-cloud-deployment
```

## Step 2: Set Up Redpanda Cloud (Message Streaming)

### Option A: Redpanda Cloud (Recommended)

1. Sign up at https://redpanda.com/cloud
2. Create a serverless cluster (free tier)
3. Create topics:
   - `task-events`
   - `reminders`
   - `task-updates`
4. Get connection details:
   - Bootstrap servers
   - SASL username
   - SASL password

### Option B: Local Redpanda (Alternative)

```bash
# Run Redpanda locally with Docker
docker run -d \
  --name redpanda \
  -p 9092:9092 \
  -p 9644:9644 \
  docker.redpanda.com/redpandadata/redpanda:latest \
  redpanda start \
  --kafka-addr internal://0.0.0.0:9092,external://0.0.0.0:19092 \
  --advertise-kafka-addr internal://redpanda:9092,external://localhost:19092

# Create topics
docker exec -it redpanda rpk topic create task-events
docker exec -it redpanda rpk topic create reminders
docker exec -it redpanda rpk topic create task-updates
```

## Step 3: Configure Environment Variables

Create `.env` file in project root:

```bash
# Copy example file
cp .env.example .env

# Edit with your values
nano .env
```

**Required Environment Variables**:

```env
# Database (Neon PostgreSQL)
DATABASE_URL=postgresql://user:password@host:5432/database

# Redpanda Cloud (or local)
KAFKA_BOOTSTRAP_SERVERS=your-cluster.cloud.redpanda.com:9092
KAFKA_SASL_USERNAME=your-username
KAFKA_SASL_PASSWORD=your-password
KAFKA_SECURITY_PROTOCOL=SASL_SSL  # or PLAINTEXT for local

# Groq API (for AI chatbot)
GROQ_API_KEY=gsk_your_api_key_here
GROQ_BASE_URL=https://api.groq.com/openai/v1
GROQ_MODEL=llama-3.3-70b-versatile

# JWT Authentication
JWT_SECRET=your-secret-key-min-32-characters-change-this

# Email Notifications (Resend)
RESEND_API_KEY=re_your_api_key_here
RESEND_FROM_EMAIL=noreply@yourdomain.com

# CORS
CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Dapr Configuration
DAPR_HTTP_PORT=3500
DAPR_GRPC_PORT=50001
```

## Step 4: Database Migration

```bash
# Navigate to backend
cd backend

# Activate virtual environment
uv venv
source .venv/bin/activate  # Linux/Mac
# or
.venv\Scripts\Activate.ps1  # Windows

# Install dependencies
uv pip install -e ".[dev]"

# Run migrations (create new tables)
alembic upgrade head

# Verify tables created
psql $DATABASE_URL -c "\dt"
# Should show: tasks, recurring_patterns, reminders, scheduled_notifications, tags, task_tags
```

## Step 5: Install Dapr

### Install Dapr CLI

```bash
# Linux/Mac
wget -q https://raw.githubusercontent.com/dapr/cli/master/install/install.sh -O - | /bin/bash

# Windows (PowerShell)
powershell -Command "iwr -useb https://raw.githubusercontent.com/dapr/cli/master/install/install.ps1 | iex"

# Verify installation
dapr --version
```

### Initialize Dapr (Local Development)

```bash
# Initialize Dapr in standalone mode
dapr init

# Verify Dapr is running
dapr --version
docker ps  # Should show dapr_redis, dapr_placement, dapr_zipkin
```

## Step 6: Configure Dapr Components

Create Dapr component files in `dapr/components/`:

**Pub/Sub Component** (`dapr/components/pubsub.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: todo-pubsub
spec:
  type: pubsub.kafka
  version: v1
  metadata:
  - name: brokers
    value: "localhost:19092"  # or Redpanda Cloud endpoint
  - name: authType
    value: "password"  # or "none" for local
  - name: saslUsername
    secretKeyRef:
      name: kafka-secrets
      key: username
  - name: saslPassword
    secretKeyRef:
      name: kafka-secrets
      key: password
  - name: consumerGroup
    value: "todo-service"
```

**State Store Component** (`dapr/components/statestore.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: statestore
spec:
  type: state.redis
  version: v1
  metadata:
  - name: redisHost
    value: "localhost:6379"
  - name: redisPassword
    value: ""
```

**Secrets Component** (`dapr/components/secrets.yaml`):
```yaml
apiVersion: dapr.io/v1alpha1
kind: Component
metadata:
  name: local-secrets
spec:
  type: secretstores.local.file
  version: v1
  metadata:
  - name: secretsFile
    value: "./dapr/secrets.json"
```

**Secrets File** (`dapr/secrets.json`):
```json
{
  "kafka-secrets": {
    "username": "your-username",
    "password": "your-password"
  }
}
```

## Step 7: Run Backend Services

### Terminal 1: Main Backend API

```bash
cd backend

# Run with Dapr sidecar
dapr run \
  --app-id todo-api \
  --app-port 8000 \
  --dapr-http-port 3500 \
  --components-path ../dapr/components \
  -- uvicorn src.main:app --reload --port 8000
```

### Terminal 2: Recurring Task Service

```bash
cd backend

# Run recurring task consumer
dapr run \
  --app-id recurring-task-service \
  --app-port 8001 \
  --dapr-http-port 3501 \
  --components-path ../dapr/components \
  -- python src/services/recurring_task_service.py
```

### Terminal 3: Notification Service

```bash
cd backend

# Run notification consumer
dapr run \
  --app-id notification-service \
  --app-port 8002 \
  --dapr-http-port 3502 \
  --components-path ../dapr/components \
  -- python src/services/notification_service.py
```

## Step 8: Run Frontend

```bash
# Terminal 4: Frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev

# Frontend available at http://localhost:3000
```

## Step 9: Verify Setup

### Check Services

```bash
# Check backend health
curl http://localhost:8000/health

# Check Dapr sidecar
curl http://localhost:3500/v1.0/healthz

# Check Kafka topics
docker exec -it redpanda rpk topic list
# Should show: task-events, reminders, task-updates
```

### Test Event Publishing

```bash
# Create a task (should publish event)
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -d '{
    "title": "Test recurring task",
    "priority": "HIGH",
    "due_date": "2026-02-12T09:00:00Z",
    "recurrence": {
      "frequency": "DAILY",
      "interval": 1
    }
  }'

# Check Kafka for event
docker exec -it redpanda rpk topic consume task-events --num 1
```

## Step 10: Deploy to Minikube (Optional)

```bash
# Start Minikube
minikube start --memory=4096 --cpus=2

# Install Dapr on Kubernetes
dapr init --kubernetes

# Build Docker images
cd k8s
./scripts/build-images.sh

# Load images to Minikube
./scripts/load-images.sh

# Deploy with Helm
helm install todo-app ./helm-charts/todo-chatbot \
  --set kafka.bootstrapServers=$KAFKA_BOOTSTRAP_SERVERS \
  --set kafka.saslUsername=$KAFKA_SASL_USERNAME \
  --set kafka.saslPassword=$KAFKA_SASL_PASSWORD

# Verify deployment
kubectl get pods
kubectl get dapr-components
```

## Common Issues and Solutions

### Issue 1: Dapr sidecar not starting

**Solution**:
```bash
# Reinitialize Dapr
dapr uninstall
dapr init

# Check Docker containers
docker ps | grep dapr
```

### Issue 2: Kafka connection refused

**Solution**:
```bash
# Check Redpanda is running
docker ps | grep redpanda

# Check connection
telnet localhost 19092

# Verify component configuration
cat dapr/components/pubsub.yaml
```

### Issue 3: Database migration fails

**Solution**:
```bash
# Check database connection
psql $DATABASE_URL -c "SELECT 1"

# Reset migrations (CAUTION: drops all data)
alembic downgrade base
alembic upgrade head
```

### Issue 4: Frontend can't connect to backend

**Solution**:
```bash
# Check CORS configuration in backend/.env
CORS_ORIGINS=http://localhost:3000

# Restart backend
# Kill process and restart with dapr run command
```

## Development Workflow

### Making Changes

1. **Backend changes**:
   ```bash
   # Edit code in backend/src/
   # Dapr will auto-reload with --reload flag
   ```

2. **Frontend changes**:
   ```bash
   # Edit code in frontend/src/
   # Next.js will hot-reload automatically
   ```

3. **Database schema changes**:
   ```bash
   cd backend
   alembic revision --autogenerate -m "Add new column"
   alembic upgrade head
   ```

### Testing

```bash
# Backend tests
cd backend
pytest

# Frontend tests
cd frontend
npm test

# Integration tests
cd backend
pytest tests/integration/
```

### Debugging

```bash
# View Dapr logs
dapr logs --app-id todo-api

# View backend logs
tail -f backend/logs/app.log

# View Kafka messages
docker exec -it redpanda rpk topic consume task-events
```

## Next Steps

1. **Implement recurring task logic** - See `backend/src/services/recurring_task_service.py`
2. **Implement notification service** - See `backend/src/services/notification_service.py`
3. **Add frontend components** - See `frontend/src/components/`
4. **Write tests** - See `backend/tests/` and `frontend/tests/`
5. **Deploy to cloud** - Follow cloud deployment guide

## Useful Commands

```bash
# Stop all Dapr services
dapr stop --app-id todo-api
dapr stop --app-id recurring-task-service
dapr stop --app-id notification-service

# View Dapr dashboard
dapr dashboard

# Check Dapr components
dapr components --kubernetes  # For K8s
ls dapr/components/  # For local

# Tail logs
dapr logs --app-id todo-api -f

# Publish test event
dapr publish --publish-app-id todo-api --pubsub todo-pubsub --topic task-events --data '{"test": true}'
```

## Resources

- **Dapr Documentation**: https://docs.dapr.io/
- **Redpanda Documentation**: https://docs.redpanda.com/
- **FastAPI Documentation**: https://fastapi.tiangolo.com/
- **Next.js Documentation**: https://nextjs.org/docs
- **Helm Documentation**: https://helm.sh/docs/

---

**Quick Start Version**: 1.0.0
**Last Updated**: 2026-02-11
**Estimated Completion Time**: 30 minutes
**Status**: Ready for Use
