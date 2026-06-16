from flask import Flask, render_template, request, redirect, url_for, flash, jsonify, make_response, session
import json
import os
import hashlib
from datetime import datetime, timedelta, timezone
import threading
import time
from llm_helper import OllamaHelper
import re
import qrcode
import io
import base64

# Импорты для новой архитектуры
from models import db, Paste, User, Tag, AppStats
from storage import MinioStorage
from config import get_config
from admin_helpers import admin_required

# ЗАПУСК МИГРАЦИЙ ПРИ ИМПОРТЕ - это гарантирует, что поле is_admin будет добавлено ДО любых операций
try:
    print("\n" + "=" * 70)
    print("🚀 ЗАПУСК МИГРАЦИЙ ПРИ СТАРТЕ ПРИЛОЖЕНИЯ")
    print("=" * 70)
    
    # Создаем временное приложение для миграций
    temp_app = Flask(__name__)
    temp_app.config.from_object(get_config())
    db.init_app(temp_app)
    
    with temp_app.app_context():
        # 1. Создаем таблицы
        db.create_all()
        print("✅ Таблицы созданы/проверены")
        
        # 2. Добавляем поле is_admin если его нет
        from sqlalchemy import text
        try:
            # Пробуем добавить поле с IF NOT EXISTS
            db.session.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE
            """))
            db.session.commit()
            print("✅ Поле is_admin добавлено/проверено (IF NOT EXISTS)")
        except Exception as e:
            if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                print("✅ Поле is_admin уже существует")
            else:
                # Пробуем простой ALTER TABLE
                try:
                    db.session.execute(text("""
                        ALTER TABLE users 
                        ADD COLUMN is_admin BOOLEAN DEFAULT FALSE
                    """))
                    db.session.commit()
                    print("✅ Поле is_admin добавлено (простой ALTER TABLE)")
                except Exception as e2:
                    if "already exists" in str(e2).lower() or "duplicate column" in str(e2).lower():
                        print("✅ Поле is_admin уже существует")
                    else:
                        print(f"⚠️ Не удалось добавить поле is_admin: {e2}")
        
        # 3. Создаем администратора если его нет
        import secrets
        
        def hash_password(password):
            """Хеширует пароль с солью"""
            salt = secrets.token_hex(16)
            password_hash = hashlib.sha256((password + salt).encode()).hexdigest()
            return f"{salt}${password_hash}"
        
        # Проверяем существование пользователя admin
        result = db.session.execute(text("SELECT username FROM users WHERE username = 'admin'")).fetchone()
        
        if not result:
            print("👑 Создаю администратора admin/admin...")
            password_hash = hash_password('admin')
            
            try:
                db.session.execute(text("""
                    INSERT INTO users (username, email, password_hash, is_active, is_admin, created_at) 
                    VALUES ('admin', 'admin@localhost', :password_hash, true, true, NOW())
                """), {'password_hash': password_hash})
                db.session.commit()
                print("✅ Администратор успешно создан!")
            except Exception as e:
                print(f"⚠️ Ошибка при создании администратора: {e}")
        else:
            print("✅ Пользователь admin уже существует")
            
            # Обновляем до администратора
            try:
                db.session.execute(text("""
                    UPDATE users 
                    SET is_admin = true 
                    WHERE username = 'admin'
                """))
                db.session.commit()
                print("✅ Пользователь admin обновлен до администратора!")
            except Exception as e:
                print(f"⚠️ Не удалось обновить до администратора: {e}")
    
    print("✅ МИГРАЦИИ УСПЕШНО ЗАВЕРШЕНЫ")
    print("=" * 70 + "\n")
    
except Exception as e:
    print(f"❌ ОШИБКА ПРИ ЗАПУСКЕ МИГРАЦИЙ: {e}")
    print("⚠️ Приложение продолжит работу, но возможны проблемы с админскими функциями")
    print("=" * 70 + "\n")

# Создаем основное приложение
app = Flask(__name__)

# Загружаем конфигурацию
app.config.from_object(get_config())

# Инициализация расширений
db.init_app(app)

# Инициализация MinIO
storage = MinioStorage()

# Инициализация AI-помощника
ai_helper = OllamaHelper()

# Импорт для хеширования паролей
import hashlib
import secrets
import string

# Функция для хеширования паролей
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

def has_is_admin_field():
    """Проверяет, существует ли поле is_admin в таблице users"""
    try:
        from sqlalchemy import text
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'users' AND column_name = 'is_admin'
        """)).fetchone()
        return result is not None
    except:
        return False

def get_user_by_username_or_email(email_or_username):
    """Безопасно получает пользователя по email или username"""
    from models import User
    from sqlalchemy import text
    
    if has_is_admin_field():
        # Поле is_admin существует, можно использовать модель User
        try:
            return User.query.filter((User.email == email_or_username) | (User.username == email_or_username)).first()
        except Exception as e:
            print(f"⚠️ Ошибка при использовании модели User: {e}")
            # Fallback к raw SQL
    
    # Используем raw SQL без поля is_admin
    try:
        sql = text("""
            SELECT id, username, email, password_hash, is_active, created_at
            FROM users 
            WHERE email = :email OR username = :username
            LIMIT 1
        """)
        
        result = db.session.execute(sql, {
            'email': email_or_username,
            'username': email_or_username
        }).fetchone()
        
        if result:
            # Создаем временный объект пользователя
            class TempUser:
                def __init__(self, row):
                    self.id = row[0]
                    self.username = row[1]
                    self.email = row[2]
                    self.password_hash = row[3]
                    self.is_active = row[4]
                    self.created_at = row[5]
                    self.is_admin = False  # По умолчанию не администратор
            
            return TempUser(result)
    except Exception as e:
        print(f"❌ Ошибка при получении пользователя: {e}")
    
    return None

def get_user_by_username(username):
    """Безопасно получает пользователя по username"""
    return get_user_by_username_or_email(username)

# Текущая сессия (упрощенная версия)
current_user = {'logged_in': False, 'username': None, 'email': None, 'is_admin': False}

# Регистрируем фильтр nl2br для преобразования переносов строк в HTML
@app.template_filter('nl2br')
def nl2br_filter(text):
    """Преобразует переносы строк в HTML-теги <br>"""
    if text is None:
        return ''
    return text.replace('\n', '<br>')

