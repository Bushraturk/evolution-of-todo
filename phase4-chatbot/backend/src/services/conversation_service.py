"""Conversation service for managing chat sessions and message history.

This service handles conversation lifecycle, message persistence,
and conversation history retrieval with pagination.
"""
import logging
from datetime import datetime, timedelta, timezone
from typing import List, Optional
from uuid import UUID

from sqlmodel import Session, select, and_

from ..models import Conversation, Message, MessageRole

logger = logging.getLogger(__name__)


class ConversationService:
    """Service for managing conversations and messages.

    Handles conversation creation, message persistence, history retrieval,
    and conversation archival.
    """

    def __init__(self, session: Session, max_history: int = 50, archive_days: int = 90):
        """Initialize conversation service.

        Args:
            session: Database session
            max_history: Maximum messages to load for context (default: 50)
            archive_days: Days of inactivity before archival (default: 90)
        """
        self.session = session
        self.max_history = max_history
        self.archive_days = archive_days

    async def create_conversation(self, user_id: str) -> Conversation:
        """Create a new conversation for the user.

        Args:
            user_id: CUID string of the user (from Better Auth)

        Returns:
            Created Conversation instance

        Raises:
            Exception: If creation fails
        """
        try:
            conversation = Conversation(user_id=user_id)
            self.session.add(conversation)
            self.session.flush()  # Flush to get ID, but don't commit yet
            self.session.refresh(conversation)

            logger.info(f"Created conversation {conversation.id} for user {user_id}")
            return conversation

        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            raise

    async def load_conversation_history(
        self,
        conversation_id: str,
        user_id: str
    ) -> List[Message]:
        """Load conversation history (last N messages, paginated).

        Args:
            conversation_id: String UUID of the conversation
            user_id: CUID string of the user (for security validation)

        Returns:
            List of Message instances (most recent first, then reversed)

        Raises:
            ValueError: If conversation not found or not owned by user
            Exception: If retrieval fails
        """
        try:
            # Verify conversation exists and belongs to user
            # Convert string UUID to UUID object for query
            conv_uuid = UUID(conversation_id) if isinstance(conversation_id, str) else conversation_id
            conversation = self.session.get(Conversation, conv_uuid)

            # Convert both to strings for comparison (handles UUID vs string mismatch)
            conv_user_id = str(conversation.user_id) if conversation else None
            if not conversation or conv_user_id != user_id:
                raise ValueError(f"Conversation {conversation_id} not found or not owned by user")

            # Load last N messages ordered by created_at DESC
            statement = (
                select(Message)
                .where(
                    and_(
                        Message.conversation_id == conversation_id,
                        Message.user_id == user_id
                    )
                )
                .order_by(Message.created_at.desc())
                .limit(self.max_history)
            )

            messages = self.session.exec(statement).all()

            # Reverse to get chronological order (oldest to newest)
            messages_chronological = list(reversed(messages))

            logger.info(
                f"Loaded {len(messages_chronological)} messages for conversation {conversation_id}"
            )
            return messages_chronological

        except ValueError as e:
            logger.warning(f"Validation error loading conversation history: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading conversation history: {e}")
            raise

    async def add_message(
        self,
        conversation_id: str,
        user_id: str,
        role: MessageRole,
        content: str,
        skip_verification: bool = False
    ) -> Message:
        """Add a message to the conversation.

        Args:
            conversation_id: String UUID of the conversation
            user_id: CUID string of the user
            role: Message role (user or assistant)
            content: Message content
            skip_verification: Skip conversation ownership check (for newly created conversations)

        Returns:
            Created Message instance

        Raises:
            ValueError: If conversation not found or validation fails
            Exception: If creation fails
        """
        try:
            # Verify conversation exists and belongs to user (unless skipped)
            if not skip_verification:
                conv_uuid = UUID(conversation_id) if isinstance(conversation_id, str) else conversation_id
                conversation = self.session.get(Conversation, conv_uuid)

                # Convert both to strings for comparison (handles UUID vs string mismatch)
                conv_user_id = str(conversation.user_id) if conversation else None
                if not conversation or conv_user_id != user_id:
                    raise ValueError(f"Conversation {conversation_id} not found or not owned by user")

            # Create message
            # Convert conversation_id to UUID if it's a string
            conv_uuid = UUID(conversation_id) if isinstance(conversation_id, str) else conversation_id
            message = Message(
                conversation_id=conv_uuid,
                user_id=user_id,
                role=role.value if hasattr(role, 'value') else role,  # Convert enum to string value
                content=content
            )
            self.session.add(message)

            # Update conversation timestamp (skip for newly created conversations)
            # Newly created conversations are already fresh and not yet committed
            if not skip_verification:
                await self.update_conversation_timestamp(conversation_id)

            self.session.flush()  # Flush to get ID, but don't commit yet
            self.session.refresh(message)

            logger.info(f"Added {role} message to conversation {conversation_id}")
            return message

        except ValueError as e:
            logger.warning(f"Validation error adding message: {e}")
            raise
        except Exception as e:
            logger.error(f"Error adding message: {e}")
            raise

    async def update_conversation_timestamp(self, conversation_id: str) -> None:
        """Update conversation's updated_at timestamp.

        Args:
            conversation_id: String UUID of the conversation

        Raises:
            ValueError: If conversation not found
            Exception: If update fails
        """
        try:
            # Convert string UUID to UUID object for query
            conv_uuid = UUID(conversation_id) if isinstance(conversation_id, str) else conversation_id
            conversation = self.session.get(Conversation, conv_uuid)
            if not conversation:
                raise ValueError(f"Conversation {conversation_id} not found")

            conversation.updated_at = datetime.now(timezone.utc)
            self.session.add(conversation)
            self.session.flush()  # Flush the update
            # Note: commit is handled by session dependency

            logger.debug(f"Updated timestamp for conversation {conversation_id}")

        except ValueError as e:
            logger.warning(f"Validation error updating timestamp: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating conversation timestamp: {e}", exc_info=True)
            raise

    async def archive_old_conversations(self) -> int:
        """Archive conversations inactive for more than archive_days.

        This is a background job that should run periodically.

        Returns:
            Number of conversations archived

        Raises:
            Exception: If archival fails
        """
        try:
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.archive_days)

            # Find conversations to archive
            statement = (
                select(Conversation)
                .where(
                    and_(
                        Conversation.updated_at < cutoff_date,
                        Conversation.archived_at.is_(None)
                    )
                )
            )

            conversations = self.session.exec(statement).all()

            # Archive each conversation
            archived_count = 0
            for conversation in conversations:
                conversation.archived_at = datetime.now(timezone.utc)
                self.session.add(conversation)
                archived_count += 1

            self.session.commit()

            logger.info(f"Archived {archived_count} conversations older than {self.archive_days} days")
            return archived_count

        except Exception as e:
            self.session.rollback()
            logger.error(f"Error archiving conversations: {e}")
            raise
