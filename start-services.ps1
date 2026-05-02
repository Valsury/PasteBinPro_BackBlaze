# PowerShell script for managing PasteBin services
# Usage: .\start-services-fixed.ps1

param(
    [Parameter(Mandatory=$false)]
    [ValidateSet("start", "stop", "restart", "status", "logs", "clean", "health")]
    [string]$Action = "start"
)

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

function Start-Services {
    Write-Info "Starting PasteBin services..."
    
    # Check if Docker is running
    try {
        docker info | Out-Null
        Write-Info "Docker detected and working"
    } catch {
        Write-Error "Docker is not running! Start Docker Desktop and try again."
        return
    }
    
    # Check for docker-compose
    try {
        docker-compose --version | Out-Null
        Write-Info "Docker Compose detected"
    } catch {
        Write-Error "Docker Compose not found! Install Docker Compose."
        return
    }
    
    # Stop existing containers
    Write-Info "Stopping existing containers..."
    docker-compose down 2>$null
    
    # Start services
    Write-Info "Starting PostgreSQL and MinIO..."
    docker-compose up -d
    
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Services started successfully"
        
        # Wait for services to start
        Write-Info "Waiting for services to start..."
        Start-Sleep -Seconds 15
        
        # Check status
        Show-Status
    } else {
        Write-Error "Error starting services"
        Show-Logs
    }
}

function Stop-Services {
    Write-Info "Stopping PasteBin services..."
    docker-compose down
    if ($LASTEXITCODE -eq 0) {
        Write-Info "Services stopped"
    } else {
        Write-Warning "Possible issues stopping services"
    }
}

function Show-Status {
    Write-Info "Service status:"
    docker-compose ps
    
    Write-Info "`nPorts and access:"
    Write-Host "  PostgreSQL: localhost:5432" -ForegroundColor Cyan
    Write-Host "  MinIO API: localhost:9000" -ForegroundColor Cyan
    Write-Host "  MinIO Console: http://localhost:9001" -ForegroundColor Cyan
    Write-Host "  Login: minioadmin" -ForegroundColor Cyan
    Write-Host "  Password: minioadmin123" -ForegroundColor Cyan
    Write-Host "  Flask App: http://127.0.0.1:5000" -ForegroundColor Cyan
}

function Show-Logs {
    Write-Info "Show service logs..."
    docker-compose logs -f
}

function Clean-Services {
    Write-Warning "Removing all service data..."
    $confirm = Read-Host "This will delete ALL data! Continue? (y/N)"
    if ($confirm -eq "y" -or $confirm -eq "Y") {
        docker-compose down -v
        Write-Info "All data removed"
    } else {
        Write-Info "Operation cancelled"
    }
}

function Check-Health {
    Write-Info "Checking service health..."
    
    # Check PostgreSQL
    try {
        $pgTest = docker exec pastebin_postgres pg_isready -U pastebin_user -d pastebin_db
        if ($LASTEXITCODE -eq 0) {
            Write-Host "  PostgreSQL: Healthy" -ForegroundColor Green
        } else {
            Write-Host "  PostgreSQL: Issues" -ForegroundColor Red
        }
    } catch {
        Write-Host "  PostgreSQL: Unavailable" -ForegroundColor Red
    }
    
    # Check MinIO
    try {
        $minioTest = Invoke-WebRequest -Uri "http://localhost:9000/minio/health/live" -UseBasicParsing -TimeoutSec 5
        if ($minioTest.StatusCode -eq 200) {
            Write-Host "  MinIO: Healthy" -ForegroundColor Green
        } else {
            Write-Host "  MinIO: Issues" -ForegroundColor Red
        }
    } catch {
        Write-Host "  MinIO: Unavailable" -ForegroundColor Red
    }
}

# Main logic
switch ($Action) {
    "start" { Start-Services }
    "stop" { Stop-Services }
    "restart" { 
        Stop-Services
        Start-Sleep -Seconds 2
        Start-Services
    }
    "status" { Show-Status }
    "logs" { Show-Logs }
    "clean" { Clean-Services }
    "health" { Check-Health }
    default { 
        Write-Info "Available commands:"
        Write-Host "  .\start-services-fixed.ps1 start    - start services" -ForegroundColor Cyan
        Write-Host "  .\start-services-fixed.ps1 stop     - stop services" -ForegroundColor Cyan
        Write-Host "  .\start-services-fixed.ps1 restart  - restart services" -ForegroundColor Cyan
        Write-Host "  .\start-services-fixed.ps1 status  - show status" -ForegroundColor Cyan
        Write-Host "  .\start-services-fixed.ps1 logs    - show logs" -ForegroundColor Cyan
        Write-Host "  .\start-services-fixed.ps1 clean   - clean all data" -ForegroundColor Cyan
        Write-Host "  .\start-services-fixed.ps1 health  - check service health" -ForegroundColor Cyan
    }
}