# Контекстный процессор для передачи current_user в шаблоны
@app.context_processor
def inject_user():
    # Восстанавливаем состояние пользователя из сессии Flask при необходимости
    if not current_user['logged_in'] and session.get('user_logged_in'):
        current_user['logged_in'] = session.get('user_logged_in', False)
        current_user['username'] = session.get('user_username')
        current_user['email'] = session.get('user_email')
        current_user['is_admin'] = session.get('user_is_admin', False)
    
    return dict(current_user=current_user)

# Инициализация приложения уже выполнена при импорте модуля
# Поле is_admin уже добавлено в базу данных и администратор создан

def cleanup_expired_pastes():
    """Удаляет истекшие пасты из БД и MinIO"""
    while True:
        try:
            with app.app_context():
                # Находим истекшие пасты (не помеченные как истекшие)
                expired_pastes = Paste.query.filter(
                    Paste.expires_at < datetime.now(timezone.utc),
                    Paste.is_expired == False
                ).all()
                
                # Также находим пасты, помеченные как истекшие более 24 часов назад
                old_expired_pastes = Paste.query.filter(
                    Paste.is_expired == True,
                    Paste.expires_at < datetime.now(timezone.utc) - timedelta(hours=24)
                ).all()
                
                # Объединяем списки для удаления
                pastes_to_delete = expired_pastes + old_expired_pastes
                
                deleted_count = 0
                for paste in pastes_to_delete:
                    try:
                        # Удаляем содержимое из MinIO
                        storage.delete_paste_content(paste.id, paste.content_hash)
                        
                        # Удаляем метаданные из MinIO
                        try:
                            storage.delete_paste_metadata(paste.id)
                        except:
                            pass  # Игнорируем ошибки при удалении метаданных
                        
                        # Удаляем пасту из БД
                        db.session.delete(paste)
                        deleted_count += 1
                        
                    except Exception as e:
                        print(f"Ошибка при удалении пасты {paste.id}: {e}")
                        # Если не удалось удалить, помечаем как истекшую
                        paste.is_expired = True
                
                if pastes_to_delete:
                    try:
                        db.session.commit()
                        print(f"✅ Удалено {deleted_count} истекших паст, {len(pastes_to_delete) - deleted_count} помечено как истекшие")
                    except Exception as e:
                        db.session.rollback()
                        print(f"❌ Ошибка при сохранении в БД: {e}")
                
            time.sleep(60)  # Проверяем каждую минуту
            
        except Exception as e:
            print(f"❌ Ошибка при очистке паст: {e}")
            time.sleep(60)

# Запуск потока очистки в фоне (только при запуске приложения)
cleanup_thread = None

def get_or_create_stat(key, default_value=0):
    """Получает или создает статистику по ключу"""
    stat = AppStats.query.filter_by(key=key).first()
    if not stat:
        stat = AppStats(key=key, value=default_value)
        db.session.add(stat)
        db.session.commit()
    return stat

def increment_stat(key, increment=1):
    """Увеличивает статистику по ключу"""
    stat = get_or_create_stat(key)
    stat.value += increment
    stat.updated_at = datetime.now(timezone.utc)
    db.session.commit()
    return stat.value

def get_stat(key, default_value=0):
    """Получает значение статистики по ключу"""
    stat = AppStats.query.filter_by(key=key).first()
    return stat.value if stat else default_value

@app.route('/')
def index():
    """Главная страница"""
    try:
        # Получаем недавние пасты из БД (только публичные и не истекшие)
        recent_pastes = Paste.query.filter_by(is_expired=False, is_private=False).order_by(
            Paste.created_at.desc()
        ).limit(5).all()
        
        # Проверяем истечение паст и обновляем их статус
        expired_pastes_ids = []
        for paste in recent_pastes:
            if paste.expires_at and paste.expires_at < datetime.now(timezone.utc):
                paste.is_expired = True
                expired_pastes_ids.append(paste.id)
        
        # Сохраняем изменения в БД если есть истекшие пасты
        if expired_pastes_ids:
            db.session.commit()
            print(f"Пасты {expired_pastes_ids} помечены как истекшие на главной странице")
        
        # Загружаем содержимое для каждой пасты
        for paste in recent_pastes:
            try:
                paste.content = storage.get_paste_content(paste.id, paste.content_hash)
                if paste.content is None:
                    paste.content = "Ошибка загрузки содержимого"
            except Exception as e:
                print(f"Ошибка при загрузке содержимого пасты {paste.id}: {e}")
                paste.content = "Ошибка загрузки содержимого"
        
        # Получаем статистику для главной страницы (только публичные пасты)
        total_pastes_ever = get_stat('total_pastes_ever')  # Общее количество паст за все время
        active_pastes = Paste.query.filter_by(is_expired=False, is_private=False).count()
        expired_pastes = Paste.query.filter_by(is_expired=True, is_private=False).count()
        
        # Пасты за последние 7 дней (только публичные)
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        pastes_this_week = Paste.query.filter(
            Paste.created_at >= week_ago,
            Paste.is_private == False
        ).count()
        
        stats = {
            'total_pastes': total_pastes_ever,  # Используем общий счетчик
            'active_pastes': active_pastes,
            'expired_pastes': expired_pastes,
            'pastes_this_week': pastes_this_week
        }
        
        return render_template('index.html', recent_pastes=recent_pastes, stats=stats)
    except Exception as e:
        print(f"Ошибка при загрузке главной страницы: {e}")
        return render_template('index.html', recent_pastes=[], stats={
            'total_pastes': 0,
            'active_pastes': 0,
            'expired_pastes': 0,
            'pastes_this_week': 0
        })

