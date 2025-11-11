@echo off
REM Setup script for Windows
echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Installing dependencies...
pip install --upgrade pip
pip install -r requirements.txt

echo.
echo Setup complete!
echo.
echo To activate the virtual environment in the future, run:
echo   venv\Scripts\activate.bat
echo.
echo To start the backend:
echo   uvicorn backend.main:app --reload --port 8000
echo.
echo To start the frontend:
echo   streamlit run frontend/app.py
echo.
pause

