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
from app.models.property import Property
from app.models.rental_payment import RentalPayment
from app.schemas.rental_payment import (
    RentalPaymentCreate,
    RentalPaymentResponse,
    RentalPaymentUpdate,
)

router = APIRouter(tags=["Rental Payments"], dependencies=[Depends(require_user)])


def _generate_monthly_dates(start: date, end: date, pay_day: int):
    """Yield (payment_date, period_start, period_end) for each month in range."""
    current_year = start.year
    current_month = start.month

    while True:
        max_day = calendar.monthrange(current_year, current_month)[1]
        period_start = date(current_year, current_month, 1)
        period_end = date(current_year, current_month, max_day)
        payment_date = date(current_year, current_month, min(pay_day, max_day))

        if period_start > end:
            break

        yield payment_date, period_start, period_end

        current_month += 1
        if current_month > 12:
            current_month = 1
            current_year += 1


def _generate_quarterly_dates(start: date, end: date, pay_day: int):
    """Yield (payment_date, period_start, period_end) for each quarter in range."""
    current_year = start.year
    current_month = start.month

    while True:
        max_day = calendar.monthrange(current_year, current_month)[1]
        period_start = date(current_year, current_month, 1)

        end_month = current_month + 2
        end_year = current_year
        if end_month > 12:
            end_month -= 12
            end_year += 1
        end_max_day = calendar.monthrange(end_year, end_month)[1]
        period_end = date(end_year, end_month, end_max_day)

        payment_date = date(current_year, current_month, min(pay_day, max_day))

        if period_start > end:
            break

        yield payment_date, period_start, period_end

        current_month += 3
        if current_month > 12:
            current_month -= 12
            current_year += 1


def _generate_annual_dates(start: date, end: date, pay_day: int):
    """Yield (payment_date, period_start, period_end) for each year in range."""
    current_year = start.year

    while True:
        period_start = date(current_year, 1, 1)
        period_end = date(current_year, 12, 31)
        pay_month = start.month
        max_day = calendar.monthrange(current_year, pay_month)[1]
        payment_date = date(current_year, pay_month, min(pay_day, max_day))

        if period_start > end:
            break

        yield payment_date, period_start, period_end
        current_year += 1


@router.get(
    "/properties/{property_id}/rental-payments",
    response_model=list[RentalPaymentResponse],
)
async def list_rental_payments(
    property_id: UUID,
    year: Optional[int] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    await require_property_access(property_id, user, db)
    prop = await db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    stmt = select(RentalPayment).where(
        RentalPayment.property_id == property_id
    )
    if year is not None:
        stmt = stmt.where(
            extract("year", RentalPayment.payment_date) == year
        )
    stmt = stmt.order_by(RentalPayment.payment_date.asc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/properties/{property_id}/rental-payments",
    response_model=list[RentalPaymentResponse],
    status_code=status.HTTP_201_CREATED,
)
async def create_rental_payment(
    property_id: UUID,
    data: RentalPaymentCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    await require_property_access(property_id, user, db)
    prop = await db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    if not data.is_recurring:
        # Single payment
        payment_data = data.model_dump()
        payment_data["property_id"] = property_id
        payment = RentalPayment(**payment_data)
        db.add(payment)
        await db.commit()
        await db.refresh(payment)
        return [payment]

    # Recurring: auto-generate entries from period_start to period_end
    rule = (data.recurrence_rule or "monthly").lower()
    pay_day = data.recurring_day or data.payment_date.day

    if rule == "monthly":
        gen = _generate_monthly_dates(data.period_start, data.period_end, pay_day)
    elif rule == "quarterly":
        gen = _generate_quarterly_dates(data.period_start, data.period_end, pay_day)
    elif rule == "annually":
        gen = _generate_annual_dates(data.period_start, data.period_end, pay_day)
    else:
        gen = _generate_monthly_dates(data.period_start, data.period_end, pay_day)

    created = []
    for pay_date, p_start, p_end in gen:
        payment = RentalPayment(
            property_id=property_id,
            tenant_contact_id=data.tenant_contact_id,
            amount=data.amount,
            payment_date=pay_date,
            payment_method=data.payment_method,
            period_start=p_start,
            period_end=p_end,
            category=data.category,
            is_recurring=True,
            recurrence_rule=data.recurrence_rule,
            recurring_day=pay_day,
            is_marked_done=False,
            notes=data.notes,
        )
        db.add(payment)
        created.append(payment)

    await db.commit()
    for p in created:
        await db.refresh(p)
    return created


@router.put(
    "/rental-payments/{payment_id}",
    response_model=RentalPaymentResponse,
)
async def update_rental_payment(
    payment_id: UUID,
    data: RentalPaymentUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    payment = await db.get(RentalPayment, payment_id)
    if not payment:
        raise HTTPException(
            status_code=404, detail="Rental payment not found"
        )
    await require_property_access(payment.property_id, user, db)
    # Block editing future recurring entries
    if payment.is_recurring and payment.payment_date > date.today():
        raise HTTPException(
            status_code=400,
            detail="Cannot edit future recurring payments",
        )
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(payment, key, value)
    await db.commit()
    await db.refresh(payment)
    return payment


@router.patch(
    "/rental-payments/{payment_id}/mark-done",
    response_model=RentalPaymentResponse,
)
async def mark_payment_done(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    payment = await db.get(RentalPayment, payment_id)
    if not payment:
        raise HTTPException(
            status_code=404, detail="Rental payment not found"
        )
    await require_property_access(payment.property_id, user, db)
    payment.is_marked_done = True
    await db.commit()
    await db.refresh(payment)
    return payment


@router.patch(
    "/rental-payments/{payment_id}/unmark-done",
    response_model=RentalPaymentResponse,
)
async def unmark_payment_done(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    payment = await db.get(RentalPayment, payment_id)
    if not payment:
        raise HTTPException(
            status_code=404, detail="Rental payment not found"
        )
    await require_property_access(payment.property_id, user, db)
    payment.is_marked_done = False
    await db.commit()
    await db.refresh(payment)
    return payment


@router.delete(
    "/rental-payments/{payment_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_rental_payment(
    payment_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    payment = await db.get(RentalPayment, payment_id)
    if not payment:
        raise HTTPException(
            status_code=404, detail="Rental payment not found"
        )
    await require_property_access(payment.property_id, user, db)
    await db.delete(payment)
    await db.commit()
