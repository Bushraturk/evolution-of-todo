# Research & Technical Decisions: AI-Powered Todo Chatbot

**Feature**: 004-ai-chatbot
**Date**: 2026-01-29
**Purpose**: Resolve technical unknowns and establish implementation patterns

## Executive Summary

This document consolidates research findings for implementing an AI-powered chatbot using MCP (Model Context Protocol) architecture with OpenAI Agents SDK. Key decisions include: separate module structure for MCP tool handlers, paginated conversation history loading, graceful degradation for OpenAI API errors, 90-day conversation archival, and JWT-based authentication integration with existing Phase III system.

---

## 1. OpenAI Agents SDK Integration

### Research Question
How to integrate OpenAI Agents SDK with FastAPI for tool-based task operations?

### Findings

**OpenAI Agents SDK Architecture**:
- Agents SDK provides `Agent` class for defining AI agents with tool capabilities
- `Runner` class executes agent with conversation history and tool registry
- Tools are defined as Python functions with type hints and docstrings
- SDK handles tool invocation, parameter validation, and response formatting

**FastAPI Integration Pattern**:
```python
# Recommended approach
from openai import OpenAI
from openai.agents import Agent, Runner

# Initialize in service layer
class AgentService:
    def __init__(self, openai_client: OpenAI):
        self.client = openai_client
        self.agent = Agent(
            name="todo_assistant",
            instructions="You are a helpful assistant for managing todo tasks...",
            tools=[add_task, list_tasks, complete_task, delete_task, update_task]
        )

    async def run_conversation(self, messages: list, tools: list):
        runner = Runner(agent=self.agent, client=self.client)
        result = await runner.run(messages=messages)
        return result
```

**Best Practices**:
- Initialize OpenAI client once at application startup (dependency injection)
- Create agent instance per request to avoid state leakage
- Use async/await for non-blocking I/O
- Implement timeout handling (default: 30s)
- Log all agent interactions for debugging

### Decision

**Approach**: Service layer pattern with dependency injection
- Create `AgentService` class in `services/agent_service.py`
- Initialize OpenAI client in `main.py` and inject into service
- Agent instance created per request with conversation history
- Tools registered at service initialization

**Rationale**: Separates AI logic from API layer, enables testing, follows FastAPI best practices

---

## 2. MCP Server Implementation

### Research Question
How to structure MCP tool handlers and integrate Official MCP SDK with FastAPI?

### Findings

**Official MCP SDK Structure**:
- MCP SDK provides `Server` class for tool registration
- Tools defined as async functions with JSON schema validation
- Server runs as separate process or embedded in application
- Communication via stdio, HTTP, or WebSocket transport

**Tool Handler Patterns**:

**Option A: Inline Handlers** (Simple, less modular)
```python
@mcp_server.tool()
async def add_task(user_id: str, title: str, description: str = None):
    # Direct database access
    task = Task(user_id=user_id, title=title, description=description)
    session.add(task)
    session.commit()
    return {"task_id": task.id, "status": "created"}
```

**Option B: Separate Modules** (Recommended, more testable)
```python
# mcp/handlers.py
class TaskHandlers:
    def __init__(self, task_service: TaskService):
        self.task_service = task_service

    async def add_task(self, user_id: str, title: str, description: str = None):
        return await self.task_service.create_task(user_id, title, description)

# mcp/server.py
def register_tools(mcp_server: Server, handlers: TaskHandlers):
    mcp_server.tool()(handlers.add_task)
    mcp_server.tool()(handlers.list_tasks)
    # ...
```

**FastAPI Integration**:
- Embed MCP server in FastAPI application lifecycle
- Use startup/shutdown events for server initialization
- Tools access database via service layer (not direct DB access)

### Decision

**Approach**: Separate module structure (Option B)
- `mcp/server.py`: MCP server initialization and lifecycle
- `mcp/tools.py`: Tool definitions with JSON schemas
- `mcp/handlers.py`: Handler classes with business logic delegation
- Handlers delegate to existing `TaskService` from Phase II

