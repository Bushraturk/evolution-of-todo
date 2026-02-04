"""Agent service using OpenAI function calling with Gemini - WORKING VERSION.

This uses direct OpenAI client with function calling instead of Agents SDK.
"""
import os
import json
import logging
from typing import Any, Dict, List, Optional

from openai import AsyncOpenAI
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

logger = logging.getLogger(__name__)


# Agent system instructions
AGENT_INSTRUCTIONS = """You are a helpful AI assistant for managing todo tasks.

Your capabilities:
- Create tasks: When users say "add", "create", "remember", or "new task"
- View tasks: When users ask to "show", "list", "see" their tasks
- Complete tasks: When users say "done", "complete", "finish" a task
- Update tasks: When users want to "change", "update", "modify" a task
- Delete tasks: When users want to "delete", "remove", "cancel" a task

Guidelines:
1. Always confirm actions with friendly, natural responses
2. If task ID is unclear, list tasks first to help user identify
3. Handle errors gracefully with helpful suggestions
4. Be conversational and helpful
5. Use the provided tools to perform all operations

Example interactions:
- "Add a task to buy groceries" → Use add_task tool
- "Show my tasks" → Use list_tasks tool
- "Mark task 3 as done" → Use complete_task tool
- "Change task 1 to 'Call mom tonight'" → Use update_task tool
- "Delete task 2" → Use delete_task tool
"""


class AgentService:
    """Service for OpenAI function calling with Gemini.

    Uses direct OpenAI client with function calling (not Agents SDK).
    """

    def __init__(
        self,
        mcp_handlers,
        api_key: str = None,
        base_url: str = None,
        model: str = "gemini-2.0-flash-exp",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize agent service.

        Args:
            mcp_handlers: TaskHandlers instance for tool execution
            api_key: Gemini API key
            base_url: Gemini base URL
            model: Gemini model name
            timeout: Request timeout
            max_retries: Maximum retry attempts
        """
        self.handlers = mcp_handlers
        self.model = model
        self.timeout = timeout
        self.max_retries = max_retries

        # Initialize AsyncOpenAI client for Gemini
        self.client = AsyncOpenAI(
            api_key=api_key or os.getenv("GEMINI_API_KEY"),
            base_url=base_url or os.getenv(
                "GEMINI_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta/openai/"
            ),
            timeout=timeout,
            max_retries=max_retries
        )

        logger.info(f"AgentService initialized with model: {model}")

    def _get_tools_schema(self) -> List[Dict[str, Any]]:
        """Get OpenAI function calling schema for tools.

        Returns:
            List of tool definitions in OpenAI format
        """
        return [
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
                                "description": "Filter tasks by status",
                                "default": "all"
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
                                "description": "New title for the task"
                            },
                            "description": {
                                "type": "string",
                                "description": "New description for the task"
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

    async def _execute_tool(
        self,
        tool_name: str,
        args: Dict[str, Any],
        user_id: str
    ) -> Dict[str, Any]:
        """Execute a tool by name.

        Args:
            tool_name: Name of the tool
            args: Tool arguments
            user_id: User ID

        Returns:
            Tool execution result
        """
        tool_map = {
            "add_task": self.handlers.add_task,
            "list_tasks": self.handlers.list_tasks,
            "complete_task": self.handlers.complete_task,
            "update_task": self.handlers.update_task,
            "delete_task": self.handlers.delete_task
        }

        if tool_name not in tool_map:
            raise ValueError(f"Unknown tool: {tool_name}")

        handler = tool_map[tool_name]
        result = await handler(user_id=user_id, **args)

        logger.info(f"Tool {tool_name} executed successfully")
        return result

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry_if_exception_type((Exception,))
    )
    async def run_conversation(
        self,
        messages: List[Dict[str, str]],
        user_id: str
    ) -> Dict[str, Any]:
        """Run conversation with function calling.

        Args:
            messages: Conversation history
            user_id: User ID for tool operations

        Returns:
            Dict with response and tool_calls
        """
        try:
            logger.info(f"Starting agent conversation for user {user_id}")

            tools = self._get_tools_schema()
            tool_calls_log = []

            # Build messages with system instruction
            full_messages = [
                {"role": "system", "content": AGENT_INSTRUCTIONS},
                *messages
            ]

            logger.info(f"Running agent with {len(messages)} messages")

            # First API call - get initial response
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=full_messages,
                tools=tools,
                tool_choice="auto",
                timeout=self.timeout
            )

            assistant_message = response.choices[0].message

            # Check if tools were called
            if assistant_message.tool_calls:
                logger.info(f"Agent called {len(assistant_message.tool_calls)} tools")

                # Add assistant's tool call message
                full_messages.append({
                    "role": "assistant",
                    "content": assistant_message.content,
                    "tool_calls": [
                        {
                            "id": tc.id,
                            "type": "function",
                            "function": {
                                "name": tc.function.name,
                                "arguments": tc.function.arguments
                            }
                        }
                        for tc in assistant_message.tool_calls
                    ]
                })

                # Execute each tool call
                for tool_call in assistant_message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)

                    logger.info(f"Executing tool: {function_name} with args: {function_args}")

                    try:
                        result = await self._execute_tool(
                            function_name,
                            function_args,
                            user_id
                        )

                        tool_calls_log.append({
                            "tool": function_name,
                            "parameters": {**function_args, "user_id": user_id},
                            "result": result
                        })

                        # Add tool result
                        full_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps(result)
                        })

                    except Exception as e:
                        logger.error(f"Tool execution error: {e}")
                        full_messages.append({
                            "role": "tool",
                            "tool_call_id": tool_call.id,
                            "content": json.dumps({
                                "status": "error",
                                "message": str(e)
                            })
                        })

                # Second API call - get final response with tool results
                final_response = await self.client.chat.completions.create(
                    model=self.model,
                    messages=full_messages,
                    timeout=self.timeout
                )

                final_message = final_response.choices[0].message.content

            else:
                # No tools called
                final_message = assistant_message.content or "I'm here to help with your tasks!"
                logger.info("No tools called, returning direct response")

            logger.info(f"Agent conversation completed successfully")

            return {
                "response": final_message,
                "tool_calls": tool_calls_log
            }

        except Exception as e:
            logger.error(f"Error in agent conversation: {e}", exc_info=True)
            raise
