#!/bin/bash
# VM Deployment Script for Ollama RAG Application
# Run this on your VM (Ubuntu/Debian)

set -e  # Exit on error

echo "🚀 Starting VM Deployment..."

# Step 1: Update system
echo "📦 Updating system packages..."
sudo apt update && sudo apt upgrade -y

# Step 2: Install Docker
echo "🐳 Installing Docker..."
if ! command -v docker &> /dev/null; then
    curl -fsSL https://get.docker.com -o get-docker.sh
    sudo sh get-docker.sh
    sudo usermod -aG docker $USER
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Step 3: Install Docker Compose
echo "🔧 Installing Docker Compose..."
if ! command -v docker-compose &> /dev/null; then
    sudo apt install docker-compose -y
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

# Step 4: Install Git
echo "📥 Installing Git..."
if ! command -v git &> /dev/null; then
    sudo apt install git -y
    echo "✅ Git installed"
else
    echo "✅ Git already installed"
fi

# Step 5: Clone repository
echo "📂 Cloning repository..."
cd /opt
if [ -d "ollama_rag" ]; then
    echo "⚠️  Directory exists, pulling latest changes..."
    cd ollama_rag
    sudo git pull origin main
else
    sudo git clone https://github.com/Gabriel-Kelvin/ollama_rag.git
    cd ollama_rag
fi

# Step 6: Setup environment
echo "⚙️  Setting up environment..."
if [ ! -f ".env" ]; then
    sudo cp env.docker.example .env
    echo "📝 Created .env file from template"
    echo "⚠️  IMPORTANT: Edit .env file with your production credentials:"
    echo "   sudo nano .env"
    echo ""
    echo "   Update these values:"
    echo "   - SUPABASE_SERVICE_ROLE"
    echo "   - SUPABASE_JWT_SECRET"
    echo "   - VITE_SUPABASE_ANON_KEY"
    echo ""
    read -p "Press Enter after editing .env file..."
else
    echo "✅ .env file already exists"
fi

# Step 7: Create data directories
echo "📁 Creating data directories..."
sudo mkdir -p data/uploads data/chunks data/temp
sudo chmod -R 755 data

# Step 8: Build and start containers
echo "🏗️  Building and starting Docker containers..."
sudo docker-compose down -v 2>/dev/null || true
sudo docker-compose up -d --build

# Step 9: Check status
echo "📊 Checking container status..."
sleep 5
sudo docker-compose ps

# Step 10: Show logs
echo "📋 Container logs (Ctrl+C to exit):"
echo ""
sudo docker-compose logs -f

