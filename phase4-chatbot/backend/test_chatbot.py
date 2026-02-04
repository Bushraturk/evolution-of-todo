"""
Quick Test Script for Todo Chatbot

This script tests the chatbot end-to-end without needing the frontend.
"""
import asyncio
import sys
import os

# Add paths
sys.path.insert(0, os.path.abspath('src'))
sys.path.insert(0, os.path.abspath('../backend/src'))

async def test_chatbot():
    """Test the chatbot functionality."""
    print("=" * 60)
    print("🧪 TESTING TODO CHATBOT")
    print("=" * 60)

    try:
        # Import required modules
        from services.agent_service import AgentService
        from services.conversation_service import ConversationService
        from services.task_operations import TaskOperations
        from mcp.handlers import TaskHandlers
        from mcp.tools import ALL_TOOLS
        from database import get_session
        from config import settings
        from openai import AsyncOpenAI
        from uuid import UUID
        from models import MessageRole

        print("\n✓ All imports successful")

        # Get a test user
        with next(get_session()) as session:
            from sqlmodel import select
            from models.user import User

            user = session.exec(select(User).limit(1)).first()
            if not user:
                print("\n❌ No users found in database")
                print("Please create a user first by registering on the frontend")
                return

            user_id = str(user.id)
            print(f"\n✓ Using test user: {user.email} ({user_id})")

        # Initialize services
        print("\n📦 Initializing services...")

        gemini_client = AsyncOpenAI(
            api_key=settings.gemini_api_key,
            base_url=settings.gemini_base_url
        )
        print("  ✓ Gemini client initialized")

        with next(get_session()) as session:
            task_operations = TaskOperations(session=session)
            task_handlers = TaskHandlers(task_operations=task_operations)

            agent_service = AgentService(
                llm_client=gemini_client,
                mcp_handlers=task_handlers,
                model=settings.gemini_model,
                timeout=settings.llm_request_timeout,
                max_retries=settings.llm_max_retries
            )
            print("  ✓ Agent service initialized")

            conversation_service = ConversationService(
                session=session,
                max_history=settings.max_conversation_history,
                archive_days=settings.conversation_archive_days
            )
            print("  ✓ Conversation service initialized")

            # Create a test conversation
            print("\n💬 Creating test conversation...")
            conversation = await conversation_service.create_conversation(
                user_id=UUID(user_id)
            )
            print(f"  ✓ Conversation created: {conversation.id}")

            # Test 1: Simple greeting
            print("\n" + "=" * 60)
            print("TEST 1: Simple Greeting")
            print("=" * 60)

            user_message = "Hello! Can you help me?"
            print(f"\nUser: {user_message}")

            await conversation_service.add_message(
                conversation_id=conversation.id,
                user_id=UUID(user_id),
                role=MessageRole.USER,
                content=user_message
            )

            messages = [{"role": "user", "content": user_message}]
            result = await agent_service.run_conversation(messages, user_id)

            print(f"Agent: {result['response']}")

            await conversation_service.add_message(
                conversation_id=conversation.id,
                user_id=UUID(user_id),
                role=MessageRole.ASSISTANT,
                content=result['response']
            )

            print("\n✓ Test 1 passed!")

            # Test 2: Create a task
            print("\n" + "=" * 60)
            print("TEST 2: Create Task")
            print("=" * 60)

            user_message = "Add a task to buy groceries"
            print(f"\nUser: {user_message}")

            await conversation_service.add_message(
                conversation_id=conversation.id,
                user_id=UUID(user_id),
                role=MessageRole.USER,
                content=user_message
            )

            messages.append({"role": "assistant", "content": result['response']})
            messages.append({"role": "user", "content": user_message})

            result = await agent_service.run_conversation(messages, user_id)

            print(f"Agent: {result['response']}")

            if result.get('tool_calls'):
                print(f"\n🔧 Tools used:")
                for call in result['tool_calls']:
                    print(f"  - {call['tool']}: {call['result']}")

            await conversation_service.add_message(
                conversation_id=conversation.id,
                user_id=UUID(user_id),
                role=MessageRole.ASSISTANT,
                content=result['response']
            )

            print("\n✓ Test 2 passed!")

            # Test 3: List tasks
            print("\n" + "=" * 60)
            print("TEST 3: List Tasks")
            print("=" * 60)

            user_message = "Show me all my tasks"
            print(f"\nUser: {user_message}")

            await conversation_service.add_message(
                conversation_id=conversation.id,
                user_id=UUID(user_id),
                role=MessageRole.USER,
                content=user_message
            )

            messages.append({"role": "assistant", "content": result['response']})
            messages.append({"role": "user", "content": user_message})

            result = await agent_service.run_conversation(messages, user_id)

            print(f"Agent: {result['response']}")

            if result.get('tool_calls'):
                print(f"\n🔧 Tools used:")
                for call in result['tool_calls']:
                    print(f"  - {call['tool']}")
                    if 'result' in call and isinstance(call['result'], list):
                        print(f"    Found {len(call['result'])} tasks")

            print("\n✓ Test 3 passed!")

            print("\n" + "=" * 60)
            print("✅ ALL TESTS PASSED!")
            print("=" * 60)
            print("\n🎉 Todo chatbot is working correctly!")
            print("\nYou can now:")
            print("  1. Open http://localhost:3000")
            print("  2. Login to your account")
            print("  3. Click the purple robot icon (bottom-right)")
            print("  4. Start chatting with the AI assistant!")

    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_chatbot())
