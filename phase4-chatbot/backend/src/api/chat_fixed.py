"""Fixed chat endpoint using OpenAI Agents SDK with Gemini.

This endpoint handles chat requests and uses the agent service
to process natural language commands.
"""
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from ..auth.dependencies import get_current_user
from ..database import get_session
from ..models import MessageRole
from ..services.agent_service_fixed import AgentService
from ..services.conversation_service import ConversationService
from ..services.task_operations import TaskOperations
from ..mcp.handlers import TaskHandlers
from ..main_fixed import get_gemini_client

logger = logging.getLogger(__name__)

router = APIRouter()


# Request/Response schemas
class ChatRequest(BaseModel):
    """Chat request schema."""
    conversation_id: Optional[str] = Field(
        None,
        description="Existing conversation ID to continue (creates new if not provided)"
    )
    message: str = Field(
        ...,
        min_length=1,
        max_length=2000,
        description="User's natural language message"
    )


class ToolCall(BaseModel):
    """Tool call information."""
    tool: str
    parameters: dict
    result: dict


class ChatResponse(BaseModel):
    """Chat response schema."""
    conversation_id: str = Field(description="Conversation ID for this session")
    response: str = Field(description="AI assistant's response")
    tool_calls: list[ToolCall] = Field(
        default_factory=list,
        description="List of tools invoked during this turn"
    )


@router.post("/{user_id}/chat", response_model=ChatResponse)
async def chat(
    user_id: str,
    request: ChatRequest,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user),
    gemini_client = Depends(get_gemini_client)
):
    """Chat endpoint for natural language task management.

    This endpoint:
    1. Receives user message
    2. Loads conversation history from database
    3. Runs agent with MCP tools
    4. Stores messages in database
    5. Returns AI response

    Args:
        user_id: User ID from path
        request: Chat request with message and optional conversation_id
        session: Database session
        current_user: Authenticated user from JWT
        gemini_client: Gemini API client

    Returns:
        ChatResponse with AI response and tool calls

    Raises:
        HTTPException: 400 (validation), 401 (auth), 403 (forbidden), 500 (server error)
    """
    try:
        # Verify user_id matches authenticated user
        if user_id != current_user.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access other user's conversations"
            )

        logger.info(f"Chat request from user {user_id}: {request.message[:50]}...")

        # Initialize services
        conv_service = ConversationService(session)
        task_ops = TaskOperations(session)
        task_handlers = TaskHandlers(task_ops)
        agent_service = AgentService(
            llm_client=gemini_client,
            mcp_handlers=task_handlers,
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp")
        )

        # Get or create conversation
        if request.conversation_id:
            # Load existing conversation
            try:
                conversation_id = request.conversation_id
                history = await conv_service.load_conversation_history(
                    conversation_id,
                    user_id
                )
                logger.info(f"Loaded {len(history)} messages from conversation {conversation_id}")
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Conversation not found: {str(e)}"
                )
        else:
            # Create new conversation
            conversation = await conv_service.create_conversation(user_id)
            conversation_id = str(conversation.id)
            history = []
            logger.info(f"Created new conversation {conversation_id}")

        # Store user message
        await conv_service.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=MessageRole.USER,
            content=request.message
        )

        # Build messages array for agent
        messages = []
        for msg in history:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })

        # Add current user message
        messages.append({
            "role": "user",
            "content": request.message
        })

        # Run agent
        logger.info(f"Running agent with {len(messages)} messages")
        result = await agent_service.run_conversation(messages, user_id)

        # Store assistant response
        await conv_service.add_message(
            conversation_id=conversation_id,
            user_id=user_id,
            role=MessageRole.ASSISTANT,
            content=result["response"]
        )

        logger.info(f"Chat completed successfully. Tools called: {len(result['tool_calls'])}")

        return ChatResponse(
            conversation_id=conversation_id,
            response=result["response"],
            tool_calls=[ToolCall(**tc) for tc in result["tool_calls"]]
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error in chat endpoint: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal server error: {str(e)}"
        )


@router.get("/{user_id}/conversations")
async def list_conversations(
    user_id: str,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """List user's conversations.

    Args:
        user_id: User ID from path
        session: Database session
        current_user: Authenticated user

    Returns:
        List of conversations
    """
    if user_id != current_user.get("user_id"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot access other user's conversations"
        )

    # TODO: Implement conversation listing
    return {"conversations": []}


import os
