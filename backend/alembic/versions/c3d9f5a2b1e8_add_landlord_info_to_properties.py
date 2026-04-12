"""add landlord info to properties

Revision ID: c3d9f5a2b1e8
Revises: b2c8e4f1a3d7
Create Date: 2026-03-28 10:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "c3d9f5a2b1e8"
down_revision: Union[str, None] = "b2c8e4f1a3d7"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("properties", sa.Column("landlord_name", sa.String(200), nullable=True))
    op.add_column("properties", sa.Column("landlord_phone", sa.String(20), nullable=True))
    op.add_column("properties", sa.Column("landlord_email", sa.String(200), nullable=True))
    op.add_column("properties", sa.Column("landlord_address", sa.Text(), nullable=True))


def downgrade() -> None:
    op.drop_column("properties", "landlord_address")
    op.drop_column("properties", "landlord_email")
    op.drop_column("properties", "landlord_phone")
    op.drop_column("properties", "landlord_name")
