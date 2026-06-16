#!/usr/bin/env python
"""
Надежная миграция для Render, которая добавляет поле is_admin и создает администратора
Этот скрипт использует только простые SQL запросы без использования inspect
"""

import os
import sys
import traceback
from flask import Flask
from sqlalchemy import text

def run_safe_migration():
    """Запускает безопасную миграцию для Render"""
    
    print("=" * 70)
    print("🔧 НАДЕЖНАЯ МИГРАЦИЯ ДЛЯ RENDER")
    print("=" * 70)
    
    # Создаем приложение Flask для контекста
    app = Flask(__name__)
    
    # Загружаем конфигурацию
    try:
        from config import get_config
        app.config.from_object(get_config())
        print("✅ Конфигурация загружена")
    except Exception as e:
        print(f"⚠️ Ошибка загрузки конфигурации: {e}")
        print("📝 Использую конфигурацию по умолчанию...")
        
        # Получаем DATABASE_URL из переменных окружения (как на Render)
        database_url = os.getenv('DATABASE_URL')
        if not database_url:
            database_url = 'postgresql://pastebin_user:pastebin_password@localhost:5432/pastebin_db'
            
        app.config['SQLALCHEMY_DATABASE_URI'] = database_url
        app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
        print(f"📝 Использую DATABASE_URL: {database_url[:50]}...")
    
    # Инициализируем базу данных
    from models import db
    db.init_app(app)
    
    with app.app_context():
        print("\n🔍 Подключаюсь к базе данных...")
        
        try:
            # Получаем соединение с базой данных
            connection = db.engine.connect()
            print("✅ Подключение к базе данных успешно")
            
            # Шаг 1: Проверяем и добавляем поле is_admin
            print("\n📝 ШАГ 1: Проверка поля is_admin в таблице users")
            print("-" * 50)
            
            # Способ 1: Пробуем использовать information_schema (наиболее надежный)
            try:
                result = connection.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'is_admin'
                """)).fetchone()
                
                if result:
                    print("✅ Поле is_admin уже существует в таблице users")
                else:
                    print("❌ Поле is_admin НЕ найдено в таблице users")
                    print("📝 Добавляю поле is_admin...")
                    
                    # Пробуем добавить поле
                    try:
                        connection.execute(text("""
                            ALTER TABLE users 
                            ADD COLUMN is_admin BOOLEAN DEFAULT FALSE
                        """))
                        print("✅ Поле is_admin успешно добавлено!")
                        
                        # Подтверждаем добавление
                        result = connection.execute(text("""
                            SELECT column_name 
                            FROM information_schema.columns 
                            WHERE table_name = 'users' AND column_name = 'is_admin'
                        """)).fetchone()
                        
                        if result:
                            print("✅ Подтверждение: поле is_admin существует")
                        else:
                            print("❌ Критическая ошибка: поле не добавлено")
                            return False
                            
                    except Exception as e:
                        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                            print("✅ Поле is_admin уже существует")
                        else:
                            print(f"❌ Ошибка при добавлении поля: {e}")
                            return False
                            
            except Exception as e:
                print(f"⚠️ Ошибка при проверке через information_schema: {e}")
                
                # Способ 2: Пробуем напрямую добавить поле с обработкой ошибки
                print("📝 Пробую добавить поле напрямую...")
                try:
                    connection.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN is_admin BOOLEAN DEFAULT FALSE
                    """))
                    print("✅ Поле is_admin успешно добавлено (способ 2)!")
                except Exception as e2:
                    if "already exists" in str(e2).lower() or "duplicate column" in str(e2).lower():
                        print("✅ Поле is_admin уже существует (способ 2)")
                    else:
                        print(f"❌ Критическая ошибка (способ 2): {e2}")
                        return False
            
            # Шаг 2: Создаем или обновляем администратора
            print("\n📝 ШАГ 2: Создание администратора admin/admin")
            print("-" * 50)
            
            # Функция хеширования пароля
            import hashlib
            import secrets
            
            def hash_password(password):
                """Хеширует пароль с солью"""
                salt = secrets.token_hex(16)
                password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                return f"{salt}${password_hash}"
            
            # Проверяем существование пользователя admin
            admin_exists = connection.execute(
                text("SELECT * FROM users WHERE username = 'admin'")
            ).fetchone()
            
            hashed_password = hash_password('admin')
            print(f"📝 Хеш пароля 'admin': {hashed_password[:30]}...")
            
            if not admin_exists:
                print("👑 Создаю администратора admin/admin...")
                
                # Пробуем создать пользователя с полем is_admin
                try:
                    connection.execute(text("""
                        INSERT INTO users (username, email, password_hash, is_active, is_admin, created_at) 
                        VALUES ('admin', 'admin@localhost', :password_hash, true, true, NOW())
                    """), {'password_hash': hashed_password})
                    
                    print("✅ Администратор успешно создан!")
                    print(f"   Логин: admin")
                    print(f"   Пароль: admin")
                    print(f"   Email: admin@localhost")
                    print(f"   Статус: администратор")
                    
                except Exception as e:
                    print(f"⚠️ Ошибка при создании с полем is_admin: {e}")
                    print("📝 Пробую создать без поля is_admin...")
                    
                    try:
                        connection.execute(text("""
                            INSERT INTO users (username, email, password_hash, is_active, created_at) 
                            VALUES ('admin', 'admin@localhost', :password_hash, true, NOW())
                        """), {'password_hash': hashed_password})
                        
                        print("✅ Администратор создан (без поля is_admin)")
                        print(f"   Логин: admin")
                        print(f"   Пароль: admin")
                        print(f"   Email: admin@localhost")
                        
                        # Обновляем до администратора
                        connection.execute(text("""
                            UPDATE users 
                            SET is_admin = true 
                            WHERE username = 'admin'
                        """))
                        print("✅ Пользователь admin обновлен до администратора")
                        
                    except Exception as e2:
                        print(f"❌ Критическая ошибка при создании администратора: {e2}")
                        return False
            else:
                print("ℹ️ Пользователь admin уже существует")
                
                # Проверяем, является ли администратором
                try:
                    # Пробуем получить значение is_admin
                    result = connection.execute(text("""
                        SELECT is_admin FROM users WHERE username = 'admin'
                    """)).fetchone()
                    
                    if result:
                        is_admin_value = result[0]
                        if is_admin_value:
                            print("✅ Пользователь admin уже является администратором")
                        else:
                            print("⚠️ Пользователь admin НЕ является администратором")
                            print("📝 Обновляю до администратора...")
                            
                            connection.execute(text("""
                                UPDATE users 
                                SET is_admin = true 
                                WHERE username = 'admin'
                            """))
                            print("✅ Пользователь admin обновлен до администратора")
                    else:
                        print("ℹ️ Не удалось проверить статус is_admin")
                        
                except Exception as e:
                    print(f"⚠️ Ошибка при проверке статуса администратора: {e}")
                    print("📝 Предполагаю, что пользователь не администратор и обновляю...")
                    
                    try:
                        connection.execute(text("""
                            UPDATE users 
                            SET is_admin = true 
                            WHERE username = 'admin'
                        """))
                        print("✅ Пользователь admin обновлен до администратора")
                    except Exception as e2:
                        print(f"⚠️ Не удалось обновить до администратора: {e2}")
            
            # Шаг 3: Проверяем результат
            print("\n📝 ШАГ 3: Проверка результата")
            print("-" * 50)
            
            # Получаем всех администраторов
            try:
                admins = connection.execute(text("""
                    SELECT username, email, is_admin 
                    FROM users 
                    WHERE is_admin = true 
                    ORDER BY created_at
                """)).fetchall()
                
                if admins:
                    print("📋 Список администраторов:")
                    for admin in admins:
                        print(f"   • {admin[0]} ({admin[1]}) - администратор")
                else:
                    print("ℹ️ В базе нет пользователей с is_admin = true")
                    
                    # Пробуем альтернативный способ
                    admins_alt = connection.execute(text("""
                        SELECT username, email 
                        FROM users 
                        WHERE username = 'admin'
                    """)).fetchall()
                    
                    if admins_alt:
                        print("📋 Альтернативный список (пользователи с именем admin):")
                        for admin in admins_alt:
                            print(f"   • {admin[0]} ({admin[1]})")
            except Exception as e:
                print(f"⚠️ Не удалось получить список администраторов: {e}")
            
            connection.close()
            print("\n" + "=" * 70)
            print("✅ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
            print("=" * 70)
            return True
            
        except Exception as e:
            print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
            traceback.print_exc()
            print("\n" + "=" * 70)
            print("❌ МИГРАЦИЯ НЕ УДАЛАСЬ!")
            print("=" * 70)
            return False

def main():
    """Главная функция"""
    print("🚀 Запуск надежной миграции для Render...")
    
    success = run_safe_migration()
    
    if success:
        print("\n🎉 ВСЕ ГОТОВО! Инструкция по использованию:")
        print("   1. Перезапустите приложение на Render")
        print("   2. Войдите с логином: admin")
        print("   3. Введите пароль: admin")
        print("   4. Вы будете администратором системы")
        print("\n⚠️  Если все еще возникают ошибки:")
        print("   - Проверьте логи приложения на Render")
        print("   - Убедитесь, что база данных работает")
        print("   - Попробуйте перезапустить приложение")
    else:
        print("\n😞 Миграция не удалась. Пожалуйста:")
        print("   1. Проверьте подключение к базе данных")
        print("   2. Убедитесь, что DATABASE_URL настроен правильно")
        print("   3. Проверьте права доступа к базе данных")
        sys.exit(1)

if __name__ == "__main__":
    main()