"""Pydantic schemas for Task API requests and responses."""

from datetime import datetime
from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field

from ..models.task import Priority


class CategoryInTask(BaseModel):
    """Category data embedded in task response."""

    id: UUID
    name: str
    color: str

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    """Response schema for a single task."""

    id: UUID
    title: str
    description: Optional[str]
    completed: bool
    priority: Priority
    category_id: Optional[UUID]
    category: Optional[CategoryInTask]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """Response schema for list of tasks."""

    data: List[TaskResponse]
    count: int


class SingleTaskResponse(BaseModel):
    """Response schema for single task operations."""

    data: TaskResponse
    message: Optional[str] = None


class CreateTaskRequest(BaseModel):
    """Request schema for creating a task."""

    title: str = Field(..., min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Priority = Priority.MEDIUM
    category_id: Optional[UUID] = None


class UpdateTaskRequest(BaseModel):
    """Request schema for updating a task."""

    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    priority: Optional[Priority] = None
    category_id: Optional[UUID] = None
