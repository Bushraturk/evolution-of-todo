"""
Script to reset NeonDB tables.
This will drop all existing tables and recreate them with the correct schema.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from sqlalchemy import text
from src.database import engine, init_db

def reset_database():
    """Drop all tables and recreate them."""
    print("Resetting NeonDB database...")

    # Drop all tables
    print("Dropping existing tables...")
    with engine.connect() as conn:
        # Drop tables in correct order (respecting foreign keys)
        conn.execute(text("DROP TABLE IF EXISTS task CASCADE;"))
        conn.execute(text("DROP TABLE IF EXISTS category CASCADE;"))
        conn.execute(text('DROP TABLE IF EXISTS "user" CASCADE;'))
        conn.execute(text("DROP TYPE IF EXISTS priority CASCADE;"))
        conn.commit()

    print("Tables dropped successfully")

    # Recreate tables
    print("Creating tables with correct schema...")
    init_db()

    print("Database reset complete!")
    print("\nNeonDB is now ready with the correct schema!")

if __name__ == "__main__":
    reset_database()
