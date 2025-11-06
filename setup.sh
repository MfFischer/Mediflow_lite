#!/bin/bash

# MediFlow Lite Setup Script
# This script sets up the development environment

set -e

echo "🏥 MediFlow Lite - Setup Script"
echo "================================"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

echo -e "${GREEN}✅ Docker and Docker Compose are installed${NC}"

# Create backend .env if it doesn't exist
if [ ! -f backend/.env ]; then
    echo -e "${YELLOW}📝 Creating backend/.env from template...${NC}"
    cp backend/.env.example backend/.env
    
    # Generate a random secret key
    SECRET_KEY=$(openssl rand -hex 32)
    
    # Update the secret key in .env
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here-change-in-production/$SECRET_KEY/" backend/.env
    else
        # Linux
        sed -i "s/your-secret-key-here-change-in-production/$SECRET_KEY/" backend/.env
    fi
    
    echo -e "${GREEN}✅ Backend .env created with generated SECRET_KEY${NC}"
else
    echo -e "${GREEN}✅ Backend .env already exists${NC}"
fi

# Create frontend .env if it doesn't exist
if [ ! -f frontend/.env ]; then
    echo -e "${YELLOW}📝 Creating frontend/.env from template...${NC}"
    cp frontend/.env.example frontend/.env
    echo -e "${GREEN}✅ Frontend .env created${NC}"
else
    echo -e "${GREEN}✅ Frontend .env already exists${NC}"
fi

# Create necessary directories
echo -e "${YELLOW}📁 Creating necessary directories...${NC}"
mkdir -p backend/uploads
mkdir -p backend/logs
mkdir -p backend/alembic/versions
echo -e "${GREEN}✅ Directories created${NC}"

# Ask user if they want to start with Docker
echo ""
read -p "Do you want to start the application with Docker? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo -e "${YELLOW}🐳 Starting Docker containers...${NC}"
    docker-compose up -d
    
    echo ""
    echo -e "${GREEN}✅ Application started successfully!${NC}"
    echo ""
    echo "📍 Access points:"
    echo "   - Frontend: http://localhost:3000"
    echo "   - Backend API: http://localhost:8000"
    echo "   - API Docs: http://localhost:8000/docs"
    echo ""
    echo "📊 View logs:"
    echo "   docker-compose logs -f"
    echo ""
    echo "🛑 Stop application:"
    echo "   docker-compose down"
else
    echo ""
    echo -e "${YELLOW}ℹ️  To start the application later, run:${NC}"
    echo "   docker-compose up -d"
fi

echo ""
echo -e "${GREEN}🎉 Setup complete!${NC}"

