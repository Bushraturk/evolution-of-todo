"""Fixed chat endpoint using OpenAI Agents SDK with Gemini.

This endpoint handles chat requests and uses the agent service
to process natural language commands.
"""
import os
import logging
from typing import Optional, Union, Any
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlmodel import Session

from ..auth.dependencies import get_current_user
from ..database import get_session
from ..models import MessageRole
from ..services.agent_service import (
    AgentService,
    AgentRateLimitError,
    AgentAPIError,
    AgentTimeoutError
)
from ..services.conversation_service import ConversationService
from ..services.task_operations import TaskOperations
from ..mcp.handlers import TaskHandlers

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
    result: Union[dict, list]  # Accept both dict and list (list_tasks returns list)


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
    current_user: dict = Depends(get_current_user)
):
    """Chat endpoint for natural language task management.

    This endpoint:
    1. Receives user message
    2. Loads conversation history from database
    3. Runs agent with MCP tools (using OpenAI Agents SDK)
    4. Stores messages in database
    5. Returns AI response

    Args:
        user_id: User ID from path
        request: Chat request with message and optional conversation_id
        session: Database session
        current_user: Authenticated user from JWT

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

        # Initialize AgentService with Gemini (reliable function calling)
        agent_service = AgentService(
            mcp_handlers=task_handlers,
            api_key=os.getenv("GEMINI_API_KEY"),
            base_url=os.getenv("GEMINI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
            model=os.getenv("GEMINI_MODEL", "gemini-2.0-flash-exp"),
            timeout=int(os.getenv("LLM_REQUEST_TIMEOUT", "30")),
            max_retries=int(os.getenv("LLM_MAX_RETRIES", "3"))
        )

        # Get or create conversation
        is_new_conversation = False
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
                logger.warning(f"Conversation not found: {e}")
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail=f"Conversation not found: {str(e)}"
                )
            except Exception as e:
                logger.error(f"Error loading conversation: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error loading conversation: {str(e)}"
                )
        else:
            # Create new conversation
            try:
                conversation = await conv_service.create_conversation(user_id)
                conversation_id = str(conversation.id)
                history = []
                is_new_conversation = True
                logger.info(f"Created new conversation {conversation_id}")
            except Exception as e:
                logger.error(f"Error creating conversation: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Error creating conversation: {str(e)}"
                )

        # Store user message
        # Skip verification for newly created conversations (not yet committed)
        try:
            await conv_service.add_message(
                conversation_id=conversation_id,
                user_id=user_id,
                role=MessageRole.USER,
                content=request.message,
                skip_verification=is_new_conversation
            )
        except Exception as e:
            logger.error(f"Error storing user message: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error storing message: {str(e)}"
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
        try:
            result = await agent_service.run_conversation(messages, user_id)
        except AgentRateLimitError as e:
            logger.warning(f"Rate limit error for user {user_id}: {e}")
            # Rollback any pending changes
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail=str(e)
            )
        except AgentTimeoutError as e:
            logger.warning(f"Timeout error for user {user_id}: {e}")
            # Rollback any pending changes
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=str(e)
            )
        except AgentAPIError as e:
            logger.error(f"API error for user {user_id}: {e}")
            # Rollback any pending changes
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_502_BAD_GATEWAY,
                detail=str(e)
            )
        except Exception as e:
            logger.error(f"Unexpected error running agent: {e}", exc_info=True)
            # Rollback any pending changes
            session.rollback()
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error processing request: {str(e)}"
            )

        # Store assistant response
        # Skip verification for newly created conversations (not yet committed)
        try:
            await conv_service.add_message(
                conversation_id=conversation_id,
                user_id=user_id,
                role=MessageRole.ASSISTANT,
                content=result["response"],
                skip_verification=is_new_conversation
            )
        except Exception as e:
            logger.error(f"Error storing assistant message: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Error storing response: {str(e)}"
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


@router.get("/{user_id}/conversations/{conversation_id}/history")
async def get_conversation_history(
    user_id: str,
    conversation_id: str,
    session: Session = Depends(get_session),
    current_user: dict = Depends(get_current_user)
):
    """Get conversation history (messages).

    Args:
        user_id: User ID from path
        conversation_id: Conversation ID from path
        session: Database session
        current_user: Authenticated user

    Returns:
        List of messages in the conversation

    Raises:
        HTTPException: 403 (forbidden), 404 (not found), 500 (server error)
    """
    try:
        # Verify user_id matches authenticated user
        if user_id != current_user.get("user_id"):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access other user's conversations"
            )

        logger.info(f"Fetching history for conversation {conversation_id}")

        # Initialize conversation service
        conv_service = ConversationService(session)

        # Load conversation history
        try:
            messages = await conv_service.load_conversation_history(
                conversation_id,
                user_id
            )
        except ValueError as e:
            logger.warning(f"Conversation not found: {e}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Conversation not found: {str(e)}"
            )

        # Format messages for response
        formatted_messages = [
            {
                "role": msg.role,
                "content": msg.content,
                "timestamp": msg.created_at.isoformat()
            }
            for msg in messages
        ]

        logger.info(f"Loaded {len(formatted_messages)} messages for conversation {conversation_id}")

        return {
            "conversation_id": conversation_id,
            "messages": formatted_messages
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching conversation history: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching conversation history: {str(e)}"
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
