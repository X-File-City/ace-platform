"""Add paused status to PlaybookStatus enum

Revision ID: bcb55d750510
Revises: c12c0d05df55
Create Date: 2026-01-09 13:35:44.747583

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "bcb55d750510"
down_revision: str | Sequence[str] | None = "c12c0d05df55"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add 'paused' value to playbookstatus enum."""
    # PostgreSQL enums require ALTER TYPE to add new values
    op.execute("ALTER TYPE playbookstatus ADD VALUE IF NOT EXISTS 'paused'")


def downgrade() -> None:
    """Remove 'paused' value from playbookstatus enum.

    Note: PostgreSQL doesn't support removing enum values directly.
    This would require recreating the enum type, which is complex.
    For simplicity, we leave this as a no-op.
    """
    pass