**Rationale**:
- Better separation of concerns
- Easier unit testing (mock service layer)
- Reuses existing task business logic
- Follows clean architecture principles

---

## 3. OpenAI ChatKit Frontend

### Research Question
How to integrate ChatKit with Next.js and configure for production deployment?

### Findings

**ChatKit Integration**:
- ChatKit is a React component library from OpenAI
- Requires domain allowlist configuration for production
- Supports custom backend endpoints
- Handles message rendering, input, and streaming

**Next.js Setup**:
```typescript
// app/chat/page.tsx
import { ChatInterface } from '@openai/chatkit';

export default function ChatPage() {
  return (
    <ChatInterface
      apiEndpoint="/api/chat"
      domainKey={process.env.NEXT_PUBLIC_OPENAI_DOMAIN_KEY}
      onMessage={handleMessage}
    />
  );
}
```

**Domain Allowlist Configuration**:
1. Deploy frontend to get production URL
2. Add URL to OpenAI dashboard: Settings → Security → Domain Allowlist
3. Receive domain key from OpenAI
4. Add key to environment variables: `NEXT_PUBLIC_OPENAI_DOMAIN_KEY`

**Authentication Flow**:
- ChatKit sends user token in request headers
- Backend validates token with existing auth system
- User ID extracted from token for task operations

### Decision

**Approach**: Standard ChatKit integration with custom backend
- Use ChatKit React component in Next.js App Router
- Configure domain allowlist after Vercel deployment
- Pass JWT token from existing auth system to ChatKit
- Backend validates token and extracts user_id

**Rationale**:
- Leverages OpenAI's maintained UI components
- Integrates with existing Phase III authentication
- Minimal custom frontend code required

---

## 4. Stateless Architecture Patterns

### Research Question
How to manage conversation state in database for stateless server architecture?

### Findings

**Conversation History Loading**:

**Option A: Full History Load** (Simple, memory intensive)
- Load all messages for conversation on each request
- Simple implementation, no pagination logic
- Risk: Large conversations (>100 messages) cause memory issues

**Option B: Paginated Load** (Recommended, scalable)
- Load last N messages (e.g., 50) for context
- Older messages archived but not loaded
- Reduces memory footprint and query time

**Session Resumption**:
- Store conversation_id in client (localStorage or cookie)
- Client sends conversation_id with each message
- Server loads conversation history from database
- No server-side session state required

**Horizontal Scaling**:
- All state in database (PostgreSQL)
- Any server instance can handle any request
- Load balancer distributes requests across instances
- Database connection pooling for performance

### Decision

**Approach**: Paginated conversation history (last 50 messages)
- Load most recent 50 messages for agent context
- Older messages remain in database but not loaded
- Implement conversation archival after 90 days of inactivity
- Use database indexes on conversation_id and created_at

**Rationale**:
- Balances context quality with performance
- Prevents memory issues with long conversations
- Enables horizontal scaling
- 50 messages provides sufficient context for task operations

---

## 5. Natural Language Intent Recognition

### Research Question
How to design agent prompts for accurate task operation intent extraction?

### Findings

**Prompt Engineering Best Practices**:
- Provide clear instructions with examples
- Define tool usage patterns explicitly
- Include error handling guidance
- Use system message for agent behavior

**Agent Instructions Template**:
```
You are a helpful assistant for managing todo tasks. Users can:
- Create tasks: "Add a task to buy groceries"
- View tasks: "Show me all my tasks" or "What's pending?"
- Complete tasks: "Mark task 3 as complete"
- Update tasks: "Change task 1 to 'Call mom tonight'"
- Delete tasks: "Delete task 2"

Always:
1. Confirm actions with friendly messages
2. Ask for clarification if intent is unclear
3. Handle errors gracefully with helpful suggestions
4. Use the provided tools to perform operations

When users reference tasks ambiguously (e.g., "that task"), use conversation context to identify the task.
```

