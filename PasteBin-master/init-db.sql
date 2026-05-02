-- Создание базы данных для PasteBin
-- Этот скрипт выполняется автоматически при первом запуске PostgreSQL контейнера

-- Подключаемся к созданной базе данных
\c pastebin_db;

-- Создание таблицы для паст
CREATE TABLE IF NOT EXISTS pastes (
    id SERIAL PRIMARY KEY,
    uuid VARCHAR(36) UNIQUE NOT NULL DEFAULT gen_random_uuid()::text,
    title VARCHAR(255) NOT NULL,
    content_hash VARCHAR(64) NOT NULL,
    language VARCHAR(50) DEFAULT 'text',
    lifetime INTEGER DEFAULT 1440,
    is_private BOOLEAN DEFAULT FALSE,
    views_count INTEGER DEFAULT 0,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE,
    is_expired BOOLEAN DEFAULT FALSE,
    author_id INTEGER,
    tags TEXT[]
);

-- Создание таблицы для пользователей
CREATE TABLE IF NOT EXISTS users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(80) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_active BOOLEAN DEFAULT TRUE
);

-- Создание таблицы для тегов
CREATE TABLE IF NOT EXISTS tags (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) UNIQUE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Создание таблицы связи паст и тегов (many-to-many)
CREATE TABLE IF NOT EXISTS paste_tags (
    paste_id INTEGER REFERENCES pastes(id) ON DELETE CASCADE,
    tag_id INTEGER REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (paste_id, tag_id)
);

-- Создание индексов для улучшения производительности
CREATE INDEX IF NOT EXISTS idx_pastes_created_at ON pastes(created_at);
CREATE INDEX IF NOT EXISTS idx_pastes_language ON pastes(language);
CREATE INDEX IF NOT EXISTS idx_pastes_is_private ON pastes(is_private);
CREATE INDEX IF NOT EXISTS idx_pastes_expires_at ON pastes(expires_at);
CREATE INDEX IF NOT EXISTS idx_pastes_content_hash ON pastes(content_hash);

-- Создание полнотекстового поиска по заголовку и тегам
CREATE INDEX IF NOT EXISTS idx_pastes_title_search ON pastes USING gin(to_tsvector('russian', title));

-- Создание представления для недавних паст
CREATE OR REPLACE VIEW recent_pastes AS
SELECT 
    p.id,
    p.uuid,
    p.title,
    p.language,
    p.created_at,
    p.views_count,
    p.is_private,
    p.is_expired,
    array_agg(t.name) FILTER (WHERE t.name IS NOT NULL) as tags
FROM pastes p
LEFT JOIN paste_tags pt ON p.id = pt.paste_id
LEFT JOIN tags t ON pt.tag_id = t.id
WHERE p.is_expired = FALSE
GROUP BY p.id, p.uuid, p.title, p.language, p.created_at, p.views_count, p.is_private, p.is_expired
ORDER BY p.created_at DESC;

-- Создание функции для очистки истекших паст
CREATE OR REPLACE FUNCTION cleanup_expired_pastes()
RETURNS INTEGER AS $$
DECLARE
    deleted_count INTEGER;
BEGIN
    UPDATE pastes 
    SET is_expired = TRUE 
    WHERE expires_at IS NOT NULL 
    AND expires_at < CURRENT_TIMESTAMP 
    AND is_expired = FALSE;
    
    GET DIAGNOSTICS deleted_count = ROW_COUNT;
    RETURN deleted_count;
END;
$$ LANGUAGE plpgsql;

-- Создание триггера для автоматического обновления времени истечения
CREATE OR REPLACE FUNCTION update_expires_at()
RETURNS TRIGGER AS $$
BEGIN
    IF NEW.lifetime > 0 THEN
        NEW.expires_at = NEW.created_at + INTERVAL '1 minute' * NEW.lifetime;
    ELSE
        NEW.expires_at = NULL;
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_update_expires_at
    BEFORE INSERT OR UPDATE ON pastes
    FOR EACH ROW
    EXECUTE FUNCTION update_expires_at();

-- Вставка начальных данных
INSERT INTO tags (name) VALUES 
    ('python'), ('javascript'), ('html'), ('css'), ('sql'), ('bash'), ('docker'), ('flask')
ON CONFLICT (name) DO NOTHING;

-- Создание пользователя по умолчанию (опционально)
-- INSERT INTO users (username, email) VALUES ('admin', 'admin@pastebin.local')
-- ON CONFLICT (username) DO NOTHING;

-- Вывод информации о созданных таблицах
\dt
