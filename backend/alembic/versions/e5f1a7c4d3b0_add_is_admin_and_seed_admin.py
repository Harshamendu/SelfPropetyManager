"""add is_admin and seed admin user

Revision ID: e5f1a7c4d3b0
Revises: d4e0f6b3c2a9
Create Date: 2026-03-28 14:00:00.000000

"""
from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from passlib.context import CryptContext

revision: str = "e5f1a7c4d3b0"
down_revision: Union[str, None] = "d4e0f6b3c2a9"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
    )

    # Seed admin account: admin@propertymanager.com / Admin@123
    users_table = sa.table(
        "users",
        sa.column("id", sa.Uuid()),
        sa.column("email", sa.String),
        sa.column("hashed_password", sa.String),
        sa.column("full_name", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("is_admin", sa.Boolean),
    )
    op.execute(
        users_table.insert().values(
            id=uuid4(),
            email="admin@propertymanager.com",
            hashed_password=pwd_context.hash("Admin@123"),
            full_name="Admin",
            is_active=True,
            is_admin=True,
        )
    )


def downgrade() -> None:
    op.execute(
        sa.text("DELETE FROM users WHERE email = 'admin@propertymanager.com'")
    )
    op.drop_column("users", "is_admin")
