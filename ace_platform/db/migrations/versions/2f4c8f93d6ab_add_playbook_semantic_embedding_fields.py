"""Add semantic embedding fields to playbooks.

Revision ID: 2f4c8f93d6ab
Revises: f3a8b2c1d7e9
Create Date: 2026-02-09
"""

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "2f4c8f93d6ab"
down_revision: str | Sequence[str] | None = "f3a8b2c1d7e9"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add semantic embedding fields for playbook matching."""
    op.add_column("playbooks", sa.Column("semantic_embedding", postgresql.JSONB(), nullable=True))
    op.add_column(
        "playbooks",
        sa.Column("semantic_embedding_model", sa.String(length=100), nullable=True),
    )
    op.add_column(
        "playbooks",
        sa.Column("semantic_embedding_updated_at", sa.DateTime(timezone=True), nullable=True),
    )


def downgrade() -> None:
    """Remove semantic embedding fields from playbooks."""
    op.drop_column("playbooks", "semantic_embedding_updated_at")
    op.drop_column("playbooks", "semantic_embedding_model")
    op.drop_column("playbooks", "semantic_embedding")
