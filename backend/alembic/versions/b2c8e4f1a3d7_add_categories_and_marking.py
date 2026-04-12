"""add categories table and marking fields

Revision ID: b2c8e4f1a3d7
Revises: 39a4d3ddad9a
Create Date: 2026-03-27 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b2c8e4f1a3d7"
down_revision: Union[str, None] = "39a4d3ddad9a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Create categories table
    op.create_table(
        "categories",
        sa.Column("id", sa.Uuid(), nullable=False),
        sa.Column("property_id", sa.Uuid(), nullable=True),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("category_type", sa.String(length=20), nullable=False),
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("requires_marking", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("default_recurrence_rule", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["property_id"], ["properties.id"]),
        sa.PrimaryKeyConstraint("id"),
    )

    # Add is_marked_done to expenses
    op.add_column(
        "expenses",
        sa.Column("is_marked_done", sa.Boolean(), nullable=False, server_default="false"),
    )

    # Add new columns to rental_payments
    op.add_column(
        "rental_payments",
        sa.Column("category", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "rental_payments",
        sa.Column("is_recurring", sa.Boolean(), nullable=False, server_default="false"),
    )
    op.add_column(
        "rental_payments",
        sa.Column("recurrence_rule", sa.String(length=50), nullable=True),
    )
    op.add_column(
        "rental_payments",
        sa.Column("recurring_day", sa.Integer(), nullable=True),
    )
    op.add_column(
        "rental_payments",
        sa.Column("is_marked_done", sa.Boolean(), nullable=False, server_default="false"),
    )


def downgrade() -> None:
    op.drop_column("rental_payments", "is_marked_done")
    op.drop_column("rental_payments", "recurring_day")
    op.drop_column("rental_payments", "recurrence_rule")
    op.drop_column("rental_payments", "is_recurring")
    op.drop_column("rental_payments", "category")
    op.drop_column("expenses", "is_marked_done")
    op.drop_table("categories")
