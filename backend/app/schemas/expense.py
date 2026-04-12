from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ExpenseCreate(BaseModel):
    property_id: Optional[UUID] = None
    category: str
    description: str
    amount: Decimal
    date: date
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    recurring_day: Optional[int] = None
    is_marked_done: bool = False
    vendor: Optional[str] = None
    receipt_document_id: Optional[UUID] = None


class ExpenseUpdate(BaseModel):
    property_id: Optional[UUID] = None
    category: Optional[str] = None
    description: Optional[str] = None
    amount: Optional[Decimal] = None
    date: Optional[date] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None
    recurring_day: Optional[int] = None
    is_marked_done: Optional[bool] = None
    vendor: Optional[str] = None
    receipt_document_id: Optional[UUID] = None


class ExpenseResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    property_id: Optional[UUID] = None
    category: str
    description: str
    amount: Decimal
    date: date
    is_recurring: bool
    recurrence_rule: Optional[str] = None
    recurring_day: Optional[int] = None
    is_marked_done: bool = False
    vendor: Optional[str] = None
    receipt_document_id: Optional[UUID] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
