#!/usr/bin/env python
"""
Скрипт для применения миграции timezone на Render
Преобразует TIMESTAMP колонки в TIMESTAMPTZ
"""

from app import app, db
from sqlalchemy import text

def apply_timezone_migration():
    """Применяет миграцию timezone для всех DateTime колонок"""
    with app.app_context():
        queries = [
            "ALTER TABLE pastes ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC'",
            "ALTER TABLE pastes ALTER COLUMN expires_at TYPE TIMESTAMPTZ USING expires_at AT TIME ZONE 'UTC'",
            "ALTER TABLE users ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC'",
            "ALTER TABLE tags ALTER COLUMN created_at TYPE TIMESTAMPTZ USING created_at AT TIME ZONE 'UTC'",
            "ALTER TABLE app_stats ALTER COLUMN updated_at TYPE TIMESTAMPTZ USING updated_at AT TIME ZONE 'UTC'"
        ]

        print("🔧 Применяем миграцию timezone для DateTime колонок...")

        for query in queries:
            try:
                db.session.execute(text(query))
                print(f"✅ {query[:60]}...")
            except Exception as e:
                error_msg = str(e).lower()
                # Игнорируем ошибки если колонка уже TIMESTAMPTZ
                if "already type timestamp with time zone" in error_msg or "type timestamptz does not exist" in error_msg:
                    print(f"⚠️ Колонка уже TIMESTAMPTZ: {query[:40]}...")
                else:
                    print(f"❌ Ошибка: {e}")
                    # Не прерываем выполнение, продолжаем со следующей колонкой

        try:
            db.session.commit()
            print("✅ Миграция timezone применена успешно")
        except Exception as e:
            db.session.rollback()
            print(f"❌ Ошибка при коммите миграции: {e}")
            raise

if __name__ == '__main__':
    apply_timezone_migration()
