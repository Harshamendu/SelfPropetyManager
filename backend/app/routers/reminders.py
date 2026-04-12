from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import (
    get_accessible_property_ids,
    get_db,
    require_property_access,
    require_user,
    require_writer,
)
from app.models.reminder import Reminder
from app.schemas.reminder import (
    ReminderCreate,
    ReminderResponse,
    ReminderUpdate,
)

router = APIRouter(tags=["Reminders"], dependencies=[Depends(require_user)])


@router.get("/reminders", response_model=list[ReminderResponse])
async def list_reminders(
    property_id: Optional[UUID] = None,
    upcoming: bool = False,
    overdue: bool = False,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    stmt = select(Reminder)
    accessible = await get_accessible_property_ids(user, db)
    if accessible is not None:
        if not accessible:
            return []
        stmt = stmt.where(Reminder.property_id.in_(accessible))
    if property_id is not None:
        if accessible is not None and property_id not in accessible:
            raise HTTPException(status_code=403, detail="No access to this property")
        stmt = stmt.where(Reminder.property_id == property_id)
    if upcoming:
        stmt = stmt.where(
            Reminder.is_completed == False,  # noqa: E712
            Reminder.due_date >= datetime.now(timezone.utc),
        )
    if overdue:
        stmt = stmt.where(
            Reminder.is_completed == False,  # noqa: E712
            Reminder.due_date < datetime.now(timezone.utc),
        )
    stmt = stmt.order_by(Reminder.due_date)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/reminders",
    response_model=ReminderResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_reminder(
    data: ReminderCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    if data.property_id:
        await require_property_access(data.property_id, user, db)
    reminder = Reminder(**data.model_dump())
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder


@router.put("/reminders/{reminder_id}", response_model=ReminderResponse)
async def update_reminder(
    reminder_id: UUID,
    data: ReminderUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    reminder = await db.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if reminder.property_id:
        await require_property_access(reminder.property_id, user, db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(reminder, key, value)
    await db.commit()
    await db.refresh(reminder)
    return reminder


@router.patch(
    "/reminders/{reminder_id}/complete",
    response_model=ReminderResponse,
)
async def complete_reminder(
    reminder_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    reminder = await db.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if reminder.property_id:
        await require_property_access(reminder.property_id, user, db)
    reminder.is_completed = True
    reminder.completed_at = datetime.now(timezone.utc)
    await db.commit()
    await db.refresh(reminder)
    return reminder


@router.delete(
    "/reminders/{reminder_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_reminder(
    reminder_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    reminder = await db.get(Reminder, reminder_id)
    if not reminder:
        raise HTTPException(status_code=404, detail="Reminder not found")
    if reminder.property_id:
        await require_property_access(reminder.property_id, user, db)
    await db.delete(reminder)
    await db.commit()
