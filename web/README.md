# React Frontend for Ollama RAG

A modern React application with Supabase authentication for the Ollama RAG system.

## Features

- 🔐 **Supabase Authentication**: Full auth flow with signup, login, password reset
- 🛡️ **Protected Routes**: Secure pages requiring authentication
- 🎨 **Modern UI**: Professional design with custom color palette
- 📱 **Responsive**: Mobile-friendly interface
- 🚀 **Fast**: Built with Vite for optimal performance
- 🎭 **Animations**: Smooth transitions with Framer Motion

## Tech Stack

- **React 18** with TypeScript
- **Vite** for build tooling
- **React Router** for routing
- **Supabase** for authentication
- **Axios** for API calls
- **Tailwind CSS** for styling
- **Zustand** for state management
- **Framer Motion** for animations
- **React Toastify** for notifications
- **Lucide React** for icons

## Setup

### 1. Install Dependencies

```bash
cd web
npm install
```

### 2. Configure Environment

Create a `.env` file in the `web/` directory:

```env
# Supabase Configuration
VITE_SUPABASE_URL=https://mukkyaabgfhwcnvxbacp.supabase.co
VITE_SUPABASE_ANON_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im11a2t5YWFiZ2Zod2NudnhiYWNwIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI3NjgxNzQsImV4cCI6MjA3ODM0NDE3NH0.qFwUYobkzctNFBBuhoCAcAHNXmCx_z-HvHu5d3LazK4

# API Configuration
VITE_API_BASE_URL=http://localhost:8000
```

**IMPORTANT**: Never include the Supabase SERVICE_ROLE key in the frontend `.env` file!

### 3. Configure Supabase

In your Supabase Dashboard:

1. Go to **Authentication → URL Configuration**
2. Add these redirect URLs:
   - `http://localhost:5173/auth/callback`
   - `http://localhost:5173/auth/reset`
   - (Add your production URLs when deploying)

3. Configure **SMTP Settings** for email verification:
   - Go to **Authentication → Email Templates**
   - Enable and configure email provider

### 4. Start Development Server

```bash
npm run dev
```

The app will run at `http://localhost:5173`

## Project Structure

```
web/
├── src/
│   ├── components/
│   │   ├── ui/              # Reusable UI components
│   │   ├── layout/          # Layout components (AppShell)
│   │   └── ProtectedRoute.tsx
│   ├── contexts/
│   │   └── AuthContext.tsx  # Authentication context
│   ├── lib/
│   │   ├── api.ts          # API client
│   │   └── supabase.ts     # Supabase client
│   ├── pages/
│   │   ├── auth/           # Auth pages (login, signup, etc.)
│   │   └── app/            # Protected app pages
│   ├── App.tsx             # Main app with routing
│   ├── main.tsx            # Entry point
│   └── index.css           # Global styles
├── public/
├── index.html
├── vite.config.ts
├── tailwind.config.js
└── package.json
```

## Color Palette

- **Primary**: `#14FFEC` - Cyan accent for emphasis
- **Secondary**: `#0D7377` - Teal for buttons and highlights
- **Dark**: `#323232` - Card backgrounds
- **Background**: `#212121` - Main background

## Pages

### Authentication Pages
- `/auth/login` - Login page
- `/auth/signup` - Signup with email verification
- `/auth/forgot-password` - Request password reset
- `/auth/reset` - Reset password with token
- `/auth/callback` - Email verification callback

### Protected Pages
- `/app/kb` - Knowledge Bases management
- `/app/upload` - Upload documents
- `/app/index` - Index documents
- `/app/chat` - Chat with RAG
- `/app/settings` - App settings and health check

## Authentication Flow

1. **Signup**: User creates account → Receives verification email → Clicks link → Redirects to app
2. **Login**: User enters credentials → Authenticated → Redirects to Knowledge Bases
3. **Password Reset**: User requests reset → Receives email → Clicks link → Sets new password → Redirects to login

## API Integration

The frontend communicates with the FastAPI backend using JWT tokens:

- All API requests include `Authorization: Bearer <token>` header
- Token is automatically attached by Axios interceptor
- 401 responses trigger automatic redirect to login

## Development

### Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

### Adding New Pages

1. Create page component in `src/pages/app/`
2. Add route in `src/App.tsx`
3. Add navigation link in `src/components/layout/AppShell.tsx`

### Styling

- Use Tailwind utility classes
- Custom components in `src/components/ui/`
- Global styles in `src/index.css`
- Theme configuration in `tailwind.config.js`

## Deployment

### Build for Production

```bash
npm run build
```

Output will be in `dist/` directory.

### Environment Variables for Production

Update your production environment with:
- Production Supabase URL and Anon Key
- Production API Base URL
- Add production redirect URLs to Supabase Dashboard

### Deploy Options

- **Vercel**: Connect GitHub repo, auto-deploys
- **Netlify**: Drag & drop `dist/` folder
- **AWS S3 + CloudFront**: Static hosting
- **Any static host**: Upload `dist/` contents

## Troubleshooting

### Email Verification Not Working
- Check Supabase SMTP configuration
- Verify redirect URLs in Supabase Dashboard
- Check spam folder

### 401 Errors
- Ensure backend has correct Supabase configuration
- Check that JWT token is being sent in headers
- Verify Supabase URL matches between frontend and backend

### CORS Errors
- Ensure backend has CORS middleware configured
- Check API base URL in `.env`

## Support

For issues or questions, check:
- Backend API docs: `http://localhost:8000/docs`
- Supabase docs: https://supabase.com/docs
- React Router docs: https://reactrouter.com/

