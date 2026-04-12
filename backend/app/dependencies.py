from collections.abc import AsyncGenerator
from uuid import UUID

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.database import async_session

security = HTTPBearer(auto_error=False)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: AsyncSession = Depends(get_db),
):
    """Extract and validate user from JWT token. Returns None if no token."""
    if not credentials:
        return None

    try:
        payload = jwt.decode(
            credentials.credentials,
            settings.jwt_secret_key,
            algorithms=[settings.jwt_algorithm],
        )
        user_id = payload.get("sub")
        if not user_id:
            return None
    except JWTError:
        return None

    from app.models.user import User
    user = await db.get(User, UUID(user_id))
    if not user or not user.is_active:
        return None
    return user


async def require_user(
    user=Depends(get_current_user),
):
    """Require authenticated user. Raises 401 if not authenticated."""
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


async def require_admin(user=Depends(require_user)):
    """Require admin role. Raises 403 if not admin."""
    from app.models.user import UserRole
    if user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required",
        )
    return user


async def require_writer(user=Depends(require_user)):
    """Require a role that can create/modify resources (not tenant or viewer)."""
    from app.models.user import UserRole
    if user.role in (UserRole.TENANT, UserRole.VIEWER):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Read-only role cannot modify resources",
        )
    return user


async def get_accessible_property_ids(user, db: AsyncSession) -> list[UUID] | None:
    """Return the set of property IDs the user can access.

    Returns None to signal "all properties" (admin) so callers can skip filtering.
    Returns a (possibly empty) list of UUIDs for scoped roles.
    """
    from app.models.contact import Contact
    from app.models.property import Property
    from app.models.user import UserRole
    from app.models.user_property import UserProperty

    if user.role == UserRole.ADMIN:
        return None  # means "all"

    if user.role == UserRole.TENANT:
        # Tenant sees the property their linked contact is on
        result = await db.execute(
            select(Contact.property_id).where(
                Contact.user_id == user.id, Contact.property_id.isnot(None)
            )
        )
        return [row[0] for row in result.all()]

    # property_manager and viewer: assignments
    result = await db.execute(
        select(UserProperty.property_id).where(UserProperty.user_id == user.id)
    )
    return [row[0] for row in result.all()]


async def require_property_access(
    property_id: UUID,
    user,
    db: AsyncSession,
) -> None:
    """Raise 403 if user cannot access the given property."""
    accessible = await get_accessible_property_ids(user, db)
    if accessible is None:
        return  # admin
    if property_id not in accessible:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have access to this property",
        )
