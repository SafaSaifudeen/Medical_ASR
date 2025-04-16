#!/bin/bash

# Text colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Function to display status messages
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}


# Start backend
print_status "Starting backend service..."
cd backend
if [ ! -d "venv" ]; then
    print_status "Creating virtual environment..."
    python -m venv venv
fi
source venv/Scripts/activate
pip install -r requirements.txt
python app.py &
BACKEND_PID=$!
cd ..

# Start frontend
print_status "Starting frontend service..."
cd frontend
npm install
yes | npm run start &
FRONTEND_PID=$!
cd ..

print_success "Services started successfully!"
print_status "Frontend will be available at: http://localhost:4200"
print_status "Backend will be available at: http://localhost:5001"
print_status ""
print_status "Press Ctrl+C to stop both services"

# Wait for user to press Ctrl+C
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait 