import uuid
from datetime import datetime

from sqlalchemy import extract, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense
from app.models.property import Property
from app.models.reminder import Reminder
from app.models.rental_payment import RentalPayment
from app.schemas.property import PropertyCreate, PropertyUpdate


async def get_all(db: AsyncSession, is_active: bool = True) -> list[Property]:
    stmt = select(Property).where(Property.is_active == is_active).order_by(Property.name)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, id: uuid.UUID) -> Property | None:
    stmt = select(Property).where(Property.id == id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create(db: AsyncSession, schema: PropertyCreate) -> Property:
    prop = Property(**schema.model_dump())
    db.add(prop)
    await db.commit()
    await db.refresh(prop)
    return prop


async def update(db: AsyncSession, id: uuid.UUID, schema: PropertyUpdate) -> Property:
    stmt = select(Property).where(Property.id == id)
    result = await db.execute(stmt)
    prop = result.scalar_one_or_none()
    if prop is None:
        raise ValueError(f"Property {id} not found")
    update_data = schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(prop, key, value)
    await db.commit()
    await db.refresh(prop)
    return prop


async def delete(db: AsyncSession, id: uuid.UUID) -> Property:
    """Soft delete: set is_active=False."""
    stmt = select(Property).where(Property.id == id)
    result = await db.execute(stmt)
    prop = result.scalar_one_or_none()
    if prop is None:
        raise ValueError(f"Property {id} not found")
    prop.is_active = False
    await db.commit()
    await db.refresh(prop)
    return prop


async def get_summary(db: AsyncSession, id: uuid.UUID, year: int) -> dict:
    """Return rent_collected_ytd, expenses_ytd, upcoming_reminders for a property."""
    # Rent collected YTD
    rent_stmt = (
        select(func.coalesce(func.sum(RentalPayment.amount), 0))
        .where(RentalPayment.property_id == id)
        .where(extract("year", RentalPayment.payment_date) == year)
    )
    rent_result = await db.execute(rent_stmt)
    rent_collected_ytd = float(rent_result.scalar_one())

    # Expenses YTD
    expense_stmt = (
        select(func.coalesce(func.sum(Expense.amount), 0))
        .where(Expense.property_id == id)
        .where(extract("year", Expense.date) == year)
    )
    expense_result = await db.execute(expense_stmt)
    expenses_ytd = float(expense_result.scalar_one())

    # Upcoming reminders (not completed, due_date >= now)
    reminder_stmt = (
        select(func.count())
        .select_from(Reminder)
        .where(Reminder.property_id == id)
        .where(Reminder.is_completed == False)  # noqa: E712
        .where(Reminder.due_date >= datetime.utcnow())
    )
    reminder_result = await db.execute(reminder_stmt)
    upcoming_reminders = reminder_result.scalar_one()

    return {
        "rent_collected_ytd": rent_collected_ytd,
        "expenses_ytd": expenses_ytd,
        "upcoming_reminders": upcoming_reminders,
    }
