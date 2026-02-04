"""Mock mode for testing chatbot without hitting Gemini API.

Use this when you hit rate limits or want to test without API calls.
"""

# Add to .env file:
# USE_MOCK_AGENT=true

# Then in agent_service.py, add this at the top of run_conversation():

async def run_conversation(self, messages, user_id):
    """Run conversation with function calling."""

    # Mock mode for testing (bypass API)
    if os.getenv("USE_MOCK_AGENT") == "true":
        logger.info("MOCK MODE: Bypassing Gemini API")

        # Extract last user message
        last_message = messages[-1]["content"].lower()

        # Mock responses based on keywords
        if "list" in last_message or "show" in last_message:
            return {
                "response": "Here are your tasks: [Mock response - API bypassed]",
                "tool_calls": [{
                    "tool": "list_tasks",
                    "parameters": {"status": "all", "user_id": user_id},
                    "result": []
                }]
            }
        elif "add" in last_message or "create" in last_message:
            return {
                "response": "I've added that task for you! [Mock response - API bypassed]",
                "tool_calls": [{
                    "tool": "add_task",
                    "parameters": {"title": "Mock task", "user_id": user_id},
                    "result": {"task_id": "mock-123", "status": "created"}
                }]
            }
        else:
            return {
                "response": "I understand. [Mock response - API bypassed]",
                "tool_calls": []
            }

    # Normal mode - continue with actual API call
    try:
        logger.info(f"Starting agent conversation for user {user_id}")
        # ... rest of the code
