"""add fairness metrics table

Revision ID: add_fairness_metrics
Revises: 2b7ce654185f
Create Date: 2024-04-02

"""
from alembic import op
import sqlalchemy as sa
from alembic.operations import ops

# revision identifiers, used by Alembic
revision = 'add_fairness_metrics'
down_revision = '2b7ce654185f'
branch_labels = None
depends_on = None

def upgrade():
    # Create fairness_metrics table with all constraints in a single operation
    op.create_table(
        'fairness_metrics',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person', sa.String(), nullable=False),
        sa.Column('group_id', sa.String(), nullable=False),
        # Year-to-date statistics
        sa.Column('ytd_regular_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ytd_friday_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ytd_weekend_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ytd_holiday_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ytd_long_weekend_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('ytd_weighted_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('ytd_total_assignments', sa.Integer(), nullable=False, server_default='0'),
        # Fairness scores
        sa.Column('fairness_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('weighted_fairness_score', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('regular_fairness_score', sa.Float(), nullable=False, server_default='0.0'),
        # Last assignment info
        sa.Column('last_assignment_date', sa.Date(), nullable=True),
        sa.Column('days_since_last_assignment', sa.Integer(), nullable=False, server_default='0'),
        # Timestamps
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        # Primary key and unique constraint
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('person', 'group_id', name='uq_fairness_metrics_person_group')
    )
    # Create indexes
    op.create_index(op.f('ix_fairness_metrics_person'), 'fairness_metrics', ['person'], unique=False)
    op.create_index(op.f('ix_fairness_metrics_group_id'), 'fairness_metrics', ['group_id'], unique=False)

def downgrade():
    # Drop indexes first
    op.drop_index(op.f('ix_fairness_metrics_group_id'), table_name='fairness_metrics')
    op.drop_index(op.f('ix_fairness_metrics_person'), table_name='fairness_metrics')
    # Drop the table
    op.drop_table('fairness_metrics') 