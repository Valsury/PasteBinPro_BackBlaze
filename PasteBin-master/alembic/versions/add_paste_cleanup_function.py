"""Add paste cleanup function

Revision ID: add_paste_cleanup_function
Revises: initial_migration
Create Date: 2025-08-22 18:15:00.000000

"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'add_paste_cleanup_function'
down_revision = 'initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add paste cleanup function and improve indexes."""
    
    # Создаем функцию для очистки истекших паст
    op.execute("""
        CREATE OR REPLACE FUNCTION cleanup_expired_pastes()
        RETURNS INTEGER AS $$
        DECLARE
            deleted_count INTEGER;
        BEGIN
            -- Удаляем истекшие пасты
            DELETE FROM pastes 
            WHERE expires_at < NOW() 
            AND is_expired = false
            AND lifetime > 0;
            
            GET DIAGNOSTICS deleted_count = ROW_COUNT;
            
            -- Обновляем флаг is_expired для оставшихся
            UPDATE pastes 
            SET is_expired = true 
            WHERE expires_at < NOW() 
            AND is_expired = false
            AND lifetime > 0;
            
            RETURN deleted_count;
        END;
        $$ LANGUAGE plpgsql;
    """)
    
    # Создаем улучшенные индексы
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_pastes_expires_at_active 
        ON pastes(expires_at) 
        WHERE is_expired = false;
    """)
    
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_pastes_created_at_recent 
        ON pastes(created_at DESC) 
        WHERE is_expired = false;
    """)
    
    # Создаем индекс для поиска по тегам
    op.execute("""
        CREATE INDEX IF NOT EXISTS idx_pastes_tags_gin 
        ON pastes USING GIN (to_tsvector('russian', tags));
    """)


def downgrade() -> None:
    """Remove paste cleanup function and indexes."""
    
    # Удаляем функцию
    op.execute("DROP FUNCTION IF EXISTS cleanup_expired_pastes();")
    
    # Удаляем индексы
    op.execute("DROP INDEX IF EXISTS idx_pastes_expires_at_active;")
    op.execute("DROP INDEX IF EXISTS idx_pastes_created_at_recent;")
    op.execute("DROP INDEX IF EXISTS idx_pastes_tags_gin;")
