# 🆓 Полностью бесплатный деплой PasteBin Pro

## 📋 Что нужно (все бесплатно)

1. **Render** - хостинг приложения (750 часов/месяц бесплатно)
2. **Render PostgreSQL** - база данных (бесплатно 90 дней, потом $7/мес)
3. **Backblaze B2** - хранилище файлов (10 GB бесплатно навсегда)
4. **OpenRouter** - LLM API (бесплатные модели без пополнения)

**Итого: $0/месяц первые 90 дней, потом $7/месяц только за PostgreSQL**

---

## 🚀 Пошаговая инструкция (20 минут)

### Шаг 1: Backblaze B2 (5 минут) 🗄️

**Зачем:** Хранилище для содержимого паст (10 GB бесплатно навсегда)

1. **Регистрация**
   - Откройте https://www.backblaze.com/b2/sign-up.html
   - Заполните форму (карта НЕ требуется)
   - Подтвердите email

2. **Создайте Bucket**
   - Войдите в панель B2
   - Нажмите **Buckets** → **Create a Bucket**
   - **Bucket Unique Name**: `pastebin-pastes-<ваше-имя>` (должно быть уникальным)
   - **Files in Bucket are**: выберите **Private**
   - **Default Encryption**: Disable
   - Нажмите **Create a Bucket**

3. **Создайте Application Key**
   - Перейдите в **App Keys** (в левом меню)
   - Нажмите **Add a New Application Key**
   - **Name of Key**: `pastebin-render`
   - **Allow access to Bucket(s)**: выберите ваш bucket `pastebin-pastes-<ваше-имя>`
   - **Type of Access**: Read and Write
   - **Allow List All Bucket Names**: оставьте включенным
   - Нажмите **Create New Key**

4. **Сохраните данные** (они покажутся только один раз!)
   ```
   keyID: 005a1b2c3d4e5f6g7h8i9j0k
   applicationKey: K005abcdefghijklmnopqrstuvwxyz1234567890
   ```

5. **Найдите Endpoint**
   - В разделе **Buckets** найдите ваш bucket
   - Нажмите на него
   - В **Bucket Details** найдите **Endpoint**
   - Пример: `s3.us-west-004.backblazeb2.com`
   - Сохраните этот endpoint

**Что сохранить:**
```
Endpoint: s3.us-west-004.backblazeb2.com
Access Key (keyID): 005a1b2c3d4e5f6g7h8i9j0k
Secret Key (applicationKey): K005abcdefghijklmnopqrstuvwxyz1234567890
Bucket Name: pastebin-pastes-<ваше-имя>
Region: us-west-004 (из endpoint)
```

---

### Шаг 2: OpenRouter API (3 минуты) 🤖

**Зачем:** AI-генерация текста (бесплатные модели без пополнения)

1. **Регистрация**
   - Откройте https://openrouter.ai/
   - Нажмите **Sign In** → **Sign up**
   - Войдите через Google/GitHub или email

2. **Создайте API ключ**
   - Перейдите в https://openrouter.ai/keys
   - Нажмите **Create Key**
   - **Name**: `pastebin-render`
   - **Credit Limit**: оставьте пустым (для бесплатных моделей)
   - Нажмите **Create**
   - Скопируйте ключ (начинается с `sk-or-v1-...`)

3. **Бесплатные модели** (не требуют пополнения баланса):
   - `mistralai/mistral-7b-instruct` ⭐ (лучшая для русского)
   - `google/gemini-flash-1.5` (быстрая)
   - `meta-llama/llama-3-8b-instruct` (хорошая для кода)
   - `nousresearch/nous-hermes-2-mixtral-8x7b-dpo`

**Что сохранить:**
```
API Key: sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
Model: mistralai/mistral-7b-instruct
```

---

### Шаг 3: Загрузите код в GitHub (5 минут) 📦

1. **Создайте репозиторий на GitHub**
   - Откройте https://github.com/new
   - **Repository name**: `pastebin-pro`
   - **Public** или **Private** (на ваш выбор)
   - НЕ добавляйте README, .gitignore, license
   - Нажмите **Create repository**

2. **Загрузите код**
   ```bash
   cd C:\Users\Avelio\Desktop\PasteBin-master
   
   # Инициализация Git
   git init
   git add .
   git commit -m "Initial commit - ready for Render"
   
   # Подключите ваш репозиторий (замените URL)
   git remote add origin https://github.com/ваш-username/pastebin-pro.git
   git branch -M main
   git push -u origin main
   ```

---

### Шаг 4: Деплой на Render (7 минут) 🚀

1. **Создайте аккаунт на Render**
   - Откройте https://dashboard.render.com/register
   - Войдите через GitHub (рекомендуется)

2. **Создайте Blueprint**
   - В Render Dashboard нажмите **New** → **Blueprint**
   - Нажмите **Connect** напротив вашего GitHub аккаунта
   - Выберите репозиторий `pastebin-pro`
   - Render автоматически обнаружит `render.yaml`
   - Нажмите **Apply**

3. **Дождитесь создания сервисов** (2-3 минуты)
   - Render создаст:
     - PostgreSQL базу данных
     - Web Service для приложения

