#!/bin/bash

# Railway Deployment Script for Sales Analytics System
# This script prepares your project for Railway deployment

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Preparing Sales Analytics System for Railway Deployment${NC}"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📦 Initializing Git repository...${NC}"
    git init
    git add .
    git commit -m "Initial commit for Railway deployment"
fi

# Check if remote origin exists
if ! git remote get-url origin &> /dev/null; then
    echo -e "${YELLOW}🔗 Please add your GitHub repository as origin:${NC}"
    echo -e "git remote add origin https://github.com/yourusername/your-repo.git"
    echo -e "git push -u origin main"
    exit 1
fi

# Push to GitHub
echo -e "${YELLOW}📤 Pushing to GitHub...${NC}"
git add .
git commit -m "Ready for Railway deployment" || echo "No changes to commit"
git push origin main

echo -e "${GREEN}✅ Project prepared for Railway deployment!${NC}"
echo ""
echo -e "${BLUE}📊 Next Steps:${NC}"
echo -e "1. Go to https://railway.app"
echo -e "2. Sign up with GitHub"
echo -e "3. Click 'New Project'"
echo -e "4. Select 'Deploy from GitHub repo'"
echo -e "5. Choose your repository"
echo -e "6. Railway will auto-detect and deploy!"
echo ""
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo -e "- Railway will automatically detect your Docker setup"
echo -e "- PostgreSQL database will be created automatically"
echo -e "- Environment variables will be set automatically"
echo -e "- Your app will be available at: https://your-app.railway.app"
echo ""
echo -e "${GREEN}🎉 Your project is ready for Railway deployment!${NC}"
