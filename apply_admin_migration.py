#!/usr/bin/env python
"""
Скрипт для применения миграции добавления поля is_admin
"""

import os
import sys
from flask import Flask
from sqlalchemy import text

def apply_migration():
    """Применяет миграцию для добавления поля is_admin"""
    
    print("🛠️ Применение миграции для добавления поля is_admin")
    print("=" * 60)
    
    # Создаем приложение Flask для контекста
    app = Flask(__name__)
    
    # Используем конфигурацию из config.py
    try:
        from config import get_config
        app.config.from_object(get_config())
    except ImportError as e:
        print(f"❌ Ошибка импорта конфигурации: {e}")
        print("📝 Использую конфигурацию по умолчанию...")
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL', 
            'postgresql://pastebin_user:pastebin_password@localhost:5432/pastebin_db'
        )
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    from models import db
    db.init_app(app)
    
    with app.app_context():
        try:
            # Создаем подключение к базе данных
            connection = db.engine.connect()
            
            print("🔍 Проверяем структуру таблицы users...")
            
            # Проверяем, существует ли поле is_admin
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'is_admin'
            """))
            
            column_exists = result.fetchone() is not None
            
            if not column_exists:
                print("📝 Добавляем поле is_admin в таблицу users...")
                
                try:
                    # Добавляем поле is_admin
                    connection.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN is_admin BOOLEAN DEFAULT FALSE
                    """))
                    print("✅ Поле is_admin успешно добавлено!")
                    
                    # Проверяем добавление
                    result = connection.execute(text("""
                        SELECT column_name 
                        FROM information_schema.columns 
                        WHERE table_name = 'users' AND column_name = 'is_admin'
                    """))
                    
                    if result.fetchone():
                        print("✅ Подтверждение: поле is_admin существует")
                    else:
                        print("❌ Ошибка: поле is_admin не добавлено")
                        return False
                        
                except Exception as e:
                    if "already exists" in str(e).lower():
                        print("✅ Поле is_admin уже существует")
                    else:
                        print(f"❌ Ошибка при добавлении поля: {e}")
                        return False
            else:
                print("✅ Поле is_admin уже существует")
            
            # Проверяем существование администратора
            print("\n🔍 Проверяем существование администратора...")
            
            result = connection.execute(text("SELECT * FROM users WHERE username = 'admin'"))
            admin_exists = result.fetchone() is not None
            
            if not admin_exists:
                print("👑 Создаем администратора admin/admin...")
                
                # Импортируем функцию хеширования
                import hashlib
                import secrets
                
                def hash_password(password):
                    """Хеширует пароль с солью"""
                    salt = secrets.token_hex(16)
                    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                    return f"{salt}${password_hash}"
                
                # Хешируем пароль
                password_hash = hash_password('admin')
                
                # Создаем администратора
                connection.execute(text("""
                    INSERT INTO users (username, email, password_hash, is_active, is_admin, created_at) 
                    VALUES ('admin', 'admin@localhost', :password_hash, true, true, NOW())
                """), {'password_hash': password_hash})
                
                print("✅ Администратор успешно создан!")
                print(f"   Логин: admin")
                print(f"   Пароль: admin")
                print(f"   Email: admin@localhost")
            else:
                print("✅ Администратор admin уже существует")
                
                # Проверяем, является ли пользователь администратором
                result = connection.execute(text("""
                    SELECT is_admin FROM users WHERE username = 'admin'
                """))
                
                admin_row = result.fetchone()
                if admin_row and not admin_row[0]:
                    print("⚠️  Пользователь admin НЕ является администратором")
                    print("   Обновляем до администратора...")
                    
                    connection.execute(text("""
                        UPDATE users 
                        SET is_admin = true 
                        WHERE username = 'admin'
                    """))
                    
                    print("✅ Пользователь admin теперь администратор!")
                else:
                    print("✅ Пользователь admin является администратором")
            
            # Показываем список всех администраторов
            print("\n📋 Список администраторов:")
            result = connection.execute(text("""
                SELECT username, email, created_at 
                FROM users 
                WHERE is_admin = true 
                ORDER BY created_at
            """))
            
            admins = result.fetchall()
            if admins:
                for admin in admins:
                    print(f"   • {admin[0]} ({admin[1]}) - {admin[2]}")
            else:
                print("   Нет администраторов")
            
            connection.close()
            print("\n✅ Миграция успешно применена!")
            return True
            
        except Exception as e:
            print(f"❌ Ошибка п��и применении миграции: {e}")
            import traceback
            traceback.print_exc()
            return False

def check_database():
    """Проверяет подключение к базе данных"""
    print("\n🔌 Проверка подключения к базе данных...")
    
    app = Flask(__name__)
    
    try:
        from config import get_config
        app.config.from_object(get_config())
    except:
        app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv(
            'DATABASE_URL', 
            'postgresql://pastebin_user:pastebin_password@localhost:5432/pastebin_db'
        )
    
    from models import db
    db.init_app(app)
    
    with app.app_context():
        try:
            # Пробуем подключиться
            connection = db.engine.connect()
            print(f"✅ Подключение к базе данных установлено")
            print(f"   URL: {app.config.get('SQLALCHEMY_DATABASE_URI', 'не указан')}")
            
            # Проверяем таблицы
            result = connection.execute(text("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public'
            """))
            
            tables = [row[0] for row in result.fetchall()]
            print(f"✅ Таблицы в базе данных: {', '.join(tables)}")
            
            connection.close()
            return True
            
        except Exception as e:
            print(f"❌ Ошибка подключения к базе данных: {e}")
            return False

def main():
    """Главная функция"""
    print("👑 Настройка системы администратора")
    print("=" * 60)
    
    print("Этапы настройки:")
    print("1. Проверка подключения к базе данных")
    print("2. Добавление поля is_admin в таблицу users")
    print("3. Создание администратора admin/admin")
    print("4. Проверка результатов")
    
    if check_database():
        if apply_migration():
            print("\n🎉 Настройка завершена успешно!")
            print("\n📋 Итоговая сводка:")
            print("   • Поле is_admin добавлено в таблицу users")
            print("   • Администратор admin/admin создан")
            print("   • Система готова к использованию")
            
            print("\n🚀 Дальнейшие действия:")
            print("   1. Перезапустите приложение на Render")
            print("   2. Перейдите на ваш сайт")
            print("   3. Войдите с логином: admin, паролем: admin")
            print("   4. Нажмите 'Админ-панель' в профиле")
        else:
            print("\n❌ Ошибка при настройке!")
            sys.exit(1)
    else:
        print("\n❌ Не удалось подключиться к базе данных!")
        print("   Убедитесь, что:")
        print("   - PostgreSQL сервер запущен")
        print("   - Переменная окружения DATABASE_URL установлена")
        print("   - База данных существует и доступна")
        sys.exit(1)

if __name__ == "__main__":
    main()