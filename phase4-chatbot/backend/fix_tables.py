"""Drop and recreate chatbot tables without foreign keys."""
import os
import sys

import psycopg2
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def fix_tables():
    """Drop old tables and create new ones without foreign keys."""
    database_url = os.getenv("DATABASE_URL")

    if not database_url:
        print("ERROR: DATABASE_URL not found in .env file")
        sys.exit(1)

    print("Fixing chatbot tables...")

    migration_sql = """
    -- Drop old tables with foreign keys
    DROP TABLE IF EXISTS message CASCADE;
    DROP TABLE IF EXISTS conversation CASCADE;

    -- Create conversation table (no foreign key to user)
    CREATE TABLE conversation (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        user_id UUID NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        updated_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW(),
        archived_at TIMESTAMP WITH TIME ZONE NULL
    );

    -- Create indexes for conversation
    CREATE INDEX idx_conversation_user_id ON conversation(user_id);
    CREATE INDEX idx_conversation_updated_at ON conversation(updated_at);
    CREATE INDEX idx_conversation_archived_at ON conversation(archived_at);

    -- Create message table
    CREATE TABLE message (
        id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
        conversation_id UUID NOT NULL REFERENCES conversation(id) ON DELETE CASCADE,
        user_id UUID NOT NULL,
        role VARCHAR(20) NOT NULL CHECK (role IN ('user', 'assistant')),
        content TEXT NOT NULL,
        created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
    );

    -- Create indexes for message
    CREATE INDEX idx_message_conversation_id ON message(conversation_id);
    CREATE INDEX idx_message_user_id ON message(user_id);
    CREATE INDEX idx_message_created_at ON message(created_at);
    CREATE INDEX idx_message_conv_created ON message(conversation_id, created_at);
    """

    try:
        # Connect to database
        conn = psycopg2.connect(database_url)
        cursor = conn.cursor()

        # Execute migration
        cursor.execute(migration_sql)
        conn.commit()

        print("SUCCESS: Tables recreated successfully!")

        # Verify tables
        cursor.execute("""
            SELECT table_name
            FROM information_schema.tables
            WHERE table_schema = 'public'
            AND table_name IN ('conversation', 'message')
            ORDER BY table_name;
        """)

        tables = cursor.fetchall()
        print("\nCreated tables:")
        for table in tables:
            print(f"  - {table[0]}")

        cursor.close()
        conn.close()

        print("\nDatabase is ready!")
        print("\nNext step: Restart chatbot backend (port 8002)")

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    fix_tables()
