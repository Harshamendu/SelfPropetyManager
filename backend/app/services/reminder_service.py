import uuid
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.reminder import Reminder
from app.schemas.reminder import ReminderCreate, ReminderUpdate


async def get_all(
    db: AsyncSession,
    property_id: uuid.UUID | None = None,
    upcoming: bool = False,
    overdue: bool = False,
) -> list[Reminder]:
    stmt = select(Reminder)
    if property_id is not None:
        stmt = stmt.where(Reminder.property_id == property_id)
    now = datetime.utcnow()
    if upcoming:
        stmt = stmt.where(Reminder.due_date >= now).where(
            Reminder.is_completed == False  # noqa: E712
        )
    if overdue:
        stmt = stmt.where(Reminder.due_date < now).where(
            Reminder.is_completed == False  # noqa: E712
        )
    stmt = stmt.order_by(Reminder.due_date)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create(db: AsyncSession, schema: ReminderCreate) -> Reminder:
    reminder = Reminder(**schema.model_dump())
    db.add(reminder)
    await db.commit()
    await db.refresh(reminder)
    return reminder


async def update(
    db: AsyncSession, id: uuid.UUID, schema: ReminderUpdate
) -> Reminder:
    stmt = select(Reminder).where(Reminder.id == id)
    result = await db.execute(stmt)
    reminder = result.scalar_one_or_none()
    if reminder is None:
        raise ValueError(f"Reminder {id} not found")
    update_data = schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(reminder, key, value)
    await db.commit()
    await db.refresh(reminder)
    return reminder


async def mark_complete(db: AsyncSession, id: uuid.UUID) -> Reminder:
    stmt = select(Reminder).where(Reminder.id == id)
    result = await db.execute(stmt)
    reminder = result.scalar_one_or_none()
    if reminder is None:
        raise ValueError(f"Reminder {id} not found")
    reminder.is_completed = True
    reminder.completed_at = datetime.utcnow()
    await db.commit()
    await db.refresh(reminder)
    return reminder


async def delete(db: AsyncSession, id: uuid.UUID) -> None:
    stmt = select(Reminder).where(Reminder.id == id)
    result = await db.execute(stmt)
    reminder = result.scalar_one_or_none()
    if reminder is None:
        raise ValueError(f"Reminder {id} not found")
    await db.delete(reminder)
    await db.commit()


async def get_due_reminders(db: AsyncSession) -> list[Reminder]:
    """Get reminders where due_date <= now and not completed."""
    now = datetime.utcnow()
    stmt = (
        select(Reminder)
        .where(Reminder.due_date <= now)
        .where(Reminder.is_completed == False)  # noqa: E712
        .order_by(Reminder.due_date)
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())
