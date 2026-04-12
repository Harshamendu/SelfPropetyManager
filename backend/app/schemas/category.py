from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class CategoryCreate(BaseModel):
    property_id: Optional[UUID] = None
    name: str
    category_type: str  # "expense" or "payment"
    is_recurring: bool = False
    requires_marking: bool = False
    default_recurrence_rule: Optional[str] = None


class CategoryUpdate(BaseModel):
    name: Optional[str] = None
    is_recurring: Optional[bool] = None
    requires_marking: Optional[bool] = None
    default_recurrence_rule: Optional[str] = None


class CategoryResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    property_id: Optional[UUID] = None
    name: str
    category_type: str
    is_recurring: bool
    requires_marking: bool
    default_recurrence_rule: Optional[str] = None
    created_at: datetime
