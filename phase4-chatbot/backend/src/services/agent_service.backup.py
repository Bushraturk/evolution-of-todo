"""Agent service for OpenAI Agents SDK integration.

This service manages the AI agent that interprets natural language
and invokes MCP tools for task operations.
"""
import json
import logging
from typing import Any, Dict, List, Optional

from openai import OpenAI, AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

logger = logging.getLogger(__name__)


# Agent instructions prompt template
AGENT_INSTRUCTIONS = """You are a helpful assistant for managing todo tasks. Users can:
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
"""


class AgentService:
    """Service for managing OpenAI Agents SDK integration.

    This service creates and runs AI agents with tool capabilities
    for natural language task management.
    """

    def __init__(
        self,
        llm_client: AsyncOpenAI,
        mcp_handlers,
        model: str = "gemini-2.0-flash-exp",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize agent service.

        Args:
            llm_client: AsyncOpenAI client instance (configured for Gemini)
            mcp_handlers: TaskHandlers instance for tool execution
            model: LLM model name (default: gemini-2.0-flash-exp)
            timeout: Request timeout in seconds (default: 30)
            max_retries: Maximum retry attempts (default: 3)
        """
        self.client = llm_client
        self.handlers = mcp_handlers
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,))
    )
    async def run_conversation(
        self,
        messages: List[Dict[str, str]],
        user_id: str
    ) -> Dict[str, Any]:
        """Run agent conversation with tool support.

        Args:
            messages: List of conversation messages
            user_id: User ID for tool operations

        Returns:
            Dict with response and tool_calls

        Raises:
            Exception: If agent execution fails after retries
        """
        try:
            # Define tools for the agent
            tools = [
                {
                    "type": "function",
                    "function": {
                        "name": "add_task",
                        "description": "Create a new task for the user",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "title": {
                                    "type": "string",
                                    "description": "Task title"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "Optional task description"
                                }
                            },
                            "required": ["title"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "list_tasks",
                        "description": "Retrieve tasks from the user's task list",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "status": {
                                    "type": "string",
                                    "enum": ["all", "pending", "completed"],
                                    "description": "Filter tasks by status"
                                }
                            }
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "complete_task",
                        "description": "Mark a task as complete",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "string",
                                    "description": "ID of the task to complete"
                                }
                            },
                            "required": ["task_id"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "update_task",
                        "description": "Modify a task's title or description",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "string",
                                    "description": "ID of the task to update"
                                },
                                "title": {
                                    "type": "string",
                                    "description": "New task title"
                                },
                                "description": {
                                    "type": "string",
                                    "description": "New task description"
                                }
                            },
                            "required": ["task_id"]
                        }
                    }
                },
                {
                    "type": "function",
                    "function": {
                        "name": "delete_task",
                        "description": "Remove a task from the user's list",
                        "parameters": {
                            "type": "object",
                            "properties": {
                                "task_id": {
                                    "type": "string",
                                    "description": "ID of the task to delete"
                                }
                            },
                            "required": ["task_id"]
                        }
                    }
                }
            ]

            # Call Gemini API with tools (using OpenAI-compatible endpoint)
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": AGENT_INSTRUCTIONS},
                    *messages
                ],
                tools=tools,
                tool_choice="auto",
                timeout=self.timeout
            )

            assistant_message = response.choices[0].message
            tool_calls_data = []

            # Execute tool calls if present
            if assistant_message.tool_calls:
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    # Execute the tool
                    result = await self._execute_tool(
                        function_name,
                        function_args,
                        user_id
                    )

                    tool_calls_data.append({
                        "tool": function_name,
                        "parameters": {**function_args, "user_id": user_id},
                        "result": result
                    })

            return {
                "response": assistant_message.content or "Action completed.",
                "tool_calls": tool_calls_data
            }

        except Exception as e:
            logger.error(f"Error in agent conversation: {e}")
            raise

    async def _execute_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        user_id: str
    ) -> Any:
        """Execute a tool by name.

        Args:
            tool_name: Name of the tool to execute
            args: Tool arguments
            user_id: User ID for the operation

        Returns:
            Tool execution result

        Raises:
            ValueError: If tool name is unknown
        """
        # Map tool names to handler methods
        tool_map = {
            "add_task": self.handlers.add_task,
            "list_tasks": self.handlers.list_tasks,
            "complete_task": self.handlers.complete_task,
            "update_task": self.handlers.update_task,
            "delete_task": self.handlers.delete_task
        }

        if tool_name not in tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")

        # Execute the tool with user_id
        handler = tool_map[tool_name]
        return await handler(user_id=user_id, **args)
