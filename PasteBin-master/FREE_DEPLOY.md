# 🆓 100% Бесплатный деплой на Render

## 🎯 Полностью бесплатная конфигурация

### Вариант 1: С Backblaze B2 (Рекомендуется) ⭐

**Стоимость: $0/месяц навсегда**

- ✅ Render Web Service: **Бесплатно** (750 часов/месяц)
- ✅ Render PostgreSQL: **Бесплатно** (90 дней, потом $7/мес)
- ✅ Backblaze B2: **10 GB бесплатно** навсегда
- ✅ OpenRouter: **Бесплатные модели** (mistral, gemini-flash, llama)

### Вариант 2: Локальное хранилище (Для тестов)

**Стоимость: $0/месяц**

- ✅ Render Web Service: **Бесплатно**
- ✅ Render PostgreSQL: **Бесплатно** (90 дней)
- ✅ Локальное хранилище: **Бесплатно**
- ⚠️ **Минус**: Данные теряются при перезапуске на Free плане

---

## 🚀 Быстрый старт (15 минут)

### Шаг 1: Backblaze B2 (5 минут)

1. **Регистрация**
   - Перейдите на https://www.backblaze.com/b2/sign-up.html
   - Зарегистрируйтесь (не требует карту для 10 GB)

2. **Создайте Bucket**
   - В панели B2 нажмите **Create a Bucket**
   - Имя: `pastebin-pastes`
   - Files in Bucket: **Private**
   - Нажмите **Create a Bucket**

3. **Создайте Application Key**
   - Перейдите в **App Keys**
   - Нажмите **Add a New Application Key**
   - Key Name: `pastebin-render`
   - Allow access to: выберите ваш bucket
   - Нажмите **Create New Key**
   - **Сохраните**:
     - `keyID` (это ваш Access Key)
     - `applicationKey` (это ваш Secret Key)
     - `Endpoint` (например: `s3.us-west-004.backblazeb2.com`)

### Шаг 2: OpenRouter API (2 минуты)

1. Зарегистрируйтесь на https://openrouter.ai/
2. Перейдите в https://openrouter.ai/keys
3. Создайте API ключ
4. **Бесплатные модели** (не требуют пополнения):
   - `mistralai/mistral-7b-instruct` ✨
   - `google/gemini-flash-1.5`
   - `meta-llama/llama-3-8b-instruct`

### Шаг 3: Загрузите код в Git (3 минуты)

```bash
cd PasteBin-master
git init
git add .
git commit -m "Ready for free Render deployment"
git remote add origin <your-github-repo-url>
git push -u origin main
```

### Шаг 4: Деплой на Render (5 минут)

1. **Создайте Blueprint**
   - Откройте https://dashboard.render.com/
   - Нажмите **New** → **Blueprint**
   - Подключите GitHub репозиторий
   - Render обнаружит `render.yaml`

2. **Добавьте переменные окружения**

   В настройках Web Service добавьте:

   **Для Backblaze B2:**
   ```bash
   # LLM API (бесплатные модели)
   LLM_PROVIDER=openrouter
   LLM_API_KEY=sk-or-v1-xxxxx
   LLM_MODEL=mistralai/mistral-7b-instruct
   
   # Backblaze B2 (10 GB бесплатно)
   STORAGE_TYPE=s3
   S3_ENDPOINT=s3.us-west-004.backblazeb2.com
   S3_ACCESS_KEY=<ваш-keyID>
   S3_SECRET_KEY=<ваш-applicationKey>
   S3_BUCKET_NAME=pastebin-pastes
   S3_SECURE=true
   S3_REGION=us-west-004
   ```

   **Или для локального хранилища (тесты):**
   ```bash
   # LLM API
   LLM_PROVIDER=openrouter
   LLM_API_KEY=sk-or-v1-xxxxx
   LLM_MODEL=mistralai/mistral-7b-instruct
   
   # Локальное хранилище (данные теряются при рестарте)
   STORAGE_TYPE=local
   STORAGE_PATH=/opt/render/project/src/storage
   ```

3. **Нажмите Apply** и дождитесь деплоя (3-5 минут)

---

## 🆓 Альтернативные бесплатные хранилища

### 1. Backblaze B2 ⭐ (Рекомендуется)
- **10 GB бесплатно** навсегда
- **1 GB трафика/день** бесплатно
- S3-совместимый
- Без привязки карты
- Endpoint: `s3.us-west-004.backblazeb2.com`

