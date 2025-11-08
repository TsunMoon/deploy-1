# Railway Docker Deployment Script for Backend Only (PowerShell)
Write-Host "🚀 Deploying Backend to Railway with Docker..." -ForegroundColor Green

# Check if we're in backend directory
if (-not (Test-Path "main.py")) {
    Write-Host "❌ Error: Please run this script from the backend directory" -ForegroundColor Red
    Write-Host "   cd backend && .\deploy-railway-docker.ps1" -ForegroundColor Yellow
    exit 1
}

# Check if railway CLI is installed
if (-not (Get-Command railway -ErrorAction SilentlyContinue)) {
    Write-Host "❌ Railway CLI not found. Please install it:" -ForegroundColor Red
    Write-Host "   npm install -g @railway/cli" -ForegroundColor Yellow
    exit 1
}

# Login check
Write-Host "🔐 Checking Railway login status..." -ForegroundColor Blue
try {
    railway whoami | Out-Null
} catch {
    Write-Host "Please login to Railway:" -ForegroundColor Yellow
    railway login
}

# Validate required files
Write-Host "📋 Validating deployment files..." -ForegroundColor Blue
$requiredFiles = @("Dockerfile", "requirements.txt", "main.py", "railway.json")
foreach ($file in $requiredFiles) {
    if (-not (Test-Path $file)) {
        Write-Host "❌ Missing required file: $file" -ForegroundColor Red
        exit 1
    }
}
Write-Host "✅ All required files present" -ForegroundColor Green

# Check environment variables
Write-Host "🔧 Checking environment variables..." -ForegroundColor Blue
if (-not (Test-Path ".env")) {
    Write-Host "⚠️  Warning: No .env file found. Make sure to set environment variables in Railway dashboard" -ForegroundColor Yellow
}

# Deploy to Railway
Write-Host "🚀 Starting deployment..." -ForegroundColor Green
railway up

if ($LASTEXITCODE -eq 0) {
    Write-Host "✅ Deployment successful!" -ForegroundColor Green
    Write-Host ""
    Write-Host "📊 Next steps:" -ForegroundColor Cyan
    Write-Host "   1. Check logs: railway logs" -ForegroundColor White
    Write-Host "   2. Open app: railway open" -ForegroundColor White
    Write-Host "   3. Set environment variables in Railway dashboard if not done" -ForegroundColor White
    Write-Host ""
    Write-Host "🔗 Important endpoints:" -ForegroundColor Cyan
    Write-Host "   - Health check: /health" -ForegroundColor White
    Write-Host "   - API docs: /docs" -ForegroundColor White
    Write-Host "   - Redoc: /redoc" -ForegroundColor White
} else {
    Write-Host "❌ Deployment failed. Check logs with: railway logs" -ForegroundColor Red
    exit 1
}