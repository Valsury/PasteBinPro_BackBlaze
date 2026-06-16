# 🚀 Быстрый старт на Render за 15 минут

## 📋 Что нужно (все бесплатно)

1. **Render** - хостинг приложения (750 часов/месяц бесплатно)
2. **Backblaze B2** - хранилище файлов (10 GB бесплатно навсегда)
3. **OpenRouter** - AI API (бесплатные модели без пополнения)
4. **GitHub** - для хранения кода

**Итого: $0/месяц**

---

## ⚡ Шаг 1: Подготовка (5 минут)

### 1.1 Backblaze B2 - хранилище файлов

1. Зарегистрируйтесь: https://www.backblaze.com/b2/sign-up.html
2. Создайте bucket:
   - **Buckets** → **Create a Bucket**
   - Имя: `pastebin-pastes-ваше-имя` (должно быть уникальным)
   - Files in Bucket: **Private**
3. Создайте Application Key:
   - **App Keys** → **Add a New Application Key**
   - Key Name: `pastebin-render`
   - Allow access to: выберите ваш bucket
   - Type of Access: **Read and Write**
4. Сохраните данные (показываются один раз!):
   - `keyID` (это ваш S3_ACCESS_KEY)
   - `applicationKey` (это ваш S3_SECRET_KEY)
   - Endpoint (например: `s3.us-west-004.backblazeb2.com`)
   - Region (из endpoint: `us-west-004`)

### 1.2 OpenRouter - AI API

1. Зарегистрируйтесь: https://openrouter.ai/
2. Создайте API ключ:
   - **Keys** → **Create Key**
   - Name: `pastebin-render`
   - Credit Limit: оставьте пустым
3. Скопируйте ключ (начинается с `sk-or-v1-...`)

**Бесплатные модели:**
- `mistralai/mistral-7b-instruct` ⭐ (рекомендуется для русского)
- `google/gemini-flash-1.5` (быстрая)
- `meta-llama/llama-3-8b-instruct` (хорошая для кода)

---

## 📦 Шаг 2: Загрузка в GitHub (3 минуты)

### 2.1 Создайте репозиторий
1. Откройте https://github.com/new
2. Repository name: `pastebin-pro`
3. Public или Private (на ваш выбор)
4. НЕ добавляйте README, .gitignore, license
5. Нажмите **Create repository**

### 2.2 Загрузите код
```bash
cd PasteBinPro_BackBlaze

# Инициализация Git
git init
git add .
git commit -m "Initial commit - PasteBin Pro ready for Render"

# Подключите ваш репозиторий (замените YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/pastebin-pro.git
git branch -M main
git push -u origin main
```

---

## 🚀 Шаг 3: Деплой на Render (7 минут)

### 3.1 Создайте Blueprint

1. Откройте https://dashboard.render.com/
2. Нажмите **New** → **Blueprint**
3. Подключите ваш GitHub аккаунт (если еще не подключен)
4. Выберите репозиторий `pastebin-pro`
5. Render автоматически обнаружит `render.yaml`
6. Нажмите **Apply**

### 3.2 Дождитесь создания сервисов

Render создаст:
- ✅ PostgreSQL базу данных (бесплатно 90 дней)
- ✅ Web Service для приложения

Это займет 2-3 минуты.

### 3.3 Добавьте переменные окружения

После создания сервисов:

1. Откройте ваш **Web Service** (pastebin-pro)
2. Перейдите в **Environment**
3. Нажмите **Add Environment Variable**

**Добавьте следующие переменные:**

```
LLM_API_KEY
sk-or-v1-ваш-ключ-openrouter

LLM_MODEL
mistralai/mistral-7b-instruct

S3_ACCESS_KEY
ваш-keyID-от-backblaze

S3_SECRET_KEY
ваш-applicationKey-от-backblaze

S3_ENDPOINT
s3.us-west-004.backblazeb2.com

S3_BUCKET_NAME
pastebin-pastes-ваше-имя

S3_REGION
us-west-004

APP_URL
https://pastebin-pro.onrender.com
```

