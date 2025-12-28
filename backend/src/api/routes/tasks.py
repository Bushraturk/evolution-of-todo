"""Task API routes."""

from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from ...database import get_session
from ...models.task import Priority
from ...schemas.task import (
    CreateTaskRequest,
    SingleTaskResponse,
    TaskListResponse,
    TaskResponse,
    UpdateTaskRequest,
)
from ...services.task_service import TaskNotFoundError, TaskService, ValidationError

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
    service: TaskService = Depends(get_task_service),
) -> TaskListResponse:
    """Get all tasks with optional filtering and sorting."""
    tasks = service.get_all_tasks(
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
    service: TaskService = Depends(get_task_service),
) -> SingleTaskResponse:
    """Create a new task."""
    try:
        task = service.create_task(
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
    service: TaskService = Depends(get_task_service),
) -> SingleTaskResponse:
    """Get a single task by ID."""
    try:
        task = service.get_task(task_id)
        return SingleTaskResponse(data=TaskResponse.model_validate(task))
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.put("/{task_id}", response_model=SingleTaskResponse)
async def update_task(
    task_id: UUID,
    request: UpdateTaskRequest,
    service: TaskService = Depends(get_task_service),
) -> SingleTaskResponse:
    """Update a task."""
    try:
        task = service.update_task(
            task_id=task_id,
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
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{task_id}", response_model=SingleTaskResponse)
async def delete_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
) -> SingleTaskResponse:
    """Delete a task."""
    try:
        task = service.delete_task(task_id)
        return SingleTaskResponse(
            data=TaskResponse.model_validate(task),
            message="Task deleted successfully",
        )
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{task_id}/toggle", response_model=SingleTaskResponse)
async def toggle_task(
    task_id: UUID,
    service: TaskService = Depends(get_task_service),
) -> SingleTaskResponse:
    """Toggle task completion status."""
    try:
        task = service.toggle_complete(task_id)
        status = "complete" if task.completed else "incomplete"
        return SingleTaskResponse(
            data=TaskResponse.model_validate(task),
            message=f"Task marked as {status}",
        )
    except TaskNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
