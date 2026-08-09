"""add embedding_model to document chunks

Revision ID: 6e6fa1c1a04f
Revises: cbc9d0d5aa5a
Create Date: 2026-08-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6e6fa1c1a04f'
down_revision: Union[str, Sequence[str], None] = 'cbc9d0d5aa5a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('document_chunks', sa.Column('embedding_model', sa.String(length=100), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('document_chunks', 'embedding_model')
