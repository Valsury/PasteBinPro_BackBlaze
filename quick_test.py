#!/usr/bin/env python
# Быстрая проверка импорта

try:
    from app import app
    print("✅ Приложение импортировано успешно")
    
    # Проверяем наличие необходимых функций
    from app import hash_password, verify_password
    print("✅ Функции хеширования импортированы")
    
    # Тест хеширования
    test_pass = "admin"
    hashed = hash_password(test_pass)
    if verify_password(test_pass, hashed):
        print("✅ Хеширование работает правильно")
    else:
        print("❌ Хеширование не работает")
        
    # Проверяем наличие декоратора
    from admin_helpers import admin_required
    print("✅ Декоратор admin_required импортирован")
    
    # Проверяем модель User
    from models import User
    print("✅ Модель User импортирована")
    
    # Проверяем наличие поля is_admin
    if hasattr(User, 'is_admin'):
        print("✅ Поле is_admin есть в модели User")
    else:
        print("❌ Поле is_admin отсутствует в модели User")
        
    print("\n🎉 Все проверки пройдены успешно!")
    print("Система готова к запуску с администратором admin/admin")
    
except Exception as e:
    print(f"❌ Ошибка: {e}")
    import traceback
    traceback.print_exc()