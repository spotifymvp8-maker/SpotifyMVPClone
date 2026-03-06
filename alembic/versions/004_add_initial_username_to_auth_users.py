"""add initial_username to auth_users

Revision ID: 004_initial_username
Revises: 003_fk_to_user_profiles
Create Date: 2025-03-01

Auth хранит initial_username при регистрации; User Service создаёт профиль при первом обращении.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

revision: str = "004_initial_username"
down_revision: Union[str, None] = "003_fk_to_user_profiles"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "auth_users",
        sa.Column("initial_username", sa.String(50), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("auth_users", "initial_username")
