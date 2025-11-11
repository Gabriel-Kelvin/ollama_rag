# Ollama RAG Application

A production-ready RAG (Retrieval-Augmented Generation) application with React frontend and FastAPI backend, featuring Docker deployment and local development workflows.

## 🏗️ Architecture

- **Frontend**: React + TypeScript + Vite + TailwindCSS (served by Nginx in production)
- **Backend**: FastAPI + Python
- **Vector DB**: Qdrant
- **LLM**: Ollama (remote server)
- **Auth**: Supabase

## 📁 Project Structure

```
ollama_rag/
├── backend/              # FastAPI application
├── core/                 # Shared business logic
│   ├── adapters/        # External service adapters
│   ├── services/        # Business logic services
│   └── utils/           # Utility functions
├── web/                 # React frontend
├── data/                # Data storage (volumes)
│   ├── uploads/         # Uploaded documents
│   ├── chunks/          # Document chunks
│   └── temp/            # Temporary files
├── Dockerfile.backend   # Backend Docker image
├── Dockerfile.frontend  # Frontend Docker image
├── docker-compose.yml   # Docker orchestration
└── nginx.conf          # Nginx reverse proxy config
```

## 🚀 Quick Start

### Option 1: Local Development (Recommended for Development)

**Backend on `http://localhost:8000`**  
**Frontend on `http://localhost:5173`**

#### 1. Setup Backend

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt

# Setup environment
cp env.local.example .env
# Edit .env with your credentials
```

#### 2. Run Backend

```bash
# From project root
uvicorn backend.main:app --reload --port 8000
```

#### 3. Setup Frontend

```bash
cd web

# Install dependencies
npm install

# Setup environment
cp env.local.example .env.local
# Edit .env.local with:
# VITE_API_BASE_URL=http://localhost:8000
# VITE_SUPABASE_URL=your_supabase_url
# VITE_SUPABASE_ANON_KEY=your_anon_key
```

#### 4. Run Frontend

```bash
# From web/ directory
npm run dev
```

**Access**: Open `http://localhost:5173` in your browser

---

### Option 2: Docker Deployment (Production-like)

**Backend on `:8015`**  
**Frontend on `:8016`** (with `/api` reverse proxy to backend)

#### Prerequisites

- Docker & Docker Compose installed
- Git installed

#### 1. Clone Repository

```bash
git clone https://github.com/Gabriel-Kelvin/ollama_rag.git
cd ollama_rag
```

#### 2. Configure Environment

```bash
# Copy docker environment template
cp env.docker.example .env

# Edit .env with your production values:
# - SUPABASE credentials
# - VITE_SUPABASE_ANON_KEY
# - Other production settings
```

#### 3. Build and Run

```bash
# Build images and start containers
docker-compose up -d --build

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Stop and remove volumes
docker-compose down -v
```

#### 4. Access Application

- **Frontend**: `http://your-server-ip:8016`
- **Backend API**: `http://your-server-ip:8015`
- **Health Check**: `http://your-server-ip:8015/health`

**Note**: Frontend calls backend via `/api` proxy (e.g., `/api/health` → `http://backend:8015/health`)

---

## 🔧 Configuration

### Environment Variables

#### Backend (.env)

```bash
# Ollama Server
OLLAMA_BASE_URL=http://47.129.127.169
OLLAMA_MODEL=llama2

# Application
DEBUG=False
LOG_LEVEL=INFO

# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE=your_service_role_key
SUPABASE_JWT_SECRET=your_jwt_secret
```

#### Frontend (web/.env.local for local dev)

```bash
# API endpoint
VITE_API_BASE_URL=http://localhost:8000

# Supabase (public keys only)
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

#### Frontend (Docker build args in .env)

```bash
VITE_API_BASE_URL=/api
VITE_SUPABASE_URL=https://your-project.supabase.co
VITE_SUPABASE_ANON_KEY=your_anon_key
```

---

## 🐳 Docker Commands

```bash
# Build only
docker-compose build

# Run in detached mode
docker-compose up -d

# View logs
docker-compose logs -f backend
docker-compose logs -f frontend

# Restart services
docker-compose restart

# Stop services
docker-compose stop

# Remove containers and networks
docker-compose down

# Remove containers, networks, and volumes
docker-compose down -v

