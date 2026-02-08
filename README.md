# Todo App - Evolution of Todo

A progressive task management application demonstrating the evolution from console app to full-stack web application.

## Project Overview

This project is part of the "Evolution of Todo" hackathon, showcasing Spec-Driven Development with Claude Code.

| Phase | Description | Status |
|-------|-------------|--------|
| Phase I | In-Memory Console App | ✅ COMPLETE |
| Phase II | Full-Stack Web Application | ✅ COMPLETE |
| Phase III | User Authentication & Multi-User Support | ✅ COMPLETE |
| Phase IV | AI-Powered Chatbot | ✅ COMPLETE |
| Phase V | Local Kubernetes Deployment | ✅ COMPLETE |
| Phase VI | Cloud-Native Distributed System | Planned |

## 🚀 Production Deployment

**Status:** Ready for deployment (security hardened, code cleaned)

**Quick Deploy:**
1. Open `START_HERE.md` for deployment overview
2. Follow `DEPLOY_NOW.md` for backend (Hugging Face Spaces)
3. Follow `DEPLOY_FRONTEND.md` for frontend (Vercel)
4. See `DEPLOYMENT_RECORD.md` for deployment tracking

**Production URLs:** (To be filled after deployment)
- **Frontend:** [Vercel URL pending]
- **Backend API:** [Hugging Face URL pending]
- **API Docs:** [Backend URL]/docs

**Deployment Platforms:**
- Backend: Hugging Face Spaces (Docker, FREE tier)
- Frontend: Vercel (Next.js, FREE tier)
- Database: Neon DB PostgreSQL (already configured)

**Security:** All secrets rotated and redacted from documentation. Use `.secrets.production.txt` for deployment (gitignored).

---

## Phase V: Local Kubernetes Deployment

Production-ready Kubernetes deployment for local development and testing with Minikube.

### Features

**Container Images**:
- Multi-stage Docker builds (backend <500MB, frontend <200MB)
- Optimized for size and security
- Non-root users, minimal base images
- Health check endpoints

**Helm Charts**:
- Declarative deployment management
- Environment-specific configurations (dev, prod)
- Resource management (requests, limits)
- Security contexts and health probes

**Automation Scripts**:
- One-command deployment (`deploy-minikube.sh`)
- Rolling updates with zero downtime
- Automated rollbacks and scaling
- Comprehensive validation suite

**AI-Assisted Operations**:
- Gordon (Docker AI) for Dockerfile optimization
- kubectl-ai for natural language Kubernetes commands
- Kagent for cluster analysis and optimization

**Production Readiness**:
- Automated health checks validation
- Resource configuration validation
- Security configuration validation
- Comprehensive troubleshooting guide

### Quick Start

#### Prerequisites

- Docker Desktop 4.53+
- Minikube 1.30+
- kubectl 1.28+
- Helm 3.12+

#### 5-Minute Deployment

```bash
# Navigate to project root
cd evolution-of-todo

# Create environment file
cp k8s/.env.example k8s/.env
# Edit k8s/.env with your credentials

# Run automated deployment
./k8s/scripts/deploy-minikube.sh

# Access application
./k8s/scripts/access-application.sh
```

#### Management Operations

```bash
# Scale deployment
./k8s/scripts/scale-deployment.sh --component backend --replicas 3

# Rolling update
./k8s/scripts/update-deployment.sh --component backend --tag v1.0.1

# Rollback
./k8s/scripts/rollback-deployment.sh --component backend

# Validate production readiness
./k8s/scripts/run-all-validations.sh

# Cleanup
./k8s/scripts/cleanup.sh
```

### Documentation

Complete documentation available in `k8s/docs/`:

- **[DEPLOYMENT.md](k8s/docs/DEPLOYMENT.md)**: Step-by-step deployment guide
- **[ARCHITECTURE.md](k8s/docs/ARCHITECTURE.md)**: System architecture and design
- **[LIFECYCLE_MANAGEMENT.md](k8s/docs/LIFECYCLE_MANAGEMENT.md)**: Updates, rollbacks, scaling
- **[TROUBLESHOOTING.md](k8s/docs/TROUBLESHOOTING.md)**: Common issues and solutions
- **[PRODUCTION_READINESS.md](k8s/docs/PRODUCTION_READINESS.md)**: Validation checklist
- **[AI_TOOLS_GUIDE.md](k8s/docs/AI_TOOLS_GUIDE.md)**: AI-assisted operations

### Tech Stack

- **Container Runtime**: Docker
- **Orchestration**: Kubernetes (Minikube)
- **Package Manager**: Helm 3
- **Base Images**: python:3.13-slim, node:20-alpine
- **AI Tools**: Gordon, kubectl-ai, Kagent

---

## Phase IV: AI-Powered Chatbot

Natural language interface for task management using AI-powered function calling.

### Features

**AI Chat Interface**:
- Natural language task management
- Function calling for CRUD operations
- Conversation history and context
- Real-time streaming responses

