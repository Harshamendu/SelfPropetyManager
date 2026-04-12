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
from app.models.contact import Contact
from app.models.property import Property
from app.schemas.contact import ContactCreate, ContactResponse, ContactUpdate

router = APIRouter(tags=["Contacts"], dependencies=[Depends(require_user)])


@router.get("/contacts", response_model=list[ContactResponse])
async def list_contacts(
    property_id: Optional[UUID] = None,
    contact_type: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    stmt = select(Contact)
    accessible = await get_accessible_property_ids(user, db)
    if accessible is not None:
        if not accessible:
            return []
        stmt = stmt.where(Contact.property_id.in_(accessible))
    if property_id is not None:
        if accessible is not None and property_id not in accessible:
            raise HTTPException(status_code=403, detail="No access to this property")
        stmt = stmt.where(Contact.property_id == property_id)
    if contact_type is not None:
        stmt = stmt.where(Contact.contact_type == contact_type)
    stmt = stmt.order_by(Contact.last_name, Contact.first_name)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get(
    "/properties/{property_id}/contacts",
    response_model=list[ContactResponse],
)
async def list_property_contacts(
    property_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    await require_property_access(property_id, user, db)
    prop = await db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    stmt = (
        select(Contact)
        .where(Contact.property_id == property_id)
        .order_by(Contact.last_name, Contact.first_name)
    )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/contacts",
    response_model=ContactResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_contact(
    data: ContactCreate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    if data.property_id:
        await require_property_access(data.property_id, user, db)
    contact = Contact(**data.model_dump())
    db.add(contact)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.put("/contacts/{contact_id}", response_model=ContactResponse)
async def update_contact(
    contact_id: UUID,
    data: ContactUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contact.property_id:
        await require_property_access(contact.property_id, user, db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(contact, key, value)
    await db.commit()
    await db.refresh(contact)
    return contact


@router.delete(
    "/contacts/{contact_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_contact(
    contact_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    contact = await db.get(Contact, contact_id)
    if not contact:
        raise HTTPException(status_code=404, detail="Contact not found")
    if contact.property_id:
        await require_property_access(contact.property_id, user, db)
    await db.delete(contact)
    await db.commit()
