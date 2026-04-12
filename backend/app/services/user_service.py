from uuid import UUID

from fastapi import HTTPException, status
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User, UserRole
from app.models.user_property import UserProperty
from app.schemas.user import UserCreate, UserUpdate

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


async def list_users(db: AsyncSession) -> list[User]:
    result = await db.execute(select(User).order_by(User.created_at))
    return list(result.scalars().all())


async def get_user(db: AsyncSession, user_id: UUID) -> User:
    user = await db.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    existing = await db.execute(select(User).where(User.email == data.email))
    if existing.scalars().first():
        raise HTTPException(status_code=400, detail="Email already registered")

    user = User(
        email=data.email,
        hashed_password=pwd_context.hash(data.password),
        full_name=data.full_name,
        role=data.role,
        is_active=data.is_active,
        is_admin=(data.role == UserRole.ADMIN),
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user(db: AsyncSession, user_id: UUID, data: UserUpdate) -> User:
    user = await get_user(db, user_id)

    if data.full_name is not None:
        user.full_name = data.full_name
    if data.role is not None:
        user.role = data.role
        user.is_admin = data.role == UserRole.ADMIN
    if data.is_active is not None:
        user.is_active = data.is_active
    if data.password:
        user.hashed_password = pwd_context.hash(data.password)

    await db.commit()
    await db.refresh(user)
    return user


async def deactivate_user(
    db: AsyncSession, user_id: UUID, current_user_id: UUID
) -> None:
    if user_id == current_user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot deactivate your own account",
        )
    user = await get_user(db, user_id)
    user.is_active = False
    await db.commit()


async def assign_property(
    db: AsyncSession, user_id: UUID, property_id: UUID
) -> UserProperty:
    # Ensure user exists
    await get_user(db, user_id)

    existing = await db.execute(
        select(UserProperty).where(
            UserProperty.user_id == user_id,
            UserProperty.property_id == property_id,
        )
    )
    assignment = existing.scalars().first()
    if assignment:
        return assignment

    assignment = UserProperty(user_id=user_id, property_id=property_id)
    db.add(assignment)
    await db.commit()
    await db.refresh(assignment)
    return assignment


async def unassign_property(
    db: AsyncSession, user_id: UUID, property_id: UUID
) -> None:
    result = await db.execute(
        select(UserProperty).where(
            UserProperty.user_id == user_id,
            UserProperty.property_id == property_id,
        )
    )
    assignment = result.scalars().first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    await db.delete(assignment)
    await db.commit()


async def list_user_assignments(
    db: AsyncSession, user_id: UUID
) -> list[UserProperty]:
    await get_user(db, user_id)
    result = await db.execute(
        select(UserProperty).where(UserProperty.user_id == user_id)
    )
    return list(result.scalars().all())
