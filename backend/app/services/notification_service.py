import uuid

from sqlalchemy import func, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.notification import Notification


async def get_all(
    db: AsyncSession, unread_only: bool = False
) -> list[Notification]:
    stmt = select(Notification)
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)  # noqa: E712
    stmt = stmt.order_by(Notification.created_at.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_unread_count(db: AsyncSession) -> int:
    stmt = (
        select(func.count())
        .select_from(Notification)
        .where(Notification.is_read == False)  # noqa: E712
    )
    result = await db.execute(stmt)
    return result.scalar_one()


async def mark_read(db: AsyncSession, id: uuid.UUID) -> Notification:
    stmt = select(Notification).where(Notification.id == id)
    result = await db.execute(stmt)
    notification = result.scalar_one_or_none()
    if notification is None:
        raise ValueError(f"Notification {id} not found")
    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification


async def mark_all_read(db: AsyncSession) -> None:
    stmt = (
        update(Notification)
        .where(Notification.is_read == False)  # noqa: E712
        .values(is_read=True)
    )
    await db.execute(stmt)
    await db.commit()


async def create(
    db: AsyncSession,
    reminder_id: uuid.UUID | None,
    title: str,
    message: str,
) -> Notification:
    notification = Notification(
        reminder_id=reminder_id,
        title=title,
        message=message,
    )
    db.add(notification)
    await db.commit()
    await db.refresh(notification)
    return notification
