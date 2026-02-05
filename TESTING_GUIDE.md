# Local Testing Guide - Phase IV AI Chatbot

**Last Updated**: 2026-02-01
**Status**: Ready for local testing

## Overview

This guide provides step-by-step instructions for setting up and testing the Phase IV AI-Powered Todo Chatbot locally. Follow these steps to verify all functionality works correctly before deployment.

---

## Prerequisites

### Required Software
- **Python**: 3.11 or higher
- **Node.js**: 18.x or higher
- **PostgreSQL**: 14.x or higher (or Neon database account)
- **Git**: Latest version

### Required Accounts
- **Gemini API Key**: Get from [Google AI Studio](https://makersuite.google.com/app/apikey)
- **Neon Database**: (Optional) Get from [Neon Console](https://console.neon.tech/)

---

## Setup Instructions

### 1. Backend Setup (Main Backend - Port 8001)

```bash
# Navigate to main backend
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Verify .env file exists with correct values
# Should contain:
# - DATABASE_URL (PostgreSQL connection string)
# - JWT_SECRET (at least 32 characters)
# - CORS_ORIGINS (http://localhost:3000)
```

### 2. Chatbot Backend Setup (Port 8002)

```bash
# Navigate to chatbot backend
cd phase4-chatbot/backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment variables
# Copy .env.example to .env and fill in:
cp .env.example .env

# Edit .env with your values:
# DATABASE_URL=postgresql://user:password@host:5432/dbname
# GEMINI_API_KEY=your_actual_gemini_api_key_here
# JWT_SECRET=your-secret-key-at-least-32-characters-here
# CORS_ORIGINS=http://localhost:3000
```

### 3. Database Migration

```bash
# From chatbot backend directory
cd phase4-chatbot/backend

# Run migration script
psql $DATABASE_URL -f migrations/001_add_chatbot_tables.sql

# Verify tables were created
psql $DATABASE_URL -c "\dt conversation"
psql $DATABASE_URL -c "\dt message"

# Verify indexes were created
psql $DATABASE_URL -c "\di idx_conversation_*"
psql $DATABASE_URL -c "\di idx_message_*"
```

### 4. Frontend Setup (Port 3000)

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Verify .env.local exists with correct values
# Should contain:
# NEXT_PUBLIC_API_URL=http://localhost:8001
# NEXT_PUBLIC_CHAT_API_URL=http://localhost:8002
# NEXT_PUBLIC_AUTH_URL=http://localhost:3000
```

---

## Starting All Servers

### Option 1: Use Batch Script (Windows)

```bash
# From project root
START_ALL_SERVERS.bat
```

This will start all three servers in separate windows:
- Main Backend: http://localhost:8001
- Chatbot Backend: http://localhost:8002
- Frontend: http://localhost:3000

### Option 2: Manual Start (All Platforms)

**Terminal 1 - Main Backend:**
```bash
cd backend
.venv\Scripts\activate  # or source .venv/bin/activate
uvicorn src.main:app --reload --port 8001
```

**Terminal 2 - Chatbot Backend:**
```bash
cd phase4-chatbot/backend
.venv\Scripts\activate  # or source .venv/bin/activate
uvicorn src.main:app --reload --port 8002
```

**Terminal 3 - Frontend:**
```bash
cd frontend
npm run dev
```

---

## Verification Steps

### 1. Check Server Health

```bash
# Main backend health check
curl http://localhost:8001/health

# Chatbot backend health check
curl http://localhost:8002/health

# Frontend (open in browser)
# http://localhost:3000
```

### 2. Create Test User

```bash
# Register a new user
curl -X POST http://localhost:8001/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!",
    "name": "Test User"
  }'

# Login to get JWT token
curl -X POST http://localhost:8001/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "TestPassword123!"
  }'

# Save the returned token for next steps
```

---

## Testing User Stories

### US1: Create Task via Chat

**Test Steps:**
1. Open http://localhost:3000 in browser
2. Login with test user credentials
3. Click purple robot icon (bottom-right corner)
4. Type: "Add a task to buy groceries"
5. Press Enter or click Send

**Expected Result:**
- Chatbot responds: "I've created a task titled 'Buy groceries' for you."
- Task appears in main task list
- Conversation ID is maintained for follow-up messages

**Verification:**
```bash
# Check task was created in database
psql $DATABASE_URL -c "SELECT * FROM task WHERE title LIKE '%groceries%';"
```

---

### US2: List Tasks via Chat

**Test Steps:**
1. In chatbot, type: "Show me all my tasks"
2. Press Enter

**Expected Result:**
- Chatbot lists all tasks with titles and completion status
- Format: "You have X tasks: 1. Task title (pending/completed)"

**Verification:**
- Compare chatbot response with main task list
- All tasks should match

---

### US3: Complete Task via Chat

**Test Steps:**
1. In chatbot, type: "Mark task 1 as complete"
2. Press Enter

**Expected Result:**
- Chatbot confirms: "I've marked task 1 as complete."
- Task shows as completed in main task list
- Strikethrough or checkmark appears

**Verification:**
```bash
# Check task completion status
psql $DATABASE_URL -c "SELECT id, title, completed FROM task WHERE id = 1;"
```

---

### US4: Maintain Conversation Context

**Test Steps:**
1. Send message: "Add a task to buy milk"
2. Send message: "Also add eggs"
3. Send message: "Show me what I just added"

**Expected Result:**
- First message creates "Buy milk" task
- Second message creates "Buy eggs" task (understands context)
- Third message lists both recently added tasks

**Verification:**
- Chatbot remembers previous messages in conversation
- No need to repeat "add a task" each time

---

### US5: Update Task via Chat

**Test Steps:**
1. In chatbot, type: "Change task 1 to 'Buy groceries and fruits'"
2. Press Enter

**Expected Result:**
- Chatbot confirms: "I've updated task 1 to 'Buy groceries and fruits'."
- Task title changes in main task list

**Verification:**
```bash
# Check task was updated
psql $DATABASE_URL -c "SELECT id, title FROM task WHERE id = 1;"
```

---

### US6: Delete Task via Chat

**Test Steps:**
1. In chatbot, type: "Delete task 2"
2. Press Enter

**Expected Result:**
- Chatbot confirms: "I've deleted task 2."
- Task disappears from main task list

**Verification:**
```bash
# Check task was deleted
psql $DATABASE_URL -c "SELECT * FROM task WHERE id = 2;"
# Should return 0 rows
```

---

## Troubleshooting

### Issue: Backend won't start

**Symptoms:**
- Error: "Address already in use"
- Error: "Port 8001/8002 is already in use"

**Solution:**
```bash
# Windows - Find and kill process on port
netstat -ano | findstr :8001
taskkill /PID <process_id> /F