**Handling Ambiguity**:
- Maintain conversation context in message history
- Ask clarifying questions when intent unclear
- Provide suggestions for valid commands
- Gracefully handle tool execution errors

**Context Maintenance**:
- Include previous messages in agent context
- Agent can reference prior conversation turns
- Tool results included in conversation history

### Decision

**Approach**: Explicit instruction prompt with examples
- Define clear agent instructions with command patterns
- Include all 5 tool operations with examples
- Specify confirmation and error handling behavior
- Maintain full conversation history for context

**Rationale**:
- Improves intent recognition accuracy
- Reduces ambiguous interpretations
- Provides consistent user experience
- Enables context-aware responses

---

## 6. OpenAI API Error Handling

### Research Question
How to handle OpenAI API rate limits, timeouts, and service errors?

### Findings

**Common Error Scenarios**:
- Rate limit exceeded (429)
- API timeout (>30s)
- Service unavailable (503)
- Invalid API key (401)
- Token limit exceeded (400)

**Error Handling Strategies**:

**Rate Limiting**:
- Implement exponential backoff with retry
- Queue requests during rate limit periods
- Return user-friendly error message

**Timeouts**:
- Set request timeout (30s default)
- Return partial response if available
- Log timeout for monitoring

**Service Unavailable**:
- Implement graceful degradation
- Return cached response if available
- Queue message for retry

**Implementation Pattern**:
```python
from tenacity import retry, stop_after_attempt, wait_exponential

@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10)
)
async def call_openai_agent(messages):
    try:
        result = await agent.run(messages, timeout=30)
        return result
    except RateLimitError:
        raise HTTPException(503, "Service temporarily unavailable")
    except TimeoutError:
        raise HTTPException(504, "Request timeout")
    except APIError as e:
        logger.error(f"OpenAI API error: {e}")
        raise HTTPException(500, "Unable to process request")
```

### Decision

**Approach**: Retry with exponential backoff + graceful degradation
- Retry up to 3 times with exponential backoff
- 30-second timeout per request
- Return user-friendly error messages
- Log all errors for monitoring
- No message queuing (keep architecture simple)

**Rationale**:
- Handles transient errors automatically
- Prevents cascading failures
- Maintains user experience during outages
- Simple implementation without queue infrastructure

---

## 7. Conversation Archival

### Research Question
Should we implement conversation archival for old sessions?

### Findings

**Storage Growth**:
- Average conversation: 20 messages
- Average message size: 200 bytes
- 10,000 users × 10 conversations/user × 20 messages = 2M messages
- Storage: 2M × 200 bytes = 400MB (manageable)

**Query Performance**:
- Active conversations (last 30 days): Fast queries with indexes
- Old conversations (>90 days): Rarely accessed
- Archival reduces active dataset size

**Archival Strategies**:

**Option A: No Archival** (Simple, acceptable for MVP)
- Keep all conversations in main table
- Add indexes for performance
- Monitor storage growth

**Option B: Soft Delete** (Recommended, balanced)
- Add `archived_at` timestamp field
- Archive conversations after 90 days of inactivity
- Exclude archived from default queries
- Can restore if needed

**Option C: Move to Archive Table** (Complex, overkill)
- Separate `conversation_archive` table
- Move old conversations periodically
- Requires migration logic

### Decision

**Approach**: Soft delete with 90-day archival (Option B)
- Add `archived_at` field to Conversation model
- Background job archives conversations after 90 days of inactivity
- Default queries exclude archived conversations
- Users can request archived conversation restoration

**Rationale**:
- Balances performance with data retention
- Simple implementation (single field)
- Reversible (can unarchive)
- Sufficient for Phase IV scope

---

## 8. Authentication Integration

### Research Question
How to integrate with existing Phase II/III authentication system?

