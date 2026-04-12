from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ReminderCreate(BaseModel):
    property_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    due_date: datetime
    reminder_type: str
    is_recurring: bool = False
    recurrence_rule: Optional[str] = None
    notify_email: bool = False
    notify_in_app: bool = True


class ReminderUpdate(BaseModel):
    property_id: Optional[UUID] = None
    title: Optional[str] = None
    description: Optional[str] = None
    due_date: Optional[datetime] = None
    reminder_type: Optional[str] = None
    is_recurring: Optional[bool] = None
    recurrence_rule: Optional[str] = None
    notify_email: Optional[bool] = None
    notify_in_app: Optional[bool] = None


class ReminderResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    property_id: Optional[UUID] = None
    title: str
    description: Optional[str] = None
    due_date: datetime
    reminder_type: str
    is_recurring: bool
    recurrence_rule: Optional[str] = None
    notify_email: bool
    notify_in_app: bool
    is_completed: bool
    completed_at: Optional[datetime] = None
    email_sent: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
