import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.property import Property


class Expense(Base):
    __tablename__ = "expenses"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    property_id: Mapped[uuid.UUID] = mapped_column(
        ForeignKey("properties.id")
    )
    category: Mapped[str] = mapped_column(String(50))
    description: Mapped[str] = mapped_column(String(500))
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2))
    date: Mapped[date] = mapped_column(Date)
    is_recurring: Mapped[bool] = mapped_column(Boolean, default=False)
    recurrence_rule: Mapped[Optional[str]] = mapped_column(
        String(50), nullable=True
    )
    recurring_day: Mapped[Optional[int]] = mapped_column(
        Integer, nullable=True
    )
    is_marked_done: Mapped[bool] = mapped_column(Boolean, default=False)
    vendor: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    receipt_document_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        ForeignKey("documents.id"), nullable=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationships
    property: Mapped["Property"] = relationship(back_populates="expenses")
