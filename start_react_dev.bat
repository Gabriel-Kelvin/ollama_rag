@echo off
echo ================================================
echo Starting React Frontend Development Server
echo ================================================
echo.

cd web

if not exist ".env" (
    echo [ERROR] .env file not found in web/ directory
    echo.
    echo Please create web/.env with the following content:
    echo.
    echo VITE_SUPABASE_URL=https://mukkyaabgfhwcnvxbacp.supabase.co
    echo VITE_SUPABASE_ANON_KEY=your_anon_key_here
    echo VITE_API_BASE_URL=http://localhost:8000
    echo.
    echo See REACT_SETUP_GUIDE.md for details.
    pause
    exit /b 1
)

echo Checking dependencies...
if not exist "node_modules" (
    echo Installing dependencies...
    call npm install
)

echo.
echo Starting development server...
echo Frontend will be available at: http://localhost:5173
echo.
call npm run dev

pause

