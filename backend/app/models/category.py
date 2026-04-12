import uuid
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.property import Property


class Category(Base):
    __tablename__ = "categories"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    property_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("properties.id"), nullable=True
    )
    name: Mapped[str] = mapped_column(String(100))
    category_type: Mapped[str] = mapped_column(String(20))  # "expense" or "payment"
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    requires_marking: Mapped[bool] = mapped_column(Boolean, default=False)
    default_recurrence_rule: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    # Relationships
    property: Mapped[Optional["Property"]] = relationship()
