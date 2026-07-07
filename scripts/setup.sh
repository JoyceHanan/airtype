#!/usr/bin/env bash

# ==============================================================================
# AirType Multi-Environment Setup Script
# Installs dependencies across Client, Server, and ML-Service.
# ==============================================================================

set -euo pipefail

echo "========================================="
echo "Initializing AirType Project Environment"
echo "========================================="

# 1. Verify Prerequisites
echo "Checking dependencies..."
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is required. Install v18.x or v20.x."
    exit 1
fi

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is required. Install v3.10 or v3.11."
    exit 1
fi

echo "✔ Node.js version: $(node -v)"
echo "✔ Python version: $(python3 -V)"

# 2. Setup Client
echo -e "\nInstalling Client dependencies..."
cd client
npm install
cd ..

# 3. Setup Server
echo -e "\nInstalling Server dependencies..."
cd server
npm install
cd ..

# 4. Setup ML-Service
echo -e "\nSetting up ML-Service Python Virtual Environment..."
cd ml-service
python3 -m venv venv
# Source environment and install dependencies
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
deactivate
cd ..

# 5. Setup Local Config Env Files
echo -e "\nGenerating environment configurations..."
if [ ! -f .env ]; then
    echo "PORT=5000" > .env
    echo "ML_SERVICE_URL=http://localhost:8000" >> .env
    echo "✔ Created default root .env"
fi

echo -e "\n========================================="
echo "Setup Complete! Run './scripts/run_dev.sh' to start."
echo "========================================="
