"""Add foreign key constraints to tasks table

Revision ID: 20260211_007
Revises: 20260211_006
Create Date: 2026-02-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20260211_007'
down_revision: Union[str, None] = '20260211_006'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add foreign key constraints
    op.create_foreign_key(
        'fk_tasks_recurrence',
        'task', 'recurring_pattern',
        ['recurrence_id'], ['id'],
        ondelete='SET NULL'
    )
    op.create_foreign_key(
        'fk_tasks_parent',
        'task', 'task',
        ['parent_task_id'], ['id'],
        ondelete='CASCADE'
    )


def downgrade() -> None:
    op.drop_constraint('fk_tasks_parent', 'task', type_='foreignkey')
    op.drop_constraint('fk_tasks_recurrence', 'task', type_='foreignkey')
