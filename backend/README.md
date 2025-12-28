# Todo App Backend - Phase II

FastAPI backend for the Todo App with SQLModel ORM and Neon DB (PostgreSQL).

## Features

- RESTful API for task management
- SQLModel ORM with PostgreSQL
- CORS middleware for frontend communication
- Automatic database initialization

## Prerequisites

- Python 3.13+
- UV package manager
- Neon DB account (free tier available)

## Setup

### 1. Create Virtual Environment

```bash
cd backend
uv venv
```

### 2. Activate Virtual Environment

```bash
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS/Linux
source .venv/bin/activate
```

### 3. Install Dependencies

```bash
uv pip install -e ".[dev]"
```

### 4. Configure Environment

Copy `.env.example` to `.env` and update:

```bash
cp .env.example .env
```

Edit `.env`:
```
DATABASE_URL=postgresql://user:pass@host.neon.tech/dbname?sslmode=require
CORS_ORIGINS=http://localhost:3000
DEBUG=true
```

### 5. Initialize Database

The database tables are created automatically when the server starts.

## Running the Server

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

Visit http://localhost:8000/docs for API documentation.

## API Endpoints

### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/tasks | List all tasks |
| POST | /api/tasks | Create a new task |
| GET | /api/tasks/{id} | Get a single task |
| PUT | /api/tasks/{id} | Update a task |
| DELETE | /api/tasks/{id} | Delete a task |
| PATCH | /api/tasks/{id}/toggle | Toggle completion |

### Categories

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | /api/categories | List all categories |
| POST | /api/categories | Create a new category |

### Query Parameters

`GET /api/tasks` supports:
- `search`: Search in title and description
- `status`: Filter by `all`, `completed`, `incomplete`
- `priority`: Filter by `high`, `medium`, `low`
- `category_id`: Filter by category UUID
- `sort_by`: Sort by `created_at`, `priority`, `title`
- `sort_order`: `asc` or `desc`

## Running Tests

```bash
# Run all tests
pytest -v

# Run with coverage
pytest --cov=src --cov-report=term-missing

# Run specific test file
pytest tests/unit/test_task_service.py -v
```

## Project Structure

```
backend/
├── src/
│   ├── __init__.py
│   ├── main.py              # FastAPI application
│   ├── config.py            # Configuration
│   ├── database.py          # Database connection
│   ├── models/              # SQLModel models
│   ├── schemas/             # Pydantic schemas
│   ├── services/            # Business logic
│   └── api/routes/          # API endpoints
├── tests/
│   ├── conftest.py          # Pytest fixtures
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── pyproject.toml
└── .env.example
```
