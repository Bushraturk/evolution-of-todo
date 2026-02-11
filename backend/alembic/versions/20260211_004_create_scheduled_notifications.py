"""Create scheduled_notifications table

Revision ID: 20260211_004
Revises: 20260211_003
Create Date: 2026-02-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20260211_004'
down_revision: Union[str, None] = '20260211_003'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'scheduled_notification',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('reminder_id', sa.Uuid(), nullable=False),
        sa.Column('task_id', sa.Uuid(), nullable=False),
        sa.Column('user_id', sa.String(255), nullable=False),
        sa.Column('scheduled_for', sa.DateTime(timezone=True), nullable=False),
        sa.Column('delivery_channel', sa.String(20), nullable=False),
        sa.Column('status', sa.String(20), nullable=False, server_default='PENDING'),
        sa.Column('retry_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('last_attempt_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['reminder_id'], ['reminder.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['task_id'], ['task.id'], ondelete='CASCADE'),
        sa.CheckConstraint("status IN ('PENDING', 'QUEUED', 'SENT', 'FAILED')", name='check_status')
    )
    
    # Create indexes
    op.create_index('idx_scheduled_notif_scheduled', 'scheduled_notification', ['scheduled_for'])
    op.create_index('idx_scheduled_notif_status', 'scheduled_notification', ['status'])
    op.create_index('idx_scheduled_notif_user', 'scheduled_notification', ['user_id'])


def downgrade() -> None:
    op.drop_index('idx_scheduled_notif_user', 'scheduled_notification')
    op.drop_index('idx_scheduled_notif_status', 'scheduled_notification')
    op.drop_index('idx_scheduled_notif_scheduled', 'scheduled_notification')
    op.drop_table('scheduled_notification')
