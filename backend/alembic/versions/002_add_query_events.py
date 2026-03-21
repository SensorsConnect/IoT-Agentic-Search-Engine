"""Add query_events table and make conversations.user_id nullable for anonymous support

Revision ID: 002_add_query_events
Revises: 001_initial_phase1
Create Date: 2026-03-21
"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "002_add_query_events"
down_revision: Union[str, None] = "001_initial_phase1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Make conversations.user_id nullable so anonymous users' messages are stored
    op.alter_column("conversations", "user_id", existing_type=UUID(as_uuid=True), nullable=True)
    op.execute("ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversations_user_id_fkey")
    op.create_foreign_key(
        "conversations_user_id_fkey", "conversations", "users",
        ["user_id"], ["id"], ondelete="SET NULL"
    )

    op.create_table(
        "query_events",
        sa.Column("id", UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True, index=True),
        sa.Column("is_authenticated", sa.Boolean, nullable=False, server_default=sa.text("false"), index=True),
        sa.Column("query_text", sa.String(200), nullable=False),
        sa.Column("thread_id", sa.String(255), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False, index=True),
    )


def downgrade() -> None:
    op.drop_table("query_events")
    op.execute("ALTER TABLE conversations DROP CONSTRAINT IF EXISTS conversations_user_id_fkey")
    op.create_foreign_key(
        "conversations_user_id_fkey", "conversations", "users",
        ["user_id"], ["id"], ondelete="CASCADE"
    )
    op.alter_column("conversations", "user_id", existing_type=UUID(as_uuid=True), nullable=False)
