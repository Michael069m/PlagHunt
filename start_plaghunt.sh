#!/bin/bash

# Complete startup script for PlagHunt
# This script starts both backend and frontend

echo "🚀 Starting PlagHunt - Plagiarism Detection System"
echo "=================================================="

# Get the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BACKEND_DIR="$SCRIPT_DIR/backend"
FRONTEND_DIR="$SCRIPT_DIR/frontend"

# Function to check if a port is in use
check_port() {
    if lsof -Pi :$1 -sTCP:LISTEN -t >/dev/null ; then
        return 0
    else
        return 1
    fi
}

# Function to start backend
start_backend() {
    echo "🔧 Starting Backend..."
    cd "$BACKEND_DIR"
    
    # Make sure the startup script is executable
    chmod +x start_backend.sh
    
    # Start backend in background
    ./start_backend.sh &
    BACKEND_PID=$!
    
    echo "⏳ Waiting for backend to start..."
    sleep 10
    
    # Check if backend is running
    if check_port 5000; then
        echo "✅ Backend started successfully on http://localhost:5000"
    else
        echo "❌ Backend failed to start"
        exit 1
    fi
}

# Function to start frontend
start_frontend() {
    echo "🎨 Starting Frontend..."
    cd "$FRONTEND_DIR"
    
    # Make sure the startup script is executable
    chmod +x start_frontend.sh
    
    # Start frontend in background
    ./start_frontend.sh &
    FRONTEND_PID=$!
    
    echo "⏳ Waiting for frontend to start..."
    sleep 15
    
    # Check if frontend is running
    if check_port 5173; then
        echo "✅ Frontend started successfully on http://localhost:5173"
    else
        echo "❌ Frontend failed to start"
        exit 1
    fi
}

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down PlagHunt..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    echo "👋 Goodbye!"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Check if MongoDB is running
echo "🔍 Checking MongoDB..."
if ! brew services list | grep -q "mongodb-community.*started"; then
    echo "🔧 Starting MongoDB..."
    brew services start mongodb-community
    sleep 3
fi

# Start services
start_backend
start_frontend

echo ""
echo "🎉 PlagHunt is now running!"
echo "================================"
echo "🌐 Frontend: http://localhost:5173"
echo "🔗 Backend API: http://localhost:5000"
echo "📊 API Health: http://localhost:5000/api/health"
echo ""
echo "🛑 Press Ctrl+C to stop all services"
echo ""

# Wait for user to stop
wait
