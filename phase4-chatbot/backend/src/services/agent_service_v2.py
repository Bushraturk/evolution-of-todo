"""Agent service using proper OpenAI Agents SDK with Gemini - FIXED.

This implementation uses the official OpenAI Agents SDK pattern correctly.
"""
import os
import logging
from typing import Any, Dict, List, Optional

from agents import Agent, Runner, OpenAIChatCompletionsModel, AsyncOpenAI, tool
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
    """Service for OpenAI Agents SDK integration with Gemini.

    This service implements the proper Agents SDK pattern using
    Agent, Runner, and OpenAIChatCompletionsModel.
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
            api_key: Gemini API key (defaults to env var)
            base_url: Gemini base URL (defaults to env var)
            model: Gemini model name (default: gemini-2.0-flash-exp)
            timeout: Request timeout in seconds
            max_retries: Maximum retry attempts
        """
        self.handlers = mcp_handlers
        self.model_name = model
        self.timeout = timeout
        self.max_retries = max_retries

        # Initialize AsyncOpenAI client for Gemini
        self.external_client = AsyncOpenAI(
            api_key=api_key or os.getenv("GEMINI_API_KEY"),
            base_url=base_url or os.getenv(
                "GEMINI_BASE_URL",
                "https://generativelanguage.googleapis.com/v1beta/openai/"
            ),
            timeout=timeout,
            max_retries=max_retries
        )

        # Create OpenAIChatCompletionsModel
        self.llm_model = OpenAIChatCompletionsModel(
            model=model,
            openai_client=self.external_client
        )

        logger.info(f"AgentService initialized with model: {model}")

    def _create_tools_for_agent(self, user_id: str) -> List[Any]:
        """Create tool definitions for the agent using @tool decorator.

        Args:
            user_id: User ID for tool operations

        Returns:
            List of decorated tool functions
        """
        handlers = self.handlers

        @tool
        async def add_task(title: str, description: str = "") -> Dict[str, Any]:
            """Create a new task for the user.

            Args:
                title: Task title (required)
                description: Optional task description
            """
            return await handlers.add_task(user_id=user_id, title=title, description=description)

        @tool
        async def list_tasks(status: str = "all") -> Dict[str, Any]:
            """Retrieve tasks from the user's task list.

            Args:
                status: Filter tasks by status - 'all', 'pending', or 'completed' (default: 'all')
            """
            return await handlers.list_tasks(user_id=user_id, status=status)

        @tool
        async def complete_task(task_id: str) -> Dict[str, Any]:
            """Mark a task as complete.

            Args:
                task_id: ID of the task to mark as complete
            """
            return await handlers.complete_task(user_id=user_id, task_id=task_id)

        @tool
        async def update_task(task_id: str, title: str = None, description: str = None) -> Dict[str, Any]:
            """Modify a task's title or description.

            Args:
                task_id: ID of the task to update
                title: New title for the task (optional)
                description: New description for the task (optional)
            """
            return await handlers.update_task(
                user_id=user_id,
                task_id=task_id,
                title=title,
                description=description
            )

        @tool
        async def delete_task(task_id: str) -> Dict[str, Any]:
            """Remove a task from the user's list.

            Args:
                task_id: ID of the task to delete
            """
            return await handlers.delete_task(user_id=user_id, task_id=task_id)

        # Return decorated tool functions
        return [add_task, list_tasks, complete_task, update_task, delete_task]

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
        """Run agent conversation using OpenAI Agents SDK.

        Args:
            messages: Conversation history (list of {role, content} dicts)
            user_id: User ID for tool operations

        Returns:
            Dict with:
                - response: Final assistant message
                - tool_calls: List of tools that were called

        Raises:
            Exception: If agent execution fails after retries
        """
        try:
            logger.info(f"Starting agent conversation for user {user_id}")

            # Get tools with user_id bound
            tools = self._create_tools_for_agent(user_id)

            # Create Agent with instructions, model, and tools
            agent = Agent(
                name="TodoAssistant",
                instructions=AGENT_INSTRUCTIONS,
                model=self.llm_model,
                tools=tools
            )

            # Get the last user message as input
            user_input = messages[-1]["content"] if messages else ""

            logger.info(f"Running agent with input: {user_input[:50]}...")

            # Run the agent using Runner (async version)
            result = await Runner.run(
                starting_agent=agent,
                input=user_input
            )

            # Extract response from result
            # The result object has different attributes depending on SDK version
            response_text = None

            # Try different ways to get the response
            if hasattr(result, 'final_output'):
                response_text = result.final_output
            elif hasattr(result, 'output'):
                response_text = result.output
            elif hasattr(result, 'content'):
                response_text = result.content
            elif hasattr(result, 'messages') and result.messages:
                # Get last message content
                last_msg = result.messages[-1]
                if hasattr(last_msg, 'content'):
                    response_text = last_msg.content
                elif isinstance(last_msg, dict):
                    response_text = last_msg.get('content', '')

            # Fallback
            if not response_text:
                response_text = str(result) if result else "I'm here to help with your tasks!"

            # Log tool calls if any
            tool_calls_log = []
            if hasattr(result, 'tool_calls') and result.tool_calls:
                for tool_call in result.tool_calls:
                    if isinstance(tool_call, dict):
                        tool_calls_log.append({
                            "tool": tool_call.get("name", "unknown"),
                            "parameters": tool_call.get("arguments", {}),
                            "result": tool_call.get("result", {})
                        })
                logger.info(f"Agent called {len(tool_calls_log)} tools")

            logger.info(f"Agent conversation completed successfully")

            return {
                "response": response_text,
                "tool_calls": tool_calls_log
            }

        except Exception as e:
            logger.error(f"Error in agent conversation: {e}", exc_info=True)
            # Log the result object structure for debugging
            logger.error(f"Result object type: {type(result) if 'result' in locals() else 'N/A'}")
            if 'result' in locals():
                logger.error(f"Result attributes: {dir(result)}")
            raise
