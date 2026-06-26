"""Rename User 'password' column to 'hashed_password'

Revision ID: 860378111d8d
Revises: 85b14add3fde
Create Date: 2026-06-26 12:26:21.848773

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '860378111d8d'
down_revision: Union[str, Sequence[str], None] = '85b14add3fde'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Вместо удаления и добавления — просто переименовываем
    op.alter_column('users', 'password', new_column_name='hashed_password')


def downgrade() -> None:
    """Downgrade schema."""
    # При откате миграции возвращаем старое имя
    op.alter_column('users', 'hashed_password', new_column_name='password')
