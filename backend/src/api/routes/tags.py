"""API routes for tags."""

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlmodel import Session

from ..routes.auth import get_current_user
from ...database import get_session
from ...services.tag_service import TagService


router = APIRouter(prefix="/api/tags", tags=["tags"])


class CreateTagRequest(BaseModel):
    """Request schema for creating a tag."""

    name: str = Field(..., min_length=1, max_length=50, description="Tag name")
    color: str = Field(default="#6366f1", description="Tag color (hex code)")


class UpdateTagRequest(BaseModel):
    """Request schema for updating a tag."""

    name: str | None = Field(None, min_length=1, max_length=50, description="Tag name")
    color: str | None = Field(None, description="Tag color (hex code)")


class TagResponse(BaseModel):
    """Response schema for a tag."""

    id: str
    name: str
    color: str
    created_at: str

    class Config:
        from_attributes = True


def get_tag_service(session: Session = Depends(get_session)) -> TagService:
    """Dependency to get TagService instance."""
    return TagService(session)


@router.get("", response_model=dict)
async def get_tags(
    current_user: dict = Depends(get_current_user),
    service: TagService = Depends(get_tag_service),
):
    """Get all tags for the current user."""
    tags = service.get_all_tags(current_user["id"])

    return {
        "data": [
            {
                "id": str(tag.id),
                "name": tag.name,
                "color": tag.color,
                "created_at": tag.created_at.isoformat(),
            }
            for tag in tags
        ],
        "count": len(tags),
    }


@router.post("", response_model=dict, status_code=201)
async def create_tag(
    request: CreateTagRequest,
    current_user: dict = Depends(get_current_user),
    service: TagService = Depends(get_tag_service),
):
    """Create a new tag."""
    try:
        tag = service.create_tag(
            user_id=current_user["id"],
            name=request.name,
            color=request.color,
        )

        return {
            "data": {
                "id": str(tag.id),
                "name": tag.name,
                "color": tag.color,
                "created_at": tag.created_at.isoformat(),
            },
            "message": "Tag created successfully",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{tag_id}", response_model=dict)
async def update_tag(
    tag_id: UUID,
    request: UpdateTagRequest,
    current_user: dict = Depends(get_current_user),
    service: TagService = Depends(get_tag_service),
):
    """Update a tag."""
    try:
        tag = service.update_tag(
            tag_id=tag_id,
            user_id=current_user["id"],
            name=request.name,
            color=request.color,
        )

        if not tag:
            raise HTTPException(status_code=404, detail="Tag not found")

        return {
            "data": {
                "id": str(tag.id),
                "name": tag.name,
                "color": tag.color,
                "created_at": tag.created_at.isoformat(),
            },
            "message": "Tag updated successfully",
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{tag_id}", status_code=204)
async def delete_tag(
    tag_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: TagService = Depends(get_tag_service),
):
    """Delete a tag."""
    success = service.delete_tag(tag_id, current_user["id"])
    if not success:
        raise HTTPException(status_code=404, detail="Tag not found")


@router.post("/{tag_id}/tasks/{task_id}", status_code=201)
async def add_tag_to_task(
    tag_id: UUID,
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: TagService = Depends(get_tag_service),
):
    """Add a tag to a task."""
    try:
        added = service.add_tag_to_task(
            task_id=task_id,
            tag_id=tag_id,
            user_id=current_user["id"],
        )

        if not added:
            raise HTTPException(status_code=400, detail="Tag already added to task")

        return {"message": "Tag added to task"}

    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.delete("/{tag_id}/tasks/{task_id}", status_code=204)
async def remove_tag_from_task(
    tag_id: UUID,
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: TagService = Depends(get_tag_service),
):
    """Remove a tag from a task."""
    success = service.remove_tag_from_task(
        task_id=task_id,
        tag_id=tag_id,
        user_id=current_user["id"],
    )

    if not success:
        raise HTTPException(status_code=404, detail="Tag or association not found")


@router.get("/tasks/{task_id}", response_model=dict)
async def get_task_tags(
    task_id: UUID,
    current_user: dict = Depends(get_current_user),
    service: TagService = Depends(get_tag_service),
):
    """Get all tags for a task."""
    tags = service.get_tags_for_task(task_id, current_user["id"])

    return {
        "data": [
            {
                "id": str(tag.id),
                "name": tag.name,
                "color": tag.color,
            }
            for tag in tags
        ],
        "count": len(tags),
    }
