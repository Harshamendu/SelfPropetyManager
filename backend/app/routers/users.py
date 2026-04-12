from uuid import UUID

from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import get_db, require_admin
from app.models.user import User
from app.schemas.user import (
    UserCreate,
    UserListResponse,
    UserPropertyAssign,
    UserPropertyResponse,
    UserUpdate,
)
from app.services import user_service

router = APIRouter(tags=["Users"], dependencies=[Depends(require_admin)])


@router.get("/users", response_model=list[UserListResponse])
async def list_users(db: AsyncSession = Depends(get_db)):
    return await user_service.list_users(db)


@router.post("/users", response_model=UserListResponse, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserCreate, db: AsyncSession = Depends(get_db)):
    return await user_service.create_user(db, data)


@router.get("/users/{user_id}", response_model=UserListResponse)
async def get_user(user_id: UUID, db: AsyncSession = Depends(get_db)):
    return await user_service.get_user(db, user_id)


@router.put("/users/{user_id}", response_model=UserListResponse)
async def update_user(
    user_id: UUID, data: UserUpdate, db: AsyncSession = Depends(get_db)
):
    return await user_service.update_user(db, user_id, data)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def deactivate_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current: User = Depends(require_admin),
):
    await user_service.deactivate_user(db, user_id, current.id)


@router.get("/users/{user_id}/properties", response_model=list[UserPropertyResponse])
async def list_user_properties(
    user_id: UUID, db: AsyncSession = Depends(get_db)
):
    return await user_service.list_user_assignments(db, user_id)


@router.post(
    "/users/{user_id}/properties",
    response_model=UserPropertyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def assign_property(
    user_id: UUID,
    data: UserPropertyAssign,
    db: AsyncSession = Depends(get_db),
):
    return await user_service.assign_property(db, user_id, data.property_id)


@router.delete(
    "/users/{user_id}/properties/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def unassign_property(
    user_id: UUID,
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    await user_service.unassign_property(db, user_id, property_id)
