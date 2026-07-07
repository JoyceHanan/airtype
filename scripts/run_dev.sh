#!/usr/bin/env bash

# ==============================================================================
# AirType Service Runner
# Starts all services concurrently in hot-reload modes.
# ==============================================================================

set -euo pipefail

echo "========================================="
echo "Starting AirType Services in Dev Mode..."
echo "========================================="

# Helper to terminate background processes on exit
cleanup() {
    echo -e "\nShutting down all services..."
    kill "$SERVER_PID" 2>/dev/null || true
    kill "$ML_PID" 2>/dev/null || true
    kill "$CLIENT_PID" 2>/dev/null || true
    exit 0
}

trap cleanup SIGINT SIGTERM EXIT

# 1. Start ML-Service
echo "Starting Python ML Service on port 8000..."
cd ml-service
source venv/bin/activate
uvicorn src.main:app --port 8000 --reload &
ML_PID=$!
deactivate
cd ..

# 2. Start Server Gateway
echo "Starting Node.js Express Gateway on port 5000..."
cd server
npm run dev &
SERVER_PID=$!
cd ..

# 3. Start React Client
echo "Starting React Client on port 3000..."
cd client
npm start &
CLIENT_PID=$!
cd ..

# Keep script running
wait
