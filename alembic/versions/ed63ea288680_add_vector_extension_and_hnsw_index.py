"""add vector extension and hnsw index on document_chunks.embedding

Revision ID: ed63ea288680
Revises: 6e6fa1c1a04f
Create Date: 2026-08-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = 'ed63ea288680'
down_revision: Union[str, Sequence[str], None] = '6e6fa1c1a04f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")
    op.execute(
        "CREATE INDEX ix_document_chunks_embedding_hnsw "
        "ON document_chunks USING hnsw (embedding vector_cosine_ops)"
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.execute("DROP INDEX IF EXISTS ix_document_chunks_embedding_hnsw")
