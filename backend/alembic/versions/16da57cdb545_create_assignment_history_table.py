"""create assignment history table

Revision ID: 16da57cdb545
Revises: ${previous_revision}
Create Date: 2024-03-24 12:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '16da57cdb545'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create enum type for day types
    op.execute("""
        CREATE TYPE daytype AS ENUM (
            'regular',
            'friday',
            'weekend',
            'holiday',
            'long_weekend_middle'
        )
    """)
    
    # Create assignment history table
    op.create_table(
        'assignment_history',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person', sa.String(), nullable=False),
        sa.Column('group_id', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('day_type', sa.Enum('regular', 'friday', 'weekend', 'holiday', 'long_weekend_middle', name='daytype'), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('cumulative_regular_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cumulative_weighted_days', sa.Float(), nullable=False, server_default='0'),
        sa.Column('cumulative_total_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes
    op.create_index(op.f('ix_assignment_history_person'), 'assignment_history', ['person'], unique=False)
    op.create_index(op.f('ix_assignment_history_group_id'), 'assignment_history', ['group_id'], unique=False)
    op.create_index(op.f('ix_assignment_history_date'), 'assignment_history', ['date'], unique=False)

def downgrade() -> None:
    # Drop indexes
    op.drop_index(op.f('ix_assignment_history_date'), table_name='assignment_history')
    op.drop_index(op.f('ix_assignment_history_group_id'), table_name='assignment_history')
    op.drop_index(op.f('ix_assignment_history_person'), table_name='assignment_history')
    
    # Drop table
    op.drop_table('assignment_history')
    
    # Drop enum type
    op.execute('DROP TYPE daytype')
