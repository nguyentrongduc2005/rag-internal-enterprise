"""add users and permissions

Revision ID: a1b2c3d4e5f6
Revises: e4cc8f0ccaff
Create Date: 2026-05-20 16:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "a1b2c3d4e5f6"
down_revision: Union[str, Sequence[str], None] = "e4cc8f0ccaff"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.String(length=36), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
        sa.Column("role", sa.String(length=50), nullable=False, server_default="user"),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)

    op.add_column("documents", sa.Column("owner_id", sa.String(length=36), nullable=True))
    op.create_index("ix_documents_owner_id", "documents", ["owner_id"])
    op.create_foreign_key(
        "fk_documents_owner_id_users",
        "documents",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.add_column("conversations", sa.Column("owner_id", sa.String(length=36), nullable=True))
    op.create_index("ix_conversations_owner_id", "conversations", ["owner_id"])
    op.create_foreign_key(
        "fk_conversations_owner_id_users",
        "conversations",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )


def downgrade() -> None:
    op.drop_constraint("fk_conversations_owner_id_users", "conversations", type_="foreignkey")
    op.drop_index("ix_conversations_owner_id", table_name="conversations")
    op.drop_column("conversations", "owner_id")

    op.drop_constraint("fk_documents_owner_id_users", "documents", type_="foreignkey")
    op.drop_index("ix_documents_owner_id", table_name="documents")
    op.drop_column("documents", "owner_id")

    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
