"""API routes for reminders."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from ..routes.auth import get_current_user
from ...database import get_session
from ...models.reminder import Channel
from ...services.reminder_service import ReminderService
from ...services.task_service import TaskNotFoundError, AccessDeniedError


router = APIRouter(prefix="/api/tasks", tags=["reminders"])


class CreateReminderRequest(BaseModel):
    """Request schema for creating a reminder."""

    offset_minutes: int = Field(..., ge=1, description="Minutes before due date")
    channel: Channel = Field(..., description="Notification channel")


class ReminderResponse(BaseModel):
    """Response schema for a reminder."""

    id: str
    task_id: str
    remind_at: str
    offset_minutes: int
    channel: str
    status: str
    created_at: str

    class Config:
        from_attributes = True


def get_reminder_service(session: Session = Depends(get_session)) -> ReminderService:
    """Dependency to get ReminderService instance."""
    return ReminderService(session)


@router.post("/{task_id}/reminders", response_model=dict, status_code=201)
async def create_reminder(
    task_id: UUID,
    request: CreateReminderRequest,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
    service: ReminderService = Depends(get_reminder_service),
):
    """Add a reminder to a task."""
    try:
        # Verify task exists and belongs to user
        from ...services.task_service import TaskService
        task_service = TaskService(session)
        task = task_service.get_task(task_id, current_user["id"])

        # Verify task has due date
        if not task.due_date:
            raise HTTPException(
                status_code=400,
                detail="Task must have a due date to add a reminder",
            )

        # Create reminder
        reminder = service.schedule_reminder(
            task_id=task_id,
            user_id=current_user["id"],
            offset_minutes=request.offset_minutes,
            channel=request.channel,
            due_date=task.due_date,
        )

        return {
            "id": str(reminder.id),
            "task_id": str(reminder.task_id),
            "remind_at": reminder.remind_at.isoformat(),
            "offset_minutes": reminder.offset_minutes,
            "channel": reminder.channel.value,
            "status": reminder.status.value,
            "created_at": reminder.created_at.isoformat(),
        }

    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError:
        raise HTTPException(status_code=404, detail="Task not found")
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}/reminders", response_model=dict)
async def get_task_reminders(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    session: Session = Depends(get_session),
    service: ReminderService = Depends(get_reminder_service),
):
    """Get all reminders for a task."""
    try:
        # Verify task exists and belongs to user
        from ...services.task_service import TaskService
        task_service = TaskService(session)
        task_service.get_task(task_id, current_user["id"])

        # Get reminders
        reminders = service.get_reminders_for_task(task_id, current_user["id"])

        return {
            "reminders": [
                {
                    "id": str(r.id),
                    "remind_at": r.remind_at.isoformat(),
                    "offset_minutes": r.offset_minutes,
                    "channel": r.channel.value,
                    "status": r.status.value,
                }
                for r in reminders
            ],
            "total": len(reminders),
        }

    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/reminders/{reminder_id}", status_code=204)
async def delete_reminder(
    reminder_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: ReminderService = Depends(get_reminder_service),
):
    """Delete a reminder."""
    success = service.delete_reminder(reminder_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Reminder not found")
