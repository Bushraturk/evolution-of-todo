"""
Database initialization script for production deployment.
Run this to create all tables in Neon DB.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.database import init_db
from src.config import get_settings

if __name__ == "__main__":
    print("=" * 60)
    print("Database Initialization Script")
    print("=" * 60)

    settings = get_settings()
    print(f"\nDatabase URL: {settings.database_url[:50]}...")
    print(f"Debug Mode: {settings.debug}")
    print(f"CORS Origins: {settings.cors_origins}")

    print("\nInitializing database tables...")
    try:
        init_db()
        print("\n✅ SUCCESS: Database tables created successfully!")
        print("\nTables created:")
        print("  - users (for authentication)")
        print("  - tasks (for todo items)")
        print("  - categories (for task organization)")
    except Exception as e:
        print(f"\n❌ ERROR: Failed to initialize database")
        print(f"Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

    print("\n" + "=" * 60)
    print("Database is ready for use!")
    print("=" * 60)
