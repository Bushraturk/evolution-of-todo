# OpenAI Agents SDK + Gemini API - Complete Setup Guide

## What Was Wrong & What's Fixed

### ❌ Original Implementation Issues

1. **Not Using Agents SDK Pattern**: Used basic `chat.completions.create()` without proper tool calling loop
2. **Missing Tool Result Feedback**: Tools were called but results weren't sent back to LLM
3. **Gemini Endpoint Issues**: OpenAI-compatible endpoint has limitations with function calling
4. **No ChatKit Frontend**: Custom React components instead of official ChatKit

### ✅ Fixed Implementation

1. **Proper Agent Loop**:
   - Call LLM with tools
   - Execute tools
   - Send results back to LLM
   - Get final response

2. **Complete Tool Calling**:
   - Tool calls logged with IDs
   - Results sent back as "tool" role messages
   - Second LLM call with tool results

3. **Better Error Handling**:
   - Retry logic with exponential backoff
   - Tool execution error handling
   - Proper logging

4. **OpenAI ChatKit Frontend**: Official UI component (next section)

---

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    OpenAI ChatKit (Frontend)                 │
│  - Official React component                                  │
│  - Handles UI, message display, input                        │
│  - Requires domain allowlist configuration                   │
└────────────────────────────┬────────────────────────────────┘
                             │ HTTP POST /api/{user_id}/chat
                             ▼
┌─────────────────────────────────────────────────────────────┐
│                  FastAPI Backend (Port 8002)                 │
│                                                              │
│  ┌──────────────────────────────────────────────────────┐  │
│  │            Chat Endpoint (chat_fixed.py)             │  │
│  │  - Receives message                                  │  │
│  │  - Loads conversation history                        │  │
│  │  - Calls AgentService                                │  │
│  │  - Stores messages                                   │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │       AgentService (agent_service_fixed.py)          │  │
│  │                                                       │  │
│  │  1. Call Gemini with tools                           │  │
│  │  2. If tools called → execute them                   │  │
│  │  3. Send tool results back to Gemini                 │  │
│  │  4. Get final response                               │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
│                       ▼                                     │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         TaskHandlers (MCP Tools)                     │  │
│  │  - add_task                                          │  │
│  │  - list_tasks                                        │  │
│  │  - complete_task                                     │  │
│  │  - update_task                                       │  │
│  │  - delete_task                                       │  │
│  └────────────────────┬─────────────────────────────────┘  │
│                       │                                     │
└───────────────────────┼─────────────────────────────────────┘
                        │
                        ▼
              ┌──────────────────┐
              │   Neon Database  │
              │  - tasks         │
              │  - conversations │
              │  - messages      │
              └──────────────────┘
```

---

## Step 1: Update Backend Files

### Replace Files

```bash
# Backup originals
cd phase4-chatbot/backend/src
cp services/agent_service.py services/agent_service.backup.py
cp main.py main.backup.py
cp api/chat.py api/chat.backup.py

# Use fixed versions
cp services/agent_service_fixed.py services/agent_service.py
cp main_fixed.py main.py
cp api/chat_fixed.py api/chat.py
```

### Key Changes in Fixed Files

**agent_service_fixed.py**:
- ✅ Implements proper agent loop (call → execute tools → send results → final response)
- ✅ Adds tool results as "tool" role messages
- ✅ Makes second API call with tool results
- ✅ Better error handling and logging

**main_fixed.py**:
- ✅ Properly initializes AsyncOpenAI client for Gemini
- ✅ Uses lifespan context manager
- ✅ Provides `get_gemini_client()` dependency

**chat_fixed.py**:
- ✅ Uses fixed AgentService
- ✅ Properly handles conversation history
- ✅ Better error responses

---

## Step 2: Environment Configuration

### Backend .env (phase4-chatbot/backend/.env)

```env
# Database Configuration
DATABASE_URL=postgresql://neondb_owner:npg_DJvwsZ97ikxH@ep-delicate-hill-adi5oaai-pooler.c-2.us-east-1.aws.neon.tech/neondb?sslmode=require

# Gemini API Configuration (OpenAI-compatible endpoint)
GEMINI_API_KEY=AIzaSyBZTL4c7o0NtBLZvKnGh-BshtsLwn3LJlI
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_MODEL=gemini-2.0-flash-exp

