"""
Вспомогательные функции для администратора
"""

from functools import wraps
from flask import flash, redirect, url_for

def admin_required(f):
    """Декоратор для проверки прав администратора"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        from flask import session
        
        # Проверяем наличие информации о пользователе в сессии
        if not session.get('user_logged_in'):
            flash('Необходимо войти в систему', 'error')
            return redirect(url_for('login'))
        
        if not session.get('user_is_admin', False):
            flash('У вас нет прав администратора', 'error')
            return redirect(url_for('index'))
        
        return f(*args, **kwargs)
    return decorated_function