**Supported Commands**:
- "Add task: buy groceries"
- "Show my tasks"
- "Mark task 1 as complete"
- "Update task 2 title to 'New title'"
- "Delete task 3"

**AI Integration**:
- Groq API with Llama 3.3 70B model
- Function calling for structured operations
- Conversation memory and context
- Error handling and retry logic

### Tech Stack

- **LLM Provider**: Groq API
- **Model**: llama-3.3-70b-versatile
- **Backend**: FastAPI with streaming support
- **Frontend**: Next.js with real-time chat UI

### Quick Start

See Phase II setup instructions. The chatbot is integrated into the main application.

---

## Phase III: User Authentication & Multi-User Support

Secure user authentication enabling multiple users to manage their own tasks.

### Features

**Authentication**:
- User registration with email/password
- Secure login/logout
- Session management with JWT tokens
- Protected routes and API endpoints

**Multi-User Support**:
- Task isolation per user
- User profile display in navigation
- Automatic redirect for unauthenticated access

### Tech Stack

- **Frontend Auth**: Better Auth + JWT plugin
- **Backend Auth**: python-jose (JWT verification via JWKS)
- **Database**: PostgreSQL (Better Auth managed tables)

---

## Phase II: Full-Stack Web Application

A modern web application with Next.js frontend and FastAPI backend.

### Features

**Basic Features (5)**:
- Add Task via web form
- View Task List with status indicators
- Mark Task Complete/Incomplete
- Update Task details
- Delete Task with confirmation

**Intermediate Features (5)**:
- Priority Levels (High, Medium, Low)
- Categories/Tags for organization
- Search by keyword
- Filter by status, priority, category
- Sort by priority, date, title

### Tech Stack

- **Backend**: FastAPI + SQLModel + PostgreSQL (Neon DB)
- **Frontend**: Next.js 14 + React 18 + TypeScript + Tailwind CSS
- **Testing**: pytest (backend) + Jest (frontend)

### Quick Start

#### Prerequisites

- Python 3.13+
- Node.js 18+
- Neon DB account (free tier)

#### Backend Setup

```bash
cd backend
uv venv
.venv\Scripts\Activate.ps1  # Windows
uv pip install -e ".[dev]"

# Configure .env with DATABASE_URL
cp .env.example .env

# Start server
uvicorn src.main:app --reload --port 8000
```

#### Frontend Setup

```bash
cd frontend
npm install

# Configure .env.local
cp .env.example .env.local

# Start dev server
npm run dev
```

Visit:
- Frontend: http://localhost:3000
- API Docs: http://localhost:8000/docs

### Project Structure

```
evolution-of-todo/
├── phase4-chatbot/          # Phase IV: AI Chatbot
│   ├── backend/             # FastAPI backend with AI
│   │   ├── src/
│   │   │   ├── api/routes/  # API endpoints + chat
│   │   │   ├── models/      # SQLModel models
│   │   │   ├── schemas/     # Pydantic schemas
│   │   │   └── services/    # Business logic + AI
│   │   └── tests/           # pytest tests
│   └── frontend/            # Next.js frontend with chat
│       ├── src/
│       │   ├── app/         # Next.js App Router
│       │   ├── components/  # React components + chat UI
│       │   ├── services/    # API client
│       │   └── types/       # TypeScript types
│       └── tests/           # Jest tests
├── k8s/                     # Phase V: Kubernetes Deployment
│   ├── dockerfiles/         # Docker build files
│   ├── helm-charts/         # Helm deployment charts
│   ├── scripts/             # Automation scripts
│   └── docs/                # Deployment documentation
├── backend/                 # Phase II: Original backend
├── frontend/                # Phase II: Original frontend
├── src/                     # Phase I: CLI source
├── tests/                   # Phase I: CLI tests
├── specs/                   # Specification documents
│   ├── 001-console-todo-app/
│   ├── 002-fullstack-webapp/
│   ├── 003-user-authentication/
│   ├── 004-ai-chatbot/
│   └── 005-k8s-local-deployment/
├── history/                 # Prompt History Records
└── .specify/                # SpecKit Plus configuration
```

---

## Phase I: Console Application

A command-line task management application with in-memory storage.

### Features

- Add, view, update, delete tasks
- Mark tasks complete/incomplete
- Status indicators and task counts

### Usage

```bash
cd todo-app
python -m src.main add "Buy groceries" -d "Milk, eggs"
python -m src.main list
python -m src.main complete 1
python -m src.main update 1 -t "New title"
python -m src.main delete 1
```

### Running Tests

```bash
pytest -v
```

---

## Development Methodology

This project follows **Spec-Driven Development (SDD)** with Claude Code:

1. **Specify** (`/sp.specify`): Write feature specification
2. **Plan** (`/sp.plan`): Generate implementation plan
3. **Tasks** (`/sp.tasks`): Break down into tasks
4. **Implement** (`/sp.implement`): Execute via Claude Code
5. **Commit** (`/sp.git.commit_pr`): Automated git workflows

All implementation code is generated by Claude Code from specifications.

## License

MIT License

## Author

Bushraturk (bushrahussain068@gmail.com)