# JWT Authentication (from Phase III)
JWT_SECRET=your-secret-key-at-least-32-characters-here
JWT_ALGORITHM=HS256
JWT_EXPIRATION_DAYS=7

# Server Configuration
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
DEBUG=true
LOG_LEVEL=INFO

# Agent Configuration
MAX_CONVERSATION_HISTORY=50
CONVERSATION_ARCHIVE_DAYS=90
LLM_REQUEST_TIMEOUT=30
LLM_MAX_RETRIES=3
```

---

## Step 3: OpenAI ChatKit Frontend Setup

### Install Dependencies

```bash
cd frontend
npm install @openai/chatkit
```

### Create ChatKit Page (frontend/src/app/chat-openai/page.tsx)

```typescript
'use client';

import { ChatKit } from '@openai/chatkit';
import { useSession } from '@/lib/auth-client';
import { useRouter } from 'next/navigation';
import { useEffect, useState } from 'react';

export default function ChatOpenAIPage() {
  const { data: session, isPending } = useSession();
  const router = useRouter();
  const [conversationId, setConversationId] = useState<string | null>(null);

  useEffect(() => {
    if (!isPending && !session) {
      router.push('/auth/signin');
    }
  }, [session, isPending, router]);

  if (isPending) {
    return <div className="flex items-center justify-center min-h-screen">Loading...</div>;
  }

  if (!session) {
    return null;
  }

  const userId = session.user.id;
  const token = localStorage.getItem('auth_token');

  // ChatKit configuration
  const chatKitConfig = {
    // Backend endpoint
    endpoint: `${process.env.NEXT_PUBLIC_CHAT_API_URL}/api/${userId}/chat`,

    // Request headers
    headers: {
      'Authorization': `Bearer ${token}`,
      'Content-Type': 'application/json',
    },

    // Transform request to match our API
    transformRequest: (message: string) => ({
      conversation_id: conversationId,
      message: message,
    }),

    // Transform response from our API
    transformResponse: (data: any) => {
      // Save conversation ID for next request
      if (data.conversation_id) {
        setConversationId(data.conversation_id);
      }

      return {
        message: data.response,
        // Optional: show tool calls in UI
        metadata: data.tool_calls?.length > 0 ? {
          tools_used: data.tool_calls.map((tc: any) => tc.tool).join(', ')
        } : undefined
      };
    },
  };

  return (
    <div className="flex flex-col h-screen">
      {/* Header */}
      <div className="bg-white border-b px-6 py-4">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-2xl font-bold text-gray-900">AI Todo Assistant</h1>
            <p className="text-sm text-gray-600">Powered by OpenAI Agents SDK + Gemini</p>
          </div>
          <button
            onClick={() => router.push('/dashboard')}
            className="px-4 py-2 text-sm font-medium text-gray-700 bg-white border border-gray-300 rounded-md hover:bg-gray-50"
          >
            Back to Dashboard
          </button>
        </div>
      </div>

      {/* ChatKit Component */}
      <div className="flex-1 overflow-hidden">
        <ChatKit
          config={chatKitConfig}
          placeholder="Ask me to manage your tasks... (e.g., 'Add a task to buy groceries')"
          welcomeMessage="👋 Hi! I'm your AI todo assistant. I can help you create, view, update, and complete tasks using natural language."
        />
      </div>
    </div>
  );
}
```

### Update Navigation (frontend/src/components/UserNav.tsx)

Add link to ChatKit page:

```typescript
<Link
  href="/chat-openai"
  className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
>
  AI Chat (ChatKit)
</Link>
```

---

## Step 4: Domain Allowlist Configuration

### For Production Deployment

1. **Deploy Frontend First**:
   ```bash
   # Deploy to Vercel
   vercel --prod
   # Get URL: https://your-app.vercel.app
   ```

2. **Add Domain to OpenAI Allowlist**:
   - Go to: https://platform.openai.com/settings/organization/security/domain-allowlist
   - Click "Add domain"
   - Enter: `https://your-app.vercel.app`
   - Save changes

