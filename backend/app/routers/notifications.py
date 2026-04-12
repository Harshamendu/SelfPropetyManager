from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import func

from app.dependencies import get_db, require_user
from app.models.notification import Notification
from app.schemas.notification import NotificationResponse, UnreadCountResponse

router = APIRouter(tags=["Notifications"], dependencies=[Depends(require_user)])


@router.get("/notifications", response_model=list[NotificationResponse])
async def list_notifications(
    unread_only: bool = False,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Notification).order_by(Notification.created_at.desc())
    if unread_only:
        stmt = stmt.where(Notification.is_read == False)  # noqa: E712
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/notifications/unread-count",
    response_model=UnreadCountResponse,
)
async def get_unread_count(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(func.count()).where(
            Notification.is_read == False  # noqa: E712
        )
    )
    count = result.scalar()
    return UnreadCountResponse(count=count)


@router.patch(
    "/notifications/{notification_id}/read",
    response_model=NotificationResponse,
)
async def mark_notification_read(
    notification_id: UUID,
    db: AsyncSession = Depends(get_db),
):
    notification = await db.get(Notification, notification_id)
    if not notification:
        raise HTTPException(
            status_code=404, detail="Notification not found"
        )
    notification.is_read = True
    await db.commit()
    await db.refresh(notification)
    return notification


@router.post("/notifications/mark-all-read")
async def mark_all_read(
    db: AsyncSession = Depends(get_db),
):
    await db.execute(
        update(Notification)
        .where(Notification.is_read == False)  # noqa: E712
        .values(is_read=True)
    )
    await db.commit()
    return {"message": "All notifications marked as read"}
