#!/bin/bash
# Setup script for Linux/Mac

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo ""
echo "Setup complete!"
echo ""
echo "To activate the virtual environment in the future, run:"
echo "  source venv/bin/activate"
echo ""
echo "To start the backend:"
echo "  uvicorn backend.main:app --reload --port 8000"
echo ""
echo "To start the frontend:"
echo "  streamlit run frontend/app.py"
echo ""

