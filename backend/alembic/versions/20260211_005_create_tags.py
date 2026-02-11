"""Create tags table

Revision ID: 20260211_005
Revises: 20260211_004
Create Date: 2026-02-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20260211_005'
down_revision: Union[str, None] = '20260211_004'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'tag',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(50), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('color', sa.String(7), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'name', name='uq_user_tag_name')
    )
    
    # Create index
    op.create_index('idx_tags_user', 'tag', ['user_id'])


def downgrade() -> None:
    op.drop_index('idx_tags_user', 'tag')
    op.drop_table('tag')
