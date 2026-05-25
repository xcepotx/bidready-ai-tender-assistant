"""add auth users table

Revision ID: 20260525_0002
Revises: 20260525_0001
Create Date: 2026-05-25
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "20260525_0002"
down_revision = "20260525_0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "app_users",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column("role", sa.String(length=80), nullable=False, server_default="viewer"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.Column("last_login_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_app_users_id", "app_users", ["id"])
    op.create_index("ix_app_users_email", "app_users", ["email"], unique=True)
    op.create_index("ix_app_users_role", "app_users", ["role"])
    op.create_index("ix_app_users_is_active", "app_users", ["is_active"])


def downgrade() -> None:
    op.drop_index("ix_app_users_is_active", table_name="app_users")
    op.drop_index("ix_app_users_role", table_name="app_users")
    op.drop_index("ix_app_users_email", table_name="app_users")
    op.drop_index("ix_app_users_id", table_name="app_users")
    op.drop_table("app_users")
