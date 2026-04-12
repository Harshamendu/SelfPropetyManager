import uuid
from datetime import datetime
from typing import Any, Optional

from sqlalchemy import DateTime, JSON, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class DocumentTemplate(Base):
    __tablename__ = "document_templates"

    id: Mapped[uuid.UUID] = mapped_column(
        primary_key=True, default=uuid.uuid4
    )
    name: Mapped[str] = mapped_column(String(200))
    state: Mapped[Optional[str]] = mapped_column(String(2), nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    template_body: Mapped[str] = mapped_column(Text)
    variables: Mapped[Any] = mapped_column(JSON)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    updated_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime(timezone=True), onupdate=func.now()
    )
