import uuid
from io import BytesIO

from docx import Document as DocxDocument
from jinja2 import Template
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.document_template import DocumentTemplate
from app.schemas.document_template import DocumentTemplateCreate, DocumentTemplateUpdate


async def get_all_templates(db: AsyncSession) -> list[DocumentTemplate]:
    stmt = select(DocumentTemplate).order_by(DocumentTemplate.name)
    result = await db.execute(stmt)
    return list(result.scalars().all())


async def get_template(db: AsyncSession, id: uuid.UUID) -> DocumentTemplate | None:
    stmt = select(DocumentTemplate).where(DocumentTemplate.id == id)
    result = await db.execute(stmt)
    return result.scalar_one_or_none()


async def create_template(
    db: AsyncSession, schema: DocumentTemplateCreate
) -> DocumentTemplate:
    data = schema.model_dump()
    # Convert variables from list of TemplateVariable to list of dicts for JSON column
    data["variables"] = [v.model_dump() if hasattr(v, "model_dump") else v for v in data["variables"]]
    template = DocumentTemplate(**data)
    db.add(template)
    await db.commit()
    await db.refresh(template)
    return template


async def update_template(
    db: AsyncSession, id: uuid.UUID, schema: DocumentTemplateUpdate
) -> DocumentTemplate:
    stmt = select(DocumentTemplate).where(DocumentTemplate.id == id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    if template is None:
        raise ValueError(f"DocumentTemplate {id} not found")
    update_data = schema.model_dump(exclude_unset=True)
    if "variables" in update_data and update_data["variables"] is not None:
        update_data["variables"] = [
            v.model_dump() if hasattr(v, "model_dump") else v
            for v in update_data["variables"]
        ]
    for key, value in update_data.items():
        setattr(template, key, value)
    await db.commit()
    await db.refresh(template)
    return template


async def delete_template(db: AsyncSession, id: uuid.UUID) -> None:
    stmt = select(DocumentTemplate).where(DocumentTemplate.id == id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    if template is None:
        raise ValueError(f"DocumentTemplate {id} not found")
    await db.delete(template)
    await db.commit()


async def generate_document(
    db: AsyncSession, template_id: uuid.UUID, variables: dict[str, str]
) -> BytesIO:
    """Render a DocumentTemplate with Jinja2 and produce a DOCX file."""
    stmt = select(DocumentTemplate).where(DocumentTemplate.id == template_id)
    result = await db.execute(stmt)
    template = result.scalar_one_or_none()
    if template is None:
        raise ValueError(f"DocumentTemplate {template_id} not found")

    # Render the template body using Jinja2
    jinja_template = Template(template.template_body)
    rendered_text = jinja_template.render(**variables)

    # Create DOCX document
    doc = DocxDocument()
    # Split rendered text by newlines into paragraphs
    for paragraph_text in rendered_text.split("\n"):
        doc.add_paragraph(paragraph_text)

    output = BytesIO()
    doc.save(output)
    output.seek(0)
    return output
