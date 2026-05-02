# PowerShell скрипт для установки зависимостей PasteBin Pro
# Запуск: .\install-dependencies.ps1

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Test-Python {
    Write-Info "Проверка Python..."
    
    try {
        $pythonVersion = py --version 2>$null
        if ($pythonVersion) {
            Write-Info "Python найден: $pythonVersion"
            return $true
        }
    } catch {
        # Игнорируем ошибки
    }
    
    try {
        $pythonVersion = python --version 2>$null
        if ($pythonVersion) {
            Write-Info "Python найден: $pythonVersion"
            return $true
        }
    } catch {
        # Игнорируем ошибки
    }
    
    Write-Error "Python не найден! Установите Python 3.8+ с https://python.org"
    return $false
}

function Install-VirtualEnv {
    Write-Info "Создание виртуального окружения..."
    
    if (Test-Path ".venv") {
        Write-Warning "Виртуальное окружение уже существует"
        return $true
    }
    
    try {
        py -m venv .venv
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Виртуальное окружение создано"
            return $true
        } else {
            Write-Error "Ошибка создания виртуального окружения"
            return $false
        }
    } catch {
        Write-Error "Ошибка создания виртуального окружения: $($_.Exception.Message)"
        return $false
    }
}

function Activate-VirtualEnv {
    Write-Info "Активация виртуального окружения..."
    
    try {
        .\.venv\Scripts\Activate.ps1
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Виртуальное окружение активировано"
            return $true
        } else {
            Write-Error "Ошибка активации виртуального окружения"
            return $false
        }
    } catch {
        Write-Error "Ошибка активации виртуального окружения: $_"
        return $false
    }
}

function Install-BasicDependencies {
    Write-Info "Установка основных зависимостей..."
    
    $dependencies = @(
        "Flask==2.3.3",
        "python-dotenv==1.0.0", 
        "requests==2.31.0",
        "SQLAlchemy==2.0.21",
        "Flask-SQLAlchemy==3.0.5",
        "minio==7.1.17",
        "alembic==1.12.0"
    )
    
    foreach ($dep in $dependencies) {
        Write-Info "Установка $dep..."
        try {
            pip install $dep
            if ($LASTEXITCODE -ne 0) {
                Write-Warning "Проблема с установкой $dep"
            }
        } catch {
            Write-Warning "Ошибка установки $dep: $_"
        }
    }
}

function Install-PostgreSQLDriver {
    Write-Info "Установка PostgreSQL драйвера..."
    
    # Попытка 1: psycopg2-binary
    Write-Info "Попытка установки psycopg2-binary..."
    try {
        pip install psycopg2-binary
        if ($LASTEXITCODE -eq 0) {
            Write-Info "psycopg2-binary установлен успешно"
            return $true
        }
    } catch {
        Write-Warning "psycopg2-binary не установился"
    }
    
    # Попытка 2: Обновление pip и повторная попытка
    Write-Info "Обновление pip и повторная попытка..."
    try {
        python -m pip install --upgrade pip
        pip install psycopg2-binary
        if ($LASTEXITCODE -eq 0) {
            Write-Info "psycopg2-binary установлен после обновления pip"
            return $true
        }
    } catch {
        Write-Warning "psycopg2-binary не установился после обновления pip"
    }
    
    # Попытка 3: Альтернативный источник
    Write-Info "Попытка установки из альтернативного источника..."
    try {
        pip install --only-binary=all psycopg2-binary
        if ($LASTEXITCODE -eq 0) {
            Write-Info "psycopg2-binary установлен из альтернативного источника"
            return $true
        }
    } catch {
        Write-Warning "psycopg2-binary не установился из альтернативного источника"
    }
    
    # Попытка 4: Установка wheel
    Write-Info "Установка wheel и повторная попытка..."
    try {
        pip install wheel
        pip install psycopg2-binary
        if ($LASTEXITCODE -eq 0) {
            Write-Info "psycopg2-binary установлен после установки wheel"
            return $true
        }
    } catch {
        Write-Warning "psycopg2-binary не установился после установки wheel"
    }
    
    Write-Error "Не удалось установить PostgreSQL драйвер автоматически"
    Write-Info "Попробуйте установить вручную:"
    Write-Host "  1. Установите Visual Studio Build Tools" -ForegroundColor Yellow
    Write-Host "  2. Установите PostgreSQL для Windows" -ForegroundColor Yellow
    Write-Host "  3. Добавьте PostgreSQL bin в PATH" -ForegroundColor Yellow
    Write-Host "  4. Выполните: pip install psycopg2" -ForegroundColor Yellow
    
    return $false
}

function Test-Docker {
    Write-Info "Проверка Docker..."
    
    try {
        docker --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Docker найден"
            return $true
        }
    } catch {
        Write-Error "Docker не найден! Установите Docker Desktop с https://docker.com"
        return $false
    }
    
    try {
        docker-compose --version | Out-Null
        if ($LASTEXITCODE -eq 0) {
            Write-Info "Docker Compose найден"
            return $true
        }
    } catch {
        Write-Error "Docker Compose не найден!"
        return $false
    }
    
    return $false
}

function Show-InstallationSummary {
    Write-Info "`n=== СВОДКА УСТАНОВКИ ==="
    
    # Проверяем Python
    if (Test-Python) {
        Write-Host "  ✅ Python" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Python" -ForegroundColor Red
    }
    
    # Проверяем виртуальное окружение
    if (Test-Path ".venv") {
        Write-Host "  ✅ Виртуальное окружение" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Виртуальное окружение" -ForegroundColor Red
    }
    
    # Проверяем Docker
    if (Test-Docker) {
        Write-Host "  ✅ Docker" -ForegroundColor Green
    } else {
        Write-Host "  ❌ Docker" -ForegroundColor Red
    }
    
    Write-Info "`n=== СЛЕДУЮЩИЕ ШАГИ ==="
    Write-Host "1. Запустите сервисы: .\start-services.ps1 start" -ForegroundColor Cyan
    Write-Host "2. Запустите приложение: py app.py" -ForegroundColor Cyan
    Write-Host "3. Откройте браузер: http://127.0.0.1:5000" -ForegroundColor Cyan
}

# Основная логика установки
Write-Info "🚀 Установка зависимостей PasteBin Pro"
Write-Info "====================================="

# Проверяем Python
if (-not (Test-Python)) {
    exit 1
}

# Создаем виртуальное окружение
if (-not (Install-VirtualEnv)) {
    exit 1
}

# Активируем виртуальное окружение
if (-not (Activate-VirtualEnv)) {
    exit 1
}

# Устанавливаем основные зависимости
Install-BasicDependencies

# Устанавливаем PostgreSQL драйвер
Install-PostgreSQLDriver

# Проверяем Docker
Test-Docker

# Показываем сводку
Show-InstallationSummary

Write-Info "`n🎉 Установка завершена!"
