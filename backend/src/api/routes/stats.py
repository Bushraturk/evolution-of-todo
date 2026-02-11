"""API routes for task statistics."""

from typing import Dict, Any
from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func

from ..routes.auth import get_current_user
from ...database import get_session
from ...models.task import Task, Priority


router = APIRouter(prefix="/api/tasks/stats", tags=["stats"])


@router.get("", response_model=dict)
async def get_task_stats(
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
) -> Dict[str, Any]:
    """Get task statistics for the current user.

    Returns:
        Dict with task statistics including counts by status, priority, and completion rate
    """
    user_id = current_user["id"]

    # Total tasks
    total_tasks = session.exec(
        select(func.count(Task.id)).where(Task.user_id == user_id)
    ).one()

    # Completed tasks
    completed_tasks = session.exec(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.completed == True,  # noqa: E712
        )
    ).one()

    # Incomplete tasks
    incomplete_tasks = total_tasks - completed_tasks

    # Tasks by priority
    high_priority = session.exec(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.priority == Priority.HIGH,
            Task.completed == False,  # noqa: E712
        )
    ).one()

    medium_priority = session.exec(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.priority == Priority.MEDIUM,
            Task.completed == False,  # noqa: E712
        )
    ).one()

    low_priority = session.exec(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.priority == Priority.LOW,
            Task.completed == False,  # noqa: E712
        )
    ).one()

    # Recurring tasks
    recurring_tasks = session.exec(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.is_recurring == True,  # noqa: E712
        )
    ).one()

    # Tasks with due dates
    tasks_with_due_dates = session.exec(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.due_date.isnot(None),
        )
    ).one()

    # Overdue tasks (incomplete tasks with due date in the past)
    from datetime import datetime
    overdue_tasks = session.exec(
        select(func.count(Task.id)).where(
            Task.user_id == user_id,
            Task.completed == False,  # noqa: E712
            Task.due_date < datetime.utcnow(),
        )
    ).one()

    # Calculate completion rate
    completion_rate = (
        round((completed_tasks / total_tasks) * 100, 1) if total_tasks > 0 else 0.0
    )

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_tasks,
        "incomplete_tasks": incomplete_tasks,
        "completion_rate": completion_rate,
        "by_priority": {
            "high": high_priority,
            "medium": medium_priority,
            "low": low_priority,
        },
        "recurring_tasks": recurring_tasks,
        "tasks_with_due_dates": tasks_with_due_dates,
        "overdue_tasks": overdue_tasks,
    }
