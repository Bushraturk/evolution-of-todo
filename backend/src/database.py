"""Database connection and session management."""

from typing import Generator

from sqlmodel import Session, SQLModel, create_engine

from .config import get_settings

# Get settings
settings = get_settings()

# Get database URL
database_url = settings.database_url

# Create database engine with appropriate settings
if database_url.startswith("sqlite"):
    print(f"INFO: Using SQLite database: {database_url}")
    engine = create_engine(
        database_url,
        echo=settings.debug,
        connect_args={"check_same_thread": False},
    )
else:
    # PostgreSQL (Neon DB) settings
    print(f"INFO: Using PostgreSQL database")
    engine = create_engine(
        database_url,
        echo=settings.debug,
        pool_pre_ping=True,
    )


def create_db_and_tables() -> None:
    """Create all database tables."""
    SQLModel.metadata.create_all(engine)


def get_session() -> Generator[Session, None, None]:
    """Get a database session."""
    with Session(engine) as session:
        yield session


def init_db() -> None:
    """Initialize the database with tables."""
    # Import models to register them with SQLModel
    from .models import Category, Task, User  # noqa: F401

    create_db_and_tables()
    print("INFO: Database tables created successfully")


if __name__ == "__main__":
    # Allow running as script to initialize database
    print("Initializing database...")
    init_db()
    print("Database initialized successfully!")
