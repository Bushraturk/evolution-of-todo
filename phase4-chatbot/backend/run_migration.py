"""Run database migration for chatbot tables."""
import os
import sys
from pathlib import Path

import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_migration():
    """Execute the chatbot tables migration."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("[ERROR] DATABASE_URL not found in .env file")
        sys.exit(1)

    # Read migration SQL
    migration_file = Path(__file__).parent / "migrations" / "001_add_chatbot_tables.sql"

    if not migration_file.exists():
        print(f"[ERROR] Migration file not found: {migration_file}")
        sys.exit(1)

    with open(migration_file, 'r', encoding='utf-8') as f:
        migration_sql = f.read()

    print("[INFO] Connecting to database...")

    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        conn.autocommit = True
        cursor = conn.cursor()

        print("[SUCCESS] Connected to database")
        print("[INFO] Running migration: 001_add_chatbot_tables.sql")

        # Execute migration
        cursor.execute(migration_sql)

        print("[SUCCESS] Migration completed successfully!")

        # Verify tables were created
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('conversation', 'message')
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        print(f"\n[INFO] Created tables:")
        for table in tables:
            print(f"   - {table[0]}")

        cursor.close()
        conn.close()

        print("\n[SUCCESS] Database migration completed successfully!")

    except psycopg2.errors.DuplicateTable as e:
        print("[WARNING] Tables already exist. Migration skipped.")
        print(f"   Details: {e}")
    except Exception as e:
        print(f"[ERROR] Migration failed")
        print(f"   {type(e).__name__}: {e}")
        sys.exit(1)

if __name__ == "__main__":
    run_migration()
