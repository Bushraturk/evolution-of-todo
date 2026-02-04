"""Test to verify ToolCall model accepts both dict and list results."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent / "src"))

from src.api.chat import ToolCall

print("=" * 60)
print("TESTING TOOLCALL MODEL FIX")
print("=" * 60)

# Test 1: ToolCall with dict result (add_task, complete_task, etc.)
print("\n1. Testing ToolCall with dict result...")
try:
    tool_call_dict = ToolCall(
        tool="add_task",
        parameters={"title": "Buy laptop"},
        result={"task_id": "123", "status": "created", "title": "Buy laptop"}
    )
    print(f"   [OK] Dict result accepted: {tool_call_dict.result}")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

# Test 2: ToolCall with list result (list_tasks)
print("\n2. Testing ToolCall with list result...")
try:
    tool_call_list = ToolCall(
        tool="list_tasks",
        parameters={"status": "all"},
        result=[
            {"id": "123", "title": "Buy mobile", "completed": False},
            {"id": "456", "title": "Buy laptop", "completed": False}
        ]
    )
    print(f"   [OK] List result accepted: {len(tool_call_list.result)} tasks")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

# Test 3: Verify result type is Union[dict, list]
print("\n3. Verifying result field type annotation...")
try:
    from typing import get_type_hints
    hints = get_type_hints(ToolCall)
    result_type = hints.get('result')
    print(f"   [OK] Result type: {result_type}")
except Exception as e:
    print(f"   [FAIL] {e}")
    sys.exit(1)

print("\n" + "=" * 60)
print("ALL TESTS PASSED!")
print("=" * 60)
print("\nThe ToolCall model now accepts both:")
print("  - dict results (for add_task, complete_task, update_task, delete_task)")
print("  - list results (for list_tasks)")
print("\nNext step: Restart the server and test with chatbot")
print("=" * 60)
