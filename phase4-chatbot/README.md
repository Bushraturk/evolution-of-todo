# AI-Powered Todo Chatbot - Phase IV

**Status**: Backend & Frontend Implementation Complete | Ready for Deployment

This directory contains the Phase IV implementation of the Evolution of Todo project: an AI-powered chatbot interface for natural language task management using MCP (Model Context Protocol) and OpenAI Agents SDK.

## 🎯 What's Been Implemented

### ✅ Backend (Complete)

**Core Infrastructure:**
- Database models (Conversation, Message) with SQLModel
- Database migrations for conversation and message tables
- MCP server initialization and lifecycle management
- MCP tool definitions for 5 task operations
- OpenAI Agents SDK integration with retry logic
- Conversation service with pagination (50 messages) and archival (90 days)
- Chat endpoint with authentication and error handling
- FastAPI application with CORS and health checks

**MCP Tool Handlers (All 5 Implemented):**
1. ✅ `add_task` - Create tasks from natural language
2. ✅ `list_tasks` - View tasks with status filtering
3. ✅ `complete_task` - Mark tasks as complete
4. ✅ `update_task` - Modify task title/description
5. ✅ `delete_task` - Remove tasks

**Features:**
- Natural language intent recognition via OpenAI GPT-4
- Tool-based task operations with validation
- Conversation history persistence
- Stateless server architecture
- Error handling with exponential backoff retry
- Comprehensive logging

### ✅ Frontend (Complete)

**Implemented:**
- Complete Next.js 14 application with TypeScript
- ChatInterface component with real-time messaging
- Chat API client with JWT authentication
- TypeScript interfaces for all chat types
- Chat page with responsive design
- Landing page with feature showcase
- Conversation state management (localStorage)
- Error handling and loading states
- Tailwind CSS styling with purple gradient theme
- Mobile-friendly responsive design

## 🚀 Quick Start

### Prerequisites

- Python 3.13+
- Node.js 18+
- PostgreSQL database (Neon DB recommended)
- OpenAI API key

### Backend Setup

1. **Navigate to backend directory:**
   ```bash
   cd phase4-chatbot/backend
   ```

2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment:**
   ```bash
   cp .env.example .env
   # Edit .env with your configuration:
   # - DATABASE_URL (Neon PostgreSQL connection string)
   # - OPENAI_API_KEY (from https://platform.openai.com/api-keys)
   # - JWT_SECRET (reuse from Phase III)
   ```

4. **Run database migrations:**
   ```bash
   # Connect to your database and run:
   psql $DATABASE_URL < migrations/001_add_chatbot_tables.sql
   ```

5. **Start the backend server:**
   ```bash
   uvicorn src.main:app --reload --port 8000
   ```

6. **Verify backend is running:**
   ```bash
   curl http://localhost:8000/health
   # Expected: {"status":"healthy","service":"todo-chatbot-backend","version":"1.0.0","mcp_initialized":true}
   ```

### Frontend Setup (To Be Completed)

1. **Navigate to frontend directory:**
   ```bash
   cd phase4-chatbot/frontend
   ```

2. **Install dependencies:**
   ```bash
   npm install
   ```

3. **Configure environment:**
   ```bash
   cp .env.local.example .env.local
   # Edit .env.local with your configuration
   ```

4. **Start the frontend server:**
   ```bash
   npm run dev
   ```

## 📁 Project Structure

```
phase4-chatbot/
├── backend/
│   ├── src/
│   │   ├── main.py              # FastAPI application entry
│   │   ├── config.py            # Environment configuration
│   │   ├── database.py          # SQLModel engine & session
│   │   ├── models/              # Database models
│   │   │   ├── conversation.py  # Conversation model
│   │   │   └── message.py       # Message model
│   │   ├── mcp/                 # MCP server implementation
│   │   │   ├── server.py        # MCP server setup
│   │   │   ├── tools.py         # Tool definitions
│   │   │   └── handlers.py      # Tool execution handlers
│   │   ├── services/            # Business logic
│   │   │   ├── agent_service.py # OpenAI Agents SDK integration
│   │   │   └── conversation_service.py # Conversation management
│   │   └── api/                 # API routes
│   │       └── chat.py          # Chat endpoint
│   ├── migrations/              # Database migrations
│   │   ├── 001_add_chatbot_tables.sql
│   │   └── 001_rollback_chatbot_tables.sql
│   ├── requirements.txt         # Python dependencies
│   ├── pyproject.toml          # Project configuration
│   └── .env.example            # Environment template
│
└── frontend/
    ├── src/                    # Frontend source (to be implemented)
    ├── package.json            # Node.js dependencies
    └── .env.local.example      # Environment template
```

## 🔧 Configuration

### Backend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | `postgresql://user:pass@host:5432/db` |
| `OPENAI_API_KEY` | OpenAI API key | `sk-...` |
| `JWT_SECRET` | JWT secret key (from Phase III) | `your-secret-key` |
| `CORS_ORIGINS` | Allowed frontend origins | `http://localhost:3000` |
| `MAX_CONVERSATION_HISTORY` | Max messages to load | `50` |
| `CONVERSATION_ARCHIVE_DAYS` | Days before archival | `90` |
| `OPENAI_REQUEST_TIMEOUT` | Request timeout (seconds) | `30` |
| `OPENAI_MAX_RETRIES` | Max retry attempts | `3` |

