# Environment setup script for API
# Creates virtual environment and installs dependencies

Write-Host "Setting up MMFOOD API environment..." -ForegroundColor Green

# Check Python version
$pythonVersion = python --version
Write-Host "Python version: $pythonVersion" -ForegroundColor Cyan

# Navigate to API directory
Set-Location -Path "app\api"

# Create virtual environment if it doesn't exist
if (-not (Test-Path ".venv")) {
    Write-Host "Creating virtual environment..." -ForegroundColor Yellow
    python -m venv .venv
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
.\.venv\Scripts\Activate.ps1

# Upgrade pip
Write-Host "Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
pip install -r requirements.txt

# Copy environment template if .env doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item .env.template .env
    Write-Host "Please edit .env with your configuration" -ForegroundColor Red
}

Write-Host "API environment setup complete!" -ForegroundColor Green
Write-Host "To start the API, run: python main.py" -ForegroundColor Cyan
