# React Frontend Setup Guide

Complete guide to set up and run the React frontend with Supabase authentication.

## Prerequisites

- Node.js 18+ and npm
- Python 3.8+ with FastAPI backend running
- Supabase account and project

## Quick Start

### 1. Backend Configuration

First, configure the backend to support Supabase JWT verification.

#### Update Backend Environment

Edit `config.env` (or create `.env` if it doesn't exist):

```env
# Existing configuration...
OLLAMA_BASE_URL=http://47.129.127.169
OLLAMA_MODEL=llama2

# Add Supabase configuration
SUPABASE_URL=https://mukkyaabgfhwcnvxbacp.supabase.co
SUPABASE_SERVICE_ROLE=<YOUR_SERVICE_ROLE_KEY>
SUPABASE_JWT_SECRET=<YOUR_JWT_SECRET>
```

**Where to find these values:**

1. Go to your Supabase project dashboard
2. Click **Settings** → **API**
3. Copy:
   - `Project URL` → `SUPABASE_URL`
   - `service_role` key → `SUPABASE_SERVICE_ROLE` (⚠️ Keep secret!)
   - For JWT_SECRET: Settings → API → JWT Settings → JWT Secret

#### Install Backend Dependencies

If not already installed:

```bash
pip install httpx
```

#### Start Backend

```bash
uvicorn backend.main:app --reload --port 8000
```

Backend will run at `http://localhost:8000`

### 2. Frontend Configuration

#### Install Dependencies

```bash
cd web
npm install
```

#### Create Environment File

Create `web/.env`:

```env
VITE_SUPABASE_URL=https://mukkyaabgfhwcnvxbacp.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11a2t5YWFiZ2Zod2NudnhiYWNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI3NjgxNzQsImV4cCI6MjA3ODM0NDE3NH0.qFwUYobkzctNFBBuhoCAcAHNXmCx_z-HvHu5d3LazK4
VITE_API_BASE_URL=http://localhost:8000
```

**⚠️ IMPORTANT**: 
- Use `ANON_KEY` in frontend (public key)
- NEVER put `SERVICE_ROLE` key in frontend `.env`

#### Start Frontend

```bash
npm run dev
```

Frontend will run at `http://localhost:5173`

### 3. Supabase Dashboard Configuration

#### Configure Authentication

1. Go to Supabase Dashboard → **Authentication** → **Providers**
2. Ensure **Email** provider is enabled

#### Add Redirect URLs

1. Go to **Authentication** → **URL Configuration**
2. Add these to **Redirect URLs**:
   ```
   http://localhost:5173/auth/callback
   http://localhost:5173/auth/reset
   ```
3. For production, add your production URLs

#### Configure Email Templates (Optional but Recommended)

1. Go to **Authentication** → **Email Templates**
2. Customize email templates for:
   - Confirm signup
   - Reset password
   - Magic link

#### Set Up SMTP (for real emails)

1. Go to **Project Settings** → **Authentication**
2. Scroll to **SMTP Settings**
3. Configure your email provider (or use Supabase's default for testing)

## Testing the Application

### Test Authentication Flow

1. **Sign Up**:
   - Navigate to `http://localhost:5173/auth/signup`
   - Enter email and password
   - Check email for verification link
   - Click link to verify

2. **Sign In**:
   - Go to `http://localhost:5173/auth/login`
   - Enter credentials
   - Should redirect to `/app/kb`

3. **Password Reset**:
   - Click "Forgot password?" on login page
   - Enter email
   - Check email for reset link
   - Click link and set new password

### Test Protected Features

1. **Knowledge Bases**:
   - Create a new KB
   - View existing KBs
   - Delete a KB

2. **Upload Documents**:
   - Select a KB
   - Drag & drop or browse for PDF/DOCX/TXT
   - Verify upload success

3. **Index Documents**:
   - View uploaded files
   - Click "Index Documents"
   - Watch indexing logs

4. **Chat**:
   - Select indexed KB
   - Ask questions
   - View AI responses with sources

5. **Settings**:
   - Check backend health
   - View account info

## Architecture

### Frontend Structure

```
React App (Port 5173)
├── Auth Pages (public)
│   ├── Login
│   ├── Signup
│   ├── Forgot Password
│   └── Reset Password
│
└── Protected Pages (requires auth)
    ├── Knowledge Bases
    ├── Upload
    ├── Index
    ├── Chat
    └── Settings
```

### Authentication Flow

```
1. User signs up/logs in
   ↓
2. Supabase returns JWT token
   ↓
3. Frontend stores token in localStorage
   ↓
4. API requests include "Authorization: Bearer <token>"
   ↓
5. Backend verifies token with Supabase
   ↓
6. If valid: process request
   If invalid: return 401 → redirect to login
```

### API Communication

```
Frontend (React)
    ↓ JWT Token in Header
Backend (FastAPI)
    ↓ Verify with Supabase
Supabase Auth
    ↓ Valid/Invalid
Backend (FastAPI)
    ↓ Response
Frontend (React)
```

## Development vs Production

### Development (Current Setup)

- Frontend: `http://localhost:5173`
- Backend: `http://localhost:8000`
- CORS: Allow all origins
- Auth: Supabase handles verification

### Production Considerations

1. **Update Environment Variables**:
   ```env
   VITE_API_BASE_URL=https://your-api-domain.com
   ```

2. **Build Frontend**:
   ```bash
   cd web
   npm run build
   ```

3. **Deploy Static Files**: Upload `web/dist/` to your hosting

4. **Update Supabase Redirect URLs**: Add production URLs

5. **Configure CORS**: Restrict to your frontend domain

6. **SSL/HTTPS**: Ensure both frontend and backend use HTTPS

## Troubleshooting

### Backend 401 Errors

**Problem**: All API requests return 401

**Solutions**:
1. Check backend has `SUPABASE_URL` in environment
2. Verify backend auth.py is importing correctly
3. Test token verification:
   ```bash
   # Check backend logs for auth errors
   ```

### Email Verification Not Received

**Problem**: No verification email after signup

**Solutions**:
1. Check Supabase SMTP configuration
2. Check spam/junk folder
3. For development, check Supabase Dashboard → Authentication → Users
   - Manually confirm user if needed

### CORS Errors

**Problem**: Browser blocks API requests

**Solutions**:
1. Ensure backend CORS middleware is configured:
   ```python
   app.add_middleware(
       CORSMiddleware,
       allow_origins=["http://localhost:5173"],
       allow_credentials=True,
       allow_methods=["*"],
       allow_headers=["*"],
   )
   ```
2. Check `VITE_API_BASE_URL` in frontend `.env`

### "Invalid authentication credentials"

**Problem**: Backend rejects valid tokens

**Solutions**:
1. Verify `SUPABASE_URL` matches in both frontend and backend
2. Check token is being sent in requests (browser DevTools → Network)
3. Ensure backend `verify_token` function is working:
   - Check backend logs for detailed errors

### Frontend Build Errors

**Problem**: `npm run build` fails

**Solutions**:
1. Delete `node_modules` and reinstall:
   ```bash
   rm -rf node_modules package-lock.json
   npm install
   ```
2. Check for TypeScript errors:
   ```bash
   npm run lint
   ```

## File Locations

### Environment Files
- **Frontend**: `web/.env` (not in git - create manually)
- **Backend**: `config.env` or `.env` (not in git - create manually)

### Key Files
- **Frontend Entry**: `web/src/main.tsx`
- **Routing**: `web/src/App.tsx`
- **Auth Context**: `web/src/contexts/AuthContext.tsx`
- **API Client**: `web/src/lib/api.ts`
- **Backend Auth**: `backend/auth.py`
- **Backend Main**: `backend/main.py`

## Coexistence with Streamlit

The React app and Streamlit app coexist:

- **Streamlit**: `frontend/app.py` (run on port 8501)
  ```bash
  streamlit run frontend/app.py
  ```

- **React**: `web/` (run on port 5173)
  ```bash
  cd web && npm run dev
  ```

Both connect to the same FastAPI backend on port 8000.

## Next Steps

1. **Customize Styling**: Edit `web/tailwind.config.js` and `web/src/index.css`
2. **Add Features**: Create new pages in `web/src/pages/app/`
3. **Improve Auth**: Add OAuth providers in Supabase
4. **Add Analytics**: Integrate analytics service
5. **Deploy**: Follow production deployment guide

## Support

- **Backend API Docs**: `http://localhost:8000/docs`
- **Supabase Docs**: https://supabase.com/docs
- **React Router**: https://reactrouter.com/
- **Tailwind CSS**: https://tailwindcss.com/

## Summary

✅ React frontend with modern UI
✅ Supabase authentication with full flow
✅ Protected routes and JWT verification
✅ Professional design with custom palette
✅ Responsive mobile-friendly interface
✅ API integration with FastAPI backend
✅ Coexists with existing Streamlit app

The React app is now the main user-facing UI while Streamlit remains available as an alternative interface.

