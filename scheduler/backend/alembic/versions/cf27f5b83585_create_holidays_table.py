"""Create holidays table

Revision ID: cf27f5b83585
Revises: 
Create Date: 2025-04-02 14:07:30.770349

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'cf27f5b83585'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('holidays',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('start_date', sa.Date(), nullable=False),
    sa.Column('end_date', sa.Date(), nullable=True),
    sa.Column('name', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_holidays_id'), 'holidays', ['id'], unique=False)
    op.create_index(op.f('ix_holidays_start_date'), 'holidays', ['start_date'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_holidays_start_date'), table_name='holidays')
    op.drop_index(op.f('ix_holidays_id'), table_name='holidays')
    op.drop_table('holidays')
    # ### end Alembic commands ###
