#!/usr/bin/env python
"""
Простой скрипт для создания администратора без подключения к базе данных
"""

import hashlib
import secrets
import os

def hash_password(password):
    """Хеширует пароль с солью"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${password_hash}"

def main():
    """Главная функция"""
    print("👑 Создание администратора admin/admin")
    print("=" * 60)
    
    # Хешируем пароль admin
    admin_password = "admin"
    hashed_password = hash_password(admin_password)
    
    print("📝 Данные администратора:")
    print(f"   Логин: admin")
    print(f"   Пароль: admin")
    print(f"   Email: admin@localhost")
    print(f"   Хеш пароля: {hashed_password}")
    
    print("\n💾 SQL команды для создания администратора:")
    print("=" * 60)
    print("""
-- 1. Проверьте, есть ли поле is_admin в таблице users
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'is_admin';

-- 2. Если поля нет, добавьте его
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- 3. Проверьте существование пользователя admin
SELECT * FROM users WHERE username = 'admin';

-- 4. Если пользователя нет, создайте его
INSERT INTO users (username, email, password_hash, is_active, is_admin, created_at) 
VALUES ('admin', 'admin@localhost', '%s', true, true, NOW());

-- 5. Если пользователь есть, обновите его до администратора
UPDATE users 
SET is_admin = true, email = 'admin@localhost' 
WHERE username = 'admin';
""" % hashed_password)
    
    print("\n📋 Инструкция:")
    print("1. Запустите PostgreSQL (или вашу базу данных)")
    print("2. Подключитесь к базе данных pastebin_db")
    print("3. Выполните SQL команды выше")
    print("4. Запустите приложение: python app.py")
    print("5. Войдите с логином: admin, паролем: admin")
    
    print("\n⚠️  Важная информация:")
    print("   - Система автоматически создаст администратора при запуске")
    print("   - Код для создания администратора уже добавлен в app.py")
    print("   - При запуске app.py проверит и создаст администратора если нужно")
    
    print("\n✅ Проверьте следующее:")
    print("   - models.py содержит поле is_admin в классе User")
    print("   - app.py содержит код создания администратора в блоке if __name__ == '__main__'")
    print("   - admin_helpers.py содержит декоратор admin_required")
    print("   - Созданы шаблоны админ-панели")
    
    print("\n🎯 Дальнейшие шаги:")
    print("1. Запустите PostgreSQL сервер")
    print("2. Запустите python app.py")
    print("3. Перейдите на http://localhost:5000")
    print("4. Войдите как admin/admin")
    print("5. Нажмите 'Админ-панель' в профиле")

if __name__ == "__main__":
    main()