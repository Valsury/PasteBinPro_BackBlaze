"""Add app_stats table

Revision ID: add_app_stats_table
Revises: update_lifetime_to_float
Create Date: 2025-01-24 21:00:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_app_stats_table'
down_revision = 'update_lifetime_to_float'
branch_labels = None
depends_on = None

def upgrade():
    # Создаем таблицу app_stats
    op.create_table('app_stats',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('key', sa.String(length=100), nullable=False),
        sa.Column('value', sa.Integer(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('key')
    )

def downgrade():
    # Удаляем таблицу app_stats
    op.drop_table('app_stats')

