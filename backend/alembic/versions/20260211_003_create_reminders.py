"""Create reminders table

Revision ID: 20260211_003
Revises: 20260211_002
Create Date: 2026-02-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20260211_003'
down_revision: Union[str, None] = '20260211_002'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'reminder',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('task_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('remind_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('offset_minutes', sa.Integer(), nullable=False),
        sa.Column('channel', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.CheckConstraint("channel IN ('EMAIL', 'PUSH', 'BOTH')", name='check_channel'),
        sa.CheckConstraint("status IN ('PENDING', 'SCHEDULED', 'SENT', 'FAILED')", name='check_status')
    )
    
    # Create indexes
    op.create_index('idx_reminders_task', 'reminder', ['task_id'])
    op.create_index('idx_reminders_user', 'reminder', ['user_id'])
    op.create_index('idx_reminders_remind_at', 'reminder', ['remind_at'])
    op.create_index('idx_reminders_status_remind', 'reminder', ['status', 'remind_at'])


def downgrade() -> None:
    op.drop_index('idx_reminders_status_remind', 'reminder')
    op.drop_index('idx_reminders_remind_at', 'reminder')
    op.drop_index('idx_reminders_user', 'reminder')
    op.drop_index('idx_reminders_task', 'reminder')
    op.drop_table('reminder')
