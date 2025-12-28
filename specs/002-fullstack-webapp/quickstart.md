# Quickstart: Full-Stack Web Application Todo App

**Feature**: 002-fullstack-webapp
**Date**: 2025-12-28

## Prerequisites

### Required Software
- Python 3.13+
- Node.js 18+ (LTS recommended)
- UV package manager (Python)
- npm or yarn (Node.js)
- Git

### External Services
- Neon DB account (free tier: https://neon.tech)

### Verify Installations

```bash
# Python
python --version
# Expected: Python 3.13.x

# UV
uv --version
# Expected: uv 0.x.x

# Node.js
node --version
# Expected: v18.x.x or higher

# npm
npm --version
# Expected: 10.x.x or higher
```

## Project Setup

### 1. Clone and Navigate

```bash
cd todo-app
git checkout 002-fullstack-webapp
```

### 2. Set Up Neon DB

1. Go to https://neon.tech and create a free account
2. Create a new project named "todo-app"
3. Copy the connection string (format: `postgresql://user:pass@host/dbname?sslmode=require`)

### 3. Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
uv venv

# Activate virtual environment
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (CMD)
.venv\Scripts\activate.bat
# macOS/Linux
source .venv/bin/activate

# Install dependencies
uv pip install -e ".[dev]"

# Create environment file
cp .env.example .env

# Edit .env with your Neon DB connection string
# DATABASE_URL=postgresql://user:pass@host/dbname?sslmode=require
# CORS_ORIGINS=http://localhost:3000
```

### 4. Initialize Database

```bash
# Run database initialization (creates tables)
python -m src.database --init
```

### 5. Start Backend Server

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

# Expected output:
# INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
# INFO:     Started reloader process
```

Verify: Open http://localhost:8000/docs for API documentation

### 6. Frontend Setup

```bash
# Open new terminal, navigate to frontend
cd frontend

# Install dependencies
npm install

# Create environment file
cp .env.example .env.local

# Edit .env.local
# NEXT_PUBLIC_API_URL=http://localhost:8000
```

### 7. Start Frontend Server

```bash
# Development mode
npm run dev

# Expected output:
# ▲ Next.js 14.x.x
# - Local:        http://localhost:3000
```

Verify: Open http://localhost:3000 in your browser

## Development Workflow

### Running Both Servers

**Terminal 1 - Backend**:
```bash
cd backend
.venv\Scripts\Activate.ps1  # Windows
uvicorn src.main:app --reload --port 8000
```

**Terminal 2 - Frontend**:
```bash
cd frontend
npm run dev
```

### Running Tests

**Backend Tests**:
```bash
cd backend
pytest -v

# With coverage
pytest --cov=src --cov-report=term-missing
```

**Frontend Tests**:
```bash
cd frontend
npm test

# With coverage
npm test -- --coverage
```

## Example Session

### 1. Create a Task

Open http://localhost:3000 and:
1. Click "Add Task" button
2. Enter title: "Buy groceries"
3. Enter description: "Milk, eggs, bread"
4. Select priority: "High"
5. Select category: "Shopping"
6. Click "Create"

**Expected**: Task appears in the list with high priority indicator

### 2. View Task List

**Expected**: See all tasks with:
- Checkbox for completion status
- Title and description
- Priority indicator (red for High, yellow for Medium, gray for Low)
- Category tag with color

### 3. Toggle Completion

1. Click the checkbox next to "Buy groceries"
2. **Expected**:
   - Checkbox shows checked state
   - Task title has strikethrough
   - "Task marked as complete" feedback

### 4. Search Tasks

1. Type "groceries" in search box
2. **Expected**: Only tasks containing "groceries" are shown

### 5. Filter Tasks

1. Select "Incomplete" from status filter
2. **Expected**: Only incomplete tasks are shown

### 6. Sort Tasks

1. Select "Priority (High to Low)" from sort dropdown
2. **Expected**: High priority tasks appear first

### 7. Edit Task

1. Click on a task to open edit modal
2. Change title to "Buy organic groceries"
3. Click "Save"
4. **Expected**: Task list shows updated title

### 8. Delete Task

1. Click delete icon on a task
2. Confirm deletion
3. **Expected**: Task removed from list

## API Testing with curl

### List Tasks
```bash
curl http://localhost:8000/api/tasks
```

### Create Task
```bash
curl -X POST http://localhost:8000/api/tasks \
  -H "Content-Type: application/json" \
  -d '{"title": "Test task", "priority": "high"}'
```

### Toggle Completion
```bash
curl -X PATCH http://localhost:8000/api/tasks/{task-id}/toggle
```

### Delete Task
```bash
curl -X DELETE http://localhost:8000/api/tasks/{task-id}
```

## Troubleshooting

### Backend Issues

**Connection refused on port 8000**:
- Ensure backend server is running
- Check for port conflicts: `netstat -an | findstr 8000`

**Database connection error**:
- Verify DATABASE_URL in .env
- Check Neon DB dashboard for connection status
- Ensure `?sslmode=require` is in connection string

### Frontend Issues

**CORS errors in browser**:
- Ensure backend CORS_ORIGINS includes `http://localhost:3000`
- Restart backend server after .env changes

**API calls failing**:
- Verify NEXT_PUBLIC_API_URL in .env.local
- Check browser network tab for actual error

### Common Solutions

1. **Clear node_modules and reinstall**:
   ```bash
   rm -rf node_modules
   npm install
   ```

2. **Reset virtual environment**:
   ```bash
   rm -rf .venv
   uv venv
   uv pip install -e ".[dev]"
   ```

3. **Reset database** (caution - deletes all data):
   ```bash
   python -m src.database --reset
   ```

## Environment Variables Reference

### Backend (.env)
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| DATABASE_URL | Yes | - | Neon DB connection string |
| CORS_ORIGINS | No | http://localhost:3000 | Allowed origins |
| DEBUG | No | false | Enable debug mode |

### Frontend (.env.local)
| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| NEXT_PUBLIC_API_URL | Yes | http://localhost:8000 | Backend API URL |
