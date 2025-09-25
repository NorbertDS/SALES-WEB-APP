#!/bin/bash

# Cloud Deployment Script for Sales Analytics System
# This script deploys the system to cloud platforms

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
ENVIRONMENT=${ENVIRONMENT:-production}
SECRET_KEY=${SECRET_KEY:-$(openssl rand -base64 32)}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD:-$(openssl rand -base64 32)}
REDIS_PASSWORD=${REDIS_PASSWORD:-$(openssl rand -base64 32)}

echo -e "${BLUE}🚀 Starting Cloud Deployment for Sales Analytics System${NC}"
echo -e "${YELLOW}Environment: ${ENVIRONMENT}${NC}"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}❌ Docker is not installed. Please install Docker first.${NC}"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}❌ Docker Compose is not installed. Please install Docker Compose first.${NC}"
    exit 1
fi

# Create environment file
echo -e "${YELLOW}📝 Creating environment configuration...${NC}"
cat > .env << EOF
# Environment Configuration
ENVIRONMENT=${ENVIRONMENT}
SECRET_KEY=${SECRET_KEY}
POSTGRES_PASSWORD=${POSTGRES_PASSWORD}
REDIS_PASSWORD=${REDIS_PASSWORD}
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=7

# Database Configuration
POSTGRES_DB=sales_analytics
POSTGRES_USER=sales_user

# Redis Configuration
REDIS_HOST=redis
REDIS_PORT=6379

# CORS Configuration
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8080,https://your-domain.com
ALLOWED_HOSTS=localhost,127.0.0.1,your-domain.com

# Cloud Platform Specific
PORT=8000
EOF

echo -e "${GREEN}✅ Environment file created${NC}"

# Create logs directory
echo -e "${YELLOW}📁 Creating logs directory...${NC}"
mkdir -p logs
mkdir -p ssl

# Build and start services
echo -e "${YELLOW}🔨 Building and starting services...${NC}"
docker-compose -f docker-compose.cloud.yml down --remove-orphans
docker-compose -f docker-compose.cloud.yml build --no-cache
docker-compose -f docker-compose.cloud.yml up -d

# Wait for services to be healthy
echo -e "${YELLOW}⏳ Waiting for services to be healthy...${NC}"
sleep 30

# Check service health
echo -e "${YELLOW}🔍 Checking service health...${NC}"

# Check database
if docker-compose -f docker-compose.cloud.yml exec -T postgres pg_isready -U sales_user -d sales_analytics; then
    echo -e "${GREEN}✅ Database is healthy${NC}"
else
    echo -e "${RED}❌ Database is not healthy${NC}"
    exit 1
fi

# Check Redis
if docker-compose -f docker-compose.cloud.yml exec -T redis redis-cli ping; then
    echo -e "${GREEN}✅ Redis is healthy${NC}"
else
    echo -e "${RED}❌ Redis is not healthy${NC}"
    exit 1
fi

# Check backend API
if curl -f http://localhost:8000/health; then
    echo -e "${GREEN}✅ Backend API is healthy${NC}"
else
    echo -e "${RED}❌ Backend API is not healthy${NC}"
    exit 1
fi

# Check frontend
if curl -f http://localhost/health; then
    echo -e "${GREEN}✅ Frontend is healthy${NC}"
else
    echo -e "${RED}❌ Frontend is not healthy${NC}"
    exit 1
fi

# Display deployment information
echo -e "${GREEN}🎉 Deployment completed successfully!${NC}"
echo ""
echo -e "${BLUE}📊 Service URLs:${NC}"
echo -e "  Frontend: http://localhost"
echo -e "  Backend API: http://localhost:8000"
echo -e "  API Documentation: http://localhost:8000/api/docs"
echo -e "  Health Check: http://localhost:8000/health"
echo ""
echo -e "${BLUE}🔐 Default Admin Credentials:${NC}"
echo -e "  Email: admin@salesanalytics.com"
echo -e "  Password: admin123"
echo ""
echo -e "${YELLOW}⚠️  Important Security Notes:${NC}"
echo -e "  1. Change default admin password immediately"
echo -e "  2. Update SECRET_KEY in production"
echo -e "  3. Configure SSL/TLS certificates"
echo -e "  4. Update ALLOWED_ORIGINS and ALLOWED_HOSTS"
echo -e "  5. Enable firewall rules"
echo ""
echo -e "${BLUE}📝 Logs:${NC}"
echo -e "  Application logs: ./logs/"
echo -e "  Docker logs: docker-compose -f docker-compose.cloud.yml logs"
echo ""
echo -e "${GREEN}🚀 Your Sales Analytics System is now running in the cloud!${NC}"