3. **Get Domain Key**:
   - OpenAI will provide a domain key
   - Add to Vercel environment variables:
     ```
     NEXT_PUBLIC_OPENAI_DOMAIN_KEY=your-domain-key-here
     ```

4. **Update ChatKit Config**:
   ```typescript
   <ChatKit
     config={chatKitConfig}
     domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
   />
   ```

### For Local Development

Local development (`localhost`) typically works without domain allowlist configuration.

---

## Step 5: Testing the Complete Setup

### Start All Servers

**Terminal 1 - Main Backend (Port 8001)**:
```bash
cd backend
python -m uvicorn src.main:app --reload --port 8001
```

**Terminal 2 - Chatbot Backend (Port 8002)**:
```bash
cd phase4-chatbot/backend
python -m uvicorn src.main:app --reload --port 8002
```

**Terminal 3 - Frontend (Port 3000)**:
```bash
cd frontend
npm run dev
```

### Test Scenarios

1. **Create Task**:
   - User: "Add a task to buy groceries"
   - Expected: Task created, confirmation message

2. **List Tasks**:
   - User: "Show me all my tasks"
   - Expected: List of tasks displayed

3. **Complete Task**:
   - User: "Mark task 1 as complete"
   - Expected: Task marked complete, confirmation

4. **Update Task**:
   - User: "Change task 2 to 'Call mom tonight'"
   - Expected: Task updated, confirmation

5. **Delete Task**:
   - User: "Delete task 3"
   - Expected: Task deleted, confirmation

6. **Conversation Continuity**:
   - User: "Add a task to pay bills"
   - User: "Show my tasks"
   - Expected: Both tasks visible, conversation context maintained

---

## Step 6: Debugging

### Check Logs

**Backend Logs** (Terminal 2):
```
INFO - Starting agent conversation for user xyz
INFO - Agent called 1 tools
INFO - Executing tool: add_task with args: {'title': 'Buy groceries'}
INFO - Tool add_task executed successfully
INFO - Chat completed successfully. Tools called: 1
```

### Common Issues

**Issue 1: "Tool not found" error**
- **Cause**: Tool name mismatch
- **Fix**: Check tool names in `agent_service_fixed.py` match `handlers.py`

**Issue 2: "Conversation not found"**
- **Cause**: Invalid conversation_id
- **Fix**: Start new conversation (don't pass conversation_id)

**Issue 3: "Gemini API error"**
- **Cause**: Invalid API key or rate limit
- **Fix**: Check GEMINI_API_KEY in .env

**Issue 4: ChatKit not loading**
- **Cause**: Domain not allowlisted (production only)
- **Fix**: Add domain to OpenAI allowlist or use localhost

---

## Key Differences: Original vs Fixed

| Aspect | Original | Fixed |
|--------|----------|-------|
| **Agent Loop** | Single API call | Call → Execute → Send Results → Final Response |
| **Tool Results** | Not sent back to LLM | Sent as "tool" role messages |
| **Error Handling** | Basic try-catch | Retry logic + detailed logging |
| **Frontend** | Custom React | OpenAI ChatKit (official) |
| **Conversation** | Basic history | Proper message threading |

---

## Production Deployment Checklist

- [ ] Backend deployed to Hugging Face Spaces / Railway
- [ ] Frontend deployed to Vercel
- [ ] Domain added to OpenAI allowlist
- [ ] Environment variables configured
- [ ] Database migrations run
- [ ] Health check endpoint working
- [ ] CORS configured correctly
- [ ] JWT authentication working
- [ ] Conversation persistence tested
- [ ] All 5 MCP tools functional

---

## Next Steps

1. **Test Locally**: Run all 3 servers and test each scenario
2. **Fix Any Issues**: Check logs and debug
3. **Deploy Backend**: Push to Hugging Face Spaces
4. **Deploy Frontend**: Push to Vercel
5. **Configure Domain**: Add to OpenAI allowlist
6. **Final Testing**: Test production deployment

---

## Support

If you encounter issues:
1. Check backend logs (Terminal 2)
2. Check browser console (F12)
3. Verify environment variables
4. Test each component separately
5. Review this guide step-by-step

**The key fix is the proper agent loop in `agent_service_fixed.py` - this is what makes tool calling work correctly with Gemini!**
