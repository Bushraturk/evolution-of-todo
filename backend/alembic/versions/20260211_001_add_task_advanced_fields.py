"""Add advanced fields to tasks table

Revision ID: 20260211_001
Revises: 
Create Date: 2026-02-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20260211_001'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns to tasks table
    op.add_column('task', sa.Column('due_date', sa.DateTime(timezone=True), nullable=True))
    op.add_column('task', sa.Column('is_recurring', sa.Boolean(), nullable=False, server_default='false'))
    op.add_column('task', sa.Column('parent_task_id', sa.Uuid(), nullable=True))
    op.add_column('task', sa.Column('recurrence_id', sa.Uuid(), nullable=True))
    
    # Create indexes
    op.create_index('idx_tasks_due_date', 'task', ['due_date'])
    op.create_index('idx_tasks_parent', 'task', ['parent_task_id'])
    op.create_index('idx_tasks_completed_due', 'task', ['completed', 'due_date'])


def downgrade() -> None:
    # Drop indexes
    op.drop_index('idx_tasks_completed_due', 'task')
    op.drop_index('idx_tasks_parent', 'task')
    op.drop_index('idx_tasks_due_date', 'task')
    
    # Drop columns
    op.drop_column('task', 'recurrence_id')
    op.drop_column('task', 'parent_task_id')
    op.drop_column('task', 'is_recurring')
    op.drop_column('task', 'due_date')
