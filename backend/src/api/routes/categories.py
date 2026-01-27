"""Category API routes with authentication."""

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from ..routes.auth import get_current_user
from ...database import get_session
from ...schemas.category import (
    CategoryListResponse,
    CategoryResponse,
    CreateCategoryRequest,
    SingleCategoryResponse,
)
from ...services.category_service import CategoryNotFoundError, CategoryService

router = APIRouter(prefix="/api/categories", tags=["categories"])


def get_category_service(session: Session = Depends(get_session)) -> CategoryService:
    """Dependency to get CategoryService instance."""
    return CategoryService(session)


@router.get("", response_model=CategoryListResponse)
async def get_categories(
    current_user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> CategoryListResponse:
    """Get all categories (requires authentication)."""
    categories = service.get_all_categories()
    return CategoryListResponse(
        data=[CategoryResponse.model_validate(cat) for cat in categories],
        count=len(categories),
    )


@router.post("", response_model=SingleCategoryResponse, status_code=201)
async def create_category(
    request: CreateCategoryRequest,
    current_user: dict = Depends(get_current_user),
    service: CategoryService = Depends(get_category_service),
) -> SingleCategoryResponse:
    """Create a new category (requires authentication)."""
    try:
        category = service.create_category(
            name=request.name,
            color=request.color,
        )
        return SingleCategoryResponse(
            data=CategoryResponse.model_validate(category),
            message="Category created successfully",
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
