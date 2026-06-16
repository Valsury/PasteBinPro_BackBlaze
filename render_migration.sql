-- SQL скрипт для применения миграции на Render
-- Выполните эти команды в консоли Render или через подключение к базе данных

-- 1. Проверьте, есть ли поле is_admin в таблице users
SELECT column_name 
FROM information_schema.columns 
WHERE table_name = 'users' AND column_name = 'is_admin';

-- 2. Если поля нет, добавьте его
ALTER TABLE users 
ADD COLUMN IF NOT EXISTS is_admin BOOLEAN DEFAULT FALSE;

-- 3. Проверьте существование пользователя admin
SELECT * FROM users WHERE username = 'admin';

-- 4. Если пользователя нет, создайте его
-- Сначала получите хеш пароля 'admin' из логов приложения
-- Или используйте этот хеш (пароль: admin):
-- Хеш: 7a009d60b5fd10a09eadf4044b563af1$3b6e9511dcbf5a5d5886fe746640589b43a40abbb114c27d8bfc5c4976295dda

INSERT INTO users (username, email, password_hash, is_active, is_admin, created_at) 
VALUES ('admin', 'admin@localhost', '7a009d60b5fd10a09eadf4044b563af1$3b6e9511dcbf5a5d5886fe746640589b43a40abbb114c27d8bfc5c4976295dda', true, true, NOW());

-- 5. Если пользователь есть, обновите его до администратора
UPDATE users 
SET is_admin = true, email = 'admin@localhost' 
WHERE username = 'admin';

-- 6. Проверьте результат
SELECT username, email, is_admin, created_at 
FROM users 
WHERE is_admin = true 
ORDER BY created_at;

-- 7. Проверьте структуру таблицы
SELECT column_name, data_type, is_nullable, column_default
FROM information_schema.columns 
WHERE table_name = 'users' 
ORDER BY ordinal_position;