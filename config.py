import os
from dotenv import load_dotenv

# Загружаем переменные окружения из config.env
load_dotenv('config.env')

class Config:
    """Базовая конфигурация Flask приложения"""

    # Flask настройки
    SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')
    FLASK_ENV = os.getenv('FLASK_ENV', 'production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', '0').lower() in ('1', 'true', 'yes')

    # PostgreSQL настройки
    # Render автоматически устанавливает DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        'DATABASE_URL',
        'postgresql://pastebin_user:pastebin_password@localhost:5432/pastebin_db'
    )

    # Исправление для Render: postgres:// -> postgresql://
    if SQLALCHEMY_DATABASE_URI.startswith('postgres://'):
        SQLALCHEMY_DATABASE_URI = SQLALCHEMY_DATABASE_URI.replace('postgres://', 'postgresql://', 1)

    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        'pool_pre_ping': True,
        'pool_recycle': 300,
        'pool_size': 10,
        'max_overflow': 20
    }

    # S3-совместимое хранилище (MinIO/AWS S3/Cloudflare R2/DigitalOcean Spaces)
    S3_ENDPOINT = os.getenv('S3_ENDPOINT', os.getenv('MINIO_ENDPOINT', 'localhost:9000'))
    S3_ACCESS_KEY = os.getenv('S3_ACCESS_KEY', os.getenv('MINIO_ACCESS_KEY', 'minioadmin'))
    S3_SECRET_KEY = os.getenv('S3_SECRET_KEY', os.getenv('MINIO_SECRET_KEY', 'minioadmin123'))
    S3_BUCKET_NAME = os.getenv('S3_BUCKET_NAME', os.getenv('MINIO_BUCKET_NAME', 'pastes'))
    S3_SECURE = os.getenv('S3_SECURE', os.getenv('MINIO_SECURE', 'false')).lower() in ('true', '1', 'yes')
    S3_REGION = os.getenv('S3_REGION', 'us-east-1')

    # Обратная совместимость с MinIO
    MINIO_ENDPOINT = S3_ENDPOINT
    MINIO_ACCESS_KEY = S3_ACCESS_KEY
    MINIO_SECRET_KEY = S3_SECRET_KEY
    MINIO_BUCKET_NAME = S3_BUCKET_NAME
    MINIO_SECURE = S3_SECURE

    # LLM API настройки (замена Ollama)
    LLM_PROVIDER = os.getenv('LLM_PROVIDER', 'openrouter')
    LLM_API_KEY = os.getenv('LLM_API_KEY', '')
    LLM_MODEL = os.getenv('LLM_MODEL', 'mistralai/mistral-7b-instruct')
    LLM_BASE_URL = os.getenv('LLM_BASE_URL', 'http://localhost:11434/v1')

    # URL приложения
    APP_URL = os.getenv('APP_URL', 'http://localhost:5000')

    # Устаревшие настройки Ollama (для обратной совместимости)
    OLLAMA_HOST = os.getenv('OLLAMA_HOST', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama2')

class DevelopmentConfig(Config):
    """Конфигурация для разработки"""
    DEBUG = True
    FLASK_ENV = 'development'
    SQLALCHEMY_ECHO = True

class ProductionConfig(Config):
    """Конфигурация для продакшена"""
    DEBUG = False
    FLASK_ENV = 'production'
    SQLALCHEMY_ECHO = False

    # Дополнительные настройки безопасности для продакшена
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'

class TestingConfig(Config):
    """Конфигурация для тестирования"""
    TESTING = True
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

# Словарь конфигураций
config = {
    'development': DevelopmentConfig,
    'production': ProductionConfig,
    'testing': TestingConfig,
    'default': ProductionConfig  # По умолчанию используем production
}

def get_config():
    """Возвращает конфигурацию на основе переменной окружения"""
    config_name = os.getenv('FLASK_ENV', 'production')
    return config.get(config_name, config['default'])
