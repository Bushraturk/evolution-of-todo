"""Database configuration and session management."""
import logging
from typing import Generator

from sqlmodel import Session, create_engine
from sqlalchemy.pool import StaticPool

from .config import settings

logger = logging.getLogger(__name__)

# Create database engine
engine = create_engine(
    settings.database_url,
    echo=settings.debug,
    pool_pre_ping=True,
    connect_args={"check_same_thread": False} if "sqlite" in settings.database_url else {}
)


def get_session() -> Generator[Session, None, None]:
    """Get database session.

    Yields:
        Database session

    Usage:
        @app.get("/endpoint")
        def endpoint(session: Session = Depends(get_session)):
            # Use session
            pass
    """
    with Session(engine) as session:
        try:
            yield session
            session.commit()  # Commit on success
        except Exception as e:
            logger.error(f"Database session error: {e}", exc_info=True)
            session.rollback()
            raise
        finally:
            session.close()
