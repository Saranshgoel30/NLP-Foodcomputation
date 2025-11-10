# Environment setup script for Web
# Installs Node.js dependencies

Write-Host "Setting up MMFOOD Web environment..." -ForegroundColor Green

# Check Node version
$nodeVersion = node --version
Write-Host "Node version: $nodeVersion" -ForegroundColor Cyan

# Navigate to web directory
Set-Location -Path "app\web"

# Install dependencies
Write-Host "Installing dependencies..." -ForegroundColor Yellow
npm install

# Create .env.local if it doesn't exist
if (-not (Test-Path ".env.local")) {
    Write-Host "Creating .env.local file..." -ForegroundColor Yellow
    "NEXT_PUBLIC_API_URL=http://localhost:8000" | Out-File -FilePath .env.local -Encoding utf8
    Write-Host "Created .env.local with default API URL" -ForegroundColor Cyan
}

# Build types package
Write-Host "Building shared types..." -ForegroundColor Yellow
Set-Location -Path "..\packages\types"
npm install
npm run build

Write-Host "Web environment setup complete!" -ForegroundColor Green
Write-Host "To start the development server, run: npm run dev" -ForegroundColor Cyan
