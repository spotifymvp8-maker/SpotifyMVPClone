"""merge_heads

Revision ID: 6c885fc11b07
Revises: 002_add_music_tables, 004_initial_username
Create Date: 2026-03-06 19:28:14.431787

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '6c885fc11b07'
down_revision: Union[str, Sequence[str], None] = ('002_add_music_tables', '004_initial_username')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
