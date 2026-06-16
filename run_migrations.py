#!/usr/bin/env python
"""
Запуск миграций при импорте модуля
Этот скрипт гарантирует, что миграции будут применены ДО любых операций с базой данных
"""

import os
import sys
import traceback

print("🚀 ЗАПУСК МИГРАЦИЙ ПРИ ИМПОРТЕ МОДУЛЯ")
print("=" * 70)

def run_immediate_migrations():
    """Запускает миграции немедленно при импорте"""
    
    try:
        # Импортируем необходимые модули
        from flask import Flask
        from sqlalchemy import text
        
        # Создаем временное приложение Flask
        app = Flask(__name__)
        
        # Загружаем конфигурацию
        from config import get_config
        app.config.from_object(get_config())
        
        # Инициализируем базу данных
        from models import db
        db.init_app(app)
        
        with app.app_context():
            print("🔧 1. Создаем таблицы если их нет...")
            try:
                db.create_all()
                print("   ✅ Таблицы созданы/проверены")
            except Exception as e:
                print(f"   ⚠️ Ошибка при создании таблиц: {e}")
            
            print("\n🔧 2. Добавляем поле is_admin в таблицу users...")
            
            # Шаг 1: Проверяем и добавляем поле is_admin
            migration_success = False
            
            # Способ 1: Проверяем через information_schema
            try:
                result = db.session.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'users' AND column_name = 'is_admin'
                """)).fetchone()
                
                if result:
                    print("   ✅ Поле is_admin уже существует в таблице users")
                    migration_success = True
                else:
                    print("   ❌ Поле is_admin НЕ найдено в таблице users")
                    migration_success = False
                    
            except Exception as e:
                print(f"   ⚠️ Не удалось проверить через information_schema: {e}")
                migration_success = False
            
            # Если поле не найдено, добавляем его
            if not migration_success:
                print("   📝 Добавляю поле is_admin...")
                
                # Пробуем несколько способов добавления поля
                add_methods = [
                    # Способ 1: С IF NOT EXISTS (PostgreSQL)
                    ("ALTER TABLE users ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE", "IF NOT EXISTS"),
                    # Способ 2: Простое добавление
                    ("ALTER TABLE users ADD COLUMN is_admin BOOLEAN DEFAULT FALSE", "простое добавление"),
                ]
                
                for sql_query, method_name in add_methods:
                    try:
                        db.session.execute(text(sql_query))
                        db.session.commit()
                        print(f"   ✅ Поле is_admin успешно добавлено (способ: {method_name})!")
                        migration_success = True
                        break
                    except Exception as e:
                        if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                            print(f"   ✅ Поле is_admin уже существует (способ: {method_name})")
                            migration_success = True
                            break
                        else:
                            print(f"   ⚠️ Способ {method_name} не сработал: {e}")
                
                if not migration_success:
                    print("   ❌ Не удалось добавить поле is_admin всеми способами")
                    return False
            
            print("\n🔧 3. Создаем/проверяем администратора admin/admin...")
            
            # Функция хеширования пароля
            import hashlib
            import secrets
            
            def hash_password(password):
                """Хеширует пароль с солью"""
                salt = secrets.token_hex(16)
                password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                return f"{salt}${password_hash}"
            
            # Проверяем существование пользователя admin
            admin_exists = db.session.execute(
                text("SELECT username FROM users WHERE username = 'admin'")
            ).fetchone()
            
            if not admin_exists:
                print("   👑 Создаю администратора admin/admin...")
                
                password_hash = hash_password('admin')
                
                # Пробуем создать с полем is_admin
                try:
                    db.session.execute(text("""
                        INSERT INTO users (username, email, password_hash, is_active, is_admin, created_at) 
                        VALUES ('admin', 'admin@localhost', :password_hash, true, true, NOW())
                    """), {'password_hash': password_hash})
                    db.session.commit()
                    print("   ✅ Администратор успешно создан (с полем is_admin)!")
                except Exception as e:
                    print(f"   ⚠️ Ошибка при создании с полем is_admin: {e}")
                    print("   📝 Пробую создать без поля is_admin...")
                    
                    try:
                        db.session.execute(text("""
                            INSERT INTO users (username, email, password_hash, is_active, created_at) 
                            VALUES ('admin', 'admin@localhost', :password_hash, true, NOW())
                        """), {'password_hash': password_hash})
                        db.session.commit()
                        print("   ✅ Администратор создан (без поля is_admin)!")
                        
                        # Обновляем до администратора
                        db.session.execute(text("""
                            UPDATE users 
                            SET is_admin = true 
                            WHERE username = 'admin'
                        """))
                        db.session.commit()
                        print("   ✅ Пользователь admin обновлен до администратора!")
                    except Exception as e2:
                        print(f"   ❌ Ошибка при создании администратора: {e2}")
                        return False
            else:
                print("   ℹ️ Пользователь admin уже существует")
                
                # Проверяем, является ли администратором
                try:
                    result = db.session.execute(text("""
                        SELECT is_admin FROM users WHERE username = 'admin'
                    """)).fetchone()
                    
                    if result and result[0]:
                        print("   ✅ Пользователь admin уже является администратором")
                    else:
                        print("   ⚠️ Пользователь admin НЕ является администратором")
                        print("   📝 Обновляю до администратора...")
                        
                        db.session.execute(text("""
                            UPDATE users 
                            SET is_admin = true 
                            WHERE username = 'admin'
                        """))
                        db.session.commit()
                        print("   ✅ Пользователь admin обновлен до администратора!")
                except Exception as e:
                    print(f"   ⚠️ Ошибка при проверке статуса администратора: {e}")
            
            print("\n" + "=" * 70)
            print("✅ МИГРАЦИИ УСПЕШНО ПРИМЕНЕНЫ!")
            print("=" * 70)
            return True
            
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА ПРИ ЗАПУСКЕ МИГРАЦИЙ: {e}")
        traceback.print_exc()
        print("\n" + "=" * 70)
        print("❌ МИГРАЦИИ НЕ УДАЛИСЬ!")
        print("=" * 70)
        return False

# Запускаем миграции при импорте модуля
try:
    success = run_immediate_migrations()
    if not success:
        print("\n⚠️ ВНИМАНИЕ: Миграции не удалось применить полностью.")
        print("   Приложение продолжит работу, но возможны ошибки с полем is_admin.")
except Exception as e:
    print(f"❌ НЕУДАЧНЫЙ ЗАПУСК МИГРАЦИЙ: {e}")
    print("⚠️ Приложение продолжит работу, но возможны ошибки.")