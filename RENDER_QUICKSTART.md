# 🚀 Быстрый старт: Деплой на Render за 10 минут

## Шаг 1: Подготовка (2 минуты)

### 1.1 Получите API ключ OpenRouter (бесплатно)
1. Зарегистрируйтесь на https://openrouter.ai/
2. Перейдите в https://openrouter.ai/keys
3. Создайте API ключ
4. Скопируйте ключ

### 1.2 Настройте Cloudflare R2 (бесплатно, 10 GB)
1. Зарегистрируйтесь на https://dash.cloudflare.com/
2. Перейдите в **R2** → **Create bucket**
3. Имя bucket: `pastebin-pastes`
4. Перейдите в **Settings** → **R2 API Tokens** → **Create API Token**
5. Сохраните:
   - Account ID (из URL)
   - Access Key ID
   - Secret Access Key

## Шаг 2: Загрузите код в Git (2 минуты)

```bash
cd PasteBin-master
git init
git add .
git commit -m "Initial commit"
git remote add origin <your-github-repo-url>
git push -u origin main
```

## Шаг 3: Деплой на Render (5 минут)

### 3.1 Создайте Blueprint
1. Откройте https://dashboard.render.com/
2. Нажмите **New** → **Blueprint**
3. Подключите ваш GitHub репозиторий
4. Render автоматически обнаружит `render.yaml`

### 3.2 Добавьте переменные окружения

В настройках Web Service добавьте:

```bash
# LLM API (OpenRouter)
LLM_API_KEY=sk-or-v1-xxxxx

# Cloudflare R2
S3_ENDPOINT=<account-id>.r2.cloudflarestorage.com
S3_ACCESS_KEY=<your-access-key>
S3_SECRET_KEY=<your-secret-key>
S3_BUCKET_NAME=pastebin-pastes
S3_SECURE=true
S3_REGION=auto

# URL приложения (замените после деплоя)
APP_URL=https://your-app.onrender.com
```

### 3.3 Деплой
1. Нажмите **Apply**
2. Дождитесь завершения (3-5 минут)
3. Откройте URL приложения

## ✅ Готово!

Ваше приложение доступно по адресу: `https://your-app.onrender.com`

## 💡 Полезные команды

### Проверка статуса
```bash
# Проверить подключение к S3
python -c "from storage import MinioStorage; s = MinioStorage(); print('✅ OK')"

# Проверить LLM API
python -c "from llm_helper import UniversalLLMHelper; h = UniversalLLMHelper(); print(h.is_available())"
```

### Просмотр логов
Render Dashboard → Ваш сервис → **Logs**

## 🐛 Проблемы?

Смотрите полную документацию: [RENDER_DEPLOY.md](RENDER_DEPLOY.md)