# Rebuild specific service
docker-compose up -d --build backend
```

---

## 🖥️ VM Deployment Guide

### Deploy to Ubuntu/Debian Server (e.g., AWS EC2, DigitalOcean)

#### 1. Connect to VM

```bash
ssh root@18.138.240.220
# or
ssh -i your-key.pem ubuntu@18.138.240.220
```

#### 2. Install Docker

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Install Docker Compose
sudo apt install docker-compose -y

# Verify installation
docker --version
docker-compose --version
```

#### 3. Install Git

```bash
sudo apt install git -y
```

#### 4. Clone Repository

```bash
cd /opt
sudo git clone https://github.com/Gabriel-Kelvin/ollama_rag.git
cd ollama_rag
```

#### 5. Configure Environment

```bash
# Copy template
sudo cp env.docker.example .env

# Edit with your credentials
sudo nano .env
```

**Important**: Update these values:
- `SUPABASE_SERVICE_ROLE`
- `SUPABASE_JWT_SECRET`
- `VITE_SUPABASE_ANON_KEY`

#### 6. Deploy

```bash
# Build and start
sudo docker-compose up -d --build

# Check status
sudo docker-compose ps

# View logs
sudo docker-compose logs -f
```

#### 7. Configure Firewall (if needed)

```bash
# Allow ports
sudo ufw allow 8015/tcp
sudo ufw allow 8016/tcp
sudo ufw enable
sudo ufw status
```

#### 8. Verify Deployment

```bash
# Test backend health
curl http://localhost:8015/health

# Test frontend
curl -I http://localhost:8016
```

**Access from browser**:
- Frontend: `http://18.138.240.220:8016`
- Backend API: `http://18.138.240.220:8015/health`

---

## 📡 API Endpoints

### Health & Status
- `GET /health` - System health check
- `GET /` - API root

### Knowledge Bases
- `GET /knowledge-bases` - List all KBs
- `POST /knowledge-bases` - Create KB
- `DELETE /knowledge-bases/{kb_name}` - Delete KB
- `GET /knowledge-bases/{kb_name}/files` - List files in KB

### Document Management
- `POST /upload` - Upload and index document
- `GET /uploads/{kb_name}` - Get uploaded files
- `DELETE /uploads/{kb_name}/{filename}` - Delete file
- `POST /index` - Re-index file

### RAG Operations
- `POST /retrieve` - Retrieve relevant documents
- `POST /chat` - RAG-powered chat

---

## 🧪 Testing

### Test Backend

```bash
# Local
curl http://localhost:8000/health

# Docker
curl http://localhost:8015/health
```

### Test Frontend

```bash
# Local dev server should be accessible
# Docker
curl -I http://localhost:8016
```

---

## 🐛 Troubleshooting

### Docker Issues

```bash
# View logs
docker-compose logs -f

# Restart services
docker-compose restart

# Rebuild from scratch
docker-compose down -v
docker-compose up -d --build
```

### Port Already in Use

```bash
# Find process using port
# Windows:
netstat -ano | findstr :8015
taskkill /PID <pid> /F

# Linux:
lsof -i :8015
kill -9 <pid>
```

### Permission Denied (VM)

```bash
# Add user to docker group
sudo usermod -aG docker $USER
newgrp docker

# Or use sudo
sudo docker-compose up -d
```

---

## 🔐 Security Notes

1. **Never commit** `.env` files with real credentials
2. **Use environment variables** for all sensitive data
3. **Rotate keys regularly** (Supabase, JWT secrets)
4. **Enable HTTPS** in production (use nginx-proxy or Cloudflare)
5. **Restrict CORS** in production (update `allow_origins` in backend/main.py)

---

## 📦 Features

- ✅ Knowledge base management
- ✅ Document upload (PDF, DOCX, TXT)
- ✅ Automatic indexing with embeddings
- ✅ RAG-powered chat interface
- ✅ Remote Ollama server integration
- ✅ Supabase authentication
- ✅ Docker deployment
- ✅ Nginx reverse proxy
- ✅ Health monitoring

---

## 🤝 Contributing

1. Fork the repository
2. Create feature branch (`git checkout -b feature/amazing-feature`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing-feature`)
5. Open Pull Request

---

## 📄 License

This project is licensed under the MIT License.

---

## 🙏 Acknowledgments

- **Ollama** - Local LLM inference
- **Qdrant** - Vector database
- **FastAPI** - Backend framework
- **React** - Frontend framework
- **Supabase** - Authentication

---

## 📞 Support

For issues and questions:
- GitHub Issues: https://github.com/Gabriel-Kelvin/ollama_rag/issues
- Email: support@example.com

---

**Happy RAG-ing! 🚀**
