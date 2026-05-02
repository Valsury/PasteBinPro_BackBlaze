# 🚀 Руководство по установке PasteBin Pro

## 📋 Предварительные требования

### Системные требования
- **Windows 10/11** или **Linux/macOS**
- **Python 3.8+** (рекомендуется 3.11+)
- **Docker Desktop** с Docker Compose
- **Git** для клонирования репозитория

### Минимальные ресурсы
- **RAM**: 4 GB (рекомендуется 8 GB)
- **Диск**: 2 GB свободного места
- **CPU**: 2 ядра (рекомендуется 4+)

## 🔧 Пошаговая установка

### 1. Клонирование репозитория

```bash
git clone https://github.com/yourusername/pastebin-pro.git
cd pastebin-pro
```

### 2. Установка Python зависимостей

#### Создание виртуального окружения

**Windows:**
```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
```

**Linux/macOS:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

#### Установка зависимостей

**Основные зависимости:**
```bash
pip install Flask==2.3.3 python-dotenv==1.0.0 requests==2.31.0
pip install SQLAlchemy==2.0.21 Flask-SQLAlchemy==3.0.5
pip install minio==7.1.17 alembic==1.12.0
```

### 3. Установка PostgreSQL драйвера

#### 🐘 **Вариант 1: psycopg2-binary (рекомендуется)**

```bash
pip install psycopg2-binary
```

#### 🐘 **Вариант 2: Альтернативные источники (если psycopg2-binary не работает)**

**Для Windows:**
```bash
# Попробуйте более новую версию
pip install psycopg2-binary --upgrade

# Или установите из альтернативного источника
pip install --only-binary=all psycopg2-binary

# Или используйте conda (если установлен)
conda install psycopg2
```

**Для Linux:**
```bash
# Ubuntu/Debian
sudo apt-get install libpq-dev python3-dev
pip install psycopg2-binary

# CentOS/RHEL
sudo yum install postgresql-devel python3-devel
pip install psycopg2-binary

# Arch
sudo pacman -S postgresql python
pip install psycopg2-binary
```

**Для macOS:**
```bash
# С помощью Homebrew
brew install postgresql
pip install psycopg2-binary

# Или с помощью conda
conda install psycopg2
```

#### 🐘 **Вариант 3: Компиляция из исходников (если ничего не помогает)**

**Windows:**
1. Установите **Visual Studio Build Tools** или **MinGW**
2. Установите **PostgreSQL** для Windows
3. Добавьте `C:\Program Files\PostgreSQL\[version]\bin` в PATH
4. Выполните:
```bash
pip install psycopg2
```

**Linux:**
```bash
# Установите необходимые пакеты
sudo apt-get install build-essential libpq-dev python3-dev

# Скомпилируйте psycopg2
pip install psycopg2
```

**macOS:**
```bash
# Установите Xcode Command Line Tools
xcode-select --install

# Установите PostgreSQL
brew install postgresql

# Скомпилируйте psycopg2
pip install psycopg2
```

### 4. Запуск сервисов

#### Запуск через PowerShell скрипт (Windows)

```powershell
# Запуск сервисов
.\start-services.ps1 start

# Проверка статуса
.\start-services.ps1 status

# Проверка здоровья сервисов
.\start-services.ps1 health
```

#### Запуск через командную строку

```bash
# Запуск PostgreSQL и MinIO
docker-compose up -d

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs -f
```

### 5. Инициализация базы данных

База данных инициализируется автоматически при первом запуске контейнера PostgreSQL.

**Проверка подключения:**
```bash
docker exec pastebin_postgres psql -U pastebin_user -d pastebin_db -c "SELECT version();"
```

### 6. Запуск Flask приложения

```bash
# Активируйте виртуальное окружение
.\.venv\Scripts\Activate.ps1  # Windows
source .venv/bin/activate     # Linux/macOS

# Запуск приложения
py app.py
```

Приложение будет доступно по адресу: **http://127.0.0.1:5000**

## 🔍 Проверка установки

### Проверка сервисов

```bash
# PostgreSQL
docker exec pastebin_postgres pg_isready -U pastebin_user -d pastebin_db

# MinIO
curl -f http://localhost:9000/minio/health/live
```

### Проверка приложения

1. Откройте браузер: http://127.0.0.1:5000
2. Создайте тестовую пасту
3. Проверьте AI-помощник

## 🚨 Решение проблем

### Проблема: psycopg2 не устанавливается

**Решение 1: Обновите pip**
```bash
python -m pip install --upgrade pip
```

**Решение 2: Используйте альтернативный источник**
```bash
pip install --index-url https://pypi.org/simple/ psycopg2-binary
```

**Решение 3: Установите wheel**
```bash
pip install wheel
pip install psycopg2-binary
```

### Проблема: Docker не запускается

**Решение:**
1. Убедитесь, что Docker Desktop запущен
2. Проверьте права доступа
3. Перезапустите Docker Desktop

### Проблема: Порты заняты

**Решение:**
1. Остановите другие сервисы на портах 5432, 9000, 5000
2. Или измените порты в `docker-compose.yml`

### Проблема: База данных не подключается

**Решение:**
1. Проверьте статус PostgreSQL контейнера
2. Убедитесь, что контейнер полностью запустился
3. Проверьте логи: `docker-compose logs postgres`

## 📚 Дополнительные команды

### Управление сервисами

```powershell
# PowerShell (Windows)
.\start-services.ps1 start      # Запуск
.\start-services.ps1 stop       # Остановка
.\start-services.ps1 restart    # Перезапуск
.\start-services.ps1 status     # Статус
.\start-services.ps1 logs       # Логи
.\start-services.ps1 clean      # Очистка данных
.\start-services.ps1 health     # Проверка здоровья
```

### Управление базой данных

```bash
# Подключение к PostgreSQL
docker exec -it pastebin_postgres psql -U pastebin_user -d pastebin_db

# Создание резервной копии
docker exec pastebin_postgres pg_dump -U pastebin_user pastebin_db > backup.sql

# Восстановление из резервной копии
docker exec -i pastebin_postgres psql -U pastebin_user -d pastebin_db < backup.sql
```

### Управление MinIO

```bash
# Подключение к MinIO Console
# Откройте http://localhost:9001
# Логин: minioadmin
# Пароль: minioadmin123
```

## 🎯 Оптимизация производительности

### Настройка PostgreSQL

```sql
-- В файле init-db.sql добавьте:
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET effective_cache_size = '1GB';
ALTER SYSTEM SET maintenance_work_mem = '64MB';
ALTER SYSTEM SET checkpoint_completion_target = 0.9;
ALTER SYSTEM SET wal_buffers = '16MB';
```

### Настройка MinIO

```yaml
# В docker-compose.yml добавьте:
environment:
  MINIO_CACHE_DRIVES: "/data"
  MINIO_CACHE_EXPIRY: "72h"
  MINIO_CACHE_MAXUSE: "80"
```

## 🔐 Безопасность

### Продакшн настройки

1. **Измените пароли** в `config.env`
2. **Настройте SSL** для PostgreSQL
3. **Ограничьте доступ** к MinIO
4. **Настройте файрвол** для портов

### Переменные окружения

```bash
# Создайте config.env с безопасными значениями
SECRET_KEY=your-super-secret-key-here
POSTGRES_PASSWORD=strong-password-here
MINIO_ROOT_PASSWORD=strong-minio-password
```

## 📞 Поддержка

### Полезные ссылки

- **PostgreSQL**: https://www.postgresql.org/docs/
- **MinIO**: https://docs.min.io/
- **Flask**: https://flask.palletsprojects.com/
- **SQLAlchemy**: https://docs.sqlalchemy.org/

### Логи и отладка

```bash
# Логи приложения
py app.py

# Логи Docker
docker-compose logs -f

# Логи PostgreSQL
docker exec pastebin_postgres tail -f /var/log/postgresql/postgresql-*.log
```

---

**🎉 Поздравляем! PasteBin Pro успешно установлен и готов к использованию!**

Если у вас возникли проблемы, проверьте:
1. Все зависимости установлены
2. Docker сервисы запущены
3. Порты не заняты другими приложениями
4. Виртуальное окружение активировано
