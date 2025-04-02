"""update timestamp columns to datetime

Revision ID: 315493acffbe
Revises: 2b7ce654185f
Create Date: 2024-04-02 12:50:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '315493acffbe'
down_revision: Union[str, None] = '2b7ce654185f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Update created_at column
    op.alter_column('assignment_history', 'created_at',
                    existing_type=sa.Date(),
                    type_=sa.DateTime(),
                    existing_nullable=True,
                    server_default=sa.text('CURRENT_TIMESTAMP'))
    
    # Update updated_at column
    op.alter_column('assignment_history', 'updated_at',
                    existing_type=sa.Date(),
                    type_=sa.DateTime(),
                    existing_nullable=True,
                    server_default=sa.text('CURRENT_TIMESTAMP'),
                    server_onupdate=sa.text('CURRENT_TIMESTAMP'))


def downgrade() -> None:
    # Revert created_at column
    op.alter_column('assignment_history', 'created_at',
                    existing_type=sa.DateTime(),
                    type_=sa.Date(),
                    existing_nullable=True,
                    server_default=sa.text('CURRENT_DATE'))
    
    # Revert updated_at column
    op.alter_column('assignment_history', 'updated_at',
                    existing_type=sa.DateTime(),
                    type_=sa.Date(),
                    existing_nullable=True,
                    server_default=sa.text('CURRENT_DATE'))
