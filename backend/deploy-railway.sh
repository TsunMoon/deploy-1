#!/bin/bash

# Railway Deployment Helper Script
# This script helps you prepare and deploy to Railway

set -e  # Exit on error

echo "=================================================="
echo "🚀 Railway Deployment Helper"
echo "=================================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if we're in the backend directory
if [ ! -f "main.py" ]; then
    echo -e "${RED}❌ Error: Please run this script from the backend directory${NC}"
    exit 1
fi

echo "✅ Running from backend directory"
echo ""

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}⚠️  Git not initialized in backend directory${NC}"
    echo "Checking parent directory..."
    cd ..
    if [ ! -d ".git" ]; then
        echo -e "${RED}❌ Error: No git repository found${NC}"
        echo "Please initialize git first: git init"
        exit 1
    fi
    cd backend
fi

echo "✅ Git repository found"
echo ""

# Check if required files exist
echo "Checking Railway configuration files..."
files=("Procfile" "railway.json" "nixpacks.toml" "runtime.txt" ".railwayignore")
all_exist=true

for file in "${files[@]}"; do
    if [ -f "$file" ]; then
        echo -e "  ${GREEN}✓${NC} $file"
    else
        echo -e "  ${RED}✗${NC} $file (missing)"
        all_exist=false
    fi
done

if [ "$all_exist" = false ]; then
    echo -e "${RED}❌ Some configuration files are missing${NC}"
    exit 1
fi

echo ""
echo "✅ All Railway configuration files present"
echo ""

# Check if .env exists
if [ ! -f ".env" ]; then
    echo -e "${YELLOW}⚠️  Warning: .env file not found${NC}"
    echo "Make sure to add environment variables in Railway dashboard"
else
    echo "✅ .env file found (remember: this won't be deployed)"
fi
echo ""

# Check if requirements.txt exists
if [ ! -f "requirements.txt" ]; then
    echo -e "${RED}❌ Error: requirements.txt not found${NC}"
    exit 1
fi

echo "✅ requirements.txt found"
echo ""

# Offer to check git status
echo "=================================================="
echo "📋 Git Status"
echo "=================================================="
git status
echo ""

# Ask if user wants to commit changes
read -p "Do you want to commit and push changes? (y/n) " -n 1 -r
echo ""
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    read -p "Enter commit message: " commit_msg
    
    if [ -z "$commit_msg" ]; then
        commit_msg="Deploy to Railway"
    fi
    
    echo ""
    echo "Committing changes..."
    git add .
    git commit -m "$commit_msg" || echo "No changes to commit"
    
    echo ""
    read -p "Push to remote? (y/n) " -n 1 -r
    echo ""
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Pushing to remote..."
        git push || echo "Failed to push. Please check your remote settings."
    fi
fi

echo ""
echo "=================================================="
echo "📝 Next Steps for Railway Deployment"
echo "=================================================="
echo ""
echo "1. Go to https://railway.app"
echo "2. Click 'New Project' → 'Deploy from GitHub repo'"
echo "3. Select your repository"
echo "4. Set Root Directory to: ${GREEN}backend${NC}"
echo "5. Add environment variables from: ${GREEN}.env.railway.template${NC}"
echo "6. Railway will automatically deploy!"
echo ""
echo "Environment variables to add in Railway:"
echo "  • AZURE_OPENAI_ENDPOINT"
echo "  • AZURE_OPENAI_API_KEY"
echo "  • AZURE_DEPLOYMENT_NAME"
echo "  • AZURE_EMBEDDING_ENDPOINT"
echo "  • AZURE_EMBEDDING_API_KEY"
echo "  • AZURE_EMBEDDING_DEPLOYMENT"
echo "  • QDRANT_API_KEY"
echo "  • QDRANT_URL"
echo "  • QDRANT_COLLECTION_NAME"
echo ""
echo "Once deployed, your API will be available at:"
echo "  ${GREEN}https://your-app.up.railway.app${NC}"
echo ""
echo "Test endpoints:"
echo "  ${GREEN}https://your-app.up.railway.app/health${NC}"
echo "  ${GREEN}https://your-app.up.railway.app/docs${NC}"
echo ""
echo "=================================================="
echo "✅ Preparation Complete!"
echo "=================================================="
echo ""
echo "For detailed instructions, see: ${GREEN}RAILWAY_DEPLOY.md${NC}"
echo ""
