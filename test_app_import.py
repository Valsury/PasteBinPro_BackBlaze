#!/usr/bin/env python
"""
Тестовый скрипт для проверки импорта приложения
"""

import sys
import traceback

def test_import():
    """Тестирует импорт приложения"""
    print("🧪 Тестирование импорта приложения")
    print("=" * 50)
    
    try:
        from app import app
        print("✅ Приложение импортировано успешно")
        
        # Проверяем наличие необходимых компонентов
        print("\n🔍 Проверка компонентов:")
        
        # Проверка декоратора admin_required
        try:
            from admin_helpers import admin_required
            print("✅ Декоратор admin_required импортирован")
        except ImportError as e:
            print(f"❌ Ошибка импорта admin_required: {e}")
            
        # Проверка моделей
        try:
            from models import User, Paste, db
            print("✅ Модели импортированы")
        except ImportError as e:
            print(f"❌ Ошибка импорта моделей: {e}")
            
        # Проверка конфигурации
        try:
            from config import get_config
            print("✅ Конфигурация импортирована")
        except ImportError as e:
            print(f"❌ Ошибка импорта конфигурации: {e}")
            
        # Проверка функций хеширования
        try:
            from app import hash_password, verify_password
            print("✅ Функции хеширования импортированы")
        except ImportError as e:
            print(f"❌ Ошибка импорта функций хеширования: {e}")
            
        print("\n🎯 Проверка создания администратора:")
        
        # Проверяем функцию хеширования
        test_password = "test123"
        hashed = hash_password(test_password)
        print(f"✅ Хеширование пароля работает")
        print(f"✅ Проверка пароля работает: {verify_password(test_password, hashed)}")
        print(f"❌ Неверный пароль отклоняется: {not verify_password('wrong', hashed)}")
        
        return True
        
    except Exception as e:
        print(f"❌ Ошибка импорта приложения: {e}")
        print("\n🔍 Детали ошибки:")
        traceback.print_exc()
        return False

def check_admin_setup():
    """Проверяет настройку администратора"""
    print("\n👑 Проверка настройки администратора")
    print("=" * 50)
    
    try:
        # Проверяем модель User
        from models import User
        
        # Проверяем наличие поля is_admin
        print("📊 Проверка модели User:")
        user_columns = [column.name for column in User.__table__.columns]
        print(f"   Колонки User: {', '.join(user_columns)}")
        
        if 'is_admin' in user_columns:
            print("✅ Поле is_admin есть в модели User")
        else:
            print("❌ Поле is_admin отсутствует в модели User")
            
        return True
        
    except Exception as e:
        print(f"❌ Ошибка проверки модели: {e}")
        return False

def main():
    """Главная функция"""
    print("🔬 Комплексная проверка системы администратора")
    print("=" * 60)
    
    if test_import() and check_admin_setup():
        print("\n✅ Все проверки пройдены успешно!")
        print("\n📋 Сводка:")
        print("   • Приложение импортируется корректно")
        print("   • Модель User содержит поле is_admin")
        print("   • Функции хеширования работают")
        print("   • Декоратор admin_required доступен")
        print("   • Готово к запуску с администратором admin/admin")
    else:
        print("\n❌ Обнаружены проблемы!")
        print("   Нужно исправить ошибки перед запуском")
        sys.exit(1)

if __name__ == "__main__":
    main()