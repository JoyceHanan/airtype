# ==============================================================================
# AirType Multi-Environment Setup Script (Windows PowerShell)
# Installs dependencies across Client, Server, and ML-Service.
# ==============================================================================

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Initializing AirType Project Environment" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# 1. Verify Prerequisites
Write-Host "Checking dependencies..."
$nodeTest = Get-Command node -ErrorAction SilentlyContinue
if (-not $nodeTest) {
    Write-Error "Error: Node.js is required. Install v18.x or v20.x."
    Exit
}

$pythonTest = Get-Command python -ErrorAction SilentlyContinue
if (-not $pythonTest) {
    Write-Error "Error: Python is required. Install v3.10 or v3.11."
    Exit
}

Write-Host "✔ Node.js version: $(node -v)" -ForegroundColor Green
Write-Host "✔ Python version: $((python -V) 2>&1)" -ForegroundColor Green

# 2. Setup Client
Write-Host "`nInstalling Client dependencies..." -ForegroundColor Yellow
cd client
npm install
cd ..

# 3. Setup Server
Write-Host "`nInstalling Server dependencies..." -ForegroundColor Yellow
cd server
npm install
cd ..

# 4. Setup ML-Service
Write-Host "`nSetting up ML-Service Python Virtual Environment..." -ForegroundColor Yellow
cd ml-service
python -m venv venv
# Source environment and install dependencies
.\venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..

# 5. Setup Local Config Env Files
Write-Host "`nGenerating environment configurations..." -ForegroundColor Yellow
if (-not (Test-Path .env)) {
    "PORT=5000`nML_SERVICE_URL=http://localhost:8000" | Out-File -FilePath .env -Encoding utf8
    Write-Host "✔ Created default root .env" -ForegroundColor Green
}

Write-Host "`n=========================================" -ForegroundColor Cyan
Write-Host "Setup Complete! Run scripts/run_dev.sh (or similar shell task) to start." -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan
