# 📝 Изменения для деплоя на Render

## ✅ Выполненные изменения

### 1. **Замена Ollama на универсальный LLM API** ✨
- **Файл**: `llm_helper.py` (полностью переписан)
- **Поддержка провайдеров**:
  - OpenRouter (рекомендуется)
  - OpenAI
  - Anthropic
  - Любой OpenAI-совместимый API
- **Обратная совместимость**: Старый файл сохранен как `llm_helper_old.py`

### 2. **S3-совместимое хранилище** 🗄️
- **Файл**: `storage.py` (обновлен)
- **Поддержка сервисов**:
  - Cloudflare R2 (рекомендуется, 10 GB бесплатно)
  - AWS S3
  - DigitalOcean Spaces
  - MinIO (для локальной разработки)

### 3. **Конфигурация для Render** ⚙️
- **Обновлены файлы**:
  - `config.py` - поддержка Render PostgreSQL, новые переменные окружения
  - `config.env` - шаблон с новыми настройками
  - `requirements.txt` - добавлен gunicorn
- **Созданы файлы**:
  - `Procfile` - команда запуска для Render
  - `render.yaml` - автоматическая конфигурация Blueprint
  - `runtime.txt` - версия Python
  - `init_db.sh` - скрипт инициализации БД

### 4. **Документация** 📚
- **RENDER_DEPLOY.md** - полное руководство по деплою (подробное)
- **RENDER_QUICKSTART.md** - быстрый старт за 10 минут
- **.gitignore** - обновлен для исключения секретов

## 🚀 Как задеплоить

### Быстрый способ (10 минут):
```bash
# 1. Получите API ключи (OpenRouter + Cloudflare R2)
# 2. Загрузите код в Git
git init
git add .
git commit -m "Ready for Render deployment"
git push origin main

# 3. Создайте Blueprint на Render
# 4. Добавьте переменные окружения
# 5. Готово!
```

Подробная инструкция: [RENDER_QUICKSTART.md](RENDER_QUICKSTART.md)

## 🔑 Необходимые переменные окружения

### Обязательные:
```bash
LLM_API_KEY=<ваш-ключ-openrouter>
S3_ENDPOINT=<account-id>.r2.cloudflarestorage.com
S3_ACCESS_KEY=<ваш-s3-access-key>
S3_SECRET_KEY=<ваш-s3-secret-key>
S3_BUCKET_NAME=pastebin-pastes
```

### Автоматические (Render установит сам):
```bash
DATABASE_URL=<render-postgresql-url>
PORT=<render-port>
```

## 💰 Стоимость

**Минимальная конфигурация:**
- Render Web Service: **Бесплатно** (750 часов/месяц)
- Render PostgreSQL: **$0** (90 дней) → **$7/месяц**
- Cloudflare R2: **Бесплатно** (10 GB, 10M запросов/месяц)
- OpenRouter: **Бесплатные модели** или от $5

**Итого: $0-7/месяц**

## 🔄 Обратная совместимость

Все изменения обратно совместимы с локальной разработкой:
- MinIO продолжит работать локально
- Ollama можно использовать через `LLM_PROVIDER=custom`
- Старые переменные окружения поддерживаются

## 📊 Что работает

✅ Создание и просмотр паст  
✅ AI-генерация текста (11 категорий)  
✅ Подсветка синтаксиса  
✅ QR-коды  
✅ Приватные пасты  
✅ Автоудаление истекших паст  
✅ PostgreSQL база данных  
✅ S3 хранилище файлов  

## 🐛 Известные ограничения Render Free Plan

⚠️ Приложение засыпает после 15 минут неактивности  
⚠️ Холодный старт занимает ~30 секунд  
⚠️ PostgreSQL бесплатен только 90 дней  

## 📚 Документация

- [RENDER_QUICKSTART.md](RENDER_QUICKSTART.md) - быстрый старт
- [RENDER_DEPLOY.md](RENDER_DEPLOY.md) - полное руководство
- [README.md](README.md) - описание проекта

## 🆘 Поддержка

Проблемы при деплое? Смотрите раздел "Устранение проблем" в [RENDER_DEPLOY.md](RENDER_DEPLOY.md)

---

**Дата изменений**: 2026-05-02  
**Статус**: ✅ Готово к деплою на Render
