import uuid

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.contact import Contact
from app.schemas.contact import ContactCreate, ContactUpdate


async def get_all(
    db: AsyncSession,
    property_id: uuid.UUID | None = None,
    contact_type: str | None = None,
) -> list[Contact]:
    stmt = select(Contact)
    if property_id is not None:
        stmt = stmt.where(Contact.property_id == property_id)
    if contact_type is not None:
        stmt = stmt.where(Contact.contact_type == contact_type)
    stmt = stmt.order_by(Contact.last_name, Contact.first_name)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_by_id(db: AsyncSession, id: uuid.UUID) -> Contact | None:
    stmt = select(Contact).where(Contact.id == id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create(db: AsyncSession, schema: ContactCreate) -> Contact:
    contact = Contact(**schema.model_dump())
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


async def update(db: AsyncSession, id: uuid.UUID, schema: ContactUpdate) -> Contact:
    stmt = select(Contact).where(Contact.id == id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact is None:
        raise ValueError(f"Contact {id} not found")
    update_data = schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(contact, key, value)
    await db.commit()
    await db.refresh(contact)
    return contact


async def delete(db: AsyncSession, id: uuid.UUID) -> None:
    stmt = select(Contact).where(Contact.id == id)
    result = await db.execute(stmt)
    contact = result.scalar_one_or_none()
    if contact is None:
        raise ValueError(f"Contact {id} not found")
    await db.delete(contact)
    await db.commit()
