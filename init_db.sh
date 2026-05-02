#!/bin/bash

# Скрипт для инициализации базы данных на Render
echo "🚀 Starting database initialization..."

# Применяем миграции Alembic
if [ -d "alembic/versions" ] && [ "$(ls -A alembic/versions)" ]; then
    echo "📦 Running Alembic migrations..."
    alembic upgrade head
else
    echo "⚠️ No Alembic migrations found, creating tables directly..."
    python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ Database tables created')"
fi

echo "✅ Database initialization complete!"
