# VM Deployment Commands

Quick reference commands to deploy on VM `18.138.240.220`

## Option 1: Automated Script (Recommended)

```bash
# SSH to VM
ssh root@18.138.240.220
# or
ssh -i your-key.pem ubuntu@18.138.240.220

# Download and run deployment script
curl -fsSL https://raw.githubusercontent.com/Gabriel-Kelvin/ollama_rag/main/deploy-vm.sh -o deploy-vm.sh
chmod +x deploy-vm.sh
./deploy-vm.sh
```

## Option 2: Manual Commands

### 1. Connect to VM
```bash
ssh root@18.138.240.220
```

### 2. Update System
```bash
sudo apt update && sudo apt upgrade -y
```

### 3. Install Docker
```bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo usermod -aG docker $USER
rm get-docker.sh
newgrp docker  # Or logout/login
```

### 4. Install Docker Compose
```bash
sudo apt install docker-compose -y
```

### 5. Install Git
```bash
sudo apt install git -y
```

### 6. Clone Repository
```bash
cd /opt
sudo git clone https://github.com/Gabriel-Kelvin/ollama_rag.git
cd ollama_rag
```

### 7. Setup Environment
```bash
# Copy template
sudo cp env.docker.example .env

# Edit with your credentials
sudo nano .env
```

**Update these values in .env:**
- `SUPABASE_SERVICE_ROLE=your_actual_service_role_key`
- `SUPABASE_JWT_SECRET=your_actual_jwt_secret`
- `VITE_SUPABASE_ANON_KEY=your_actual_anon_key`

### 8. Create Data Directories
```bash
sudo mkdir -p data/uploads data/chunks data/temp
sudo chmod -R 755 data
```

### 9. Build and Start
```bash
# Build and start containers
sudo docker-compose up -d --build

# View logs
sudo docker-compose logs -f
```

### 10. Check Status
```bash
# Check containers
sudo docker-compose ps

# Test backend
curl http://localhost:8015/health

# Test frontend
curl -I http://localhost:8016
```

### 11. Configure Firewall (if needed)
```bash
sudo ufw allow 8015/tcp
sudo ufw allow 8016/tcp
sudo ufw enable
sudo ufw status
```

## Access Application

- **Frontend**: `http://18.138.240.220:8016`
- **Backend API**: `http://18.138.240.220:8015`
- **Health Check**: `http://18.138.240.220:8015/health`

## Useful Commands

```bash
# View logs
sudo docker-compose logs -f backend
sudo docker-compose logs -f frontend

# Restart services
sudo docker-compose restart

# Stop services
sudo docker-compose stop

# Stop and remove
sudo docker-compose down

# Rebuild specific service
sudo docker-compose up -d --build backend

# Check resource usage
sudo docker stats
```

## Troubleshooting

```bash
# If permission denied
sudo usermod -aG docker $USER
newgrp docker

# If port already in use
sudo lsof -i :8015
sudo lsof -i :8016

# Rebuild from scratch
sudo docker-compose down -v
sudo docker-compose up -d --build
```

