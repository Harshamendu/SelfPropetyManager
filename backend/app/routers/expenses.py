import calendar
from datetime import date
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import (
    get_db,
    require_property_access,
    require_user,
    require_writer,
)
from app.models.expense import Expense
from app.models.property import Property
from app.schemas.expense import ExpenseCreate, ExpenseResponse, ExpenseUpdate

router = APIRouter(tags=["Expenses"], dependencies=[Depends(require_user)])


def _generate_monthly_dates(start_date: date, year: int):
    """Yield expense dates for each month of the year from start_date month."""
    start_month = start_date.month if start_date.year == year else 1
    for month in range(start_month, 13):
        max_day = calendar.monthrange(year, month)[1]
        day = min(start_date.day, max_day)
        yield date(year, month, day)


def _generate_quarterly_dates(start_date: date, year: int):
    """Yield expense dates for each quarter of the year."""
    start_month = start_date.month if start_date.year == year else 1
    for month in [1, 4, 7, 10]:
        if month < start_month:
            continue
        max_day = calendar.monthrange(year, month)[1]
        day = min(start_date.day, max_day)
        yield date(year, month, day)


def _generate_annual_dates(start_date: date, year: int):
    """Yield a single expense date for the year."""
    month = start_date.month
    max_day = calendar.monthrange(year, month)[1]
    day = min(start_date.day, max_day)
    yield date(year, month, day)


@router.get(
    "/properties/{property_id}/expenses",
    response_model=list[ExpenseResponse],
)
async def list_expenses(
    property_id: UUID,
    year: Optional[int] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    await require_property_access(property_id, user, db)
    prop = await db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    stmt = select(Expense).where(Expense.property_id == property_id)
    if year is not None:
        stmt = stmt.where(extract("year", Expense.date) == year)
    if category is not None:
        stmt = stmt.where(Expense.category == category)
    stmt = stmt.order_by(Expense.date.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/properties/{property_id}/expenses",
    response_model=list[ExpenseResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_expense(
    property_id: UUID,
    data: ExpenseCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    await require_property_access(property_id, user, db)
    prop = await db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    if not data.is_recurring:
        # Single expense
        expense_data = data.model_dump()
        expense_data["property_id"] = property_id
        expense = Expense(**expense_data)
        db.add(expense)
        await db.commit()
        await db.refresh(expense)
        return [expense]

    # Recurring: auto-generate entries for the year of the date
    rule = (data.recurrence_rule or "monthly").lower()
    year = data.date.year

    if rule == "monthly":
        dates = list(_generate_monthly_dates(data.date, year))
    elif rule == "quarterly":
        dates = list(_generate_quarterly_dates(data.date, year))
    elif rule == "annually":
        dates = list(_generate_annual_dates(data.date, year))
    else:
        dates = list(_generate_monthly_dates(data.date, year))

    created = []
    for exp_date in dates:
        expense = Expense(
            property_id=property_id,
            category=data.category,
            description=data.description,
            amount=data.amount,
            date=exp_date,
            is_recurring=True,
            recurrence_rule=data.recurrence_rule,
            recurring_day=data.recurring_day or data.date.day,
            is_marked_done=False,
            vendor=data.vendor,
        )
        db.add(expense)
        created.append(expense)

    await db.commit()
    for exp in created:
        await db.refresh(exp)
    return created


@router.put("/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    expense_id: UUID,
    data: ExpenseUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    expense = await db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    await require_property_access(expense.property_id, user, db)
    # Block editing future recurring entries
    if expense.is_recurring and expense.date > date.today():
        raise HTTPException(
            status_code=400,
            detail="Cannot edit future recurring expenses",
        )
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(expense, key, value)
    await db.commit()
    await db.refresh(expense)
    return expense


@router.patch("/expenses/{expense_id}/mark-done", response_model=ExpenseResponse)
async def mark_expense_done(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    expense = await db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    await require_property_access(expense.property_id, user, db)
    expense.is_marked_done = True
    await db.commit()
    await db.refresh(expense)
    return expense


@router.patch("/expenses/{expense_id}/unmark-done", response_model=ExpenseResponse)
async def unmark_expense_done(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    expense = await db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    await require_property_access(expense.property_id, user, db)
    expense.is_marked_done = False
    await db.commit()
    await db.refresh(expense)
    return expense


@router.delete(
    "/expenses/{expense_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_expense(
    expense_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    expense = await db.get(Expense, expense_id)
    if not expense:
        raise HTTPException(status_code=404, detail="Expense not found")
    await require_property_access(expense.property_id, user, db)
    await db.delete(expense)
    await db.commit()
