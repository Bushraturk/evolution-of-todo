"""Agent service using native Google Generative AI SDK.

This uses the official Google Generative AI Python SDK for more reliable Gemini integration.
"""
import os
import json
import logging
from typing import Any, Dict, List, Optional

import google.generativeai as genai
from tenacity import (
    retry,
    stop_after_attempt,
    wait_exponential,
    retry_if_exception_type
)

logger = logging.getLogger(__name__)


# Custom exceptions
class AgentRateLimitError(Exception):
    """Raised when API rate limit is exceeded."""
    pass


class AgentAPIError(Exception):
    """Raised when API returns an error."""
    pass


class AgentTimeoutError(Exception):
    """Raised when API request times out."""
    pass


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
    """Service for Gemini function calling using native SDK."""

    def __init__(
        self,
        mcp_handlers,
        api_key: str = None,
        model: str = "gemini-1.5-flash",
        timeout: int = 30,
        max_retries: int = 3
    ):
        """Initialize agent service.

        Args:
            mcp_handlers: TaskHandlers instance for tool execution
            api_key: Gemini API key
            model: Gemini model name (gemini-1.5-flash or gemini-1.5-pro)
            timeout: Request timeout
            max_retries: Maximum retry attempts
        """
        self.handlers = mcp_handlers
        self.model_name = model
        self.timeout = timeout
        self.max_retries = max_retries

        # Configure Gemini
        genai.configure(api_key=api_key or os.getenv("GEMINI_API_KEY"))

        # Define function declarations for Gemini
        self.tools = [
            genai.protos.Tool(
                function_declarations=[
                    genai.protos.FunctionDeclaration(
                        name="add_task",
                        description="Create a new task for the user",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "title": genai.protos.Schema(type=genai.protos.Type.STRING, description="Task title"),
                                "description": genai.protos.Schema(type=genai.protos.Type.STRING, description="Optional task description"),
                            },
                            required=["title"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="list_tasks",
                        description="Retrieve tasks from the user's task list",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "status": genai.protos.Schema(
                                    type=genai.protos.Type.STRING,
                                    description="Filter tasks by status",
                                    enum=["all", "pending", "completed"]
                                ),
                            }
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="complete_task",
                        description="Mark a task as complete",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "task_id": genai.protos.Schema(type=genai.protos.Type.STRING, description="ID of the task to complete"),
                            },
                            required=["task_id"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="update_task",
                        description="Modify a task's title or description",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "task_id": genai.protos.Schema(type=genai.protos.Type.STRING, description="ID of the task to update"),
                                "title": genai.protos.Schema(type=genai.protos.Type.STRING, description="New title for the task"),
                                "description": genai.protos.Schema(type=genai.protos.Type.STRING, description="New description for the task"),
                            },
                            required=["task_id"]
                        )
                    ),
                    genai.protos.FunctionDeclaration(
                        name="delete_task",
                        description="Remove a task from the user's list",
                        parameters=genai.protos.Schema(
                            type=genai.protos.Type.OBJECT,
                            properties={
                                "task_id": genai.protos.Schema(type=genai.protos.Type.STRING, description="ID of the task to delete"),
                            },
                            required=["task_id"]
                        )
                    ),
                ]
            )
        ]

        # Try multiple model names with fallback
        model_names_to_try = [
            model,  # User-specified model first
            "gemini-pro",  # Most stable
            "gemini-1.0-pro",  # Explicit version
            "models/gemini-pro",  # With prefix
            "gemini-1.5-pro",  # Newer version
            "gemini-1.5-flash",  # Flash version
        ]

        # Remove duplicates while preserving order
        seen = set()
        model_names_to_try = [x for x in model_names_to_try if not (x in seen or seen.add(x))]

        initialized = False
        last_error = None

        for model_name in model_names_to_try:
            try:
                logger.info(f"Trying to initialize Gemini model: {model_name}")
                self.model = genai.GenerativeModel(
                    model_name=model_name,
                    tools=self.tools,
                    system_instruction=AGENT_INSTRUCTIONS
                )
                self.model_name = model_name
                initialized = True
                logger.info(f"✅ Successfully initialized with model: {model_name}")
                break
            except Exception as e:
                last_error = e
                logger.warning(f"❌ Failed to initialize {model_name}: {str(e)}")
                continue

        if not initialized:
            error_msg = f"Failed to initialize any Gemini model. Last error: {last_error}"
            logger.error(error_msg)
            raise AgentAPIError(error_msg)

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
        retry=retry_if_exception_type((AgentRateLimitError, AgentTimeoutError))
    )
    async def run_conversation(
        self,
        messages: List[Dict[str, str]],
        user_id: str
    ) -> Dict[str, Any]:
        """Run conversation with Gemini using function calling.

        Args:
            messages: List of conversation messages
            user_id: User ID for tool execution

        Returns:
            Dict with response and tool_calls
        """
        try:
            # Convert messages to Gemini format
            history = []
            user_message = ""

            for msg in messages:
                role = msg["role"]
                content = msg["content"]

                if role == "user":
                    user_message = content
                elif role == "assistant":
                    history.append({
                        "role": "model",
                        "parts": [content]
                    })

            # Start chat session
            chat = self.model.start_chat(history=history if history else None)

            # Send message
            response = chat.send_message(user_message)

            tool_calls = []
            final_response = ""

            # Process function calls
            for part in response.parts:
                if fn := part.function_call:
                    # Execute the function
                    function_name = fn.name
                    function_args = dict(fn.args)

                    logger.info(f"Executing function: {function_name} with args: {function_args}")

                    try:
                        result = await self._execute_tool(function_name, function_args, user_id)

                        # Record tool call
                        tool_calls.append({
                            "tool": function_name,
                            "parameters": function_args,
                            "result": result
                        })

                        # Send function response back to model
                        function_response = genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response={"result": result}
                            )
                        )

                        response = chat.send_message(function_response)

                    except Exception as e:
                        logger.error(f"Error executing tool {function_name}: {e}")
                        # Send error back to model
                        function_response = genai.protos.Part(
                            function_response=genai.protos.FunctionResponse(
                                name=function_name,
                                response={"error": str(e)}
                            )
                        )
                        response = chat.send_message(function_response)

            # Get final text response
            final_response = response.text

            return {
                "response": final_response,
                "tool_calls": tool_calls
            }

        except Exception as e:
            logger.error(f"Error in run_conversation: {e}", exc_info=True)
            raise AgentAPIError(f"AI service error: {str(e)}")
