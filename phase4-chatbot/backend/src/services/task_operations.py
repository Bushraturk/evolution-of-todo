"""Simple task operations wrapper for chatbot backend.

This module provides basic task operations without importing from main backend.
It directly uses SQLModel to interact with the database.
"""
import logging
import sys
from pathlib import Path
from typing import List, Optional

from sqlmodel import Session, select, and_

# Add main backend to path once at module level
BACKEND_PATH = Path(__file__).resolve().parents[4] / "backend" / "src"
if str(BACKEND_PATH) not in sys.path:
    sys.path.insert(0, str(BACKEND_PATH))

from models.task import Task

logger = logging.getLogger(__name__)


class TaskOperations:
    """Simple wrapper for task database operations.

    This avoids importing TaskService from main backend which causes
    import conflicts with chatbot backend's own services.
    """

    def __init__(self, session: Session):
        """Initialize with database session.

        Args:
            session: SQLModel database session
        """
        self.session = session

    async def create_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None
    ):
        """Create a new task.

        Args:
            user_id: User CUID string (from Better Auth)
            title: Task title
            description: Optional task description

        Returns:
            Created task object
        """
        task = Task(
            user_id=user_id,
            title=title,
            description=description,
            completed=False
        )

        self.session.add(task)
        self.session.flush()  # Flush to get ID, commit handled by session dependency
        self.session.refresh(task)

        logger.info(f"Created task {task.id} for user {user_id}")
        return task

    async def get_tasks(
        self,
        user_id: str,
        completed: Optional[bool] = None
    ) -> List:
        """Get tasks for a user.

        Args:
            user_id: User CUID string (from Better Auth)
            completed: Filter by completion status (None = all)

        Returns:
            List of task objects
        """
        statement = select(Task).where(Task.user_id == user_id)

        if completed is not None:
            statement = statement.where(Task.completed == completed)

        tasks = self.session.exec(statement).all()

        logger.info(f"Retrieved {len(tasks)} tasks for user {user_id}")
        return tasks

    async def get_task(
        self,
        user_id: str,
        task_id: str
    ):
        """Get a specific task.

        Args:
            user_id: User CUID string (from Better Auth)
            task_id: Task CUID string

        Returns:
            Task object or None
        """
        statement = select(Task).where(
            and_(
                Task.id == task_id,
                Task.user_id == user_id
            )
        )

        task = self.session.exec(statement).first()
        return task

    async def update_task(
        self,
        user_id: str,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None,
        completed: Optional[bool] = None
    ):
        """Update a task.

        Args:
            user_id: User CUID string (from Better Auth)
            task_id: Task CUID string
            title: New title (optional)
            description: New description (optional)
            completed: New completion status (optional)

        Returns:
            Updated task object or None
        """
        task = await self.get_task(user_id, task_id)

        if not task:
            return None

        if title is not None:
            task.title = title
        if description is not None:
            task.description = description
        if completed is not None:
            task.completed = completed

        self.session.add(task)
        self.session.flush()  # Flush to get changes, commit handled by session dependency
        self.session.refresh(task)

        logger.info(f"Updated task {task_id} for user {user_id}")
        return task

    async def delete_task(
        self,
        user_id: str,
        task_id: str
    ) -> bool:
        """Delete a task.

        Args:
            user_id: User CUID string (from Better Auth)
            task_id: Task CUID string

        Returns:
            True if deleted, False if not found
        """
        task = await self.get_task(user_id, task_id)

        if not task:
            return False

        self.session.delete(task)
        self.session.flush()  # Flush deletion, commit handled by session dependency

        logger.info(f"Deleted task {task_id} for user {user_id}")
        return True
