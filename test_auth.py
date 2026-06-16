#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Тестовый скрипт для проверки новых роутов авторизации
"""

print("=" * 60)
print("ПРОВЕРКА РОУТОВ АВТОРИЗАЦИИ")
print("=" * 60)

# Импортируем Flask app
try:
    from app import app
    print("[OK] app.py успешно импортирован")
except Exception as e:
    print(f"[ERROR] Ошибка импорта app.py: {e}")
    exit(1)

# Проверяем наличие новых роутов
routes_to_check = [
    '/login',
    '/register',
    '/logout',
    '/profile'
]

print("\nПроверка зарегистрированных роутов:")
print("-" * 60)

available_routes = []
for rule in app.url_map.iter_rules():
    available_routes.append(str(rule))

for route in routes_to_check:
    if any(route in r for r in available_routes):
        print(f"[OK] {route:<20} - найден")
    else:
        print(f"[ERROR] {route:<20} - НЕ найден")

print("\nПроверка шаблонов:")
print("-" * 60)

import os

templates_to_check = [
    'templates/login.html',
    'templates/register.html',
    'templates/profile.html'
]

for template in templates_to_check:
    if os.path.exists(template):
        size = os.path.getsize(template)
        print(f"[OK] {template:<30} - {size:>6} bytes")
    else:
        print(f"[ERROR] {template:<30} - НЕ найден")

print("\n" + "=" * 60)
print("ПРОВЕРКА ЗАВЕРШЕНА")
print("=" * 60)

print("\nЗапустите приложение командой:")
print("   python app.py")
print("\nДоступные страницы:")
print("   http://localhost:5000/login      - Страница входа")
print("   http://localhost:5000/register   - Страница регистрации")
print("   http://localhost:5000/profile    - Страница профиля")
print("\n" + "=" * 60)
