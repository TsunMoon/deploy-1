#!/bin/bash

# Railway Docker Deployment Script for Backend Only
echo "🚀 Deploying Backend to Railway with Docker..."

# Check if we're in backend directory
if [ ! -f "main.py" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    echo "   cd backend && ./deploy-railway-docker.sh"
    exit 1
fi

# Check if railway CLI is installed
if ! command -v railway &> /dev/null; then
    echo "❌ Railway CLI not found. Installing..."
    npm install -g @railway/cli
fi

# Login check
echo "🔐 Checking Railway login status..."
if ! railway whoami &> /dev/null; then
    echo "Please login to Railway:"
    railway login
fi

# Validate required files
echo "📋 Validating deployment files..."
required_files=("Dockerfile" "requirements.txt" "main.py" "railway.json")
for file in "${required_files[@]}"; do
    if [ ! -f "$file" ]; then
        echo "❌ Missing required file: $file"
        exit 1
    fi
done
echo "✅ All required files present"

# Check environment variables
echo "🔧 Checking environment variables..."
if [ ! -f ".env" ]; then
    echo "⚠️  Warning: No .env file found. Make sure to set environment variables in Railway dashboard"
fi

# Deploy to Railway
echo "🚀 Starting deployment..."
railway up

if [ $? -eq 0 ]; then
    echo "✅ Deployment successful!"
    echo ""
    echo "📊 Next steps:"
    echo "   1. Check logs: railway logs"
    echo "   2. Open app: railway open"
    echo "   3. Set environment variables in Railway dashboard if not done"
    echo ""
    echo "🔗 Important endpoints:"
    echo "   - Health check: /health"
    echo "   - API docs: /docs"
    echo "   - Redoc: /redoc"
else
    echo "❌ Deployment failed. Check logs with: railway logs"
    exit 1
fi