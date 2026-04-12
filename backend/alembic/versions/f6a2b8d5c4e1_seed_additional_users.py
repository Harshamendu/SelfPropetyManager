"""seed additional users

Revision ID: f6a2b8d5c4e1
Revises: e5f1a7c4d3b0
Create Date: 2026-04-10 10:00:00.000000

"""
from typing import Sequence, Union
from uuid import uuid4

import sqlalchemy as sa
from alembic import op
from passlib.context import CryptContext

revision: str = "f6a2b8d5c4e1"
down_revision: Union[str, None] = "e5f1a7c4d3b0"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

USERS = [
    {
        "email": "manager@propertymanager.com",
        "password": "Manager@123",
        "full_name": "Property Manager",
    },
    {
        "email": "tenant@propertymanager.com",
        "password": "Tenant@123",
        "full_name": "Tenant User",
    },
    {
        "email": "maintenance@propertymanager.com",
        "password": "Maint@123",
        "full_name": "Maintenance Staff",
    },
    {
        "email": "viewer@propertymanager.com",
        "password": "Viewer@123",
        "full_name": "Read Only Viewer",
    },
]


def upgrade() -> None:
    users_table = sa.table(
        "users",
        sa.column("id", sa.Uuid()),
        sa.column("email", sa.String),
        sa.column("hashed_password", sa.String),
        sa.column("full_name", sa.String),
        sa.column("is_active", sa.Boolean),
        sa.column("is_admin", sa.Boolean),
    )
    for u in USERS:
        op.execute(
            users_table.insert().values(
                id=uuid4(),
                email=u["email"],
                hashed_password=pwd_context.hash(u["password"]),
                full_name=u["full_name"],
                is_active=True,
                is_admin=False,
            )
        )


def downgrade() -> None:
    emails = [u["email"] for u in USERS]
    for email in emails:
        op.execute(sa.text(f"DELETE FROM users WHERE email = '{email}'"))
