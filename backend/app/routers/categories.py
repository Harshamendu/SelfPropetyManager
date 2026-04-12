from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_admin, require_user
from app.models.category import Category
from app.schemas.category import CategoryCreate, CategoryResponse, CategoryUpdate

router = APIRouter(tags=["Categories"], dependencies=[Depends(require_user)])


@router.get("/categories", response_model=list[CategoryResponse])
async def list_categories(
    category_type: Optional[str] = None,
    property_id: Optional[UUID] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Category)
    if category_type:
        stmt = stmt.where(Category.category_type == category_type)
    if property_id:
        # Return both global (null property_id) and property-specific categories
        stmt = stmt.where(
            or_(
                Category.property_id == property_id,
                Category.property_id.is_(None),
            )
        )
    stmt = stmt.order_by(Category.name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/categories",
    response_model=CategoryResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_category(
    data: CategoryCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin),
):
    if data.category_type not in ("expense", "payment"):
        raise HTTPException(
            status_code=400,
            detail="category_type must be 'expense' or 'payment'",
        )
    category = Category(**data.model_dump())
    db.add(category)
    await db.commit()
    await db.refresh(category)
    return category


@router.put("/categories/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: UUID,
    data: CategoryUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin),
):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(category, key, value)
    await db.commit()
    await db.refresh(category)
    return category


@router.delete(
    "/categories/{category_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_category(
    category_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin),
):
    category = await db.get(Category, category_id)
    if not category:
        raise HTTPException(status_code=404, detail="Category not found")
    await db.delete(category)
    await db.commit()