**Как добавлять:**
- В поле **Key** вводите имя переменной (например, `LLM_API_KEY`)
- В поле **Value** вводите значение
- Нажмите **Add**
- Повторите для всех переменных

### 3.4 Сохраните и передеплойте

1. Нажмите **Save Changes**
2. Render автоматически перезапустит приложение
3. Дождитесь завершения деплоя (3-5 минут)

### 3.5 Обновите APP_URL

После деплоя:
1. Скопируйте URL вашего приложения (например, `https://pastebin-pro-abc123.onrender.com`)
2. Вернитесь в **Environment**
3. Измените значение `APP_URL` на ваш реальный URL
4. Нажмите **Save Changes**

---

## ✅ Шаг 4: Проверка (2 минуты)

### Откройте ваше приложение
```
https://pastebin-pro-xxx.onrender.com
```

### Проверьте функции:
- ✅ Главная страница открывается
- ✅ Создайте тестовую пасту
- ✅ Просмотрите пасту
- ✅ Попробуйте AI-генерацию текста
- ✅ Проверьте регистрацию и вход
- ✅ Откройте список недавних паст

---

## 🎉 Готово!

Ваше приложение PasteBin Pro работает на:
- 🚀 **Render** (хостинг)
- 🗄️ **Backblaze B2** (хранилище)
- 🤖 **OpenRouter** (AI)
- 🗃️ **Render PostgreSQL** (база данных)

**URL приложения:** `https://pastebin-pro-xxx.onrender.com`

---

## 🐛 Устранение проблем

### Проблема: Application Error при запуске

**Решение:**
1. Откройте **Logs** в Render Dashboard
2. Найдите ошибку в логах
3. Проверьте, что все переменные окружения установлены

### Проблема: Backblaze B2 не подключается

**Проверьте:**
- ✅ Endpoint без `https://` (должен быть `s3.us-west-004.backblazeb2.com`)
- ✅ Access Key и Secret Key скопированы правильно
- ✅ Bucket Name совпадает с созданным
- ✅ Region совпадает с endpoint

### Проблема: AI не генерирует текст

**Проверьте:**
- ✅ API ключ OpenRouter установлен
- ✅ Используете бесплатную модель (`mistralai/mistral-7b-instruct`)
- ✅ `LLM_PROVIDER=openrouter` (опционально, по умолчанию)

### Проблема: Приложение засыпает

**Причина:** Render Free план засыпает после 15 минут неактивности

**Решение:**
- Первый запуск после сна занимает ~30 секунд
- Для постоянной работы нужен платный план ($7/мес)

---

## 💰 Стоимость

### Первые 90 дней: **$0/месяц**
- ✅ Render Web Service: бесплатно
- ✅ Render PostgreSQL: бесплатно (90 дней)
- ✅ Backblaze B2: бесплатно (10 GB навсегда)
- ✅ OpenRouter: бесплатно (бесплатные модели)

### После 90 дней: **$7/месяц**
- ✅ Render Web Service: бесплатно
- 💰 Render PostgreSQL: **$7/месяц**
- ✅ Backblaze B2: бесплатно
- ✅ OpenRouter: бесплатно

---

## 📚 Дополнительные ресурсы

- **Render документация**: https://render.com/docs
- **Backblaze B2 документация**: https://www.backblaze.com/b2/docs/
- **OpenRouter документация**: https://openrouter.ai/docs
- **GitHub репозиторий**: https://github.com/YOUR_USERNAME/pastebin-pro

---

## 🆘 Нужна помощь?

- Проверьте логи в Render Dashboard → Logs
- Создайте issue в GitHub репозитории
- Telegram: [@avelio_bruno](https://t.me/avelio_bruno)

---

**Время деплоя:** ~15 минут  
**Стоимость:** $0/месяц (первые 90 дней)  
**Статус:** ✅ Готово к использованию