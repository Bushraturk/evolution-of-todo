"""Create task_tags junction table

Revision ID: 20260211_006
Revises: 20260211_005
Create Date: 2026-02-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20260211_006'
down_revision: Union[str, None] = '20260211_005'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'task_tag',
        sa.Column('task_id', sa.Uuid(), nullable=False),
        sa.Column('tag_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('task_id', 'tag_id'),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['tag_id'], ['tag.id'], ondelete='CASCADE')
    )
    
    # Create indexes
    op.create_index('idx_task_tags_task', 'task_tag', ['task_id'])
    op.create_index('idx_task_tags_tag', 'task_tag', ['tag_id'])


def downgrade() -> None:
    op.drop_index('idx_task_tags_tag', 'task_tag')
    op.drop_index('idx_task_tags_task', 'task_tag')
    op.drop_table('task_tag')
