---
description: Create a Gemini-powered AI agent using OpenAI Agents SDK with custom tools
---

# Gemini Agent Generator

## User Input

```text
$ARGUMENTS
```

You **MUST** consider the user input before proceeding (if not empty).

## Overview

This skill helps you create AI agents powered by Google's Gemini models using the OpenAI Agents SDK. The agent can:
- Understand natural language queries
- Execute custom tools/functions
- Maintain conversation context
- Handle errors gracefully with automatic retries

**Use Cases**: Task management, customer support, data analysis, automation, chatbots, and more.

## Quick Start (5 Minutes)

Here's a minimal working example:

```python
import os
from openai import AsyncOpenAI

# 1. Initialize Gemini client
client = AsyncOpenAI(
    api_key=os.getenv("GEMINI_API_KEY"),
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/"
)

# 2. Define a simple tool
tools = [{
    "type": "function",
    "function": {
        "name": "get_time",
        "description": "Get current time",
        "parameters": {"type": "object", "properties": {}}
    }
}]

# 3. Run agent
async def run_agent(query):
    response = await client.chat.completions.create(
        model="gemini-2.0-flash-exp",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": query}
        ],
        tools=tools,
        tool_choice="auto"
    )
    return response.choices[0].message.content

# 4. Use it
result = await run_agent("What time is it?")
print(result)
```

## Prerequisites

