"""Dapr subscription endpoints for event consumers."""

from typing import Dict, Any, List
from fastapi import APIRouter, Request, Depends
from sqlmodel import Session

from ...database import get_session
from ...services.audit_service import AuditService
from ...services.recurring_task_service import RecurringTaskService

router = APIRouter(prefix="/dapr", tags=["dapr"])


@router.get("/subscribe")
async def get_subscriptions() -> List[Dict[str, str]]:
    """Return Dapr pub/sub subscriptions.

    Dapr calls this endpoint to discover which topics this service subscribes to.

    Returns:
        List of subscription configurations
    """
    return [
        {
            "pubsubname": "todo-pubsub",
            "topic": "task.created",
            "route": "/dapr/events/task-created",
        },
        {
            "pubsubname": "todo-pubsub",
            "topic": "task.updated",
            "route": "/dapr/events/task-updated",
        },
        {
            "pubsubname": "todo-pubsub",
            "topic": "task.completed",
            "route": "/dapr/events/task-completed",
        },
        {
            "pubsubname": "todo-pubsub",
            "topic": "task.deleted",
            "route": "/dapr/events/task-deleted",
        },
        {
            "pubsubname": "todo-pubsub",
            "topic": "reminder.scheduled",
            "route": "/dapr/events/reminder-scheduled",
        },
    ]


@router.post("/events/task-created")
async def handle_task_created(
    request: Request,
    session: Session = Depends(get_session),
):
    """Handle task.created event from Dapr.

    Args:
        request: FastAPI request containing event data
        session: Database session

    Returns:
        Success response
    """
    event_data = await request.json()
    data = event_data.get("data", {})

    # Process with audit service
    audit_service = AuditService(session)
    await audit_service.handle_task_created(data)

    return {"success": True}


@router.post("/events/task-updated")
async def handle_task_updated(
    request: Request,
    session: Session = Depends(get_session),
):
    """Handle task.updated event from Dapr.

    Args:
        request: FastAPI request containing event data
        session: Database session

    Returns:
        Success response
    """
    event_data = await request.json()
    data = event_data.get("data", {})

    # Process with audit service
    audit_service = AuditService(session)
    await audit_service.handle_task_updated(data)

    return {"success": True}


@router.post("/events/task-completed")
async def handle_task_completed(
    request: Request,
    session: Session = Depends(get_session),
):
    """Handle task.completed event from Dapr.

    Args:
        request: FastAPI request containing event data
        session: Database session

    Returns:
        Success response
    """
    event_data = await request.json()
    data = event_data.get("data", {})

    # Process with audit service
    audit_service = AuditService(session)
    await audit_service.handle_task_completed(data)

    # Process with recurring task service if task is recurring
    if data.get("is_recurring"):
        recurring_service = RecurringTaskService(session)
        await recurring_service.handle_task_completed(data)

    return {"success": True}


@router.post("/events/task-deleted")
async def handle_task_deleted(
    request: Request,
    session: Session = Depends(get_session),
):
    """Handle task.deleted event from Dapr.

    Args:
        request: FastAPI request containing event data
        session: Database session

    Returns:
        Success response
    """
    event_data = await request.json()
    data = event_data.get("data", {})

    # Process with audit service
    audit_service = AuditService(session)
    await audit_service.handle_task_deleted(data)

    return {"success": True}


@router.post("/events/reminder-scheduled")
async def handle_reminder_scheduled(
    request: Request,
    session: Session = Depends(get_session),
):
    """Handle reminder.scheduled event from Dapr.

    Args:
        request: FastAPI request containing event data
        session: Database session

    Returns:
        Success response
    """
    event_data = await request.json()
    data = event_data.get("data", {})

    # Process with audit service
    audit_service = AuditService(session)
    await audit_service.handle_reminder_scheduled(data)

    return {"success": True}
