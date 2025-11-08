#!/bin/bash
# Railway startup script

echo "Starting application..."
echo "Python version:"
python --version

echo "Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

echo "Starting FastAPI server on port $PORT..."
uvicorn main:app --host 0.0.0.0 --port $PORT
