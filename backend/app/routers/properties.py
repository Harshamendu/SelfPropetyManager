from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.dependencies import (
    get_accessible_property_ids,
    get_db,
    require_admin,
    require_property_access,
    require_user,
)
from app.models.property import Property
from app.schemas.property import (
    LeaseSummary,
    PropertyCreate,
    PropertyResponse,
    PropertySummary,
    PropertyUpdate,
)

router = APIRouter(tags=["Properties"])


@router.get("/properties", response_model=list[PropertyResponse])
async def list_properties(
    is_active: bool = True,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    stmt = select(Property).where(Property.is_active == is_active)
    accessible = await get_accessible_property_ids(user, db)
    if accessible is not None:
        if not accessible:
            return []
        stmt = stmt.where(Property.id.in_(accessible))
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/properties",
    response_model=PropertyResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_property(
    data: PropertyCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin),
):
    prop = Property(**data.model_dump())
    db.add(prop)
    await db.commit()
    await db.refresh(prop)
    return prop


@router.get("/properties/{property_id}", response_model=PropertyResponse)
async def get_property(
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    await require_property_access(property_id, user, db)
    prop = await db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    return prop


@router.put("/properties/{property_id}", response_model=PropertyResponse)
async def update_property(
    property_id: UUID,
    data: PropertyUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    await require_property_access(property_id, user, db)
    from app.models.user import UserRole
    if user.role in (UserRole.TENANT, UserRole.VIEWER):
        raise HTTPException(status_code=403, detail="Read-only role cannot modify resources")
    prop = await db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(prop, key, value)
    await db.commit()
    await db.refresh(prop)
    return prop


@router.delete(
    "/properties/{property_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_property(
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_admin),
):
    prop = await db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    prop.is_active = False
    await db.commit()


@router.get(
    "/properties/{property_id}/summary",
    response_model=PropertySummary,
)
async def get_property_summary(
    property_id: UUID,
    year: int,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    await require_property_access(property_id, user, db)
    from datetime import date
    from datetime import datetime, timezone

    from sqlalchemy import func, or_

    from app.models.contact import Contact
    from app.models.expense import Expense
    from app.models.reminder import Reminder
    from app.models.rental_payment import RentalPayment

    prop = await db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    today = date.today()
    year_start = date(year, 1, 1)
    year_end = date(year, 12, 31)

    # Rent collected YTD — only marked done or past date
    rent_result = await db.execute(
        select(func.coalesce(func.sum(RentalPayment.amount), 0)).where(
            RentalPayment.property_id == property_id,
            RentalPayment.payment_date >= year_start,
            RentalPayment.payment_date <= year_end,
            or_(
                RentalPayment.is_marked_done == True,  # noqa: E712
                RentalPayment.payment_date <= today,
            ),
        )
    )
    rent_collected = float(rent_result.scalar())

    # Expenses YTD — only marked done or past date
    expense_result = await db.execute(
        select(func.coalesce(func.sum(Expense.amount), 0)).where(
            Expense.property_id == property_id,
            Expense.date >= year_start,
            Expense.date <= year_end,
            or_(
                Expense.is_marked_done == True,  # noqa: E712
                Expense.date <= today,
            ),
        )
    )
    expenses_ytd = float(expense_result.scalar())

    # Upcoming reminders
    reminder_result = await db.execute(
        select(func.count()).where(
            Reminder.property_id == property_id,
            Reminder.is_completed == False,  # noqa: E712
            Reminder.due_date >= datetime.now(timezone.utc),
        )
    )
    upcoming_reminders = reminder_result.scalar()

    # Lease status — find active tenant with current lease
    lease_result = await db.execute(
        select(Contact).where(
            Contact.property_id == property_id,
            Contact.contact_type == "tenant",
            Contact.is_active == True,  # noqa: E712
            Contact.lease_start.isnot(None),
            Contact.lease_end.isnot(None),
        ).order_by(Contact.lease_end.desc())
    )
    tenant = lease_result.scalars().first()

    is_leased = False
    lease_info = None
    if tenant and tenant.lease_end and tenant.lease_end >= today:
        is_leased = True
        lease_info = LeaseSummary(
            tenant_name=f"{tenant.first_name} {tenant.last_name}",
            lease_start=tenant.lease_start,
            lease_end=tenant.lease_end,
            monthly_rent=float(tenant.monthly_rent) if tenant.monthly_rent else None,
        )

    return PropertySummary(
        id=prop.id,
        name=prop.name,
        address_line1=prop.address_line1,
        city=prop.city,
        state=prop.state,
        is_leased=is_leased,
        lease=lease_info,
        rent_collected_ytd=rent_collected,
        expenses_ytd=expenses_ytd,
        upcoming_reminders=upcoming_reminders,
    )
