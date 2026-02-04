"""Test script to verify database transaction fix.

This script tests the conversation creation and message addition flow
to ensure no transaction errors occur.
"""
import asyncio
import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlmodel import Session, create_engine
from src.models import Conversation, Message, MessageRole
from src.services.conversation_service import ConversationService
from src.config import settings


async def test_new_conversation_flow():
    """Test creating a new conversation and adding messages.

    This simulates the exact flow that was causing transaction errors.
    """
    print("=" * 60)
    print("Testing New Conversation Flow")
    print("=" * 60)

    # Create engine and session
    engine = create_engine(settings.database_url, echo=True)

    with Session(engine) as session:
        try:
            # Initialize service
            conv_service = ConversationService(session)
            test_user_id = "test_user_123"

            print("\n1. Creating new conversation...")
            conversation = await conv_service.create_conversation(test_user_id)
            conversation_id = str(conversation.id)
            print(f"   [OK] Created conversation: {conversation_id}")

            print("\n2. Adding user message (skip_verification=True)...")
            user_msg = await conv_service.add_message(
                conversation_id=conversation_id,
                user_id=test_user_id,
                role=MessageRole.USER,
                content="Test message from user",
                skip_verification=True  # This should skip timestamp update
            )
            print(f"   [OK] Added user message: {user_msg.id}")

            print("\n3. Adding assistant message (skip_verification=True)...")
            assistant_msg = await conv_service.add_message(
                conversation_id=conversation_id,
                user_id=test_user_id,
                role=MessageRole.ASSISTANT,
                content="Test response from assistant",
                skip_verification=True  # This should skip timestamp update
            )
            print(f"   [OK] Added assistant message: {assistant_msg.id}")

            print("\n4. Committing transaction...")
            session.commit()
            print("   [OK] Transaction committed successfully")

            print("\n5. Loading conversation history...")
            history = await conv_service.load_conversation_history(
                conversation_id,
                test_user_id
            )
            print(f"   [OK] Loaded {len(history)} messages")

            print("\n6. Adding another message (skip_verification=False)...")
            user_msg2 = await conv_service.add_message(
                conversation_id=conversation_id,
                user_id=test_user_id,
                role=MessageRole.USER,
                content="Second message from user",
                skip_verification=False  # This should update timestamp
            )
            print(f"   [OK] Added second user message: {user_msg2.id}")

            print("\n7. Committing second transaction...")
            session.commit()
            print("   [OK] Second transaction committed successfully")

            print("\n" + "=" * 60)
            print("[PASS] ALL TESTS PASSED - No transaction errors!")
            print("=" * 60)

            # Cleanup
            print("\n8. Cleaning up test data...")
            session.delete(conversation)
            session.commit()
            print("   [OK] Test data cleaned up")

            return True

        except Exception as e:
            print(f"\n[FAIL] TEST FAILED: {e}")
            print(f"   Error type: {type(e).__name__}")
            session.rollback()
            return False


async def test_existing_conversation_flow():
    """Test adding messages to an existing conversation."""
    print("\n" + "=" * 60)
    print("Testing Existing Conversation Flow")
    print("=" * 60)

    engine = create_engine(settings.database_url, echo=True)

    with Session(engine) as session:
        try:
            conv_service = ConversationService(session)
            test_user_id = "test_user_456"

            print("\n1. Creating and committing conversation...")
            conversation = await conv_service.create_conversation(test_user_id)
            conversation_id = str(conversation.id)
            session.commit()
            print(f"   [OK] Created and committed conversation: {conversation_id}")

            print("\n2. Adding message to existing conversation (skip_verification=False)...")
            user_msg = await conv_service.add_message(
                conversation_id=conversation_id,
                user_id=test_user_id,
                role=MessageRole.USER,
                content="Message to existing conversation",
                skip_verification=False  # Should update timestamp
            )
            print(f"   [OK] Added message: {user_msg.id}")

            print("\n3. Committing transaction...")
            session.commit()
            print("   [OK] Transaction committed successfully")

            print("\n" + "=" * 60)
            print("[PASS] EXISTING CONVERSATION TEST PASSED!")
            print("=" * 60)

            # Cleanup
            print("\n4. Cleaning up test data...")
            session.delete(conversation)
            session.commit()
            print("   [OK] Test data cleaned up")

            return True

        except Exception as e:
            print(f"\n[FAIL] TEST FAILED: {e}")
            print(f"   Error type: {type(e).__name__}")
            session.rollback()
            return False


async def main():
    """Run all tests."""
    print("\n" + "=" * 60)
    print("DATABASE TRANSACTION FIX VALIDATION")
    print("=" * 60)
    print(f"\nDatabase URL: {settings.database_url[:50]}...")
    print(f"Testing timestamp: {asyncio.get_event_loop().time()}")

    # Run tests
    test1_passed = await test_new_conversation_flow()
    test2_passed = await test_existing_conversation_flow()

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"New Conversation Flow:      {'[PASS]' if test1_passed else '[FAIL]'}")
    print(f"Existing Conversation Flow: {'[PASS]' if test2_passed else '[FAIL]'}")
    print("=" * 60)

    if test1_passed and test2_passed:
        print("\n[OK] All tests passed! Transaction fix is working correctly.")
        return 0
    else:
        print("\n[ERROR] Some tests failed. Please review the errors above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)
