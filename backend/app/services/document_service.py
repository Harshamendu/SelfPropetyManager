import os
import uuid

import aiofiles
from fastapi import UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document import Document
from app.schemas.document import DocumentUpdate


async def get_by_property(db: AsyncSession, property_id: uuid.UUID) -> list[Document]:
    stmt = (
        select(Document)
        .where(Document.property_id == property_id)
        .order_by(Document.uploaded_at.desc())
    )
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def upload(
    db: AsyncSession,
    property_id: uuid.UUID,
    file: UploadFile,
    category: str,
    description: str | None,
    storage_path: str,
) -> Document:
    """Save file to disk and create DB record."""
    # Build directory: {storage_path}/{property_id}/{category}/
    dir_path = os.path.join(storage_path, str(property_id), category)
    os.makedirs(dir_path, exist_ok=True)

    # Generate unique filename
    file_uuid = uuid.uuid4()
    original_filename = file.filename or "unnamed"
    stored_filename = f"{file_uuid}_{original_filename}"
    full_path = os.path.join(dir_path, stored_filename)

    # Write file to disk
    content = await file.read()
    async with aiofiles.open(full_path, "wb") as f:
        await f.write(content)

    # Relative path for DB storage
    stored_path = os.path.join(str(property_id), category, stored_filename)

    doc = Document(
        property_id=property_id,
        file_name=original_filename,
        stored_path=stored_path,
        category=category,
        description=description,
        file_size_bytes=len(content),
        mime_type=file.content_type or "application/octet-stream",
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


async def download(storage_path: str, stored_path: str) -> str:
    """Return full file path for streaming."""
    full_path = os.path.join(storage_path, stored_path)
    if not os.path.exists(full_path):
        raise FileNotFoundError(f"File not found: {full_path}")
    return full_path


async def delete(db: AsyncSession, id: uuid.UUID, storage_path: str) -> None:
    """Delete file from disk and DB."""
    stmt = select(Document).where(Document.id == id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if doc is None:
        raise ValueError(f"Document {id} not found")

    # Remove file from disk
    full_path = os.path.join(storage_path, doc.stored_path)
    if os.path.exists(full_path):
        os.remove(full_path)

    await db.delete(doc)
    await db.commit()


async def update(db: AsyncSession, id: uuid.UUID, schema: DocumentUpdate) -> Document:
    stmt = select(Document).where(Document.id == id)
    result = await db.execute(stmt)
    doc = result.scalar_one_or_none()
    if doc is None:
        raise ValueError(f"Document {id} not found")
    update_data = schema.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(doc, key, value)
    await db.commit()
    await db.refresh(doc)
    return doc
