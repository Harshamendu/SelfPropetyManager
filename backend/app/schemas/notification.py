from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class NotificationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    reminder_id: Optional[UUID] = None
    title: str
    message: str
    is_read: bool
    created_at: datetime


class UnreadCountResponse(BaseModel):
    count: int
