"""rbac: roles, user_properties, contact user link

Revision ID: g7b3c9e6d5f2
Revises: f6a2b8d5c4e1
Create Date: 2026-04-10 12:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "g7b3c9e6d5f2"
down_revision: Union[str, None] = "f6a2b8d5c4e1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


ROLE_ENUM_NAME = "user_role"
ROLE_VALUES = ("admin", "property_manager", "tenant", "viewer")


def upgrade() -> None:
    # 1. Create user_role enum type and add role column
    role_enum = sa.Enum(*ROLE_VALUES, name=ROLE_ENUM_NAME)
    role_enum.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            role_enum,
            nullable=False,
            server_default="viewer",
        ),
    )

    # Backfill role from is_admin
    op.execute("UPDATE users SET role = 'admin' WHERE is_admin = true")

    # Promote seeded users by email
    op.execute(
        "UPDATE users SET role = 'property_manager' WHERE email = 'manager@propertymanager.com'"
    )
    op.execute(
        "UPDATE users SET role = 'tenant' WHERE email = 'tenant@propertymanager.com'"
    )
    op.execute(
        "UPDATE users SET role = 'viewer' "
        "WHERE email IN ('viewer@propertymanager.com', 'maintenance@propertymanager.com')"
    )

    # 2. Create user_properties join table
    op.create_table(
        "user_properties",
        sa.Column("id", sa.Uuid(), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "property_id",
            sa.Uuid(),
            sa.ForeignKey("properties.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "assigned_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.UniqueConstraint("user_id", "property_id", name="uq_user_properties_user_property"),
    )
    op.create_index("ix_user_properties_user_id", "user_properties", ["user_id"])
    op.create_index("ix_user_properties_property_id", "user_properties", ["property_id"])

    # Backfill: assign every existing property to every admin user
    op.execute(
        """
        INSERT INTO user_properties (id, user_id, property_id, assigned_at)
        SELECT gen_random_uuid(), u.id, p.id, NOW()
        FROM users u
        CROSS JOIN properties p
        WHERE u.role = 'admin'
        """
    )

    # 3. Add user_id FK on contacts (nullable) for tenant login linkage
    op.add_column(
        "contacts",
        sa.Column(
            "user_id",
            sa.Uuid(),
            sa.ForeignKey("users.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_contacts_user_id", "contacts", ["user_id"])


def downgrade() -> None:
    op.drop_index("ix_contacts_user_id", table_name="contacts")
    op.drop_column("contacts", "user_id")

    op.drop_index("ix_user_properties_property_id", table_name="user_properties")
    op.drop_index("ix_user_properties_user_id", table_name="user_properties")
    op.drop_table("user_properties")

    op.drop_column("users", "role")
    sa.Enum(name=ROLE_ENUM_NAME).drop(op.get_bind(), checkfirst=True)
