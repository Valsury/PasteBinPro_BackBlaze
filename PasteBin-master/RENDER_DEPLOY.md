# 🚀 Деплой PasteBin Pro на Render

Это руководство поможет вам развернуть PasteBin Pro на платформе [Render](https://render.com).

## 📋 Что изменилось для Render

### ✅ Выполненные изменения:

1. **Замена Ollama на универсальный LLM API**
   - Поддержка OpenRouter, OpenAI, Anthropic и других провайдеров
   - Файл: `llm_helper.py` (новая версия)

2. **S3-совместимое хранилище вместо MinIO**
   - Поддержка AWS S3, Cloudflare R2, DigitalOcean Spaces
   - Файл: `storage.py` (обновлен)

3. **Конфигурация для продакшена**
   - Добавлен `gunicorn` в зависимости
   - Создан `Procfile` для Render
   - Создан `render.yaml` для автоматического деплоя
   - Обновлен `config.py` для работы с Render PostgreSQL

## 🎯 Предварительные требования

1. **Аккаунт на Render** - [Зарегистрироваться](https://dashboard.render.com/register)
2. **Git репозиторий** - GitHub, GitLab или Bitbucket
3. **API ключ для LLM** - один из:
   - [OpenRouter](https://openrouter.ai/) (рекомендуется, бесплатные модели доступны)
   - [OpenAI](https://platform.openai.com/)
   - [Anthropic](https://console.anthropic.com/)
4. **S3-совместимое хранилище** - один из:
   - [Cloudflare R2](https://www.cloudflare.com/products/r2/) (10 GB бесплатно)
   - [AWS S3](https://aws.amazon.com/s3/)
   - [DigitalOcean Spaces](https://www.digitalocean.com/products/spaces)

## 📦 Шаг 1: Подготовка S3 хранилища

### Вариант A: Cloudflare R2 (рекомендуется для бесплатного плана)

1. Перейдите в [Cloudflare Dashboard](https://dash.cloudflare.com/)
2. Выберите **R2** в боковом меню
3. Создайте новый bucket с именем `pastebin-pastes`
4. Перейдите в **Settings** → **R2 API Tokens**
5. Создайте новый API токен с правами на чтение/запись
6. Сохраните:
   - **Account ID** (будет в URL: `<account-id>.r2.cloudflarestorage.com`)
   - **Access Key ID**
   - **Secret Access Key**

### Вариант B: AWS S3

1. Создайте S3 bucket в [AWS Console](https://console.aws.amazon.com/s3/)
2. Создайте IAM пользователя с правами на S3
3. Сохраните Access Key и Secret Key

### Вариант C: DigitalOcean Spaces

1. Создайте Space в [DigitalOcean](https://cloud.digitalocean.com/spaces)
2. Создайте API ключ в разделе **API** → **Spaces Keys**
3. Сохраните Access Key и Secret Key

## 🔑 Шаг 2: Получение LLM API ключа

### OpenRouter (рекомендуется)

1. Зарегистрируйтесь на [OpenRouter](https://openrouter.ai/)
2. Перейдите в [Keys](https://openrouter.ai/keys)
3. Создайте новый API ключ
4. Пополните баланс (минимум $5) или используйте бесплатные модели

**Рекомендуемые модели:**
- `mistralai/mistral-7b-instruct` (бесплатная)
- `google/gemini-flash-1.5` (бесплатная)
- `meta-llama/llama-3-8b-instruct` (бесплатная)

## 🚀 Шаг 3: Деплой на Render

### Способ 1: Автоматический деплой через render.yaml

1. **Загрузите код в Git репозиторий**
   ```bash
   git init
   git add .
   git commit -m "Initial commit for Render deployment"
   git remote add origin <your-repo-url>
   git push -u origin main
   ```

2. **Создайте новый Blueprint на Render**
   - Перейдите в [Render Dashboard](https://dashboard.render.com/)
   - Нажмите **New** → **Blueprint**
   - Подключите ваш Git репозиторий
   - Render автоматически обнаружит `render.yaml`

3. **Настройте переменные окружения**
   
   После создания сервиса, добавьте следующие переменные в **Environment**:

   **Обязательные:**
   ```
   LLM_API_KEY=<ваш-api-ключ-от-openrouter>
   S3_ENDPOINT=<ваш-s3-endpoint>
   S3_ACCESS_KEY=<ваш-s3-access-key>
   S3_SECRET_KEY=<ваш-s3-secret-key>
   S3_BUCKET_NAME=pastebin-pastes
   ```

   **Опциональные (уже установлены в render.yaml):**
   ```
   LLM_PROVIDER=openrouter
   LLM_MODEL=mistralai/mistral-7b-instruct
   S3_SECURE=true
   S3_REGION=us-east-1
   FLASK_ENV=production
   ```

### Способ 2: Ручной деплой

1. **Создайте PostgreSQL базу данных**
   - В Render Dashboard нажмите **New** → **PostgreSQL**
   - Выберите имя: `pastebin-db`
   - План: **Free**
   - Нажмите **Create Database**
   - Сохраните **Internal Database URL**

2. **Создайте Web Service**
   - Нажмите **New** → **Web Service**
   - Подключите Git репозиторий
   - Настройки:
     - **Name**: `pastebin-pro`
     - **Environment**: `Python 3`
     - **Region**: выберите ближайший
     - **Branch**: `main`
     - **Build Command**: 
       ```bash
       pip install -r requirements.txt && python -c "from app import app, db; app.app_context().push(); db.create_all()"
       ```
     - **Start Command**: 
       ```bash
       gunicorn app:app --bind 0.0.0.0:$PORT --workers 2 --timeout 120
       ```
     - **Plan**: `Free`

3. **Добавьте переменные окружения** (см. список выше)

4. **Нажмите Create Web Service**

## 🔧 Шаг 4: Настройка переменных окружения

### Примеры конфигурации для разных провайдеров

#### Cloudflare R2:
```bash
S3_ENDPOINT=<account-id>.r2.cloudflarestorage.com
S3_ACCESS_KEY=<your-access-key>
S3_SECRET_KEY=<your-secret-key>
S3_BUCKET_NAME=pastebin-pastes
S3_SECURE=true
S3_REGION=auto
```

#### AWS S3:
```bash
S3_ENDPOINT=s3
S3_ACCESS_KEY=<your-access-key>
S3_SECRET_KEY=<your-secret-key>
S3_BUCKET_NAME=pastebin-pastes
S3_SECURE=true
S3_REGION=us-east-1
```

#### DigitalOcean Spaces:
```bash
S3_ENDPOINT=nyc3.digitaloceanspaces.com
S3_ACCESS_KEY=<your-access-key>
S3_SECRET_KEY=<your-secret-key>
S3_BUCKET_NAME=pastebin-pastes
S3_SECURE=true
S3_REGION=us-east-1
```

#### OpenRouter:
```bash
LLM_PROVIDER=openrouter
LLM_API_KEY=<your-openrouter-key>
LLM_MODEL=mistralai/mistral-7b-instruct
APP_URL=https://your-app.onrender.com
```

#### OpenAI:
```bash
LLM_PROVIDER=openai
LLM_API_KEY=<your-openai-key>
LLM_MODEL=gpt-3.5-turbo
```

#### Anthropic:
```bash
LLM_PROVIDER=anthropic
LLM_API_KEY=<your-anthropic-key>
LLM_MODEL=claude-3-haiku-20240307
```

## ✅ Шаг 5: Проверка деплоя

1. **Дождитесь завершения деплоя** (обычно 3-5 минут)
2. **Откройте URL вашего приложения** (будет вида `https://pastebin-pro.onrender.com`)
3. **Проверьте основные функции:**
   - Создание пасты
   - Просмотр пасты
   - AI-генерация текста
   - Загрузка/сохранение в S3

## 🐛 Устранение проблем

### Проблема: База данных не инициализируется

**Решение:** Выполните миграции вручную через Render Shell:
```bash
python -c "from app import app, db; app.app_context().push(); db.create_all()"
```

### Проблема: S3 хранилище недоступно

**Проверьте:**
1. Правильность endpoint (без `https://`)
2. Корректность Access Key и Secret Key
3. Существование bucket
4. Права доступа к bucket

**Тест подключения:**
```bash
python -c "from storage import MinioStorage; s = MinioStorage(); print('✅ Storage OK' if s.client else '❌ Storage Error')"
```

### Проблема: LLM API не работает

**Проверьте:**
1. Наличие API ключа в переменных окружения
2. Баланс на аккаунте (для платных провайдеров)
3. Правильность имени модели

**Тест LLM:**
```bash
python -c "from llm_helper import UniversalLLMHelper; h = UniversalLLMHelper(); print(h.is_available())"
```

### Проблема: Application Error при запуске

**Проверьте логи:**
1. В Render Dashboard откройте ваш сервис
2. Перейдите в **Logs**
3. Найдите ошибку и исправьте

**Частые причины:**
- Отсутствует переменная окружения `DATABASE_URL`
- Неправильный формат `DATABASE_URL` (должен начинаться с `postgresql://`)
- Отсутствуют обязательные переменные S3 или LLM

## 💰 Стоимость

### Бесплатный план Render:
- ✅ Web Service: 750 часов/месяц (достаточно для одного приложения)
- ✅ PostgreSQL: 90 дней бесплатно, затем $7/месяц
- ⚠️ Приложение засыпает после 15 минут неактивности
- ⚠️ Холодный старт занимает ~30 секунд

### Рекомендуемая конфигурация для минимальных затрат:
- **Render Web Service**: Free
- **Render PostgreSQL**: Free (90 дней) → $7/месяц
- **Cloudflare R2**: Free (10 GB хранилища, 10M запросов/месяц)
- **OpenRouter**: Free модели или от $5 пополнения

**Итого:** $0-7/месяц в зависимости от использования

## 🔄 Обновление приложения

Render автоматически деплоит изменения при push в Git:

```bash
git add .
git commit -m "Update application"
git push origin main
```

Render обнаружит изменения и автоматически пересоберет приложение.

## 📊 Мониторинг

1. **Логи**: Render Dashboard → Logs
2. **Метрики**: Render Dashboard → Metrics
3. **База данных**: Render Dashboard → PostgreSQL → Metrics

## 🔐 Безопасность

1. **Обязательно измените SECRET_KEY** в переменных окружения
2. **Не коммитьте** файлы с секретами (`.env`, `config.env`)
3. **Используйте HTTPS** (Render предоставляет автоматически)
4. **Ограничьте доступ к S3 bucket** только для вашего приложения

## 📚 Дополнительные ресурсы

- [Документация Render](https://render.com/docs)
- [Документация OpenRouter](https://openrouter.ai/docs)
- [Документация Cloudflare R2](https://developers.cloudflare.com/r2/)
- [Документация Flask](https://flask.palletsprojects.com/)

## 🆘 Поддержка

Если у вас возникли проблемы:

1. Проверьте логи в Render Dashboard
2. Убедитесь, что все переменные окружения установлены
3. Создайте issue в GitHub репозитории
4. Напишите в Telegram: [@avelio_bruno](https://t.me/avelio_bruno)

---

**🎉 Готово! Ваше приложение PasteBin Pro теперь работает на Render!**