### 2. Cloudflare R2
- **10 GB бесплатно**
- **10M запросов/месяц**
- Требует домен на Cloudflare
- Endpoint: `<account-id>.r2.cloudflarestorage.com`

### 3. Локальное хранилище
- **Полностью бесплатно**
- ⚠️ Данные теряются при рестарте Render Free
- Подходит для тестов

---

## 🔧 Конфигурация для разных хранилищ

### Backblaze B2:
```bash
STORAGE_TYPE=s3
S3_ENDPOINT=s3.us-west-004.backblazeb2.com
S3_ACCESS_KEY=<keyID>
S3_SECRET_KEY=<applicationKey>
S3_BUCKET_NAME=pastebin-pastes
S3_SECURE=true
S3_REGION=us-west-004
```

### Cloudflare R2:
```bash
STORAGE_TYPE=s3
S3_ENDPOINT=<account-id>.r2.cloudflarestorage.com
S3_ACCESS_KEY=<access-key>
S3_SECRET_KEY=<secret-key>
S3_BUCKET_NAME=pastebin-pastes
S3_SECURE=true
S3_REGION=auto
```

### Локальное хранилище:
```bash
STORAGE_TYPE=local
STORAGE_PATH=/opt/render/project/src/storage
```

---

## 💡 Бесплатные LLM модели на OpenRouter

Эти модели **не требуют пополнения баланса**:

```bash
# Mistral (рекомендуется для русского языка)
LLM_MODEL=mistralai/mistral-7b-instruct

# Google Gemini Flash (быстрая)
LLM_MODEL=google/gemini-flash-1.5

# Meta Llama 3
LLM_MODEL=meta-llama/llama-3-8b-instruct

# Nous Hermes (хорошая для кода)
LLM_MODEL=nousresearch/nous-hermes-2-mixtral-8x7b-dpo
```

---

## ✅ Проверка работы

После деплоя проверьте:

1. **Главная страница** - должна открыться
2. **Создание пасты** - создайте тестовую пасту
3. **AI генерация** - попробуйте сгенерировать текст
4. **Хранилище** - паста должна сохраниться

### Проверка через Shell (Render Dashboard → Shell):

```bash
# Проверка хранилища
python -c "from storage import MinioStorage; s = MinioStorage(); print(s.get_bucket_info())"

# Проверка LLM API
python -c "from llm_helper import UniversalLLMHelper; h = UniversalLLMHelper(); print('✅ OK' if h.is_available() else '❌ Error')"
```

---

## 🐛 Устранение проблем

### Проблема: Backblaze B2 не подключается

**Решение:**
1. Проверьте правильность endpoint (должен быть без `https://`)
2. Убедитесь, что Application Key имеет доступ к bucket
3. Проверьте region (должен совпадать с endpoint)

### Проблема: Данные теряются при рестарте

**Причина:** Используется локальное хранилище на Render Free

**Решение:** Переключитесь на Backblaze B2:
```bash
STORAGE_TYPE=s3
S3_ENDPOINT=s3.us-west-004.backblazeb2.com
# ... остальные настройки B2
```

### Проблема: LLM API не работает

**Проверьте:**
1. API ключ установлен в переменных окружения
2. Используете бесплатную модель
3. Правильно указан `LLM_PROVIDER=openrouter`

---

## 💰 Итоговая стоимость

### Первые 90 дней:
- Render Web Service: **$0**
- Render PostgreSQL: **$0** (90 дней бесплатно)
- Backblaze B2: **$0** (10 GB навсегда)
- OpenRouter: **$0** (бесплатные модели)

**Итого: $0/месяц**

### После 90 дней:
- Render Web Service: **$0**
- Render PostgreSQL: **$7/месяц** (или мигрируйте на Supabase бесплатно)
- Backblaze B2: **$0**
- OpenRouter: **$0**

**Итого: $7/месяц** (только PostgreSQL)

### Полностью бесплатно навсегда:
Используйте **Supabase PostgreSQL** (1 GB бесплатно) вместо Render PostgreSQL:
```bash
DATABASE_URL=postgresql://user:pass@db.xxx.supabase.co:5432/postgres
```

**Итого: $0/месяц навсегда!** 🎉

---

## 📚 Дополнительные ресурсы

- [Backblaze B2 Documentation](https://www.backblaze.com/b2/docs/)
- [OpenRouter Free Models](https://openrouter.ai/docs#models)
- [Render Documentation](https://render.com/docs)
- [Supabase PostgreSQL](https://supabase.com/docs/guides/database)

---

**🎉 Готово! Ваше приложение работает полностью бесплатно!**
