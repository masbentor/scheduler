"""update timestamp columns to datetime

Revision ID: 315493acffbe
Revises: 2b7ce654185f
Create Date: 2024-04-02

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic
revision = '315493acffbe'
down_revision = '2b7ce654185f'
branch_labels = None
depends_on = None

def upgrade():
    # SQLite doesn't support ALTER COLUMN, so we need to:
    # 1. Create a new table with the desired schema
    # 2. Copy the data
    # 3. Drop the old table
    # 4. Rename the new table
    
    # Create new table
    op.create_table(
        'assignment_history_new',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person', sa.String(), nullable=False),
        sa.Column('group_id', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('day_type', sa.String(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('cumulative_regular_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cumulative_weighted_days', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('cumulative_total_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.text('CURRENT_TIMESTAMP'), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data
    op.execute("""
        INSERT INTO assignment_history_new 
        SELECT id, person, group_id, date, day_type, weight, 
               cumulative_regular_days, cumulative_weighted_days, cumulative_total_days,
               datetime(created_at), datetime(updated_at)
        FROM assignment_history
    """)
    
    # Drop old table
    op.drop_table('assignment_history')
    
    # Rename new table
    op.rename_table('assignment_history_new', 'assignment_history')
    
    # Recreate indexes
    op.create_index(op.f('ix_assignment_history_date'), 'assignment_history', ['date'], unique=False)
    op.create_index(op.f('ix_assignment_history_group_id'), 'assignment_history', ['group_id'], unique=False)
    op.create_index(op.f('ix_assignment_history_person'), 'assignment_history', ['person'], unique=False)

def downgrade():
    # Create new table with old schema
    op.create_table(
        'assignment_history_old',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('person', sa.String(), nullable=False),
        sa.Column('group_id', sa.String(), nullable=False),
        sa.Column('date', sa.Date(), nullable=False),
        sa.Column('day_type', sa.String(), nullable=False),
        sa.Column('weight', sa.Float(), nullable=False),
        sa.Column('cumulative_regular_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('cumulative_weighted_days', sa.Float(), nullable=False, server_default='0.0'),
        sa.Column('cumulative_total_days', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('created_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.Column('updated_at', sa.Date(), server_default=sa.text('CURRENT_DATE')),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Copy data
    op.execute("""
        INSERT INTO assignment_history_old 
        SELECT id, person, group_id, date, day_type, weight, 
               cumulative_regular_days, cumulative_weighted_days, cumulative_total_days,
               date(created_at), date(updated_at)
        FROM assignment_history
    """)
    
    # Drop old table
    op.drop_table('assignment_history')
    
    # Rename new table
    op.rename_table('assignment_history_old', 'assignment_history')
    
    # Recreate indexes
    op.create_index(op.f('ix_assignment_history_date'), 'assignment_history', ['date'], unique=False)
    op.create_index(op.f('ix_assignment_history_group_id'), 'assignment_history', ['group_id'], unique=False)
    op.create_index(op.f('ix_assignment_history_person'), 'assignment_history', ['person'], unique=False)
