import mimetypes
import os
import shutil
from typing import Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, Form, HTTPException, UploadFile, status
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import settings
from app.dependencies import (
    get_db,
    require_property_access,
    require_user,
    require_writer,
)
from app.models.document import Document
from app.models.property import Property
from app.schemas.document import DocumentResponse, DocumentUpdate

router = APIRouter(tags=["Documents"], dependencies=[Depends(require_user)])


@router.get(
    "/properties/{property_id}/documents",
    response_model=list[DocumentResponse],
)
async def list_documents(
    property_id: UUID,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    await require_property_access(property_id, user, db)
    prop = await db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")
    stmt = select(Document).where(Document.property_id == property_id)
    if category:
        stmt = stmt.where(Document.category == category)
    stmt = stmt.order_by(Document.uploaded_at.desc())
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post(
    "/properties/{property_id}/documents",
    response_model=DocumentResponse,
    status_code=status.HTTP_201_CREATED,
)
async def upload_document(
    property_id: UUID,
    file: UploadFile,
    category: str = Form(...),
    description: str = Form(None),
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    await require_property_access(property_id, user, db)
    prop = await db.get(Property, property_id)
    if not prop:
        raise HTTPException(status_code=404, detail="Property not found")

    # Create storage directory
    property_dir = os.path.join(
        settings.document_storage_path, str(property_id)
    )
    os.makedirs(property_dir, exist_ok=True)

    # Generate unique file name
    ext = os.path.splitext(file.filename or "")[1]
    stored_filename = f"{uuid4()}{ext}"
    stored_path = os.path.join(property_dir, stored_filename)

    # Save file to disk
    with open(stored_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    file_size = os.path.getsize(stored_path)
    mime_type = (
        file.content_type
        or mimetypes.guess_type(file.filename or "")[0]
        or "application/octet-stream"
    )

    doc = Document(
        property_id=property_id,
        file_name=file.filename or stored_filename,
        stored_path=stored_path,
        category=category,
        description=description,
        file_size_bytes=file_size,
        mime_type=mime_type,
    )
    db.add(doc)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.get("/documents/{document_id}/download")
async def download_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_user),
):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await require_property_access(doc.property_id, user, db)

    if not os.path.exists(doc.stored_path):
        raise HTTPException(status_code=404, detail="File not found on disk")

    def iterfile():
        with open(doc.stored_path, "rb") as f:
            while chunk := f.read(1024 * 64):
                yield chunk

    return StreamingResponse(
        iterfile(),
        media_type=doc.mime_type,
        headers={
            "Content-Disposition": f'attachment; filename="{doc.file_name}"'
        },
    )


@router.put("/documents/{document_id}", response_model=DocumentResponse)
async def update_document(
    document_id: UUID,
    data: DocumentUpdate,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await require_property_access(doc.property_id, user, db)
    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(doc, key, value)
    await db.commit()
    await db.refresh(doc)
    return doc


@router.delete(
    "/documents/{document_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_document(
    document_id: UUID,
    db: AsyncSession = Depends(get_db),
    user=Depends(require_writer),
):
    doc = await db.get(Document, document_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    await require_property_access(doc.property_id, user, db)

    # Remove file from disk
    if os.path.exists(doc.stored_path):
        os.remove(doc.stored_path)

    await db.delete(doc)
    await db.commit()
