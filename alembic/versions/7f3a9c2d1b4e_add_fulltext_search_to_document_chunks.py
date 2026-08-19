"""add fulltext search to document_chunks

Revision ID: 7f3a9c2d1b4e
Revises: 3de11d4ffefb
Create Date: 2026-08-13 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = '7f3a9c2d1b4e'
down_revision: Union[str, Sequence[str], None] = '3de11d4ffefb'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute(
        "ALTER TABLE document_chunks "
        "ADD COLUMN search_vector tsvector "
        "GENERATED ALWAYS AS (to_tsvector('english', text)) STORED"
    )
    op.execute(
        "CREATE INDEX ix_document_chunks_search_vector_gin "
        "ON document_chunks USING gin (search_vector)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_search_vector_gin")
    op.execute("ALTER TABLE document_chunks DROP COLUMN IF EXISTS search_vector")
