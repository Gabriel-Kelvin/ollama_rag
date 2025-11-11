@echo off
echo ================================================
echo Starting FastAPI Backend Server
echo ================================================
echo.

if not exist "venv" (
    echo [ERROR] Virtual environment not found.
    echo Please run setup_env.bat first.
    pause
    exit /b 1
)

call venv\Scripts\activate

echo Checking environment configuration...
if not exist "config.env" (
    if not exist ".env" (
        echo [WARNING] config.env or .env not found
        echo Using default configuration
        echo.
        echo For Supabase auth, please add to config.env:
        echo SUPABASE_URL=your_supabase_url
        echo SUPABASE_SERVICE_ROLE=your_service_role_key
        echo SUPABASE_JWT_SECRET=your_jwt_secret
        echo.
    )
)

echo Starting backend server...
echo Backend will be available at: http://localhost:8000
echo API docs at: http://localhost:8000/docs
echo.
uvicorn backend.main:app --reload --port 8000

pause