4. **Добавьте переменные окружения**
   
   После создания сервисов:
   - Откройте ваш **Web Service** (pastebin-pro)
   - Перейдите в **Environment**
   - Нажмите **Add Environment Variable**
   
   **Добавьте следующие переменные:**

   ```bash
   # OpenRouter API
   LLM_API_KEY
   sk-or-v1-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
   
   # Backblaze B2 Storage
   S3_ACCESS_KEY
   005a1b2c3d4e5f6g7h8i9j0k
   
   S3_SECRET_KEY
   K005abcdefghijklmnopqrstuvwxyz1234567890
   
   S3_ENDPOINT
   s3.us-west-004.backblazeb2.com
   
   S3_BUCKET_NAME
   pastebin-pastes-<ваше-имя>
   
   S3_REGION
   us-west-004
   
   # URL приложения (замените после деплоя)
   APP_URL
   https://pastebin-pro.onrender.com
   ```

   **Как добавлять:**
   - В поле **Key** вводите имя переменной (например, `LLM_API_KEY`)
   - В поле **Value** вводите значение
   - Нажмите **Add**
   - Повторите для всех переменных

5. **Сохраните и передеплойте**
   - Нажмите **Save Changes**
   - Render автоматически перезапустит приложение
   - Дождитесь завершения деплоя (3-5 минут)

6. **Обновите APP_URL**
   - После деплоя скопируйте URL вашего приложения (например, `https://pastebin-pro-abc123.onrender.com`)
   - Вернитесь в **Environment**
   - Измените значение `APP_URL` на ваш реальный URL
   - Нажмите **Save Changes**

---

## ✅ Проверка работы

1. **Откройте ваше приложение**
   - URL будет вида: `https://pastebin-pro-xxx.onrender.com`
   - Первый запуск может занять ~30 секунд (холодный старт)

2. **Проверьте функции:**
   - ✅ Главная страница открывается
   - ✅ Создайте тестовую пасту
   - ✅ Просмотрите пасту
   - ✅ Попробуйте AI-генерацию текста
   - ✅ Проверьте список недавних паст

3. **Проверка через Shell** (опционально)
   - В Render Dashboard откройте ваш Web Service
   - Перейдите в **Shell**
   - Выполните команды:
   
   ```bash
   # Проверка хранилища
   python -c "from storage import MinioStorage; s = MinioStorage(); print(s.get_bucket_info())"
   
   # Проверка LLM API
   python -c "from llm_helper import UniversalLLMHelper; h = UniversalLLMHelper(); print('✅ LLM OK' if h.is_available() else '❌ LLM Error')"
   ```

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
- ✅ Region совпадает с endpoint (например, `us-west-004`)

**Тест подключения:**
```bash
# В Render Shell
python -c "from storage import MinioStorage; s = MinioStorage(); print('✅ OK')"
```

### Проблема: AI не генерирует текст

**Проверьте:**
- ✅ API ключ OpenRouter установлен
- ✅ Используете бесплатную модель (`mistralai/mistral-7b-instruct`)
- ✅ `LLM_PROVIDER=openrouter`

**Тест LLM:**
```bash
# В Render Shell
python -c "from llm_helper import UniversalLLMHelper; h = UniversalLLMHelper(); result = h.generate_text('Привет'); print(result)"
```

### Проблема: База данных не инициализируется

**Решение:**
```bash
# В Render Shell
python -c "from app import app, db; app.app_context().push(); db.create_all(); print('✅ DB OK')"
```

### Проблема: Приложение засыпает

**Причина:** Render Free план засыпает после 15 минут неактивности

**Решение:**
- Первый запуск после сна занимает ~30 секунд
- Для постоянной работы нужен платный план ($7/мес)
- Или используйте UptimeRobot для пинга каждые 5 минут

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

### Полностью бесплатно навсегда: **$0/месяц**
Замените Render PostgreSQL на **Supabase** (1 GB бесплатно):
1. Создайте проект на https://supabase.com/
2. Скопируйте Database URL
3. Замените `DATABASE_URL` в Render Environment

---

## 🔄 Обновление приложения

Render автоматически деплоит при push в Git:

```bash
cd PasteBin-master
git add .
git commit -m "Update application"
git push origin main
```

Render обнаружит изменения и автоматически пересоберет приложение (3-5 минут).

---

## 📊 Лимиты бесплатных планов

### Render Free:
- ✅ 750 часов/месяц (достаточно для 1 приложения)
- ⚠️ Засыпает после 15 минут неактивности
- ⚠️ Холодный старт ~30 секунд
- ✅ Автоматический SSL (HTTPS)

### Backblaze B2:
- ✅ 10 GB хранилища
- ✅ 1 GB трафика/день (30 GB/месяц)
- ✅ Неограниченное количество запросов

### OpenRouter (бесплатные модели):
- ✅ Неограниченное количество запросов
- ⚠️ Могут быть медленнее платных
- ⚠️ Могут иметь очередь при высокой нагрузке

### Render PostgreSQL:
- ✅ 90 дней бесплатно
- ⚠️ Потом $7/месяц
- ✅ 256 MB RAM
- ✅ 1 GB хранилища

---

## 🎉 Готово!

Ваше приложение PasteBin Pro работает полностью бесплатно на:
- 🚀 **Render** (хостинг)
- 🗄️ **Backblaze B2** (хранилище)
- 🤖 **OpenRouter** (AI)
- 🗃️ **Render PostgreSQL** (база данных)

**URL приложения:** `https://pastebin-pro-xxx.onrender.com`

---

## 📚 Дополнительные ресурсы

- [Backblaze B2 Docs](https://www.backblaze.com/b2/docs/)
- [OpenRouter Docs](https://openrouter.ai/docs)
- [Render Docs](https://render.com/docs)
- [Supabase PostgreSQL](https://supabase.com/docs/guides/database) (альтернатива Render DB)

## 🆘 Нужна помощь?

- Проверьте логи в Render Dashboard → Logs
- Создайте issue в GitHub репозитории
- Telegram: [@avelio_bruno](https://t.me/avelio_bruno)
