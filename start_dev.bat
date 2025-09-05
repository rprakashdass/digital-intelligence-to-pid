@echo off
echo P^&ID Analyzer - Smart Diagram Analysis
echo ======================================

echo Step 1: Installing required packages...
pip install torch torchvision ultralytics fastapi uvicorn sentence-transformers openai
echo.

echo Step 2: Initializing YOLO model...
python backend\initialize_yolo.py

echo.
echo Step 3: Starting Backend Server...
start "Backend Server" cmd /k "python -m uvicorn backend.main:app --reload --port 8000"

echo.
echo Step 4: Waiting 3 seconds for backend to start...
timeout /t 3 /nobreak > nul

echo.
echo Step 5: Starting Frontend Server...
start "Frontend Server" cmd /k "cd frontend && npm install && npm run dev"

echo.
echo ======================================
echo Development servers are starting:
echo.
echo Backend API: http://localhost:8000
echo Frontend UI: http://localhost:5173
echo.
echo Usage:
echo 1. Upload a P^&ID diagram using the "Upload P^&ID" button
echo 2. Click "Analyze" to process the diagram
echo 3. Use the "Smart Q^&A" tab to ask questions about the diagram
echo ======================================
echo.
echo Press any key to exit this launcher (servers will continue running)...
pause > nul
