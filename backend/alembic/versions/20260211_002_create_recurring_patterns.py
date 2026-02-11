"""Create recurring_patterns table

Revision ID: 20260211_002
Revises: 20260211_001
Create Date: 2026-02-11

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '20260211_002'
down_revision: Union[str, None] = '20260211_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'recurring_pattern',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('frequency', sa.String(20), nullable=False),
        sa.Column('interval', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('day_of_week', sa.Integer(), nullable=True),
        sa.Column('day_of_month', sa.Integer(), nullable=True),
        sa.Column('next_occurrence_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.text('NOW()')),
        sa.PrimaryKeyConstraint('id'),
        sa.CheckConstraint("frequency IN ('DAILY', 'WEEKLY', 'MONTHLY')", name='check_frequency')
    )
    
    # Create index
    op.create_index('idx_recurring_next_occurrence', 'recurring_pattern', ['next_occurrence_date'])


def downgrade() -> None:
    op.drop_index('idx_recurring_next_occurrence', 'recurring_pattern')
    op.drop_table('recurring_pattern')
