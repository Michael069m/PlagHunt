#!/bin/bash

# Master setup script for PlagHunt

echo "🎯 PlagHunt Setup Script"
echo "========================"

# Check if we're in the project root
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "❌ Error: Please run this script from the project root directory"
    exit 1
fi

# Make scripts executable
echo "🔧 Making scripts executable..."
chmod +x backend/start_backend.sh
chmod +x frontend/start_frontend.sh

echo "📋 Setup Instructions:"
echo ""
echo "1. Make sure MongoDB is installed and running:"
echo "   brew install mongodb-community"
echo "   brew services start mongodb-community"
echo ""
echo "2. To start the backend:"
echo "   cd backend && ./start_backend.sh"
echo ""
echo "3. To start the frontend (in a new terminal):"
echo "   cd frontend && ./start_frontend.sh"
echo ""
echo "4. Open your browser to: http://localhost:5173"
echo ""
echo "✅ Setup complete! Follow the instructions above to start the application."

# Check if MongoDB is available
if command -v mongod &> /dev/null; then
    echo "✅ MongoDB is installed"
    if pgrep mongod > /dev/null; then
        echo "✅ MongoDB is running"
    else
        echo "⚠️  MongoDB is installed but not running. Start it with:"
        echo "   brew services start mongodb-community"
    fi
else
    echo "❌ MongoDB not found. Install it with:"
    echo "   brew tap mongodb/brew"
    echo "   brew install mongodb-community"
fi

# Check Node.js
if command -v node &> /dev/null; then
    NODE_VERSION=$(node --version)
    echo "✅ Node.js is installed: $NODE_VERSION"
else
    echo "❌ Node.js not found. Install it from: https://nodejs.org/"
fi

# Check Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    echo "✅ Python is installed: $PYTHON_VERSION"
else
    echo "❌ Python3 not found. Install it from: https://python.org/"
fi
