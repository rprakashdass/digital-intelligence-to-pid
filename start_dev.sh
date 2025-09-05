#!/bin/bash

echo "Starting P&ID Analyzer Development Environment"
echo "============================================="

echo ""
echo "1. Starting Backend Server..."
cd backend
uvicorn main:app --reload --port 8000 &
BACKEND_PID=$!

echo ""
echo "2. Waiting 3 seconds for backend to start..."
sleep 3

echo ""
echo "3. Starting Frontend Server..."
cd ../frontend
pnpm run dev &
FRONTEND_PID=$!

echo ""
echo "Development servers are starting..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:5173"
echo ""
echo "Press Ctrl+C to stop both servers"

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "Stopping servers..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait
