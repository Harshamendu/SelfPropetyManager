from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class PropertyCreate(BaseModel):
    name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str = "GA"
    zip_code: str
    property_type: str
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    notes: Optional[str] = None
    landlord_name: Optional[str] = None
    landlord_phone: Optional[str] = None
    landlord_email: Optional[str] = None
    landlord_address: Optional[str] = None


class PropertyUpdate(BaseModel):
    name: Optional[str] = None
    address_line1: Optional[str] = None
    address_line2: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    zip_code: Optional[str] = None
    property_type: Optional[str] = None
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    notes: Optional[str] = None
    landlord_name: Optional[str] = None
    landlord_phone: Optional[str] = None
    landlord_email: Optional[str] = None
    landlord_address: Optional[str] = None


class PropertyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    address_line1: str
    address_line2: Optional[str] = None
    city: str
    state: str
    zip_code: str
    property_type: str
    purchase_date: Optional[date] = None
    purchase_price: Optional[Decimal] = None
    notes: Optional[str] = None
    landlord_name: Optional[str] = None
    landlord_phone: Optional[str] = None
    landlord_email: Optional[str] = None
    landlord_address: Optional[str] = None
    is_active: bool
    created_at: datetime
    updated_at: Optional[datetime] = None


class LeaseSummary(BaseModel):
    tenant_name: str
    lease_start: Optional[date] = None
    lease_end: Optional[date] = None
    monthly_rent: Optional[float] = None


class PropertySummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: str
    address_line1: str
    city: str
    state: str
    is_leased: bool = False
    lease: Optional[LeaseSummary] = None
    rent_collected_ytd: float
    expenses_ytd: float
    upcoming_reminders: int
