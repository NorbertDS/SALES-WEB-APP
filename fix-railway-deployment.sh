#!/bin/bash

# Railway Deployment Fix Script
# This script fixes the healthcheck failure issue

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔧 Fixing Railway Healthcheck Failure${NC}"

# Check if git is initialized
if [ ! -d ".git" ]; then
    echo -e "${YELLOW}📦 Initializing Git repository...${NC}"
    git init
fi

# Add all changes
echo -e "${YELLOW}📝 Adding changes...${NC}"
git add .

# Commit changes
echo -e "${YELLOW}💾 Committing fixes...${NC}"
git commit -m "Fix Railway healthcheck failure - updated port config and health endpoint"

# Push to GitHub
echo -e "${YELLOW}📤 Pushing to GitHub...${NC}"
git push origin main

echo -e "${GREEN}✅ Railway deployment fixes applied!${NC}"
echo ""
echo -e "${BLUE}📊 Changes Made:${NC}"
echo -e "1. ✅ Updated port configuration in backend server"
echo -e "2. ✅ Simplified health check endpoint"
echo -e "3. ✅ Updated Railway configuration"
echo -e "4. ✅ Fixed Dockerfile healthcheck"
echo ""
echo -e "${YELLOW}⏳ Railway will automatically redeploy in a few minutes...${NC}"
echo ""
echo -e "${GREEN}🎉 Your deployment should now work!${NC}"
