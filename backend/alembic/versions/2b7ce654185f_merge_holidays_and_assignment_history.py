"""merge_holidays_and_assignment_history

Revision ID: 2b7ce654185f
Revises: 16da57cdb545, cf27f5b83585
Create Date: 2025-04-02 14:52:33.538901

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '2b7ce654185f'
down_revision: Union[str, None] = ('16da57cdb545', 'cf27f5b83585')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
