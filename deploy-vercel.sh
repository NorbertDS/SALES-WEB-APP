#!/bin/bash

# Vercel Deployment Script for Sales Analytics Dashboard
# This script deploys the frontend to Vercel

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🚀 Deploying Sales Analytics Dashboard to Vercel${NC}"

# Check if Vercel CLI is installed
if ! command -v vercel &> /dev/null; then
    echo -e "${YELLOW}📦 Installing Vercel CLI...${NC}"
    npm install -g vercel
fi

# Check if user is logged in
if ! vercel whoami &> /dev/null; then
    echo -e "${YELLOW}🔐 Please login to Vercel...${NC}"
    vercel login
fi

# Deploy to Vercel
echo -e "${YELLOW}🚀 Deploying to Vercel...${NC}"
vercel --prod

echo -e "${GREEN}✅ Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Next Steps:${NC}"
echo -e "1. Deploy your backend to Heroku or Railway"
echo -e "2. Update API_BASE_URL in Vercel environment variables"
echo -e "3. Test the application"
echo ""
echo -e "${YELLOW}⚠️  Important Notes:${NC}"
echo -e "- Vercel only hosts the frontend"
echo -e "- You need a separate backend service"
echo -e "- Update the API_BASE_URL in your frontend code"
echo ""
echo -e "${GREEN}🎉 Your frontend is now live on Vercel!${NC}"
