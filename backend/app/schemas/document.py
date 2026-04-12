from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class DocumentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    property_id: UUID
    file_name: str
    stored_path: str
    category: str
    description: Optional[str] = None
    file_size_bytes: int
    mime_type: str
    uploaded_at: datetime


class DocumentUpdate(BaseModel):
    category: Optional[str] = None
    description: Optional[str] = None
