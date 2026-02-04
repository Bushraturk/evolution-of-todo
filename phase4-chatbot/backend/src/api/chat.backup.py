"""Chat API endpoint for natural language task management.

This module provides the chat endpoint that integrates:
- Authentication (reuse from Phase III)
- Conversation management
- OpenAI Agents SDK
- MCP tool handlers
"""
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Request
from pydantic import BaseModel, Field
from sqlmodel import Session

from ..models import MessageRole
from ..auth.dependencies import get_current_user
from ..database import get_session
from ..services.conversation_service import ConversationService
from ..services.agent_service import AgentService
from ..mcp.handlers import TaskHandlers
from ..config import settings

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["chat"])


# Request/Response Schemas

class ChatRequest(BaseModel):
    """Request schema for chat endpoint."""
    conversation_id: Optional[str] = Field(
        None,
        description="Existing conversation ID to continue. Omit to start new conversation."
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's natural language message"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": 123,
                "message": "Add a task to buy groceries"
            }
        }


class ToolCall(BaseModel):
    """Tool call information."""
    tool: str = Field(..., description="Name of the MCP tool invoked")
    parameters: dict = Field(..., description="Parameters passed to the tool")
    result: dict = Field(..., description="Result returned by the tool")


class ChatResponse(BaseModel):
    """Response schema for chat endpoint."""
    conversation_id: str = Field(
        ...,
        description="Conversation ID for this session"
    )
    response: str = Field(
        ...,
        description="AI assistant's natural language response"
    )
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="List of MCP tools invoked"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "conversation_id": 123,
                "response": "I've created a task titled 'Buy groceries' for you.",
                "tool_calls": [
                    {
                        "tool": "add_task",
                        "parameters": {
                            "user_id": "d17cb5d1-5a51-4f2f-9cb8-8cd7f19720e2",
                            "title": "Buy groceries"
                        },
                        "result": {
                            "task_id": "323fc8dc-e29e-4868-aa93-8351ff5f6261",
                            "status": "created",
                            "title": "Buy groceries"
                        }
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Error response schema."""
    detail: str = Field(..., description="Human-readable error message")


# Chat endpoint

@router.post(
    "/{user_id}/chat",
    response_model=ChatResponse,
    responses={
        400: {"model": ErrorResponse, "description": "Bad request"},
        401: {"model": ErrorResponse, "description": "Unauthorized"},
        403: {"model": ErrorResponse, "description": "Forbidden"},
        500: {"model": ErrorResponse, "description": "Internal server error"},
        503: {"model": ErrorResponse, "description": "Service unavailable"}
    }
)
async def chat(
    user_id: str,
    request: ChatRequest,
    app_request: Request,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session)
) -> ChatResponse:
    """Send message to chatbot and receive response.

    The chatbot interprets user intent and performs task operations via MCP tools.
    Conversation state is maintained in the database.

    Args:
        user_id: Authenticated user's ID (must match JWT token)
        request: Chat request with message and optional conversation_id
        current_user: Current authenticated user from JWT
        session: Database session
        app_request: FastAPI request object to access app state

    Returns:
        ChatResponse with assistant's reply and tool calls

    Raises:
        HTTPException: For various error conditions
    """
    try:
        # Validate user_id matches authenticated user
        if current_user["id"] != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Forbidden: Cannot access another user's chat"
            )

        # Validate message
        if not request.message or not request.message.strip():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Message cannot be empty"
            )

        # Initialize services
        conversation_service = ConversationService(
            session=session,
            max_history=settings.max_conversation_history,
            archive_days=settings.conversation_archive_days
        )

        # Initialize TaskOperations (simple wrapper for database operations)
        from ..services.task_operations import TaskOperations
        task_operations = TaskOperations(session=session)

        # Initialize MCP handlers and agent service
        task_handlers = TaskHandlers(task_operations=task_operations)

        # Get Gemini client from app state
        gemini_client = app_request.app.state.gemini_client if app_request else None
        if not gemini_client:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="AI service not available"
            )

        agent_service = AgentService(
            llm_client=gemini_client,
            mcp_handlers=task_handlers,
            model=settings.gemini_model,
            timeout=settings.llm_request_timeout,
            max_retries=settings.llm_max_retries
        )

        # 1. Get or create conversation
        if request.conversation_id:
            # Load existing conversation
            conversation_id = request.conversation_id
            history = await conversation_service.load_conversation_history(
                conversation_id=conversation_id,
                user_id=user_id
            )
        else:
            # Create new conversation
            conversation = await conversation_service.create_conversation(user_id=user_id)
            conversation_id = str(conversation.id)
            history = []

        # 2. Add user message to conversation
        await conversation_service.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=MessageRole.USER,
            content=request.message
        )

        # 3. Prepare conversation history for agent
        messages = [
            {"role": msg.role.value, "content": msg.content}
            for msg in history
        ]
        messages.append({"role": "user", "content": request.message})

        # 4. Run agent with conversation history
        agent_response = await agent_service.run_conversation(
            messages=messages,
            user_id=user_id
        )

        # 5. Add assistant response to conversation
        await conversation_service.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=agent_response["response"]
        )

        # 6. Return response
        return ChatResponse(
            conversation_id=conversation_id,
            response=agent_response["response"],
            tool_calls=[
                ToolCall(**tool_call)
                for tool_call in agent_response.get("tool_calls", [])
            ]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing chat request: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unable to process request: {str(e)}"
        )
