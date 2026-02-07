---
title: Todo Chatbot Backend
emoji: 🤖
colorFrom: purple
colorTo: pink
sdk: docker
pinned: false
---

# Backend Implementation Guide

## Overview

This guide provides instructions for completing the AI-Powered Todo Chatbot backend implementation.

## Prerequisites

Before starting, ensure you have:
- Python 3.13+ installed
- PostgreSQL database (Neon DB recommended)
- OpenAI API key from https://platform.openai.com/api-keys
- Existing Phase II/III backend running (for TaskService integration)

## Installation

### 1. Install Dependencies

```bash
cd phase4-chatbot/backend
pip install -r requirements.txt
```

### 2. Configure Environment

Create `.env` file from template:

```bash
cp .env.example .env
```

Edit `.env` with your configuration:

```env
# Database Configuration (reuse from Phase II/III)
DATABASE_URL=postgresql://user:password@host:5432/database

# OpenAI API Configuration
OPENAI_API_KEY=sk-...your-api-key...

# JWT Authentication (reuse from Phase III)
JWT_SECRET=your-jwt-secret-key
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# Server Configuration
CORS_ORIGINS=http://localhost:3000,https://your-frontend-domain.vercel.app
DEBUG=true
LOG_LEVEL=INFO

# Application Settings
MAX_CONVERSATION_HISTORY=50
CONVERSATION_ARCHIVE_DAYS=90
OPENAI_REQUEST_TIMEOUT=30
OPENAI_MAX_RETRIES=3
```

### 3. Run Database Migrations

Connect to your PostgreSQL database and run the migration script:

```bash
psql $DATABASE_URL < migrations/001_add_chatbot_tables.sql
```

Verify tables were created:

```bash
psql $DATABASE_URL -c "\dt"
# Should show: conversation, message (new), user, task (existing)
```

### 4. Integration with Phase II/III

**IMPORTANT**: The chatbot backend requires integration with existing Phase II/III code:

1. **TaskService Integration**: The MCP handlers expect to import TaskService from Phase II:
   ```python
   # In phase4-chatbot/backend/src/mcp/handlers.py
   # Add import for existing TaskService:
   from backend.src.services.task_service import TaskService
   ```

2. **Authentication Integration**: The chat endpoint needs the actual auth dependency from Phase III:
   ```python
   # In phase4-chatbot/backend/src/api/chat.py
   # Replace placeholder with actual import:
   from backend.src.auth.dependencies import get_current_user
   ```

3. **Database Session**: Ensure database session is properly configured to access existing tables.

### 5. Start the Server

```bash
uvicorn src.main:app --reload --port 8000
```

Or using Python:

```bash
python -m src.main
```

### 6. Verify Backend is Running

Test the health endpoint:

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "healthy",
  "service": "todo-chatbot-backend",
  "version": "1.0.0",
  "mcp_initialized": true
}
```

## Testing

### Test Chat Endpoint

**Note**: You'll need a valid JWT token from Phase III authentication.

1. **Get JWT Token** (from Phase III):
   ```bash
   curl -X POST http://localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"email":"user@example.com","password":"password"}'
   ```

2. **Test Chat** (replace `{user_id}` and `{token}`):
   ```bash
   curl -X POST http://localhost:8000/api/{user_id}/chat \
     -H "Authorization: Bearer {token}" \
     -H "Content-Type: application/json" \
     -d '{
       "message": "Add a task to buy groceries"
     }'
   ```

### Expected Response

```json
{
  "conversation_id": 1,
  "response": "I've created a task titled 'Buy groceries' for you. Is there anything else you'd like to add?",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {
        "user_id": "d17cb5d1-5a51-4f2f-9cb8-8cd7f19720e2",
        "title": "Buy groceries"
      },
      "result": {
        "task_id": "323fc8dc-e29e-4868-aa93-8351ff5f6261",
        "status": "created",
        "title": "Buy groceries"
      }
    }
  ]
}
```

## API Documentation

Once running, access interactive API documentation:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Troubleshooting

### Common Issues

1. **Import Errors**
   - Ensure Phase II/III backend is accessible
   - Check Python path includes parent directories
   - Verify all dependencies are installed

2. **Database Connection Errors**
   - Verify DATABASE_URL is correct
   - Ensure database is running
   - Check network connectivity

3. **OpenAI API Errors**
   - Verify OPENAI_API_KEY is set correctly
   - Check API key has sufficient credits
   - Monitor rate limits

4. **Authentication Errors**
   - Ensure JWT_SECRET matches Phase III
   - Verify token is not expired
   - Check user_id matches token

## Next Steps

After backend is running:

1. **Test All MCP Tools**:
   - add_task: "Add a task to buy groceries"
   - list_tasks: "Show me all my tasks"
   - complete_task: "Mark task 1 as complete"
   - update_task: "Change task 1 to 'Buy groceries and fruits'"
   - delete_task: "Delete task 2"

2. **Test Conversation Continuity**:
   - Send multiple messages in same conversation
   - Verify conversation_id is maintained
   - Check message history is loaded

3. **Test Error Handling**:
   - Invalid task IDs
   - Ambiguous requests
   - Rate limit scenarios

4. **Build Frontend** (Phase 8):
   - Implement ChatInterface component
   - Create chat API client
   - Build chat page

## Deployment

See main README.md for deployment instructions to:
- Backend: Hugging Face Spaces
- Frontend: Vercel
- Database: Neon PostgreSQL

---

**Status**: Implementation guide complete
**Last Updated**: 2026-01-29
