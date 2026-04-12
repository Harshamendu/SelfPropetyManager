import uuid
from datetime import date, datetime
from decimal import Decimal
from typing import TYPE_CHECKING, Optional

from sqlalchemy import Boolean, Date, DateTime, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.contact import Contact
    from app.models.document import Document
    from app.models.expense import Expense
    from app.models.reminder import Reminder
    from app.models.rental_payment import RentalPayment
    from app.models.user_property import UserProperty


class Property(Base):
    __tablename__ = "properties"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200))
    address_line1: Mapped[str] = mapped_column(String(300))
    address_line2: Mapped[Optional[str]] = mapped_column(
        String(300), nullable=True
    )
    city: Mapped[str] = mapped_column(String(100))
    state: Mapped[str] = mapped_column(String(2), default="GA")
    zip_code: Mapped[str] = mapped_column(String(10))
    property_type: Mapped[str] = mapped_column(String(50))
    purchase_date: Mapped[Optional[date]] = mapped_column(
        Date, nullable=True
    )
    purchase_price: Mapped[Optional[Decimal]] = mapped_column(
        Numeric(12, 2), nullable=True
    )
    notes: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Landlord info per property
    landlord_name: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    landlord_phone: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)
    landlord_email: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    landlord_address: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )

    # Relationships
    documents: Mapped[list["Document"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    expenses: Mapped[list["Expense"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    rental_payments: Mapped[list["RentalPayment"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
    contacts: Mapped[list["Contact"]] = relationship(
        back_populates="property"
    )
    reminders: Mapped[list["Reminder"]] = relationship(
        back_populates="property"
    )
    user_assignments: Mapped[list["UserProperty"]] = relationship(
        back_populates="property", cascade="all, delete-orphan"
    )
