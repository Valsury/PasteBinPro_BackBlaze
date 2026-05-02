from flask_sqlalchemy import SQLAlchemy
from datetime import datetime, timezone
import uuid

db = SQLAlchemy()

class Paste(db.Model):
    __tablename__ = 'pastes'
    
    id = db.Column(db.Integer, primary_key=True)
    uuid = db.Column(db.String(36), unique=True, default=lambda: str(uuid.uuid4()))
    title = db.Column(db.String(255), nullable=False)
    content_hash = db.Column(db.String(64), nullable=False)
    language = db.Column(db.String(50), default='text')
    lifetime = db.Column(db.Float, default=1440)
    is_private = db.Column(db.Boolean, default=False)
    secret_key = db.Column(db.String(64), unique=True, nullable=True)  # Секретный ключ для приватных паст
    views_count = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    expires_at = db.Column(db.DateTime)
    is_expired = db.Column(db.Boolean, default=False)
    author_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    tags = db.Column(db.ARRAY(db.String), default=[])  # Массив строк для тегов
    
    def __repr__(self):
        return f'<Paste {self.id}: {self.title}>'
    
    def to_dict(self):
        """Преобразует объект в словарь для JSON"""
        return {
            'id': self.id,
            'uuid': self.uuid,
            'title': self.title,
            'language': self.language,
            'lifetime': self.lifetime,
            'is_private': self.is_private,
            'secret_key': self.secret_key,
            'views_count': self.views_count,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'is_expired': self.is_expired,
            'tags': self.tags
        }
    
    def get_remaining_time(self):
        """Возвращает оставшееся время жизни пасты в минутах"""
        if self.lifetime == 0 or not self.expires_at:
            return None
        
        now = datetime.now(timezone.utc)
        if now >= self.expires_at:
            return 0
        
        remaining = self.expires_at - now
        return remaining.total_seconds() / 60  # Возвращаем float для точности
    
    def get_remaining_time_formatted(self):
        """Возвращает отформатированное оставшееся время"""
        remaining_minutes = self.get_remaining_time()
        
        if remaining_minutes is None:
            return "Бессрочно"
        
        if remaining_minutes <= 0:
            return "Истекла"
        
        # Конвертируем в секунды для более точного расчета
        total_seconds = int(remaining_minutes * 60)
        
        if total_seconds < 60:
            # Меньше минуты - показываем в секундах
            return f"{total_seconds}с"
        elif total_seconds < 3600:
            # Меньше часа - показываем в минутах и секундах
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            if seconds == 0:
                return f"{minutes}м"
            else:
                return f"{minutes}м {seconds}с"
        elif total_seconds < 86400:
            # Меньше дня - показываем в часах, минутах и секундах
            hours = total_seconds // 3600
            remaining_seconds = total_seconds % 3600
            minutes = (remaining_seconds % 3600) // 60
            seconds = remaining_seconds % 60
            
            if minutes == 0 and seconds == 0:
                return f"{hours}ч"
            elif seconds == 0:
                return f"{hours}ч {minutes}м"
            else:
                return f"{hours}ч {minutes}м {seconds}с"
        else:
            # Больше дня - показываем в днях, часах, минутах
            days = total_seconds // 86400
            remaining_seconds = total_seconds % 86400
            hours = remaining_seconds // 3600
            minutes = (remaining_seconds % 3600) // 60
            
            if hours == 0 and minutes == 0:
                return f"{days}д"
            elif minutes == 0:
                return f"{days}д {hours}ч"
            else:
                return f"{days}д {hours}ч {minutes}м"
    
    def generate_secret_key(self):
        """Генерирует секретный ключ для приватной пасты"""
        import secrets
        import string
        
        # Генерируем случайный ключ из 32 символов
        alphabet = string.ascii_letters + string.digits
        return ''.join(secrets.choice(alphabet) for _ in range(32))
    
    def get_secret_url(self):
        """Возвращает секретную ссылку для приватной пасты"""
        if not self.is_private or not self.secret_key:
            return None
        return f"/secret/{self.secret_key}"

class User(db.Model):
    __tablename__ = 'users'
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    is_active = db.Column(db.Boolean, default=True)
    
    pastes = db.relationship('Paste', backref='author', lazy=True)
    
    def __repr__(self):
        return f'<User {self.username}>'

class Tag(db.Model):
    __tablename__ = 'tags'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<Tag {self.name}>'

class AppStats(db.Model):
    __tablename__ = 'app_stats'
    
    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Integer, default=0)
    updated_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    
    def __repr__(self):
        return f'<AppStats {self.key}: {self.value}>'
