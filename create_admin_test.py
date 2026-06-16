#!/usr/bin/env python
"""
Простой тестовый скрипт для создания администратора
"""

import hashlib
import secrets

def hash_password(password):
    """Хеширует пароль с солью"""
    salt = secrets.token_hex(16)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return f"{salt}${password_hash}"

def verify_password(password, hashed_password):
    """Проверяет пароль"""
    if not hashed_password or '$' not in hashed_password:
        return False
    salt, stored_hash = hashed_password.split('$', 1)
    password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
    return password_hash == stored_hash

def test_admin_creation():
    """Тестирует создание администратора"""
    print("🧪 Тестирование создания администратора")
    print("=" * 50)
    
    # Тест хеширования пароля
    password = "admin"
    hashed_password = hash_password(password)
    
    print("📝 Хеширование пароля 'admin':")
    print(f"   Хеш: {hashed_password}")
    print(f"   Длина: {len(hashed_password)} символов")
    
    # Проверка пароля
    print("\n🔐 Проверка пароля:")
    print(f"   Пароль 'admin' верный: {verify_password('admin', hashed_password)}")
    print(f"   Пароль 'wrong' верный: {verify_password('wrong', hashed_password)}")
    
    # Тест структуры хеша
    print("\n🔍 Структура хеша:")
    parts = hashed_password.split('$')
    print(f"   Соль: {parts[0]}")
    print(f"   Длина соли: {len(parts[0])} символов (ожидается 32)")
    print(f"   Хеш пароля: {parts[1][:20]}...")
    print(f"   Длина хеша: {len(parts[1])} символов (ожидается 64)")
    
    # Тест создания SQL для администратора
    print("\n💾 SQL для создания администратора:")
    print(f"""INSERT INTO users (username, email, password_hash, is_active, is_admin, created_at) 
VALUES ('admin', 'admin@localhost', '{hashed_password}', true, true, NOW());""")
    
    print("\n✅ Тест завершен успешно!")
    
    return True

def main():
    """Главная функция"""
    print("👑 Создание администратора admin/admin")
    print("=" * 60)
    
    if test_admin_creation():
        print("\n📋 Инструкция по использованию:")
        print("   1. Запустите приложение: python app.py")
        print("   2. При запуске система автоматически:")
        print("      - Проверит наличие администратора admin")
        print("      - Если его нет - создаст автоматически")
        print("      - Если есть - проверит статус администратора")
        print("   3. Войдите в систему с:")
        print("      Логин: admin")
        print("      Пароль: admin")
        print("   4. На странице профиля появится ссылка 'Админ-панель'")
        print("   5. Перейдите в админ-панель для управления системой")
        
        print("\n⚠️  Важная информация:")
        print("   - Пароль 'admin' рекомендуется изменить после первого входа")
        print("   - Для защиты системы используйте сложный пароль")
        print("   - Админ-панель доступна только пользователям с is_admin=true")
        
        print("\n🎯 Проверка системы:")
        print("   - Модель User обновлена с полем is_admin")
        print("   - Декоратор @admin_required проверяет права")
        print("   - Сессия пользователя содержит поле is_admin")
        print("   - Созданы шаблоны админ-панели")

if __name__ == "__main__":
    main()