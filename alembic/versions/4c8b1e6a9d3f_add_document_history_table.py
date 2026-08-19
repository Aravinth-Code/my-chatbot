"""add document_history table

Revision ID: 4c8b1e6a9d3f
Revises: 7f3a9c2d1b4e
Create Date: 2026-08-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = '4c8b1e6a9d3f'
down_revision: Union[str, Sequence[str], None] = '7f3a9c2d1b4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        'document_history',
        sa.Column('document_id', sa.UUID(), nullable=False),
        sa.Column(
            'status',
            postgresql.ENUM(
                'UPLOADED', 'EXTRACTING', 'EXTRACTED', 'CHUNKING', 'EMBEDDING',
                'PROCESSING', 'PROCESSED', 'FAILED',
                name='document_status', create_type=False,
            ),
            nullable=False,
        ),
        sa.Column('error_message', sa.String(length=1000), nullable=True),
        sa.Column('id', sa.UUID(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.ForeignKeyConstraint(['document_id'], ['documents.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index(op.f('ix_document_history_document_id'), 'document_history', ['document_id'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f('ix_document_history_document_id'), table_name='document_history')
    op.drop_table('document_history')
