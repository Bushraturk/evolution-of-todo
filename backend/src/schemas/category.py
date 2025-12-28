"""Pydantic schemas for Category API requests and responses."""

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel, Field


class CategoryResponse(BaseModel):
    """Response schema for a single category."""

    id: UUID
    name: str
    color: str

    class Config:
        from_attributes = True


class CategoryListResponse(BaseModel):
    """Response schema for list of categories."""

    data: List[CategoryResponse]
    count: int


class SingleCategoryResponse(BaseModel):
    """Response schema for single category operations."""

    data: CategoryResponse
    message: Optional[str] = None


class CreateCategoryRequest(BaseModel):
    """Request schema for creating a category."""

    name: str = Field(..., min_length=1, max_length=50)
    color: str = Field("#808080", max_length=7, pattern=r"^#[0-9A-Fa-f]{6}$")
