#!/usr/bin/env python
"""
Скрипт для тестирования миграции
"""

import os
import sys
sys.path.append('.')
from flask import Flask
from sqlalchemy import text, inspect
from models import db

app = Flask(__name__)

# Загружаем конфигурацию
from config import get_config
app.config.from_object(get_config())

db.init_app(app)

with app.app_context():
    print('🔍 Проверяем структуру базы данных...')
    
    try:
        # Пробуем inspect
        inspector = inspect(db.engine)
        columns = inspector.get_columns('users')
        column_names = [col['name'] for col in columns]
        print(f'Колонки в таблице users: {column_names}')
        
        # Проверяем наличие is_admin
        is_admin_col = next((col for col in columns if col['name'] == 'is_admin'), None)
        print(f'Поле is_admin найдено: {is_admin_col is not None}')
        
        # Пробуем простой SQL запрос
        result = db.session.execute(text('''
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'is_admin'
        ''')).fetchone()
        print(f'SQL запрос нашел is_admin: {result is not None}')
        
        # Если поле не найдено, добавляем его
        if not is_admin_col and not result:
            print('📝 Добавляем поле is_admin...')
            try:
                db.session.execute(text('''
                    ALTER TABLE users 
                    ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE
                '''))
                db.session.commit()
                print('✅ Поле is_admin добавлено!')
            except Exception as e:
                print(f'❌ Ошибка при добавлении поля: {e}')
        
        # Проверяем существование пользователя admin
        result = db.session.execute(text("SELECT * FROM users WHERE username = 'admin'")).fetchone()
        print(f'Пользователь admin существует: {result is not None}')
        
    except Exception as e:
        print(f'❌ Ошибка при проверке: {e}')
        import traceback
        traceback.print_exc()