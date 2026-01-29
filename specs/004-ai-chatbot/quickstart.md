# Quick Start Guide: AI-Powered Todo Chatbot

**Feature**: 004-ai-chatbot
**Date**: 2026-01-29
**Purpose**: Developer setup and testing guide

## Overview

This guide helps developers set up and test the AI-powered todo chatbot locally. The chatbot enables natural language task management through a conversational interface powered by OpenAI Agents SDK and MCP (Model Context Protocol).

---

## Prerequisites

### Required Software
- Python 3.13+
- Node.js 18+
- PostgreSQL (or Neon DB connection)
- Git

### Required Accounts
- OpenAI API account with API key
- Neon DB account (or local PostgreSQL)
- GitHub account (for deployment)

### Existing Setup
This feature builds on Phase II/III. Ensure you have:
- ✅ Existing task database with `user` and `task` tables
- ✅ Working authentication system (JWT-based)
- ✅ Backend running on port 8000
- ✅ Frontend running on port 3000

---

## Backend Setup

### 1. Navigate to Backend Directory

```bash
cd phase4-chatbot/backend
```

### 2. Install Dependencies

```bash
# Using UV (recommended)
uv pip install -r requirements.txt

# Or using pip
pip install -r requirements.txt
```

**Key Dependencies**:
- `fastapi>=0.109.0` - Web framework
- `openai>=1.0.0` - OpenAI Agents SDK
- `mcp>=1.0.0` - Official MCP SDK
- `sqlmodel>=0.0.14` - ORM
- `psycopg2-binary>=2.9.9` - PostgreSQL driver

### 3. Configure Environment Variables

Create `.env` file in `phase4-chatbot/backend/`:

```bash
# Database (reuse from Phase II/III)
DATABASE_URL=postgresql://user:password@host:5432/database

# OpenAI API
OPENAI_API_KEY=sk-...your-api-key...

# Server Configuration
CORS_ORIGINS=http://localhost:3000
DEBUG=true

# JWT Secret (reuse from Phase III)
JWT_SECRET=your-jwt-secret-key
```

**Get OpenAI API Key**:
1. Go to https://platform.openai.com/api-keys
2. Click "Create new secret key"
3. Copy the key and add to `.env`

### 4. Run Database Migrations

```bash
# Apply chatbot table migrations
python -m alembic upgrade head

# Or run migration script directly
psql $DATABASE_URL < specs/004-ai-chatbot/data-model.md  # Extract SQL from data-model.md
```

**Verify Tables Created**:
```bash
psql $DATABASE_URL -c "\dt"
# Should show: conversation, message (new), user, task (existing)
```

### 5. Start Backend Server

```bash
# Development mode with auto-reload
uvicorn src.main:app --reload --port 8000

# Or using Python
python -m src.main
```

**Verify Backend Running**:
```bash
curl http://localhost:8000/health
# Expected: {"status":"healthy"}
```

---

## Frontend Setup

### 1. Navigate to Frontend Directory

```bash
cd phase4-chatbot/frontend
```

### 2. Install Dependencies

```bash
npm install
```

**Key Dependencies**:
- `next@14+` - React framework
- `@openai/chatkit` - Chat UI components
- `react@18+` - UI library
- `typescript@5+` - Type safety

### 3. Configure Environment Variables

Create `.env.local` file in `phase4-chatbot/frontend/`:

```bash
# Backend API
NEXT_PUBLIC_API_URL=http://localhost:8000

# OpenAI ChatKit (leave empty for local development)
NEXT_PUBLIC_OPENAI_DOMAIN_KEY=

# Authentication (reuse from Phase III)
NEXT_PUBLIC_AUTH_URL=http://localhost:3000
```

**Note**: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` is only required for production deployment. Local development works without it.

### 4. Start Frontend Server

```bash
npm run dev
```

**Verify Frontend Running**:
- Open http://localhost:3000/chat
- Should see chat interface

---

## Testing the Chatbot

### 1. Authenticate

**Option A: Use Existing Account** (from Phase III)
1. Go to http://localhost:3000/login
2. Login with existing credentials
3. Navigate to http://localhost:3000/chat

**Option B: Create New Account**
1. Go to http://localhost:3000/register
2. Register new account
3. Automatically redirected to dashboard
4. Navigate to http://localhost:3000/chat

### 2. Test Natural Language Commands

**Create Task**:
```
You: Add a task to buy groceries
Bot: I've created a task titled "Buy groceries" for you. Is there anything else you'd like to add?
```

**List Tasks**:
```
You: Show me all my tasks
Bot: You have 3 pending tasks:
1. Buy groceries
2. Call mom
3. Pay bills
```

**Complete Task**:
```
You: Mark task 1 as complete
Bot: Great! I've marked "Buy groceries" as complete. Anything else?
```

**Update Task**:
```
You: Change task 2 to "Call mom tonight"
Bot: I've updated the task to "Call mom tonight".
```

**Delete Task**:
```
You: Delete task 3
Bot: I've removed "Pay bills" from your list.
```

### 3. Test Conversation Continuity

**Multi-Turn Conversation**:
```
You: Add a task to buy milk
Bot: Task created: "Buy milk"

You: Actually, change that to "Buy milk and eggs"
Bot: Updated to "Buy milk and eggs"

