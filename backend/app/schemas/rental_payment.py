from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RentalPaymentCreate(BaseModel):
    property_id: Optional[UUID] = None
    tenant_contact_id: Optional[UUID] = None
    amount: Decimal
    payment_date: date
    payment_method: str
    period_start: date
    period_end: date
    category: Optional[str] = None
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    recurring_day: Optional[int] = None
    is_marked_done: bool = False
    notes: Optional[str] = None


class RentalPaymentUpdate(BaseModel):
    property_id: Optional[UUID] = None
    tenant_contact_id: Optional[UUID] = None
    amount: Optional[Decimal] = None
    payment_date: Optional[date] = None
    payment_method: Optional[str] = None
    period_start: Optional[date] = None
    period_end: Optional[date] = None
    category: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None
    recurring_day: Optional[int] = None
    is_marked_done: Optional[bool] = None
    notes: Optional[str] = None


class RentalPaymentResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    property_id: Optional[UUID] = None
    tenant_contact_id: Optional[UUID] = None
    amount: Decimal
    payment_date: date
    payment_method: str
    period_start: date
    period_end: date
    category: Optional[str] = None
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    recurring_day: Optional[int] = None
    is_marked_done: bool = False
    notes: Optional[str] = None
    created_at: datetime
