from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class TemplateVariable(BaseModel):
    name: str
    label: str
    default_value: Optional[str] = None


class DocumentTemplateCreate(BaseModel):
    name: str
    state: Optional[str] = None
    description: Optional[str] = None
    template_body: str
    variables: list[TemplateVariable]


class DocumentTemplateUpdate(BaseModel):
    name: Optional[str] = None
    state: Optional[str] = None
    description: Optional[str] = None
    template_body: Optional[str] = None
    variables: Optional[list[TemplateVariable]] = None


class DocumentTemplateResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    state: Optional[str] = None
    description: Optional[str] = None
    template_body: str
    variables: list[TemplateVariable]
    created_at: datetime
    updated_at: Optional[datetime] = None


class GenerateDocumentRequest(BaseModel):
    variables: dict[str, str]
