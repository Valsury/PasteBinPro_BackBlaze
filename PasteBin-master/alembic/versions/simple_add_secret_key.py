"""Add secret_key field for private pastes

Revision ID: simple_add_secret_key
Revises: add_app_stats_table
Create Date: 2025-08-29 16:25:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = 'simple_add_secret_key'
down_revision: Union[str, Sequence[str], None] = 'add_app_stats_table'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Добавляем поле secret_key для приватных паст
    op.add_column('pastes', sa.Column('secret_key', sa.String(length=64), nullable=True))
    op.create_unique_constraint('uq_pastes_secret_key', 'pastes', ['secret_key'])


def downgrade() -> None:
    """Downgrade schema."""
    # Удаляем поле secret_key
    op.drop_constraint('uq_pastes_secret_key', 'pastes', type_='unique')
    op.drop_column('pastes', 'secret_key')
