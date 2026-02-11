"""API routes for internal event debugging."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends

from ..routes.auth import get_current_user


router = APIRouter(prefix="/api/internal/events", tags=["events"])


@router.get("", response_model=dict)
async def get_events(
    current_user: dict = Depends(get_current_user),
    limit: int = 50,
):
    """Get recent events for debugging.

    This endpoint is for internal debugging only.
    In production, events would be queried from Kafka or a dedicated event store.

    Args:
        current_user: Current authenticated user
        limit: Maximum number of events to return

    Returns:
        Dict with events list
    """
    # In production, this would query Kafka topics or event store
    # For now, return a placeholder response

    return {
        "message": "Event debugging endpoint",
        "note": "In production, this would query Kafka topics for recent events",
        "events": [],
        "total": 0,
        "limit": limit,
    }


@router.get("/topics", response_model=dict)
async def get_event_topics(
    current_user: dict = Depends(get_current_user),
):
    """Get list of available event topics.

    Returns:
        Dict with topic list
    """
    topics = [
        {
            "name": "task.created",
            "description": "Published when a new task is created",
            "schema": {
                "task_id": "UUID",
                "user_id": "string",
                "task_data": {
                    "title": "string",
                    "description": "string",
                    "priority": "string",
                    "due_date": "ISO 8601 datetime",
                    "is_recurring": "boolean",
                },
            },
        },
        {
            "name": "task.updated",
            "description": "Published when a task is updated",
            "schema": {
                "task_id": "UUID",
                "user_id": "string",
                "task_data": {
                    "title": "string",
                    "description": "string",
                    "priority": "string",
                    "category_id": "UUID",
                },
            },
        },
        {
            "name": "task.completed",
            "description": "Published when a task is marked as completed",
            "schema": {
                "task_id": "UUID",
                "user_id": "string",
                "completed_at": "ISO 8601 datetime",
                "is_recurring": "boolean",
                "recurrence_id": "UUID",
                "next_occurrence_date": "ISO 8601 datetime",
            },
        },
        {
            "name": "task.deleted",
            "description": "Published when a task is deleted",
            "schema": {
                "task_id": "UUID",
                "user_id": "string",
            },
        },
        {
            "name": "reminder.scheduled",
            "description": "Published when a reminder is scheduled",
            "schema": {
                "reminder_id": "UUID",
                "task_id": "UUID",
                "user_id": "string",
                "remind_at": "ISO 8601 datetime",
                "channel": "string",
                "task_title": "string",
            },
        },
    ]

    return {
        "topics": topics,
        "total": len(topics),
    }