**Required**:
- Python 3.10 or higher
- Gemini API key (get free key from https://aistudio.google.com/apikey)

**Dependencies**:
```bash
pip install openai>=1.0.0 tenacity>=8.2.3 python-dotenv>=1.0.0
```

**Environment Variables**:
Create a `.env` file:
```env
GEMINI_API_KEY=your-api-key-here
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_MODEL=gemini-2.0-flash-exp
```

## Step-by-Step Implementation

### Step 1: Set Up Environment

Create your project structure:
```bash
mkdir my-agent
cd my-agent
touch .env agent_service.py config.py tools.py handlers.py main.py
```

Create `.env` file:
```env
# Required
GEMINI_API_KEY=your-gemini-api-key-here

# Optional (with defaults)
GEMINI_BASE_URL=https://generativelanguage.googleapis.com/v1beta/openai/
GEMINI_MODEL=gemini-2.0-flash-exp
LLM_REQUEST_TIMEOUT=30
LLM_MAX_RETRIES=3
```

### Step 2: Create Configuration Module

**File**: `config.py`

```python
"""Configuration management for Gemini agent."""
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Agent configuration from environment variables."""

    # Required
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

    # Optional with defaults
    GEMINI_BASE_URL = os.getenv(
        "GEMINI_BASE_URL",
        "https://generativelanguage.googleapis.com/v1beta/openai/"
    )
    GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
    LLM_REQUEST_TIMEOUT = int(os.getenv("LLM_REQUEST_TIMEOUT", "30"))
    LLM_MAX_RETRIES = int(os.getenv("LLM_MAX_RETRIES", "3"))

    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if not cls.GEMINI_API_KEY:
            raise ValueError(
                "GEMINI_API_KEY is required. "
                "Get your key from https://aistudio.google.com/apikey"
            )

# Validate on import
Config.validate()
```

### Step 3: Define Tools

**File**: `tools.py`

```python
"""Tool definitions in OpenAI function calling format."""

# Example 1: Simple tool (no parameters)
GET_TIME_TOOL = {
    "type": "function",
    "function": {
        "name": "get_current_time",
        "description": "Get the current date and time",
        "parameters": {
            "type": "object",
            "properties": {}
        }
    }
}

# Example 2: Tool with required parameters
ADD_TASK_TOOL = {
    "type": "function",
    "function": {
        "name": "add_task",
        "description": "Create a new task for the user",
        "parameters": {
            "type": "object",
            "properties": {
                "title": {
                    "type": "string",
                    "description": "Task title (what needs to be done)"
                },
                "description": {
                    "type": "string",
                    "description": "Optional detailed description"
                }
            },
            "required": ["title"]
        }
    }
}

# Example 3: Tool with optional parameters
SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "search",
        "description": "Search for information",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "Search query"
                },
                "limit": {
                    "type": "integer",
                    "description": "Maximum number of results",
                    "default": 10
                }
            },
            "required": ["query"]
        }
    }
}

# All available tools
ALL_TOOLS = [
    GET_TIME_TOOL,
    ADD_TASK_TOOL,
    SEARCH_TOOL
]
```

### Step 4: Create Tool Handlers

**File**: `handlers.py`

```python
"""Tool execution handlers."""
import json
from datetime import datetime
from typing import Any, Dict

class ToolHandlers:
    """Handlers for executing tool calls."""

    async def get_current_time(self) -> Dict[str, Any]:
        """Get current time."""
        return {
            "time": datetime.now().isoformat(),
            "timezone": "UTC"
        }

    async def add_task(self, title: str, description: str = None) -> Dict[str, Any]:
        """Add a task (example implementation)."""
        # Replace with your actual task creation logic
        task_id = f"task-{datetime.now().timestamp()}"
        return {
            "task_id": task_id,
            "title": title,
            "description": description,
            "status": "created"
        }

    async def search(self, query: str, limit: int = 10) -> Dict[str, Any]:
        """Search for information (example implementation)."""
        # Replace with your actual search logic
        return {
            "query": query,
            "results": [
                {"title": f"Result {i}", "url": f"https://example.com/{i}"}
                for i in range(min(limit, 3))
            ]
        }

    async def execute(self, tool_name: str, args: Dict[str, Any]) -> Any:
        """Execute a tool by name."""
        # Map tool names to handler methods
        tool_map = {
            "get_current_time": self.get_current_time,
            "add_task": self.add_task,
            "search": self.search
        }

        if tool_name not in tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")

        handler = tool_map[tool_name]
        return await handler(**args)
```

### Step 5: Create Agent Service

**File**: `agent_service.py`

```python
"""Gemini agent service with tool support."""
import json
import logging
from typing import Any, Dict, List

from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

from config import Config
from handlers import ToolHandlers

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# System instructions for the agent
AGENT_INSTRUCTIONS = """You are a helpful AI assistant.

When users ask you to perform actions:
1. Use the available tools to complete the task
2. Confirm actions with friendly messages
3. Ask for clarification if the request is unclear
4. Handle errors gracefully with helpful suggestions

Always be concise, accurate, and helpful."""

class AgentService:
    """Service for managing Gemini agent with tool support."""

    def __init__(self):
        """Initialize agent service."""
        self.client = AsyncOpenAI(
            api_key=Config.GEMINI_API_KEY,
            base_url=Config.GEMINI_BASE_URL
        )
        self.handlers = ToolHandlers()
        self.model = Config.GEMINI_MODEL
        self.timeout = Config.LLM_REQUEST_TIMEOUT

    @retry(
        stop=stop_after_attempt(Config.LLM_MAX_RETRIES),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    async def run_conversation(
        self,
        messages: List[Dict[str, str]],
        tools: List[Dict] = None
    ) -> Dict[str, Any]:
        """Run agent conversation with tool support.

        Args:
            messages: List of conversation messages
            tools: List of tool definitions (optional)

        Returns:
            Dict with response and tool_calls
        """
        try:
            # Prepare messages with system instructions
            full_messages = [
                {"role": "system", "content": AGENT_INSTRUCTIONS},
                *messages
            ]

            # Call Gemini API
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                tools=tools or [],
                tool_choice="auto" if tools else None,
                timeout=self.timeout
            )

            assistant_message = response.choices[0].message
            tool_calls_data = []

            # Execute tool calls if present
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    logger.info(f"Executing tool: {function_name}")

                    # Execute the tool
                    result = await self.handlers.execute(
                        function_name,
                        function_args
                    )

                    tool_calls_data.append({
                        "tool": function_name,
                        "parameters": function_args,
                        "result": result
                    })

            return {
                "response": assistant_message.content or "Action completed.",
                "tool_calls": tool_calls_data
            }

        except Exception as e:
            logger.error(f"Error in agent conversation: {e}")
            raise
```

### Step 6: Create Main Entry Point

**File**: `main.py`

```python
"""Main entry point for Gemini agent."""
import asyncio
from agent_service import AgentService
from tools import ALL_TOOLS

async def main():
    """Run the agent."""
    agent = AgentService()

    # Example conversation
    messages = [
        {"role": "user", "content": "What time is it?"}
    ]

    result = await agent.run_conversation(messages, tools=ALL_TOOLS)

    print(f"Agent: {result['response']}")

    if result['tool_calls']:
        print("\nTool Calls:")
        for call in result['tool_calls']:
            print(f"  - {call['tool']}: {call['result']}")

if __name__ == "__main__":
    asyncio.run(main())
```

## Tool Definition Guide

### Tool Schema Format

Tools use OpenAI function calling format:

```python
{
    "type": "function",
    "function": {
        "name": "tool_name",           # Unique identifier
        "description": "What it does",  # Clear description for AI
        "parameters": {                 # JSON Schema
            "type": "object",
            "properties": {
                "param_name": {
                    "type": "string",   # string, integer, boolean, array, object
                    "description": "What this parameter is for"
                }
            },
            "required": ["param_name"]  # List of required parameters
        }
    }
}
```

### Parameter Types

- `string`: Text values
- `integer`: Whole numbers
- `number`: Decimal numbers
- `boolean`: true/false
- `array`: Lists of values
- `object`: Nested structures
- `enum`: Predefined choices

### Best Practices

1. **Clear Descriptions**: Help the AI understand when to use the tool
2. **Specific Names**: Use descriptive function names (e.g., `create_task` not `do_thing`)
3. **Validate Inputs**: Check parameters in your handler
4. **Return Structured Data**: Use dictionaries with clear keys
5. **Handle Errors**: Return error information in a structured format

## Configuration Reference

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `GEMINI_API_KEY` | Yes | - | Your Gemini API key |
| `GEMINI_BASE_URL` | No | Gemini OpenAI endpoint | Custom API endpoint |
| `GEMINI_MODEL` | No | `gemini-2.0-flash-exp` | Model to use |
| `LLM_REQUEST_TIMEOUT` | No | `30` | Request timeout (seconds) |
| `LLM_MAX_RETRIES` | No | `3` | Max retry attempts |

### Available Models

- `gemini-2.0-flash-exp`: Fast, efficient (recommended)
- `gemini-2.0-flash-thinking-exp`: Advanced reasoning
- `gemini-1.5-pro`: Balanced performance
- `gemini-1.5-flash`: Fast responses

## Error Handling

### Common Errors and Solutions

**1. Missing API Key**
```
ValueError: GEMINI_API_KEY is required
```
**Solution**: Set your API key in `.env` file

**2. Rate Limiting**
```
RateLimitError: Too many requests
```
**Solution**: Automatic retry with exponential backoff (built-in)

**3. Invalid Tool Call**
```
ValueError: Unknown tool: tool_name
```
**Solution**: Ensure tool name matches handler method name

**4. Timeout**
```
TimeoutError: Request timed out
```
**Solution**: Increase `LLM_REQUEST_TIMEOUT` in `.env`

**5. Network Errors**
```
ConnectionError: Failed to connect
```
**Solution**: Check internet connection, automatic retry will attempt 3 times

### Retry Logic

The agent automatically retries failed requests with exponential backoff:
- Attempt 1: Immediate
- Attempt 2: Wait 2 seconds
- Attempt 3: Wait 4 seconds
- Attempt 4: Wait 8 seconds (up to 10 seconds max)

## Usage Examples

### Example 1: Simple Query (No Tools)

```python
import asyncio
from agent_service import AgentService

async def simple_query():
    agent = AgentService()

    messages = [
        {"role": "user", "content": "What is 2+2?"}
    ]

    result = await agent.run_conversation(messages)
    print(result['response'])

asyncio.run(simple_query())
```

### Example 2: Using Tools

```python
import asyncio
from agent_service import AgentService
from tools import ALL_TOOLS

async def with_tools():
    agent = AgentService()

    messages = [
        {"role": "user", "content": "Add a task to buy groceries"}
    ]

    result = await agent.run_conversation(messages, tools=ALL_TOOLS)

    print(f"Response: {result['response']}")

    if result['tool_calls']:
        for call in result['tool_calls']:
            print(f"Tool used: {call['tool']}")
            print(f"Result: {call['result']}")

asyncio.run(with_tools())
```

### Example 3: Multi-Turn Conversation

```python
import asyncio
from agent_service import AgentService
from tools import ALL_TOOLS

async def conversation():
    agent = AgentService()

    messages = []

    # Turn 1
    messages.append({"role": "user", "content": "Add a task to buy milk"})
    result = await agent.run_conversation(messages, tools=ALL_TOOLS)
    messages.append({"role": "assistant", "content": result['response']})
    print(f"Agent: {result['response']}")

    # Turn 2
    messages.append({"role": "user", "content": "What time is it?"})
    result = await agent.run_conversation(messages, tools=ALL_TOOLS)
    print(f"Agent: {result['response']}")

asyncio.run(conversation())
```

### Example 4: Custom Domain Agent

```python
# Customer Support Agent
SUPPORT_INSTRUCTIONS = """You are a customer support agent.
Help users with:
- Order tracking
- Returns and refunds
- Product questions
- Account issues

Always be polite, empathetic, and solution-oriented."""

# Update agent_service.py AGENT_INSTRUCTIONS with SUPPORT_INSTRUCTIONS
```

## Testing Your Agent

### Basic Test

```bash
python main.py
```

Expected output:
```
Agent: The current time is 2026-01-31T18:30:00

Tool Calls:
  - get_current_time: {'time': '2026-01-31T18:30:00', 'timezone': 'UTC'}
```

### Test Checklist

- [ ] Agent responds to simple queries
- [ ] Tools are executed correctly
- [ ] Error handling works (try invalid API key)
- [ ] Retry logic activates on failures
- [ ] Multi-turn conversations maintain context
- [ ] Custom tools can be added
- [ ] Configuration changes take effect

## Troubleshooting

### Agent Not Responding

**Check**:
1. API key is set correctly
2. Internet connection is working
3. No firewall blocking requests
4. Model name is correct

### Tools Not Being Called

**Check**:
1. Tool descriptions are clear
2. Tool names match handler methods
3. Parameters are correctly defined
4. User query clearly indicates tool usage

### Slow Responses

**Solutions**:
1. Use `gemini-2.0-flash-exp` for faster responses
2. Reduce conversation history length
3. Simplify tool schemas
4. Check network latency

## Advanced Topics

### Streaming Responses

```python
async def stream_response(messages, tools):
    stream = await client.chat.completions.create(
        model="gemini-2.0-flash-exp",
        messages=messages,
        tools=tools,
        stream=True
    )

    async for chunk in stream:
        if chunk.choices[0].delta.content:
            print(chunk.choices[0].delta.content, end="")
```

### Conversation History Management

```python
# Keep last N messages
MAX_HISTORY = 10

def trim_history(messages):
    if len(messages) > MAX_HISTORY:
        # Keep system message + last N messages
        return [messages[0]] + messages[-(MAX_HISTORY-1):]
    return messages
```

### Custom Error Handling

```python
try:
    result = await agent.run_conversation(messages, tools)
except ValueError as e:
    print(f"Configuration error: {e}")
except TimeoutError as e:
    print(f"Request timed out: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Security Considerations

### API Key Management

- **Never commit** `.env` files to version control
- Use environment variables in production
- Rotate keys regularly
- Use separate keys for dev/prod

### Input Validation

```python
def validate_input(user_input: str) -> bool:
    """Validate user input before sending to agent."""
    if len(user_input) > 2000:
        raise ValueError("Input too long")
    if not user_input.strip():
        raise ValueError("Input cannot be empty")
    return True
```

### Rate Limiting

```python
from time import time

class RateLimiter:
    def __init__(self, max_requests=10, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = []

    def allow_request(self):
        now = time()
        self.requests = [r for r in self.requests if now - r < self.window]

        if len(self.requests) >= self.max_requests:
            return False

        self.requests.append(now)
        return True
```

## Performance Optimization

### Caching Responses

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def cached_tool_call(tool_name, args_tuple):
    """Cache tool results for identical calls."""
    args = dict(args_tuple)
    return execute_tool(tool_name, args)
```

### Parallel Tool Execution

```python
import asyncio

async def execute_tools_parallel(tool_calls):
    """Execute multiple tools in parallel."""
    tasks = [
        execute_tool(call['name'], call['args'])
        for call in tool_calls
    ]
    return await asyncio.gather(*tasks)
```

### Cost Management

- Use `gemini-2.0-flash-exp` for lower costs
- Implement caching for repeated queries
- Trim conversation history
- Monitor API usage

## Reference Implementation

See working example in this codebase:
- `phase4-chatbot/backend/src/services/agent_service.py` - Agent implementation
- `phase4-chatbot/backend/src/mcp/handlers.py` - Tool handlers
- `phase4-chatbot/backend/src/mcp/tools.py` - Tool definitions
- `phase4-chatbot/backend/src/config.py` - Configuration

## Next Steps

1. **Customize Tools**: Add domain-specific tools for your use case
2. **Enhance Instructions**: Tailor system prompt to your needs
3. **Add Persistence**: Store conversations in database
4. **Build UI**: Create web interface or CLI
5. **Deploy**: Host on cloud platform (Vercel, Railway, etc.)

## Resources

- [Gemini API Documentation](https://ai.google.dev/docs)
- [OpenAI SDK Documentation](https://platform.openai.com/docs/api-reference)
- [Function Calling Guide](https://platform.openai.com/docs/guides/function-calling)
- [Get Gemini API Key](https://aistudio.google.com/apikey)

---

**Created with ❤️ using Claude Code**
