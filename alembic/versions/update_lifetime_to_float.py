"""Update lifetime field to Float

Revision ID: update_lifetime_to_float
Revises: add_paste_cleanup_function
Create Date: 2025-01-24 20:30:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'update_lifetime_to_float'
down_revision = 'add_paste_cleanup_function'
branch_labels = None
depends_on = None

def upgrade():
    # Изменяем тип поля lifetime с INTEGER на FLOAT
    op.alter_column('pastes', 'lifetime',
                    existing_type=sa.INTEGER(),
                    type_=sa.FLOAT(),
                    existing_nullable=True,
                    existing_server_default=sa.text('1440'))

def downgrade():
    # Возвращаем тип поля lifetime обратно к INTEGER
    op.alter_column('pastes', 'lifetime',
                    existing_type=sa.FLOAT(),
                    type_=sa.INTEGER(),
                    existing_nullable=True,
                    existing_server_default=sa.text('1440'))
