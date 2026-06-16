#!/usr/bin/env python
"""
Скрипт для добавления поля is_admin в таблицу users
и создания администратора admin/admin
"""

import os
import sys
from flask import Flask
from models import db, User
from config import get_config

def add_admin_field():
    """Добавляет поле is_admin и создает администратора"""
    
    # Создаем приложение Flask для контекста
    app = Flask(__name__)
    app.config.from_object(get_config())
    
    with app.app_context():
        # Инициализируем базу данных
        db.init_app(app)
        
        # Создаем подключение к базе данных
        from sqlalchemy import text
        
        # Проверяем, существует ли поле is_admin
        try:
            connection = db.engine.connect()
            
            # Проверяем структуру таблицы users
            result = connection.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'is_admin'
            """))
            
            column_exists = result.fetchone() is not None
            
            if not column_exists:
                print("Добавляем поле is_admin в таблицу users...")
                
                # Добавляем поле is_admin
                connection.execute(text("""
                    ALTER TABLE users 
                    ADD COLUMN is_admin BOOLEAN DEFAULT FALSE
                """))
                
                print("✅ Поле is_admin успешно добавлено")
            else:
                print("✅ Поле is_admin уже существует")
            
            # Проверяем существование администратора
            admin_user = User.query.filter_by(username='admin').first()
            
            if not admin_user:
                print("\nСоздаем администратора admin/admin...")
                
                # Импортируем функцию хеширования пароля
                import hashlib
                import secrets
                
                def hash_password(password):
                    """Хеширует пароль с солью"""
                    salt = secrets.token_hex(16)
                    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
                    return f"{salt}${password_hash}"
                
                # Создаем администратора
                admin_user = User(
                    username='admin',
                    email='admin@localhost',
                    password_hash=hash_password('admin'),
                    is_active=True,
                    is_admin=True
                )
                
                db.session.add(admin_user)
                db.session.commit()
                
                print("✅ Администратор admin/admin успешно создан!")
                print(f"   Логин: admin")
                print(f"   Пароль: admin")
                print(f"   Email: admin@localhost")
            else:
                # Проверяем, является ли пользователь администратором
                if not admin_user.is_admin:
                    print("\nОбновляем пользователя admin до администратора...")
                    admin_user.is_admin = True
                    db.session.commit()
                    print("✅ Пользователь admin теперь администратор!")
                else:
                    print("\n✅ Администратор admin уже существует")
                
                print(f"   Текущий статус: {'администратор' if admin_user.is_admin else 'обычный пользователь'}")
            
            # Показываем список всех администраторов
            print("\n📋 Список администраторов:")
            admins = User.query.filter_by(is_admin=True).all()
            
            if admins:
                for admin in admins:
                    print(f"   • {admin.username} ({admin.email})")
            else:
                print("   Нет администраторов")
            
            connection.close()
            
        except Exception as e:
            print(f"❌ Ошибка: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True

def verify_admin_login():
    """Проверяет вход администратора"""
    app = Flask(__name__)
    app.config.from_object(get_config())
    
    with app.app_context():
        db.init_app(app)
        
        # Импортируем функцию проверки пароля
        import hashlib
        
        def verify_password(password, hashed_password):
            """Проверяет пароль"""
            if not hashed_password or '$' not in hashed_password:
                return False
            salt, stored_hash = hashed_password.split('$', 1)
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return password_hash == stored_hash
        
        # Пробуем войти как admin
        admin_user = User.query.filter_by(username='admin').first()
        
        if admin_user:
            print("\n🔐 Проверка входа администратора:")
            
            # Проверяем пароль
            if verify_password('admin', admin_user.password_hash):
                print("✅ Пароль admin верный")
                
                # Проверяем, что это администратор
                if admin_user.is_admin:
                    print("✅ Пользователь является администратором")
                    print("✅ Вход администратора работает корректно!")
                else:
                    print("❌ Пользователь НЕ является администратором")
            else:
                print("❌ Пароль admin неверный")
        else:
            print("❌ Пользователь admin не найден")

if __name__ == "__main__":
    print("🛠️ Настройка системы администратора")
    print("=" * 50)
    
    success = add_admin_field()
    
    if success:
        verify_admin_login()
        
        print("\n" + "=" * 50)
        print("✅ Настройка завершена!")
        print("\n📝 Инструкция по использованию:")
        print("   1. Запустите приложение: python app.py")
        print("   2. Войдите с логином: admin")
        print("   3. Введите пароль: admin")
        print("   4. Вы будете администр��тором системы")
    else:
        print("\n❌ Настройка не удалась")
        sys.exit(1)