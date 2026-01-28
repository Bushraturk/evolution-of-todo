"""
Deployment verification script.
Run this to verify all environment variables and database connectivity.
"""

import os
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))


def check_env_vars():
    """Check if all required environment variables are set."""
    print("=" * 60)
    print("Environment Variables Check")
    print("=" * 60)

    required_vars = {
        "DATABASE_URL": "PostgreSQL connection string",
        "CORS_ORIGINS": "Allowed frontend origins",
        "JWT_SECRET": "Secret key for JWT tokens (min 32 chars)",
    }

    optional_vars = {
        "DEBUG": "Debug mode (true/false)",
        "JWKS_URL": "Better Auth JWKS endpoint (if using Better Auth)",
        "JWT_ISSUER": "JWT issuer URL (if using Better Auth)",
    }

    all_good = True

    print("\n✓ Required Variables:")
    for var, description in required_vars.items():
        value = os.getenv(var)
        if value:
            # Mask sensitive values
            if "SECRET" in var or "PASSWORD" in var or "DATABASE_URL" in var:
                display_value = value[:20] + "..." if len(value) > 20 else "***"
            else:
                display_value = value
            print(f"  ✓ {var}: {display_value}")

            # Validate JWT_SECRET length
            if var == "JWT_SECRET" and len(value) < 32:
                print(f"    ⚠️  WARNING: JWT_SECRET should be at least 32 characters (current: {len(value)})")
                all_good = False
        else:
            print(f"  ✗ {var}: NOT SET - {description}")
            all_good = False

    print("\n✓ Optional Variables:")
    for var, description in optional_vars.items():
        value = os.getenv(var)
        if value:
            print(f"  ✓ {var}: {value}")
        else:
            print(f"  - {var}: Not set (using default) - {description}")

    return all_good


def test_database_connection():
    """Test database connection."""
    print("\n" + "=" * 60)
    print("Database Connection Test")
    print("=" * 60)

    try:
        from src.config import get_settings
        from src.database import engine

        settings = get_settings()
        print(f"\nDatabase URL: {settings.database_url[:50]}...")

        # Try to connect
        with engine.connect() as conn:
            print("✓ Database connection successful!")
            return True
    except Exception as e:
        print(f"✗ Database connection failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def test_database_tables():
    """Check if all required tables exist."""
    print("\n" + "=" * 60)
    print("Database Tables Check")
    print("=" * 60)

    try:
        from sqlmodel import text
        from src.database import engine

        required_tables = ["user", "task", "category"]

        with engine.connect() as conn:
            # Query to check if tables exist (PostgreSQL)
            result = conn.execute(text(
                "SELECT tablename FROM pg_tables WHERE schemaname = 'public'"
            ))
            existing_tables = [row[0] for row in result]

            print("\nExisting tables:")
            for table in existing_tables:
                print(f"  ✓ {table}")

            print("\nRequired tables:")
            all_exist = True
            for table in required_tables:
                if table in existing_tables:
                    print(f"  ✓ {table}")
                else:
                    print(f"  ✗ {table} - MISSING")
                    all_exist = False

            if not all_exist:
                print("\n⚠️  Some tables are missing. Run: python init_db.py")
                return False

            return True
    except Exception as e:
        print(f"✗ Failed to check tables: {str(e)}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all verification checks."""
    print("\n" + "=" * 60)
    print("🚀 DEPLOYMENT VERIFICATION")
    print("=" * 60)

    results = {
        "Environment Variables": check_env_vars(),
        "Database Connection": test_database_connection(),
        "Database Tables": test_database_tables(),
    }

    print("\n" + "=" * 60)
    print("SUMMARY")
    print("=" * 60)

    for check, passed in results.items():
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check}")

    all_passed = all(results.values())

    if all_passed:
        print("\n✅ All checks passed! Deployment is ready.")
        return 0
    else:
        print("\n❌ Some checks failed. Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
