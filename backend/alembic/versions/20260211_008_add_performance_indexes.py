"""Add performance indexes for task queries.

Revision ID: 20260211_008_add_performance_indexes
Revises: 20260211_007_add_foreign_keys
Create Date: 2026-02-11

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260211_008_add_performance_indexes'
down_revision = '20260211_007_add_foreign_keys'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add performance indexes for common queries."""
    # Index for filtering by due_date (for overdue tasks, upcoming tasks)
    op.create_index(
        'ix_tasks_due_date',
        'task',
        ['due_date'],
        unique=False
    )

    # Index for filtering by priority (for priority-based queries)
    op.create_index(
        'ix_tasks_priority',
        'task',
        ['priority'],
        unique=False
    )

    # Composite index for user_id + completed (for filtering incomplete tasks)
    op.create_index(
        'ix_tasks_user_completed',
        'task',
        ['user_id', 'completed'],
        unique=False
    )

    # Composite index for user_id + due_date (for user's upcoming tasks)
    op.create_index(
        'ix_tasks_user_due_date',
        'task',
        ['user_id', 'due_date'],
        unique=False
    )

    # Index for recurring tasks queries
    op.create_index(
        'ix_tasks_is_recurring',
        'task',
        ['is_recurring'],
        unique=False
    )

    # Index for parent_task_id (for getting task occurrences)
    op.create_index(
        'ix_tasks_parent_task_id',
        'task',
        ['parent_task_id'],
        unique=False
    )

    # Index for reminders scheduled_for (for pending notifications query)
    op.create_index(
        'ix_scheduled_notifications_scheduled_for',
        'scheduled_notification',
        ['scheduled_for'],
        unique=False
    )

    # Composite index for status + scheduled_for (for pending notifications)
    op.create_index(
        'ix_scheduled_notifications_status_scheduled',
        'scheduled_notification',
        ['status', 'scheduled_for'],
        unique=False
    )

    # Index for tags by user_id (for user's tags)
    op.create_index(
        'ix_tags_user_id',
        'tag',
        ['user_id'],
        unique=False
    )

    # Index for task_tags task_id (for getting task's tags)
    op.create_index(
        'ix_task_tags_task_id',
        'task_tag',
        ['task_id'],
        unique=False
    )


def downgrade() -> None:
    """Remove performance indexes."""
    op.drop_index('ix_task_tags_task_id', table_name='task_tag')
    op.drop_index('ix_tags_user_id', table_name='tag')
    op.drop_index('ix_scheduled_notifications_status_scheduled', table_name='scheduled_notification')
    op.drop_index('ix_scheduled_notifications_scheduled_for', table_name='scheduled_notification')
    op.drop_index('ix_tasks_parent_task_id', table_name='task')
    op.drop_index('ix_tasks_is_recurring', table_name='task')
    op.drop_index('ix_tasks_user_due_date', table_name='task')
    op.drop_index('ix_tasks_user_completed', table_name='task')
    op.drop_index('ix_tasks_priority', table_name='task')
    op.drop_index('ix_tasks_due_date', table_name='task')
