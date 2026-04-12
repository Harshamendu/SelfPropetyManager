import uuid

from sqlalchemy import extract, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.rental_payment import RentalPayment
from app.schemas.rental_payment import RentalPaymentCreate, RentalPaymentUpdate


async def get_by_property(
    db: AsyncSession,
    property_id: uuid.UUID,
    year: int | None = None,
) -> list[RentalPayment]:
    stmt = select(RentalPayment).where(RentalPayment.property_id == property_id)
    if year is not None:
        stmt = stmt.where(extract("year", RentalPayment.payment_date) == year)
    stmt = stmt.order_by(RentalPayment.payment_date.desc())
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def create(
    db: AsyncSession, property_id: uuid.UUID, schema: RentalPaymentCreate
) -> RentalPayment:
    data = schema.model_dump()
    data["property_id"] = property_id
    payment = RentalPayment(**data)
    db.add(payment)
    await db.commit()
    await db.refresh(payment)
    return payment


async def update(
    db: AsyncSession, id: uuid.UUID, schema: RentalPaymentUpdate
) -> RentalPayment:
    stmt = select(RentalPayment).where(RentalPayment.id == id)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()
    if payment is None:
        raise ValueError(f"RentalPayment {id} not found")
    update_data = schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(payment, key, value)
    await db.commit()
    await db.refresh(payment)
    return payment


async def delete(db: AsyncSession, id: uuid.UUID) -> None:
    stmt = select(RentalPayment).where(RentalPayment.id == id)
    result = await db.execute(stmt)
    payment = result.scalar_one_or_none()
    if payment is None:
        raise ValueError(f"RentalPayment {id} not found")
    await db.delete(payment)
    await db.commit()
