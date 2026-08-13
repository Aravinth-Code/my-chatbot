"""add source_type and source_url to documents

Revision ID: 3de11d4ffefb
Revises: ed63ea288680
Create Date: 2026-08-09 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '3de11d4ffefb'
down_revision: Union[str, Sequence[str], None] = 'ed63ea288680'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    document_source_type = sa.Enum('FILE', 'URL', name='document_source_type')
    document_source_type.create(op.get_bind())

    op.add_column(
        'documents',
        sa.Column(
            'source_type',
            document_source_type,
            nullable=False,
            server_default='FILE',
        ),
    )
    op.add_column('documents', sa.Column('source_url', sa.String(length=2048), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('documents', 'source_url')
    op.drop_column('documents', 'source_type')

    sa.Enum(name='document_source_type').drop(op.get_bind())