@app.route('/create', methods=['GET', 'POST'])
def create_paste():
    """Страница создания пасты"""
    if request.method == 'POST':
        title = request.form.get('title', '').strip()
        content = request.form.get('content', '').strip()
        language = request.form.get('language', 'text')
        lifetime = float(request.form.get('lifetime', 1440))
        is_private = request.form.get('is_private') == 'on'
        secret_key = request.form.get('secret_key', '').strip()
        
        if not title or not content:
            flash('Заполните все обязательные поля', 'error')
            return redirect(url_for('create_paste'))
        
        try:
            # Сначала создаем hash содержимого
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            # Создаем новую пасту в БД с уже известным hash
            new_paste = Paste(
                 title=title,
                 content_hash=content_hash,  # Устанавливаем hash сразу
                 language=language,
                 lifetime=lifetime,
                 is_private=is_private,
                 tags=[]  # Пустой массив тегов
             )
            
            # Если паста приватная, устанавливаем секретный ключ
            if is_private:
                if secret_key:
                    new_paste.secret_key = secret_key
                else:
                    new_paste.secret_key = new_paste.generate_secret_key()
            
            # Устанавливаем время истечения если указан срок
            if lifetime > 0:
                new_paste.expires_at = datetime.now(timezone.utc) + timedelta(minutes=lifetime)
            
            # Сохраняем в БД
            db.session.add(new_paste)
            db.session.flush()
            
            # Сохраняем содержимое в MinIO
            storage.save_paste_content(new_paste.id, content)
            
            # Сохраняем метаданные в MinIO
            metadata = {
                'title': title,
                'language': language,
                'lifetime': lifetime,
                'is_private': is_private,
                'created_at': new_paste.created_at.isoformat()
            }
            storage.save_paste_metadata(new_paste.id, metadata)
            
            # Финализируем сохранение
            db.session.commit()
            
            # Увеличиваем счетчик общего количества паст
            increment_stat('total_pastes_ever')
            
            if is_private:
                # Для приватных паст показываем секретную ссылку
                secret_url = url_for('view_secret_paste', secret_key=new_paste.secret_key, _external=True)
                flash(f'Приватная паста успешно создана! Секретная ссылка: {secret_url}', 'success')
                return redirect(url_for('view_secret_paste', secret_key=new_paste.secret_key))
            else:
                flash('Паста успешно создана!', 'success')
                return redirect(url_for('view_paste', paste_id=new_paste.id))
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при создании пасты: {e}")
            flash(f'Ошибка при создании пасты: {e}', 'error')
            return redirect(url_for('create_paste'))
    
    return render_template('create.html')

@app.route('/paste/<int:paste_id>')
def view_paste(paste_id):
    """Страница просмотра пасты"""
    try:
        # Получаем пасту из БД
        paste = Paste.query.get_or_404(paste_id)
        
        # Проверяем, не является ли паста приватной
        if paste.is_private:
            flash('Эта паста является приватной и доступна только по секретной ссылке', 'error')
            return redirect(url_for('index'))
        
        # Проверяем, не истекла ли паста
        if paste.expires_at and paste.expires_at < datetime.now(timezone.utc):
            # Помечаем как истекшую если еще не помечена
            if not paste.is_expired:
                paste.is_expired = True
                db.session.commit()
                print(f"Паста {paste_id} помечена как истекшая при попытке просмотра")
            
            flash('Паста истекла', 'error')
            return redirect(url_for('index'))
        
        if paste.is_expired:
            flash('Паста истекла', 'error')
            return redirect(url_for('index'))
        
        # Получаем содержимое из MinIO
        try:
            content = storage.get_paste_content(paste.id, paste.content_hash)
            if content is None:
                content = "Ошибка загрузки содержимого"
        except Exception as e:
            print(f"Ошибка при загрузке содержимого из MinIO: {e}")
            content = "Ошибка загрузки содержимого"
        
        # Увеличиваем счетчик просмотров
        paste.views_count += 1
        db.session.commit()
        
        return render_template('view.html', paste=paste, content=content)
        
    except Exception as e:
        print(f"Ошибка при просмотре пасты: {e}")
        flash('Ошибка при загрузке пасты', 'error')
        return redirect(url_for('index'))

@app.route('/secret/<secret_key>')
def view_secret_paste(secret_key):
    """Страница просмотра приватной пасты по секретному ключу"""
    try:
        # Получаем пасту по секретному ключу
        paste = Paste.query.filter_by(secret_key=secret_key, is_private=True).first()
        
        if not paste:
            flash('Приватная паста не найдена или ключ неверный', 'error')
            return redirect(url_for('index'))
        
        # Проверяем, не истекла ли паста
        if paste.expires_at and paste.expires_at < datetime.now(timezone.utc):
            # Помечаем как истекшую если еще не помечена
            if not paste.is_expired:
                paste.is_expired = True
                db.session.commit()
                print(f"Приватная паста {paste.id} помечена как истекшая при попытке просмотра")
            
            flash('Приватная паста истекла', 'error')
            return redirect(url_for('index'))
        
        if paste.is_expired:
            flash('Приватная паста истекла', 'error')
            return redirect(url_for('index'))
        
        # Получаем содержимое из MinIO
        try:
            content = storage.get_paste_content(paste.id, paste.content_hash)
            if content is None:
                content = "Ошибка загрузки содержимого"
        except Exception as e:
            print(f"Ошибка при загрузке содержимого приватной пасты {paste.id}: {e}")
            content = "Ошибка загрузки содержимого"
        
        # Увеличиваем счетчик просмотров
        paste.views_count += 1
        db.session.commit()
        
        return render_template('view.html', paste=paste, content=content)
        
    except Exception as e:
        print(f"Ошибка при просмотре приватной пасты: {e}")
        flash('Ошибка при загрузке приватной пасты', 'error')
        return redirect(url_for('index'))

@app.route('/paste/<int:paste_id>/delete', methods=['POST'])
def delete_paste(paste_id):
    """Удаление пасты"""
    try:
        paste = Paste.query.get_or_404(paste_id)
        
        # Проверяем, не является ли паста приватной
        if paste.is_private:
            return jsonify({'success': False, 'error': 'Приватные пасты нельзя удалить через обычную ссылку'}), 403
        
        # Удаляем содержимое из MinIO
        storage.delete_paste_content(paste.id, paste.content_hash)
        
        # Удаляем из БД
        db.session.delete(paste)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Паста успешно удалена'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при удалении пасты: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/secret/<secret_key>/delete', methods=['POST'])