# macOS/Linux - Find and kill process on port
lsof -ti:8001 | xargs kill -9
```

---

### Issue: Database connection fails

**Symptoms:**
- Error: "could not connect to server"
- Error: "FATAL: password authentication failed"

**Solution:**
1. Verify DATABASE_URL is correct in .env files
2. Check PostgreSQL is running: `pg_isready`
3. Test connection: `psql $DATABASE_URL -c "SELECT 1;"`
4. Verify SSL mode for Neon: `?sslmode=require`

---

### Issue: Gemini API key invalid

**Symptoms:**
- Error: "API key not valid"
- Error: "Service unavailable"

**Solution:**
1. Verify API key in `phase4-chatbot/backend/.env`
2. Test API key:
```bash
curl "https://generativelanguage.googleapis.com/v1beta/models?key=YOUR_API_KEY"
```
3. Get new key from [Google AI Studio](https://makersuite.google.com/app/apikey)

---

### Issue: Frontend can't connect to backend

**Symptoms:**
- Error: "Network Error"
- Error: "Failed to fetch"

**Solution:**
1. Verify all servers are running
2. Check `frontend/.env.local` has correct URLs:
   - NEXT_PUBLIC_API_URL=http://localhost:8001
   - NEXT_PUBLIC_CHAT_API_URL=http://localhost:8002
3. Check CORS settings in backend .env files
4. Clear browser cache and reload

---

### Issue: Chatbot button not visible

**Symptoms:**
- Purple robot icon doesn't appear
- Can't access chatbot

**Solution:**
1. Verify you're logged in
2. Check browser console for errors (F12)
3. Verify ChatbotButton component is imported in dashboard
4. Check z-index CSS conflicts

---

### Issue: Messages not sending

**Symptoms:**
- Spinner keeps spinning
- No response from chatbot

**Solution:**
1. Check chatbot backend logs for errors
2. Verify JWT token is valid (check Network tab in browser)
3. Check database connection
4. Verify Gemini API is responding

---

## Performance Testing

### Load Test (Optional)

```bash
# Install Apache Bench
# Windows: Download from Apache website
# macOS: brew install httpd
# Linux: sudo apt-get install apache2-utils

# Test chatbot endpoint (replace TOKEN with actual JWT)
ab -n 100 -c 10 \
  -H "Authorization: Bearer TOKEN" \
  -H "Content-Type: application/json" \
  -p chat_request.json \
  http://localhost:8002/api/USER_ID/chat

# chat_request.json:
# {"message": "Show me all my tasks"}
```

**Expected Results:**
- 95% of requests complete in < 2 seconds
- No 500 errors
- Consistent response times

---

## Database Verification

### Check Conversation History

```sql
-- View all conversations for a user
SELECT id, created_at, updated_at, archived_at
FROM conversation
WHERE user_id = 'USER_CUID_HERE'
ORDER BY updated_at DESC;

-- View messages in a conversation
SELECT role, content, created_at
FROM message
WHERE conversation_id = 'CONVERSATION_UUID_HERE'
ORDER BY created_at ASC;

-- Check conversation message count
SELECT conversation_id, COUNT(*) as message_count
FROM message
GROUP BY conversation_id
ORDER BY message_count DESC;
```

---

## Success Criteria

✅ **All servers start without errors**
- Main backend on port 8001
- Chatbot backend on port 8002
- Frontend on port 3000

✅ **All 6 user stories work correctly**
- US1: Create task via chat
- US2: List tasks via chat
- US3: Complete task via chat
- US4: Maintain conversation context
- US5: Update task via chat
- US6: Delete task via chat

✅ **Database operations succeed**
- Conversations are created
- Messages are stored
- Task operations work
- Indexes are used (check EXPLAIN ANALYZE)

✅ **No security vulnerabilities**
- No eval() usage
- Credentials not exposed
- JWT authentication works
- User isolation enforced

---

## Next Steps

After successful local testing:
1. Review deployment documentation (phase4-chatbot/docs/DEPLOYMENT_CHECKLIST.md)
2. Run database migration on production database
3. Deploy chatbot backend to Hugging Face Spaces
4. Deploy frontend to Vercel
5. Configure production environment variables
6. Test production deployment

---

**Questions or Issues?**
- Check troubleshooting section above
- Review error logs in terminal windows
- Check browser console (F12) for frontend errors
- Verify all environment variables are set correctly
