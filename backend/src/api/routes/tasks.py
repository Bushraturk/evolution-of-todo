"""Task API routes with authentication."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ...auth.dependencies import get_current_user
from ...database import get_session
from ...models.task import Priority
from ...schemas.task import (
    CreateTaskRequest,
    SingleTaskResponse,
    TaskListResponse,
    TaskResponse,
    UpdateTaskRequest,
)
from ...services.task_service import (
    AccessDeniedError,
    TaskNotFoundError,
    TaskService,
    ValidationError,
)

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


def get_task_service(session: Session = Depends(get_session)) -> TaskService:
    """Dependency to get TaskService instance."""
    return TaskService(session)


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    search: Optional[str] = Query(None, description="Search in title and description"),
    status: Optional[str] = Query(
        None, description="Filter by status: all, completed, incomplete"
    ),
    priority: Optional[Priority] = Query(None, description="Filter by priority"),
    category_id: Optional[UUID] = Query(None, description="Filter by category"),
    sort_by: str = Query("created_at", description="Sort by: created_at, priority, title"),
    sort_order: str = Query("desc", description="Sort order: asc, desc"),
    current_user: dict = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> TaskListResponse:
    """Get all tasks for the authenticated user with optional filtering and sorting."""
    tasks = service.get_all_tasks(
        user_id=current_user["id"],
        search=search,
        status=status,
        priority=priority,
        category_id=category_id,
        sort_by=sort_by,
        sort_order=sort_order,
    )
    return TaskListResponse(
        data=[TaskResponse.model_validate(task) for task in tasks],
        count=len(tasks),
    )


@router.post("", response_model=SingleTaskResponse, status_code=201)
async def create_task(
    request: CreateTaskRequest,
    current_user: dict = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> SingleTaskResponse:
    """Create a new task for the authenticated user."""
    try:
        task = service.create_task(
            user_id=current_user["id"],
            title=request.title,
            description=request.description,
            priority=request.priority,
            category_id=request.category_id,
        )
        return SingleTaskResponse(
            data=TaskResponse.model_validate(task),
            message="Task created successfully",
        )
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/{task_id}", response_model=SingleTaskResponse)
async def get_task(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> SingleTaskResponse:
    """Get a single task by ID (must belong to authenticated user)."""
    try:
        task = service.get_task(task_id, current_user["id"])
        return SingleTaskResponse(data=TaskResponse.model_validate(task))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.put("/{task_id}", response_model=SingleTaskResponse)
async def update_task(
    task_id: UUID,
    request: UpdateTaskRequest,
    current_user: dict = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> SingleTaskResponse:
    """Update a task (must belong to authenticated user)."""
    try:
        task = service.update_task(
            task_id=task_id,
            user_id=current_user["id"],
            title=request.title,
            description=request.description,
            priority=request.priority,
            category_id=request.category_id,
        )
        return SingleTaskResponse(
            data=TaskResponse.model_validate(task),
            message="Task updated successfully",
        )
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError:
        raise HTTPException(status_code=404, detail="Task not found")
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{task_id}", response_model=SingleTaskResponse)
async def delete_task(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> SingleTaskResponse:
    """Delete a task (must belong to authenticated user)."""
    try:
        task = service.delete_task(task_id, current_user["id"])
        return SingleTaskResponse(
            data=TaskResponse.model_validate(task),
            message="Task deleted successfully",
        )
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.patch("/{task_id}/toggle", response_model=SingleTaskResponse)
async def toggle_task(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: TaskService = Depends(get_task_service),
) -> SingleTaskResponse:
    """Toggle task completion status (must belong to authenticated user)."""
    try:
        task = service.toggle_complete(task_id, current_user["id"])
        status = "complete" if task.completed else "incomplete"
        return SingleTaskResponse(
            data=TaskResponse.model_validate(task),
            message=f"Task marked as {status}",
        )
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except AccessDeniedError:
        raise HTTPException(status_code=404, detail="Task not found")