def delete_secret_paste(secret_key):
    """Удаление приватной пасты по секретному ключу"""
    try:
        paste = Paste.query.filter_by(secret_key=secret_key, is_private=True).first()
        
        if not paste:
            return jsonify({'success': False, 'error': 'Приватная паста не найдена или ключ неверный'}), 404
        
        # Удаляем содержимое из MinIO
        storage.delete_paste_content(paste.id, paste.content_hash)
        
        # Удаляем из БД
        db.session.delete(paste)
        db.session.commit()
        
        return jsonify({'success': True, 'message': 'Приватная паста успешно удалена'})
        
    except Exception as e:
        db.session.rollback()
        print(f"Ошибка при удалении приватной пасты: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/recent')
def recent_pastes():
    """Страница недавних паст"""
    try:
        # Получаем параметры поиска и фильтрации
        search_query = request.args.get('search', '').strip()
        category_filter = request.args.get('category', '').strip()
        
        # Базовый запрос для паст (только публичные и не истекшие)
        query = Paste.query.filter_by(is_expired=False, is_private=False)
        
        # Применяем фильтр по категории
        if category_filter:
            query = query.filter(Paste.language == category_filter)
        
        # Получаем все пасты для поиска по содержимому
        all_pastes = query.order_by(Paste.created_at.desc()).all()
        
        # Загружаем содержимое для каждой пасты
        for paste in all_pastes:
            try:
                paste.content = storage.get_paste_content(paste.id, paste.content_hash)
                if paste.content is None:
                    paste.content = "Ошибка загрузки содержимого"
            except Exception as e:
                print(f"Ошибка при загрузке содержимого пасты {paste.id}: {e}")
                paste.content = "Ошибка загрузки содержимого"
        
        # Применяем поиск по названию и содержимому
        if search_query:
            filtered_pastes = []
            search_lower = search_query.lower()
            for paste in all_pastes:
                # Поиск по названию
                if search_lower in paste.title.lower():
                    filtered_pastes.append(paste)
                    continue
                
                # Поиск по содержимому (если содержимое доступно)
                if paste.content and search_lower in paste.content.lower():
                    filtered_pastes.append(paste)
                    continue
            pastes = filtered_pastes
        else:
            pastes = all_pastes
        
        # Проверяем истечение паст и обновляем их статус
        expired_pastes_ids = []
        for paste in pastes:
            if paste.expires_at and paste.expires_at < datetime.now(timezone.utc):
                paste.is_expired = True
                expired_pastes_ids.append(paste.id)
        
        # Сохраняем изменения в БД если есть истекшие пасты
        if expired_pastes_ids:
            db.session.commit()
            print(f"Пасты {expired_pastes_ids} помечены как истекшие")
        
        # Получаем статистику для страницы недавних паст (только публичные)
        total_pastes_ever = get_stat('total_pastes_ever')  # Общее количество паст за все время
        active_pastes = Paste.query.filter_by(is_expired=False, is_private=False).count()
        expired_pastes = Paste.query.filter_by(is_expired=True, is_private=False).count()
        
        # Пасты за последние 7 дней (только публичные)
        week_ago = datetime.now(timezone.utc) - timedelta(days=7)
        pastes_this_week = Paste.query.filter(
            Paste.created_at >= week_ago,
            Paste.is_private == False
        ).count()
        
        # Подсчитываем уникальные категории (только публичные)
        categories = db.session.query(Paste.language).filter_by(is_private=False).distinct().count()
        
        # Получаем список всех доступных категорий для фильтра (только публичные)
        available_categories = db.session.query(Paste.language).filter_by(is_private=False).distinct().all()
        category_list = [cat[0] for cat in available_categories if cat[0]]
        
        stats = {
            'total_pastes': total_pastes_ever,  # Используем общий счетчик
            'active_pastes': active_pastes,
            'expired_pastes': expired_pastes,
            'pastes_this_week': pastes_this_week,
            'categories': categories
        }
        
        return render_template('recent.html', 
                             pastes=pastes, 
                             stats=stats, 
                             search_query=search_query,
                             category_filter=category_filter,
                             available_categories=category_list)
        
    except Exception as e:
        print(f"Ошибка при загрузке недавних паст: {e}")
        return render_template('recent.html', 
                             pastes=[], 
                             stats={
                                 'total_pastes': 0,
                                 'active_pastes': 0,
                                 'expired_pastes': 0,
                                 'pastes_this_week': 0,
                                 'categories': 0
                             },
                             search_query='',
                             category_filter='',
                             available_categories=[])

@app.route('/login', methods=['GET', 'POST'])
def login():
    """Страница входа"""
    if request.method == 'POST':
        email_or_username = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()

        # Используем безопасную функцию для получения пользователя
        user = get_user_by_username_or_email(email_or_username)
        
        if user and verify_password(password, user.password_hash):
            # Успешный вход - обновляем текущую сессию
            current_user['logged_in'] = True
            current_user['username'] = user.username
            current_user['email'] = user.email
            
            # Безопасно получаем is_admin (может отсутствовать)
            try:
                is_admin = getattr(user, 'is_admin', False)
            except:
                is_admin = False
                
            current_user['is_admin'] = is_admin
            
            # Сохраняем в сессии Flask для admin_required
            session['user_logged_in'] = True
            session['user_username'] = user.username
            session['user_email'] = user.email
            session['user_is_admin'] = is_admin
            session['user_id'] = getattr(user, 'id', None)
            
            # Специальное сообщение для администратора
            if is_admin:
                flash(f'Добро пожаловать, АДМИНИСТРАТОР {user.username}!', 'success')
            else:
                flash(f'Добро пожаловать, {user.username}!', 'success')
            
            return redirect(url_for('profile'))
        else:
            flash('Неверный логин или пароль', 'error')
            return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    """Страница регистрации"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '').strip()
        password_confirm = request.form.get('password_confirm', '').strip()

        # Валидация
        if not username or not email or not password:
            flash('Заполните все обязательные поля', 'error')
            return redirect(url_for('register'))

        if password != password_confirm:
            flash('Пароли не совпадают', 'error')
            return redirect(url_for('register'))

        if len(password) < 8:
            flash('Пароль должен содержать минимум 8 символов', 'error')
            return redirect(url_for('register'))

        # Проверка существующего пользователя
        from models import User
        existing_user = User.query.filter((User.email == email) | (User.username == username)).first()
        if existing_user:
            if existing_user.email == email:
                flash('Пользователь с таким email уже существует', 'error')
            else:
                flash('Пользователь с таким именем уже существует', 'error')
            return redirect(url_for('register'))

        # Создаем нового пользователя
        try:
            hashed_password = hash_password(password)
            new_user = User(
                username=username,
                email=email,
                password_hash=hashed_password,
                is_active=True
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            flash(f'Регистрация успешна! Теперь вы можете войти.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            print(f"Ошибка при регистрации пользователя: {e}")
            flash('Ошибка при регистрации. Пожалуйста, попробуйте позже.', 'error')
            return redirect(url_for('register'))

    return render_template('register.html')

@app.route('/logout')
def logout():
    """Выход из системы"""
    # Очищаем текущую сессию
    current_user['logged_in'] = False
    current_user['username'] = None
    current_user['email'] = None
    current_user['is_admin'] = False
    
    # Очищаем сессию Flask
    session.pop('user_logged_in', None)
    session.pop('user_username', None)
    session.pop('user_email', None)
    session.pop('user_is_admin', None)
    session.pop('user_id', None)
    
    flash('Вы успешно вышли из системы', 'success')
    return redirect(url_for('index'))

@app.route('/profile')
def profile():
    """Страница профиля пользователя"""
    if not current_user['logged_in']:
        flash('Необходимо войти в систему', 'error')
        return redirect(url_for('login'))

    return render_template('profile.html', user=current_user)

@app.route('/admin')
@admin_required
def admin_panel():
    """Административная панель"""
    # Получаем статистику
    total_users = User.query.count()
    total_pastes = Paste.query.count()
    total_pastes_ever = get_or_create_stat('total_pastes_ever', 0)
    
    # Получаем последние 10 пользователей
    recent_users = User.query.order_by(User.created_at.desc()).limit(10).all()
    
    # Получаем последние 10 паст
    recent_pastes = Paste.query.order_by(Paste.created_at.desc()).limit(10).all()
    
    # Получаем статистику по языкам
    from sqlalchemy import func
    language_stats = db.session.query(
        Paste.language, func.count(Paste.id).label('count')
    ).group_by(Paste.language).order_by(func.count(Paste.id).desc()).all()
    
    return render_template('admin_panel.html',
                         user=current_user,
                         total_users=total_users,
                         total_pastes=total_pastes,
                         total_pastes_ever=total_pastes_ever,
                         recent_users=recent_users,
                         recent_pastes=recent_pastes,
                         language_stats=language_stats)

@app.route('/admin/users')
@admin_required
def admin_users():
    """Управление пользователями"""
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin_users.html', users=users, user=current_user)

@app.route('/admin/pastes')
@admin_required
def admin_pastes():
    """Управление пастами"""
    pastes = Paste.query.order_by(Paste.created_at.desc()).all()
    return render_template('admin_pastes.html', pastes=pastes, user=current_user)

@app.route('/admin/stats')
@admin_required
def admin_stats():
    """Статистика системы"""
    # Основная статистика
    total_users = User.query.count()
    total_pastes = Paste.query.count()
    total_pastes_ever = get_or_create_stat('total_pastes_ever', 0)
    
    # Статистика по дням (последние 7 дней)
    from sqlalchemy import func, cast, Date
    daily_stats = db.session.query(
        cast(Paste.created_at, Date).label('date'),
        func.count(Paste.id).label('count')
    ).group_by(cast(Paste.created_at, Date)).order_by(cast(Paste.created_at, Date).desc()).limit(7).all()
    
    # Статистика по языкам
    language_stats = db.session.query(
        Paste.language, func.count(Paste.id).label('count')
    ).group_by(Paste.language).order_by(func.count(Paste.id).desc()).all()
    
    # Статистика по времени жизни
    lifetime_stats = db.session.query(
        Paste.lifetime, func.count(Paste.id).label('count')
    ).group_by(Paste.lifetime).order_by(Paste.lifetime).all()
    
    return render_template('admin_stats.html',
                         user=current_user,
                         total_users=total_users,
                         total_pastes=total_pastes,
                         total_pastes_ever=total_pastes_ever,
                         daily_stats=daily_stats,
                         language_stats=language_stats,
                         lifetime_stats=lifetime_stats)

@app.route('/ai')
def ai_helper_page():
    """Страница AI-помощника"""
    return render_template('ai_helper.html')

# === API ЭНДПОИНТЫ ДЛЯ AI-ПОМОЩНИКА ===

@app.route('/ai/status')
def ai_status():
    """Статус AI-помощника"""
    return jsonify({
        'available': ai_helper.is_available(),
        'model': ai_helper.model,
        'models_count': len(ai_helper.get_available_models())
    })

@app.route('/ai/models')
def ai_models():
    """Список доступных моделей"""
    return jsonify({
        'models': ai_helper.get_available_models(),
        'current': ai_helper.model
    })

@app.route('/api/search')
def api_search():
    """API для живого поиска паст"""
    try:
        search_query = request.args.get('q', '').strip()
        category_filter = request.args.get('category', '').strip()
        
        # Базовый запрос (только публичные и не истекшие)
        query = Paste.query.filter_by(is_expired=False, is_private=False)
        
        # Применяем фильтр по категории
        if category_filter:
            query = query.filter(Paste.language == category_filter)
        
        # Получаем пасты
        pastes = query.order_by(Paste.created_at.desc()).limit(100).all()
        
        # Загружаем содержимое для поиска
        for paste in pastes:
            try:
                paste.content = storage.get_paste_content(paste.id, paste.content_hash)
                if paste.content is None:
                    paste.content = ""
            except Exception as e:
                paste.content = ""
        
        # Применяем поиск
        if search_query:
            search_lower = search_query.lower()
            filtered_pastes = []
            for paste in pastes:
                if (search_lower in paste.title.lower() or 
                    (paste.content and search_lower in paste.content.lower())):
                    filtered_pastes.append(paste)
            pastes = filtered_pastes
        
        # Получаем актуальный список категорий из активных паст (только публичные)
        active_categories = db.session.query(Paste.language).filter_by(is_expired=False, is_private=False).distinct().all()
        category_list = [cat[0] for cat in active_categories if cat[0]]
        
        # Формируем результат
        result = []
        for paste in pastes:
            result.append({
                'id': paste.id,
                'title': paste.title,
                'language': paste.language,
                'lifetime': paste.lifetime,
                'created_at': paste.created_at.isoformat() if paste.created_at else None,
                'expires_at': paste.expires_at.isoformat() if paste.expires_at else None,
                'is_expired': paste.is_expired,
                'url': url_for('view_paste', paste_id=paste.id)
            })
        
        return jsonify({
            'pastes': result,
            'total': len(result),
            'categories': category_list
        })
        
    except Exception as e:
        print(f"Ошибка при поиске: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/api/categories')
def api_categories():
    """API для получения списка активных категорий"""
    try:
        # Получаем только активные категории (не истекшие и публичные пасты)
        active_categories = db.session.query(Paste.language).filter_by(is_expired=False, is_private=False).distinct().all()
        category_list = [cat[0] for cat in active_categories if cat[0]]
        
        return jsonify({
            'categories': category_list,
            'total': len(category_list)
        })
        
    except Exception as e:
        print(f"Ошибка при получении категорий: {e}")
        return jsonify({'error': str(e)}), 500

@app.route('/ai/set-model', methods=['POST'])
def ai_set_model():
    """Установка модели"""
    data = request.get_json()
    model_name = data.get('model')
    
    if ai_helper.set_model(model_name):
        return jsonify({'success': True, 'model': model_name})
    else:
        return jsonify({'success': False, 'error': 'Модель не найдена'}), 400

# === УНИВЕРСАЛЬНЫЕ МЕТОДЫ ГЕНЕРАЦИИ ===

@app.route('/ai/generate-text', methods=['POST'])
def ai_generate_text():
    """Универсальный эндпоинт для генерации текста"""
    data = request.get_json()
    
    if not ai_helper.is_available():
        return jsonify({'error': 'AI-сервер недоступен'}), 503
    
    text_type = data.get('type', 'general')
    topic = data.get('topic', '')
    max_tokens = int(data.get('max_tokens', 800))
    
    if not topic:
        return jsonify({'error': 'Тема не указана'}), 400
    
    try:
        if text_type == 'creative':
            style = data.get('style', 'общий')
            result = ai_helper.generate_creative_text(topic, style, max_tokens)
        elif text_type == 'business':
            text_type_business = data.get('business_type', 'описание')
            result = ai_helper.generate_business_text(topic, text_type_business, max_tokens)
        elif text_type == 'educational':
            level = data.get('level', 'средний')
            result = ai_helper.generate_educational_text(topic, level, max_tokens)
        elif text_type == 'story':
            genre = data.get('genre', 'общий')
            result = ai_helper.generate_story(genre, topic, max_tokens)
        elif text_type == 'article':
            style = data.get('style', 'информационный')
            result = ai_helper.generate_article(topic, style, max_tokens)
        elif text_type == 'social':
            platform = data.get('platform', 'общий')
            tone = data.get('tone', 'дружелюбный')
            result = ai_helper.generate_social_media_content(platform, topic, tone, max_tokens)
        elif text_type == 'poem':
            style = data.get('style', 'современный')
            result = ai_helper.generate_poem(topic, style, max_tokens)
        elif text_type == 'marketing':
            target_audience = data.get('target_audience', 'общая аудитория')
            result = ai_helper.generate_marketing_copy(topic, target_audience, max_tokens)
        elif text_type == 'email':
            purpose = data.get('purpose', 'общее')
            tone = data.get('tone', 'профессиональный')
            result = ai_helper.generate_email_template(purpose, tone, max_tokens)
        elif text_type == 'presentation':
            audience = data.get('audience', 'общая аудитория')
            result = ai_helper.generate_presentation_outline(topic, audience, max_tokens)
        else:
            # Общая генерация текста
            result = ai_helper.generate_text(topic, max_tokens)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'text': result['text'],
            'model': result['model'],
            'tokens_used': result['tokens_used'],
            'type': text_type
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации: {str(e)}'}), 500

# === СПЕЦИАЛИЗИРОВАННЫЕ МЕТОДЫ ДЛЯ КОДА ===

@app.route('/ai/generate-code', methods=['POST'])
def ai_generate_code():
    """Генерация кода (для обратной совместимости)"""
    data = request.get_json()
    
    if not ai_helper.is_available():
        return jsonify({'error': 'AI-сервер недоступен'}), 503
    
    language = data.get('language', 'python')
    description = data.get('description', '')
    max_tokens = int(data.get('max_tokens', 600))
    
    if not description:
        return jsonify({'error': 'Описание не указано'}), 400
    
    try:
        result = ai_helper.generate_code(language, description, max_tokens)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'text': result['text'],
            'model': result['model'],
            'tokens_used': result['tokens_used']
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации: {str(e)}'}), 500

@app.route('/ai/improve-code', methods=['POST'])
def ai_improve_code():
    """Улучшение кода"""
    data = request.get_json()
    
    if not ai_helper.is_available():
        return jsonify({'error': 'AI-сервер недоступен'}), 503
    
    code = data.get('code', '')
    language = data.get('language', 'python')
    description = data.get('description', '')
    max_tokens = int(data.get('max_tokens', 800))
    
    if not code:
        return jsonify({'error': 'Код не указан'}), 400
    
    try:
        result = ai_helper.improve_code(code, language, description, max_tokens)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'text': result['text'],
            'model': result['model'],
            'tokens_used': result['tokens_used']
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка улучшения: {str(e)}'}), 500

@app.route('/ai/explain-code', methods=['POST'])
def ai_explain_code():
    """Объяснение кода"""
    data = request.get_json()
    
    if not ai_helper.is_available():
        return jsonify({'error': 'AI-сервер недоступен'}), 503
    
    code = data.get('code', '')
    language = data.get('language', 'python')
    max_tokens = int(data.get('max_tokens', 600))
    
    if not code:
        return jsonify({'error': 'Код не указан'}), 400
    
    try:
        result = ai_helper.explain_code(code, language, max_tokens)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'text': result['text'],
            'model': result['model'],
            'tokens_used': result['tokens_used']
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка объяснения: {str(e)}'}), 500

@app.route('/ai/generate-docs', methods=['POST'])
def ai_generate_docs():
    """Генерация документации"""
    data = request.get_json()
    
    if not ai_helper.is_available():
        return jsonify({'error': 'AI-сервер недоступен'}), 503
    
    code = data.get('code', '')
    language = data.get('language', 'python')
    max_tokens = int(data.get('max_tokens', 500))
    
    if not code:
        return jsonify({'error': 'Код не указан'}), 400
    
    try:
        result = ai_helper.generate_documentation(code, language, max_tokens)
        
        if 'error' in result:
            return jsonify({'error': result['error']}), 500
        
        return jsonify({
            'success': True,
            'text': result['text'],
            'model': result['model'],
            'tokens_used': result['tokens_used']
        })
        
    except Exception as e:
        return jsonify({'error': f'Ошибка генерации документации: {str(e)}'}), 500

@app.route('/admin/cleanup', methods=['POST'])
def manual_cleanup():
    """Ручная очистка истекших паст"""
    try:
        with app.app_context():
            # Находим все истекшие пасты
            expired_pastes = Paste.query.filter(
                Paste.expires_at < datetime.now(timezone.utc)
            ).all()
            
            deleted_count = 0
            for paste in expired_pastes:
                try:
                    # Удаляем содержимое из MinIO
                    storage.delete_paste_content(paste.id, paste.content_hash)
                    
                    # Удаляем метаданные из MinIO
                    try:
                        storage.delete_paste_metadata(paste.id)
                    except:
                        pass
                    
                    # Удаляем пасту из БД
                    db.session.delete(paste)
                    deleted_count += 1
                    
                except Exception as e:
                    print(f"Ошибка при удалении пасты {paste.id}: {e}")
            
            if expired_pastes:
                db.session.commit()
                return jsonify({
                    'success': True,
                    'message': f'Удалено {deleted_count} истекших паст'
                })
            else:
                return jsonify({
                    'success': True,
                    'message': 'Истекших паст не найдено'
                })
                
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'Ошибка при очистке: {str(e)}'
        }), 500

def generate_qr_code(data, size=400):
    """Генерирует QR-код и возвращает его как base64 строку"""
    try:
        # Используем более высокий уровень коррекции ошибок для лучшего сканирования
        qr = qrcode.QRCode(
            version=None,  # Автоматический выбор версии
            error_correction=qrcode.constants.ERROR_CORRECT_H,  # Высокий уровень коррекции
            box_size=15,  # Увеличиваем размер блоков для лучшего сканирования
            border=4,  # Достаточная граница
        )
        qr.add_data(data)
        qr.make(fit=True)

        # Создаем изображение с использованием PIL для лучшего качества
        img = qr.make_image(fill_color="black", back_color="white")

        # Конвертируем в RGB если необходимо
        if img.mode != 'RGB':
            img = img.convert('RGB')

        # НЕ изменяем размер - используем оригинальный размер для лучшего качества
        # Это обеспечит четкие края и лучшее сканирование

        # Конвертируем в base64
        buffer = io.BytesIO()
        img.save(buffer, format='PNG', optimize=False, quality=100)  # Максимальное качество
        buffer.seek(0)

        img_base64 = base64.b64encode(buffer.getvalue()).decode()

        print(f"✅ QR-код сгенерирован для URL: {data[:50]}... (размер: {img.size})")

        return f"data:image/png;base64,{img_base64}"

    except Exception as e:
        print(f"❌ Ошибка генерации QR-кода: {e}")
        return None

@app.route('/paste/<int:paste_id>/qr')
def paste_qr_code(paste_id):
    """Генерирует QR-код для пасты"""
    try:
        paste = Paste.query.get_or_404(paste_id)
        
        # Проверяем, не является ли паста приватной
        if paste.is_private:
            return jsonify({'error': 'QR-код недоступен для приватных паст'}), 403
        
        # Проверяем, не истекла ли паста
        if paste.expires_at and paste.expires_at < datetime.now(timezone.utc):
            return jsonify({'error': 'QR-код недоступен для истекших паст'}), 403
        
        if paste.is_expired:
            return jsonify({'error': 'QR-код недоступен для истекших паст'}), 403
        
        # Генерируем URL для пасты
        paste_url = url_for('view_paste', paste_id=paste_id, _external=True)
        
        # Генерируем QR-код
        qr_code = generate_qr_code(paste_url)
        
        if qr_code:
            return jsonify({
                'success': True,
                'qr_code': qr_code,
                'url': paste_url,
                'title': paste.title
            })
        else:
            return jsonify({'error': 'Ошибка генерации QR-кода'}), 500
            
    except Exception as e:
        print(f"Ошибка при генерации QR-кода: {e}")
        return jsonify({'error': 'Ошибка при генерации QR-кода'}), 500

@app.route('/secret/<secret_key>/qr')
def secret_paste_qr_code(secret_key):
    """Генерирует QR-код для приватной пасты"""
    try:
        paste = Paste.query.filter_by(secret_key=secret_key, is_private=True).first()
        
        if not paste:
            return jsonify({'error': 'Приватная паста не найдена'}), 404
        
        # Проверяем, не истекла ли паста
        if paste.expires_at and paste.expires_at < datetime.now(timezone.utc):
            return jsonify({'error': 'QR-код недоступен для истекших паст'}), 403
        
        if paste.is_expired:
            return jsonify({'error': 'QR-код недоступен для истекших паст'}), 403
        
        # Генерируем URL для приватной пасты
        paste_url = url_for('view_secret_paste', secret_key=secret_key, _external=True)
        
        # Генерируем QR-код
        qr_code = generate_qr_code(paste_url)
        
        if qr_code:
            return jsonify({
                'success': True,
                'qr_code': qr_code,
                'url': paste_url,
                'title': paste.title
            })
        else:
            return jsonify({'error': 'Ошибка генерации QR-кода'}), 500
            
    except Exception as e:
        print(f"Ошибка при генерации QR-кода для приватной пасты: {e}")
        return jsonify({'error': 'Ошибка при генерации QR-кода'}), 500

def apply_admin_migration():
    """Применяет миграцию для добавления поля is_admin при запуске"""
    print("\n🔧 НАДЕЖНАЯ МИГРАЦИЯ ДЛЯ ПОЛЯ IS_ADMIN")
    print("-" * 50)
    
    try:
        from sqlalchemy import text
        
        # Шаг 1: Проверяем и добавляем поле is_admin
        print("📝 ШАГ 1: Проверка поля is_admin в таблице users")
        
        # Используем надежный подход с несколькими fallback
        migration_success = False
        
        # Способ 1: Пробуем информацию о схеме
        try:
            result = db.session.execute(text("""
                SELECT column_name 
                FROM information_schema.columns 
                WHERE table_name = 'users' AND column_name = 'is_admin'
            """)).fetchone()
            
            if result:
                print("✅ Поле is_admin уже существует в таблице users")
                migration_success = True
            else:
                print("❌ Поле is_admin НЕ найдено в таблице users")
                migration_success = False
                
        except Exception as e:
            print(f"⚠️ Не удалось проверить через information_schema: {e}")
            migration_success = False
        
        # Если поле не найдено, добавляем его
        if not migration_success:
            print("📝 Добавляю поле is_admin...")
            
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
                    print(f"✅ Поле is_admin успешно добавлено (способ: {method_name})!")
                    migration_success = True
                    break
                except Exception as e:
                    if "already exists" in str(e).lower() or "duplicate column" in str(e).lower():
                        print(f"✅ Поле is_admin уже существует (способ: {method_name})")
                        migration_success = True
                        break
                    else:
                        print(f"⚠️ Способ {method_name} не сработал: {e}")
            
            if not migration_success:
                print("❌ Не удалось добавить поле is_admin всеми способами")
                return False
        
        # Шаг 2: Проверяем и создаем администратора
        print("\n📝 ШАГ 2: Создание/проверка администратора admin/admin")
        
        # Проверяем существование пользователя admin
        admin_exists = db.session.execute(
            text("SELECT username FROM users WHERE username = 'admin'")
        ).fetchone()
        
        if not admin_exists:
            print("👑 Создаю администратора admin/admin...")
            
            password_hash = hash_password('admin')
            
            # Пробуем создать с полем is_admin
            try:
                db.session.execute(text("""
                    INSERT INTO users (username, email, password_hash, is_active, is_admin, created_at) 
                    VALUES ('admin', 'admin@localhost', :password_hash, true, true, NOW())
                """), {'password_hash': password_hash})
                db.session.commit()
                print("✅ Администратор успешно создан (с полем is_admin)!")
                print(f"   Логин: admin | Пароль: admin | Email: admin@localhost")
            except Exception as e:
                print(f"⚠️ Ошибка при создании с полем is_admin: {e}")
                print("📝 Пробую создать без поля is_admin...")
                
                try:
                    db.session.execute(text("""
                        INSERT INTO users (username, email, password_hash, is_active, created_at) 
                        VALUES ('admin', 'admin@localhost', :password_hash, true, NOW())
                    """), {'password_hash': password_hash})
                    db.session.commit()
                    print("✅ Администратор создан (без поля is_admin)!")
                    
                    # Обновляем до администратора
                    db.session.execute(text("""
                        UPDATE users 
                        SET is_admin = true 
                        WHERE username = 'admin'
                    """))
                    db.session.commit()
                    print("✅ Пользователь admin обновлен до администратора!")
                except Exception as e2:
                    print(f"❌ Ошибка при создании администратора: {e2}")
                    return False
        else:
            print("ℹ️ Пользователь admin уже существует")
            
            # Проверяем, является ли администратором
            try:
                result = db.session.execute(text("""
                    SELECT is_admin FROM users WHERE username = 'admin'
                """)).fetchone()
                
                if result and result[0]:
                    print("✅ Пользователь admin уже является администратором")
                else:
                    print("⚠️ Пользователь admin НЕ является администратором")
                    print("📝 Обновляю до администратора...")
                    
                    db.session.execute(text("""
                        UPDATE users 
                        SET is_admin = true 
                        WHERE username = 'admin'
                    """))
                    db.session.commit()
                    print("✅ Пользователь admin обновлен до администратора!")
            except Exception as e:
                print(f"⚠️ Ошибка при проверке статуса администратора: {e}")
                print("📝 Предполагаю, что пользователь не администратор и обновляю...")
                
                try:
                    db.session.execute(text("""
                        UPDATE users 
                        SET is_admin = true 
                        WHERE username = 'admin'
                    """))
                    db.session.commit()
                    print("✅ Пользователь admin обновлен до администратора!")
                except Exception as e2:
                    print(f"⚠️ Не удалось обновить до администратора: {e2}")
        
        # Шаг 3: Финальная проверка
        print("\n📝 ШАГ 3: Финальная проверка")
        
        try:
            admins = db.session.execute(text("""
                SELECT username, email, is_admin 
                FROM users 
                WHERE is_admin = true 
                ORDER BY created_at
            """)).fetchall()
            
            if admins:
                print("📋 Список администраторов:")
                for admin in admins:
                    status = "администратор" if admin[2] else "обычный пользователь"
                    print(f"   • {admin[0]} ({admin[1]}) - {status}")
            else:
                print("ℹ️ В базе нет пользователей с is_admin = true")
        except Exception as e:
            print(f"⚠️ Не удалось получить список администраторов: {e}")
        
        print("\n✅ МИГРАЦИЯ ЗАВЕРШЕНА УСПЕШНО!")
        return True
        
    except Exception as e:
        print(f"\n❌ КРИТИЧЕСКАЯ ОШИБКА: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == '__main__':
    # Инициализируем приложение (применяем миграции, создаем администратора)
    initialize_application()
    
    # Запуск потока очистки в фоне
    cleanup_thread = threading.Thread(target=cleanup_expired_pastes, daemon=True)
    cleanup_thread.start()
    print("Запущен поток очистки истекших паст")
    
    app.run(debug=True, host='0.0.0.0', port=5000)