You: Mark it as complete
Bot: Done! "Buy milk and eggs" is now complete.
```

### 4. Test Error Handling

**Non-Existent Task**:
```
You: Complete task 999
Bot: I couldn't find task 999. Would you like to see your current tasks?
```

**Ambiguous Request**:
```
You: Delete that
Bot: Which task would you like to delete? Please specify the task number or name.
```

---

## API Testing (Manual)

### Test Chat Endpoint

**Create New Conversation**:
```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

**Expected Response**:
```json
{
  "conversation_id": 1,
  "response": "I've created a task titled 'Buy groceries' for you.",
  "tool_calls": [
    {
      "tool": "add_task",
      "parameters": {
        "user_id": "...",
        "title": "Buy groceries"
      },
      "result": {
        "task_id": "...",
        "status": "created",
        "title": "Buy groceries"
      }
    }
  ]
}
```

**Continue Conversation**:
```bash
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "conversation_id": 1,
    "message": "Show me all my tasks"
  }'
```

---

## Running Tests

### Backend Tests

```bash
cd phase4-chatbot/backend

# Run all tests
pytest

# Run specific test suites
pytest tests/unit/test_mcp_tools.py
pytest tests/integration/test_chat_endpoint.py
pytest tests/contract/test_mcp_contract.py

# Run with coverage
pytest --cov=src --cov-report=html
```

### Frontend Tests

```bash
cd phase4-chatbot/frontend

# Run all tests
npm test

# Run specific test
npm test ChatInterface.test.tsx

# Run with coverage
npm test -- --coverage
```

---

## Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'openai'`
**Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: `Connection refused` when connecting to database
**Solution**: Verify `DATABASE_URL` in `.env` and database is running

**Issue**: `OpenAI API key not found`
**Solution**: Add `OPENAI_API_KEY` to `.env` file

**Issue**: `Rate limit exceeded` from OpenAI
**Solution**: Wait a moment and retry. Consider upgrading OpenAI plan.

### Frontend Issues

**Issue**: `Cannot connect to backend`
**Solution**: Verify backend is running on port 8000 and `NEXT_PUBLIC_API_URL` is correct

**Issue**: `ChatKit not rendering`
**Solution**: Check browser console for errors. Verify `@openai/chatkit` is installed.

**Issue**: `Authentication failed`
**Solution**: Verify JWT token is valid and not expired. Re-login if needed.

### Database Issues

**Issue**: `Table "conversation" does not exist`
**Solution**: Run database migrations (see step 4 in Backend Setup)

**Issue**: `Foreign key constraint violation`
**Solution**: Ensure `user` table exists from Phase III setup

---

## Development Workflow

### 1. Make Code Changes

Edit files in `phase4-chatbot/backend/src/` or `phase4-chatbot/frontend/src/`

### 2. Test Locally

```bash
# Backend: Auto-reloads on file changes
uvicorn src.main:app --reload

# Frontend: Auto-reloads on file changes
npm run dev
```

### 3. Run Tests

```bash
# Backend
pytest

# Frontend
npm test
```

### 4. Commit Changes

```bash
git add .
git commit -m "feat: implement chatbot feature"
```

---

## Production Deployment

### Backend Deployment (Hugging Face Spaces)

1. **Prepare Dockerfile** (already exists in `phase4-chatbot/backend/`)
2. **Set Environment Variables** in Hugging Face dashboard:
   - `DATABASE_URL`
   - `OPENAI_API_KEY`
   - `JWT_SECRET`
   - `CORS_ORIGINS` (add Vercel URL)
3. **Deploy**: Push to Hugging Face repository
4. **Verify**: Test health endpoint

### Frontend Deployment (Vercel)

1. **Connect Repository** to Vercel
2. **Set Environment Variables**:
   - `NEXT_PUBLIC_API_URL` (Hugging Face URL)
   - `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` (from OpenAI dashboard)
3. **Deploy**: Vercel auto-deploys on push
4. **Configure Domain Allowlist**:
   - Go to https://platform.openai.com/settings/organization/security/domain-allowlist
   - Add Vercel URL
   - Copy domain key to environment variables

---

## Monitoring & Debugging

### View Backend Logs

```bash
# Local development
tail -f logs/app.log

# Production (Hugging Face)
# View logs in Hugging Face dashboard
```

### View Frontend Logs

```bash
# Local development
# Check browser console (F12)

# Production (Vercel)
# View logs in Vercel dashboard
```

### Monitor OpenAI API Usage

1. Go to https://platform.openai.com/usage
2. View API calls and costs
3. Set up usage alerts if needed

---

## Next Steps

After completing local setup:

1. ✅ Test all 5 MCP tools (add, list, complete, update, delete)
2. ✅ Test conversation continuity across multiple messages
3. ✅ Test error handling (invalid inputs, non-existent tasks)
4. ✅ Run full test suite (backend + frontend)
5. ⏳ Deploy to production (Hugging Face + Vercel)
6. ⏳ Configure OpenAI domain allowlist
7. ⏳ Monitor API usage and costs

---

## Additional Resources

- **OpenAI Agents SDK**: https://platform.openai.com/docs/agents
- **MCP Documentation**: https://modelcontextprotocol.io
- **OpenAI ChatKit**: https://platform.openai.com/docs/chatkit
- **FastAPI Documentation**: https://fastapi.tiangolo.com
- **Next.js Documentation**: https://nextjs.org/docs

---

## Support

For issues or questions:
1. Check troubleshooting section above
2. Review error logs (backend and frontend)
3. Consult API documentation
4. Create GitHub issue with error details

---

**Status**: ✅ Complete
**Last Updated**: 2026-01-29