### Findings

**Existing Auth System** (from Phase III):
- JWT-based authentication
- User model with id, email, hashed_password
- Auth endpoints: /api/auth/login, /api/auth/register, /api/auth/me
- JWT token contains user_id in payload

**Integration Pattern**:
```python
# Reuse existing auth dependency
from backend.src.auth.dependencies import get_current_user

@router.post("/api/{user_id}/chat")
async def chat(
    user_id: str,
    request: ChatRequest,
    current_user: dict = Depends(get_current_user)
):
    # Validate user_id matches authenticated user
    if current_user["id"] != user_id:
        raise HTTPException(403, "Forbidden")

    # Process chat request
    ...
```

**Frontend Integration**:
- Frontend obtains JWT token from existing login flow
- Token stored in localStorage (existing pattern)
- Token sent in Authorization header with chat requests
- ChatKit configured to include token in API calls

### Decision

**Approach**: Reuse existing JWT authentication system
- Import `get_current_user` dependency from Phase III
- Validate user_id in chat endpoint matches authenticated user
- Frontend uses existing token from localStorage
- No changes to existing auth system required

**Rationale**:
- Zero duplication of auth logic
- Consistent security model across phases
- Leverages existing, tested authentication
- Minimal integration code

---

## Technology Stack Summary

| Component | Technology | Version | Rationale |
|-----------|-----------|---------|-----------|
| Backend Framework | FastAPI | 0.109+ | Async support, OpenAPI generation, existing Phase II/III |
| AI Framework | OpenAI Agents SDK | Latest | Official SDK, tool support, maintained by OpenAI |
| MCP | Official MCP SDK | Latest | Standardized protocol, tool interface |
| ORM | SQLModel | 0.0.14+ | Existing Phase II/III, Pydantic integration |
| Database | Neon PostgreSQL | Latest | Existing Phase II/III, serverless scaling |
| Frontend Framework | Next.js | 14+ | Existing Phase II/III, App Router |
| UI Library | OpenAI ChatKit | Latest | Official chat UI, maintained by OpenAI |
| Testing | pytest | Latest | Existing Phase II/III, async support |

---

## Implementation Priorities

### Phase 0 (Foundation)
1. Set up MCP server with tool definitions
2. Implement conversation and message models
3. Create database migrations

### Phase 1 (Core Functionality)
1. Implement MCP tool handlers (delegate to existing TaskService)
2. Create AgentService with OpenAI Agents SDK
3. Build chat endpoint with conversation management
4. Integrate authentication

### Phase 2 (Frontend)
1. Set up ChatKit in Next.js
2. Implement chat API client
3. Configure authentication flow

### Phase 3 (Polish)
1. Add error handling and retry logic
2. Implement conversation archival
3. Add monitoring and logging
4. Deploy and configure domain allowlist

---

## Open Questions & Risks

### Resolved
- ✅ MCP tool handler structure: Separate modules
- ✅ Conversation history loading: Paginated (50 messages)
- ✅ OpenAI API error handling: Retry with backoff
- ✅ Conversation archival: 90-day soft delete
- ✅ Authentication integration: Reuse existing JWT system

### Remaining Risks
- **OpenAI API Costs**: Monitor usage, implement rate limiting if needed
- **Natural Language Accuracy**: Iterate on agent instructions based on testing
- **Database Performance**: Add indexes, monitor query times

---

## References

- OpenAI Agents SDK Documentation: https://platform.openai.com/docs/agents
- Official MCP SDK: https://github.com/modelcontextprotocol/sdk
- OpenAI ChatKit: https://platform.openai.com/docs/chatkit
- FastAPI Documentation: https://fastapi.tiangolo.com
- SQLModel Documentation: https://sqlmodel.tiangolo.com

---

**Status**: ✅ Complete - All technical decisions resolved
**Next Step**: Proceed to Phase 1 (Data Model & Contracts)
