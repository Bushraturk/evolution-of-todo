"""Query all tasks from the database."""
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Fix Windows console encoding for emojis
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv('backend/.env')

# Get database URL
DATABASE_URL = os.getenv('DATABASE_URL')

# Create engine
engine = create_engine(DATABASE_URL)

# Query all tasks
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT
            id,
            title,
            description,
            completed,
            priority,
            user_id,
            category_id,
            created_at,
            updated_at
        FROM task
        ORDER BY created_at DESC
    """))

    tasks = result.fetchall()

    if not tasks:
        print("\n❌ No tasks found in the database.\n")
    else:
        print(f"\n📋 Total Tasks: {len(tasks)}\n")
        print("=" * 100)

        for i, task in enumerate(tasks, 1):
            status = "✅" if task.completed else "⬜"
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")

            print(f"\n{i}. {status} {priority_emoji} {task.title}")
            print(f"   ID: {task.id}")
            if task.description:
                print(f"   Description: {task.description}")
            print(f"   Priority: {task.priority}")
            print(f"   Completed: {task.completed}")
            print(f"   User ID: {task.user_id}")
            if task.category_id:
                print(f"   Category ID: {task.category_id}")
            print(f"   Created: {task.created_at}")
            print(f"   Updated: {task.updated_at}")
            print("-" * 100)

        # Summary by status
        completed_count = sum(1 for t in tasks if t.completed)
        pending_count = len(tasks) - completed_count

        print(f"\n📊 Summary:")
        print(f"   ✅ Completed: {completed_count}")
        print(f"   ⬜ Pending: {pending_count}")
        print(f"   📝 Total: {len(tasks)}\n")
