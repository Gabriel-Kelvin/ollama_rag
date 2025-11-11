# Quick Start Guide - Running All Services

## Prerequisites Check

Before starting, ensure you have:

- ✅ Python virtual environment set up (`venv/`)
- ✅ Node.js and npm installed
- ✅ Environment files created (`.env` for frontend, `config.env` for backend)
- ✅ Supabase redirect URLs configured

## Option 1: Manual Start (Recommended for Development)

Open **3 separate terminals** and run:

### Terminal 1: Backend
```bash
# Windows
venv\Scripts\activate
uvicorn backend.main:app --reload --port 8000

# Linux/Mac
source venv/bin/activate
uvicorn backend.main:app --reload --port 8000
```

### Terminal 2: React Frontend
```bash
cd web
npm run dev
```

### Terminal 3: Streamlit (Optional)
```bash
# Windows
venv\Scripts\activate
streamlit run frontend/app.py

# Linux/Mac
source venv/bin/activate
streamlit run frontend/app.py
```

## Option 2: Using Batch Scripts (Windows)

### Start Backend
Double-click: `start_backend.bat`

Or from command line:
```bash
start_backend.bat
```

### Start React Frontend
Double-click: `start_react_dev.bat`

Or from command line:
```bash
start_react_dev.bat
```

### Start Streamlit (Optional)
Use existing setup or manually:
```bash
venv\Scripts\activate
streamlit run frontend/app.py
```

## Service URLs

Once all services are running:

| Service | URL | Purpose |
|---------|-----|---------|
| **React Frontend** | http://localhost:5173 | Main user interface |
| **FastAPI Backend** | http://localhost:8000 | API server |
| **API Documentation** | http://localhost:8000/docs | Interactive API docs |
| **Streamlit UI** | http://localhost:8501 | Alternative interface |

## Verification Steps

### 1. Check Backend Health
Open in browser: http://localhost:8000/health

Should return JSON with status information.

### 2. Test React Frontend
1. Open http://localhost:5173
2. Should see login page
3. Try signing up with a test email

### 3. Test Authentication
1. Sign up with valid email
2. Check email for verification link
3. Click link → should redirect to app
4. Try creating a knowledge base

## Common Issues

### Backend Won't Start
- **Issue**: `ModuleNotFoundError`
- **Fix**: Activate venv and install requirements
  ```bash
  venv\Scripts\activate
  pip install -r requirements.txt
  ```

### Frontend Won't Start
- **Issue**: `Cannot find module`
- **Fix**: Install dependencies
  ```bash
  cd web
  npm install
  ```

### Port Already in Use
- **Issue**: `Address already in use`
- **Fix**: Kill process on port or use different port
  ```bash
  # For backend on different port
  uvicorn backend.main:app --reload --port 8001
  
  # For frontend on different port
  npm run dev -- --port 5174
  ```

### Authentication Not Working
- **Issue**: 401 errors on API calls
- **Fix**: 
  1. Check `SUPABASE_URL` in backend config matches frontend
  2. Verify `SUPABASE_SERVICE_ROLE` is set in backend
  3. Check backend logs for auth errors

### Email Verification Not Received
- **Issue**: No verification email after signup
- **Fix**:
  1. Check Supabase SMTP configuration
  2. Check spam/junk folder
  3. For testing: manually verify user in Supabase dashboard

## Development Workflow

### Typical Day-to-Day Usage

1. **Morning Start**:
   ```bash
   # Terminal 1: Backend
   start_backend.bat
   
   # Terminal 2: Frontend
   start_react_dev.bat
   ```

2. **Making Changes**:
   - Backend changes: Auto-reload with `--reload` flag
   - Frontend changes: Hot Module Replacement (HMR) automatic
   - Both update without restart!

3. **Testing**:
   - Backend: http://localhost:8000/docs
   - Frontend: Check browser console for errors
   - Check terminal outputs for server logs

4. **End of Day**:
   - Ctrl+C in each terminal to stop services
   - No need to clean up (unless deploying)

## Quick Commands Reference

### Backend
```bash
# Start
uvicorn backend.main:app --reload --port 8000

# With custom config
uvicorn backend.main:app --reload --port 8000 --env-file .env

# Production mode (no reload)
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
# Development
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint
```

### Streamlit
```bash
# Default
streamlit run frontend/app.py

# Custom port
streamlit run frontend/app.py --server.port 8502
```

## Environment Variables Quick Reference

### Backend (`config.env` or `.env`)
```env
OLLAMA_BASE_URL=http://47.129.127.169
OLLAMA_MODEL=llama2
SUPABASE_URL=https://mukkyaabgfhwcnvxbacp.supabase.co
SUPABASE_SERVICE_ROLE=<secret>
SUPABASE_JWT_SECRET=<secret>
```

### Frontend (`web/.env`)
```env
VITE_SUPABASE_URL=https://mukkyaabgfhwcnvxbacp.supabase.co
VITE_SUPABASE_ANON_KEY=<public_key>
VITE_API_BASE_URL=http://localhost:8000
```

## Next Steps

1. ✅ Start all services
2. ✅ Test authentication flow
3. ✅ Create a knowledge base
4. ✅ Upload and index documents
5. ✅ Start chatting!

## Need Help?

- 📖 Full setup guide: `REACT_SETUP_GUIDE.md`
- 🎯 Implementation details: `IMPLEMENTATION_COMPLETE.md`
- 📚 API docs: http://localhost:8000/docs
- 🔧 Frontend docs: `web/README.md`

---

**Pro Tip**: Keep all three terminals visible while developing to catch errors immediately!

