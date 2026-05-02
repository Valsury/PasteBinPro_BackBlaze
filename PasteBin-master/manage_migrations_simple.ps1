param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("status", "current", "history", "upgrade", "downgrade", "create", "reset")]
    [string]$Action,
    
    [Parameter(Mandatory=$false)]
    [string]$Message
)

# Python path
$pythonPath = "C:\Users\Avelio\AppData\Local\Programs\Python\Python312\python.exe"

Write-Host "Migration Management for PasteBin" -ForegroundColor Green
Write-Host "Action: $Action" -ForegroundColor Cyan
Write-Host ""

switch ($Action) {
    "status" {
        Write-Host "Migration Status:" -ForegroundColor Blue
        & $pythonPath -m alembic current
        Write-Host ""
        Write-Host "Migration History:" -ForegroundColor Blue
        & $pythonPath -m alembic history
    }
    
    "current" {
        Write-Host "Current Version:" -ForegroundColor Blue
        & $pythonPath -m alembic current
    }
    
    "history" {
        Write-Host "Migration History:" -ForegroundColor Blue
        & $pythonPath -m alembic history
    }
    
    "upgrade" {
        Write-Host "Applying migrations..." -ForegroundColor Blue
        & $pythonPath -m alembic upgrade head
        if ($LASTEXITCODE -eq 0) {
            Write-Host "SUCCESS: Migrations applied!" -ForegroundColor Green
        } else {
            Write-Host "ERROR: Migration failed" -ForegroundColor Red
        }
    }
    
    "downgrade" {
        Write-Host "Downgrading one version..." -ForegroundColor Blue
        & $pythonPath -m alembic downgrade -1
        if ($LASTEXITCODE -eq 0) {
            Write-Host "SUCCESS: Downgrade completed!" -ForegroundColor Green
        } else {
            Write-Host "ERROR: Downgrade failed" -ForegroundColor Red
        }
    }
    
    "create" {
        if (-not $Message) {
            Write-Error "For creating migration specify message: .\manage_migrations_simple.ps1 create 'Description'"
            exit 1
        }
        Write-Host "Creating migration: $Message" -ForegroundColor Blue
        & $pythonPath -m alembic revision --autogenerate -m $Message
        if ($LASTEXITCODE -eq 0) {
            Write-Host "SUCCESS: Migration created!" -ForegroundColor Green
        } else {
            Write-Host "ERROR: Migration creation failed" -ForegroundColor Red
        }
    }
    
    "reset" {
        Write-Host "WARNING: This will delete all data!" -ForegroundColor Red
        $confirm = Read-Host "Continue? (y/N)"
        if ($confirm -eq "y" -or $confirm -eq "Y") {
            Write-Host "Cleaning database..." -ForegroundColor Yellow
            
            $cleanScript = @"
DROP VIEW IF EXISTS recent_pastes CASCADE;
DROP TABLE IF EXISTS paste_tags CASCADE;
DROP TABLE IF EXISTS pastes CASCADE;
DROP TABLE IF EXISTS tags CASCADE;
DROP TABLE IF EXISTS users CASCADE;
DROP TABLE IF EXISTS alembic_version CASCADE;
"@
            $cleanScript | docker exec -i pastebin_postgres psql -U pastebin_user -d pastebin_db
            
            Write-Host "Applying migrations..." -ForegroundColor Yellow
            & $pythonPath -m alembic upgrade head
            
            if ($LASTEXITCODE -eq 0) {
                Write-Host "SUCCESS: Database reset and migrations applied!" -ForegroundColor Green
            } else {
                Write-Host "ERROR: Database reset failed" -ForegroundColor Red
            }
        } else {
            Write-Host "Operation cancelled" -ForegroundColor Yellow
        }
    }
}

Write-Host ""
Write-Host "Done!" -ForegroundColor Green
