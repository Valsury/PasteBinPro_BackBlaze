"""add timezone to datetime columns

Revision ID: add_timezone_to_datetime
Revises:
Create Date: 2026-06-15

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_timezone_to_datetime'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    """Изменяем все DateTime колонки на TIMESTAMPTZ (с timezone)"""

    # Для PostgreSQL используем ALTER COLUMN TYPE
    # TIMESTAMP -> TIMESTAMPTZ

    # Pastes table
    op.execute("ALTER TABLE pastes ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC'")
    op.execute("ALTER TABLE pastes ALTER COLUMN expires_at TYPE TIMESTAMPTZ USING expires_at AT TIME ZONE 'UTC'")

    # Users table
    op.execute("ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC'")

    # Tags table
    op.execute("ALTER TABLE tags ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC'")

    # AppStats table
    op.execute("ALTER TABLE app_stats ALTER COLUMN updated_at TYPE TIMESTAMPTZ USING updated_at AT TIME ZONE 'UTC'")


def downgrade():
    """Откатываем изменения обратно на TIMESTAMP без timezone"""

    # Pastes table
    op.execute("ALTER TABLE pastes ALTER COLUMN created_at TYPE TIMESTAMP")
    op.execute("ALTER TABLE pastes ALTER COLUMN expires_at TYPE TIMESTAMP")

    # Users table
    op.execute("ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMP")

    # Tags table
    op.execute("ALTER TABLE tags ALTER COLUMN created_at TYPE TIMESTAMP")

    # AppStats table
    op.execute("ALTER TABLE app_stats ALTER COLUMN updated_at TYPE TIMESTAMP")
