"""MCP tool handlers for task operations.

These handlers delegate to TaskOperations for database operations.
"""
import logging
from typing import Any, Dict, Optional

logger = logging.getLogger(__name__)


class TaskHandlers:
    """Handlers for MCP task operation tools.

    These handlers provide the implementation for MCP tools,
    delegating to TaskOperations for actual database operations.
    """

    def __init__(self, task_operations):
        """Initialize handlers with task operations dependency.

        Args:
            task_operations: TaskOperations instance
        """
        self.task_ops = task_operations

    async def add_task(
        self,
        user_id: str,
        title: str,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new task for the user.

        Args:
            user_id: UUID of the user creating the task
            title: Task title (1-200 characters)
            description: Optional task description (max 1000 characters)

        Returns:
            Dict with task_id, status, and title

        Raises:
            ValueError: If validation fails
            Exception: If task creation fails
        """
        try:
            # Validate inputs
            if not title or len(title) > 200:
                raise ValueError("Title must be 1-200 characters")
            if description and len(description) > 1000:
                raise ValueError("Description must be max 1000 characters")

            # Delegate to TaskOperations
            task = await self.task_ops.create_task(
                user_id=user_id,  # Keep as CUID string, not UUID
                title=title,
                description=description
            )

            logger.info(f"Task created via MCP: {task.id} for user {user_id}")

            return {
                "task_id": str(task.id),
                "status": "created",
                "title": task.title
            }

        except ValueError as e:
            logger.warning(f"Validation error in add_task: {e}")
            raise
        except Exception as e:
            logger.error(f"Error creating task: {e}")
            raise

    async def list_tasks(
        self,
        user_id: str,
        status: str = "all"
    ) -> list[Dict[str, Any]]:
        """Retrieve tasks from the user's task list.

        Args:
            user_id: UUID of the user whose tasks to retrieve
            status: Filter by status (all, pending, completed)

        Returns:
            List of task dictionaries

        Raises:
            ValueError: If status is invalid
            Exception: If retrieval fails
        """
        try:
            # Validate status
            if status not in ["all", "pending", "completed"]:
                raise ValueError("Status must be 'all', 'pending', or 'completed'")

            # Delegate to TaskOperations
            tasks = await self.task_ops.get_tasks(
                user_id=user_id,  # Keep as CUID string, not UUID
                completed=None if status == "all" else (status == "completed")
            )

            logger.info(f"Listed {len(tasks)} tasks for user {user_id} (status: {status})")

            return [
                {
                    "id": str(task.id),
                    "title": task.title,
                    "description": task.description,
                    "completed": task.completed,
                    "priority": task.priority,
                    "created_at": task.created_at.isoformat()
                }
                for task in tasks
            ]

        except ValueError as e:
            logger.warning(f"Validation error in list_tasks: {e}")
            raise
        except Exception as e:
            logger.error(f"Error listing tasks: {e}")
            raise

    async def complete_task(
        self,
        user_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        """Mark a task as complete.

        Args:
            user_id: UUID of the user who owns the task
            task_id: UUID of the task to mark as complete

        Returns:
            Dict with task_id, status, and title

        Raises:
            ValueError: If task not found or not owned by user
            Exception: If update fails
        """
        try:
            # Validate task_id format (should be UUID-like)
            if not task_id or len(task_id) < 20:
                # If task_id looks like a title (too short), return helpful error
                raise ValueError(
                    f"Invalid task ID format. Please provide the task ID (not the title). "
                    f"Use list_tasks to see all task IDs."
                )

            # Delegate to TaskOperations
            task = await self.task_ops.update_task(
                user_id=user_id,  # Keep as CUID string, not UUID
                task_id=task_id,  # Keep as CUID string, not UUID
                completed=True
            )

            if not task:
                raise ValueError(f"Task {task_id} not found or not owned by user")

            logger.info(f"Task completed via MCP: {task_id} for user {user_id}")

            return {
                "task_id": str(task.id),
                "status": "completed",
                "title": task.title
            }

        except ValueError as e:
            logger.warning(f"Validation error in complete_task: {e}")
            raise
        except Exception as e:
            logger.error(f"Error completing task: {e}")
            raise

    async def update_task(
        self,
        user_id: str,
        task_id: str,
        title: Optional[str] = None,
        description: Optional[str] = None
    ) -> Dict[str, Any]:
        """Modify a task's title or description.

        Args:
            user_id: UUID of the user who owns the task
            task_id: UUID of the task to update
            title: New task title (optional, 1-200 characters)
            description: New task description (optional, max 1000 characters)

        Returns:
            Dict with task_id, status, and title

        Raises:
            ValueError: If validation fails or task not found
            Exception: If update fails
        """
        try:
            # Validate inputs
            if title is not None and (not title or len(title) > 200):
                raise ValueError("Title must be 1-200 characters")
            if description is not None and len(description) > 1000:
                raise ValueError("Description must be max 1000 characters")

            # Delegate to TaskOperations
            task = await self.task_ops.update_task(
                user_id=user_id,  # Keep as CUID string, not UUID
                task_id=task_id,  # Keep as CUID string, not UUID
                title=title,
                description=description
            )

            if not task:
                raise ValueError(f"Task {task_id} not found or not owned by user")

            logger.info(f"Task updated via MCP: {task_id} for user {user_id}")

            return {
                "task_id": str(task.id),
                "status": "updated",
                "title": task.title
            }

        except ValueError as e:
            logger.warning(f"Validation error in update_task: {e}")
            raise
        except Exception as e:
            logger.error(f"Error updating task: {e}")
            raise

    async def delete_task(
        self,
        user_id: str,
        task_id: str
    ) -> Dict[str, Any]:
        """Remove a task from the user's list.

        Args:
            user_id: UUID of the user who owns the task
            task_id: UUID of the task to delete

        Returns:
            Dict with task_id, status, and title

        Raises:
            ValueError: If task not found or not owned by user
            Exception: If deletion fails
        """
        try:
            # Get task before deletion to return title
            task = await self.task_ops.get_task(
                user_id=user_id,  # Keep as CUID string, not UUID
                task_id=task_id   # Keep as CUID string, not UUID
            )

            if not task:
                raise ValueError(f"Task {task_id} not found or not owned by user")

            task_title = task.title

            # Delegate to TaskOperations
            success = await self.task_ops.delete_task(
                user_id=user_id,  # Keep as CUID string, not UUID
                task_id=task_id   # Keep as CUID string, not UUID
            )

            if not success:
                raise ValueError(f"Failed to delete task {task_id}")

            logger.info(f"Task deleted via MCP: {task_id} for user {user_id}")

            return {
                "task_id": task_id,
                "status": "deleted",
                "title": task_title
            }

        except ValueError as e:
            logger.warning(f"Validation error in delete_task: {e}")
            raise
        except Exception as e:
            logger.error(f"Error deleting task: {e}")
            raise
