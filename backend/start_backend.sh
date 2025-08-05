#!/bin/bash

# Backend startup script for PlagHunt

echo "🚀 Starting PlagHunt Backend..."

# Check if we're in the right directory
if [ ! -f "requirements.txt" ]; then
    echo "❌ Error: Please run this script from the backend directory"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📚 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if MongoDB is running
echo "🔍 Checking MongoDB connection..."
if ! brew services list | grep -q "mongodb-community.*started"; then
    echo "⚠️  MongoDB not running. Starting MongoDB..."
    brew services start mongodb-community
    sleep 3
fi

# Check if config.env exists
if [ ! -f "config.env" ]; then
    echo "⚠️  config.env not found. Please create it from config.env.template"
    echo "📝 See README.md for configuration instructions"
fi

# Set environment variables
export FLASK_APP=app.py
export FLASK_ENV=development
export FLASK_DEBUG=True

# Start the Flask application
echo "🌟 Starting Flask application on http://localhost:5000"
echo "📊 API documentation available at http://localhost:5000/api/health"
echo "🛑 Press Ctrl+C to stop the server"

python app.py
