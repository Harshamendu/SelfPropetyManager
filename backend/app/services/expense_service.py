import uuid
from datetime import date

from sqlalchemy import and_, extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.expense import Expense
from app.schemas.expense import ExpenseCreate, ExpenseUpdate


async def get_by_property(
    db: AsyncSession,
    property_id: uuid.UUID,
    year: int | None = None,
    category: str | None = None,
) -> list[Expense]:
    stmt = select(Expense).where(Expense.property_id == property_id)
    if year is not None:
        stmt = stmt.where(extract("year", Expense.date) == year)
    if category is not None:
        stmt = stmt.where(Expense.category == category)
    stmt = stmt.order_by(Expense.date.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create(
    db: AsyncSession, property_id: uuid.UUID, schema: ExpenseCreate
) -> Expense:
    data = schema.model_dump()
    data["property_id"] = property_id
    expense = Expense(**data)
    db.add(expense)
    await db.commit()
    await db.refresh(expense)
    return expense


async def update(db: AsyncSession, id: uuid.UUID, schema: ExpenseUpdate) -> Expense:
    stmt = select(Expense).where(Expense.id == id)
    result = await db.execute(stmt)
    expense = result.scalar_one_or_none()
    if expense is None:
        raise ValueError(f"Expense {id} not found")
    update_data = schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(expense, key, value)
    await db.commit()
    await db.refresh(expense)
    return expense


async def delete(db: AsyncSession, id: uuid.UUID) -> None:
    stmt = select(Expense).where(Expense.id == id)
    result = await db.execute(stmt)
    expense = result.scalar_one_or_none()
    if expense is None:
        raise ValueError(f"Expense {id} not found")
    await db.delete(expense)
    await db.commit()


async def generate_recurring(
    db: AsyncSession, property_id: uuid.UUID, year: int, month: int
) -> list[Expense]:
    """Generate recurring expense instances for a given property/year/month.

    Finds all recurring expenses for the property, computes the date based on
    recurrence_rule and recurring_day, and only creates if no existing expense
    matches (same category, same month, from a recurring source).
    """
    # Find all recurring expense definitions for this property
    stmt = (
        select(Expense)
        .where(Expense.property_id == property_id)
        .where(Expense.is_recurring == True)  # noqa: E712
    )
    result = await db.execute(stmt)
    recurring_templates = list(result.scalars().all())

    created: list[Expense] = []

    for template in recurring_templates:
        recurrence = template.recurrence_rule or "monthly"

        # Determine if this recurring expense applies to the requested month
        if recurrence == "monthly":
            pass  # applies every month
        elif recurrence == "quarterly":
            # Quarters: Jan(1), Apr(4), Jul(7), Oct(10)
            if month not in (1, 4, 7, 10):
                continue
        elif recurrence == "annually":
            # Only the month matching the original expense date
            if month != template.date.month:
                continue
        else:
            # Unknown recurrence rule; treat as monthly
            pass

        # Compute the day for this expense
        day = template.recurring_day or template.date.day
        # Clamp day to valid range for the month
        import calendar
        max_day = calendar.monthrange(year, month)[1]
        day = min(day, max_day)
        expense_date = date(year, month, day)

        # Check if an expense already exists for this category in this month
        # that was generated from a recurring source
        check_stmt = (
            select(Expense)
            .where(
                and_(
                    Expense.property_id == property_id,
                    Expense.category == template.category,
                    extract("year", Expense.date) == year,
                    extract("month", Expense.date) == month,
                    Expense.description == template.description,
                )
            )
        )
        check_result = await db.execute(check_stmt)
        existing = check_result.scalar_one_or_none()
        if existing is not None:
            continue

        # Create the recurring instance
        new_expense = Expense(
            property_id=property_id,
            category=template.category,
            description=template.description,
            amount=template.amount,
            date=expense_date,
            is_recurring=False,
            vendor=template.vendor,
        )
        db.add(new_expense)
        created.append(new_expense)

    if created:
        await db.commit()
        for exp in created:
            await db.refresh(exp)

    return created