### Frontend Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `NEXT_PUBLIC_API_URL` | Backend API URL | `http://localhost:8000` |
| `NEXT_PUBLIC_OPENAI_DOMAIN_KEY` | OpenAI ChatKit domain key | (leave empty for local dev) |

## 🧪 Testing the Backend

### Test Chat Endpoint

```bash
# Create new conversation
curl -X POST http://localhost:8000/api/{user_id}/chat \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Add a task to buy groceries"
  }'
```

### Expected Response

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

## 📝 API Documentation

Once the backend is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔗 Integration with Existing Phases

### Phase II Integration (Task Management)
- Reuses existing `TaskService` for all CRUD operations
- No changes to existing task database schema
- MCP handlers delegate to Phase II business logic

### Phase III Integration (Authentication)
- Reuses existing JWT authentication system
- Chat endpoint validates user_id matches JWT token
- All operations isolated by user_id

## 🚧 Remaining Work

### Deployment Tasks (8 tasks - Require Manual Execution)

These tasks require access to cloud platforms and cannot be automated:

- [ ] **T082**: Run database migrations on production database
- [ ] **T083**: Verify all database indexes are created correctly
- [ ] **T084**: Test conversation archival background job logic
- [ ] **T085**: Deploy backend to Hugging Face Spaces with environment variables
- [ ] **T086**: Deploy frontend to Vercel with environment variables
- [ ] **T087**: Configure OpenAI domain allowlist with Vercel URL
- [ ] **T088**: Add NEXT_PUBLIC_OPENAI_DOMAIN_KEY to Vercel environment variables

**See DEPLOYMENT.md for detailed deployment instructions.**

## 📚 Documentation

- **Specification**: `../../specs/004-ai-chatbot/spec.md`
- **Implementation Plan**: `../../specs/004-ai-chatbot/plan.md`
- **Task Breakdown**: `../../specs/004-ai-chatbot/tasks.md`
- **Research Decisions**: `../../specs/004-ai-chatbot/research.md`
- **Data Model**: `../../specs/004-ai-chatbot/data-model.md`
- **API Contracts**: `../../specs/004-ai-chatbot/contracts/`
- **Quick Start Guide**: `../../specs/004-ai-chatbot/quickstart.md`

## 🎓 Architecture Decisions

### MCP (Model Context Protocol)
- Standardized tool interface for AI agents
- Separates tool definitions from implementations
- Enables tool reusability across different AI frameworks

### Stateless Server
- All conversation state persisted to database
- Enables horizontal scaling
- Survives server restarts

### Conversation Pagination
- Loads last 50 messages for context
- Prevents memory issues with long conversations
- Balances context quality with performance

### Tool Handler Delegation
- MCP handlers delegate to existing TaskService
- Maintains separation of concerns
- Reuses tested business logic from Phase II

## 🐛 Troubleshooting

### Backend Issues

**Issue**: `ModuleNotFoundError: No module named 'openai'`
**Solution**: Install dependencies: `pip install -r requirements.txt`

**Issue**: `Connection refused` when connecting to database
**Solution**: Verify `DATABASE_URL` in `.env` and database is running

**Issue**: `OpenAI API key not found`
**Solution**: Add `OPENAI_API_KEY` to `.env` file

**Issue**: `Rate limit exceeded` from OpenAI
**Solution**: Wait and retry. Consider upgrading OpenAI plan.

### Database Issues

**Issue**: `Table "conversation" does not exist`
**Solution**: Run database migrations: `psql $DATABASE_URL < migrations/001_add_chatbot_tables.sql`

**Issue**: `Foreign key constraint violation`
**Solution**: Ensure `user` table exists from Phase III setup

## 📊 Implementation Status

**Completed Tasks**: 84 / 92 (91%)

- ✅ Phase 1: Setup (6/6 tasks)
- ✅ Phase 2: Foundational (24/24 tasks)
- ✅ Phase 3: User Story 1 - Task Creation (7/7 tasks)
- ✅ Phase 4: User Story 2 - Task Viewing (7/7 tasks)
- ✅ Phase 5: User Story 3 - Task Completion (7/7 tasks)
- ✅ Phase 6: User Story 5 - Task Modification (7/7 tasks)
- ✅ Phase 7: User Story 6 - Task Deletion (7/7 tasks)
- ✅ Phase 8: Frontend Integration (8/8 tasks)
- ✅ Phase 9: Polish & Documentation (11/19 tasks)
  - ✅ All code polish tasks complete
  - ⏳ Deployment tasks require manual execution (8 tasks)

## 🎯 Next Steps

1. **Complete Frontend Integration** (Phase 8)
   - Implement ChatInterface component
   - Create chat API client
   - Build chat page

2. **Polish & Deploy** (Phase 9)
   - Add comprehensive logging
   - Create deployment configurations
   - Deploy to production
   - Validate all user stories

3. **Testing**
   - Test all 5 MCP tools
   - Test conversation continuity
   - Test error handling
   - Run full test suite

## 📞 Support

For issues or questions:
1. Check troubleshooting section above
2. Review error logs (backend and frontend)
3. Consult API documentation at `/docs`
4. Create GitHub issue with error details

---

**Version**: 1.0.0
**Last Updated**: 2026-01-29
**Status**: Backend Complete | Frontend Pending
