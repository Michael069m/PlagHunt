#!/bin/bash

# Plagiarism Detection API Startup Script

echo "🚀 Starting Plagiarism Detection API..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please set up your Python environment first."
    exit 1
fi

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  GEMINI_API_KEY environment variable not set."
    echo "Please set it with: export GEMINI_API_KEY='your_api_key_here'"
    exit 1
fi

# Activate virtual environment and start the API
echo "🔧 Activating virtual environment..."
source .venv/bin/activate

echo "🌐 Starting Flask API server on http://localhost:5000..."
echo "📊 Ready to detect plagiarism!"
echo "🛑 Press Ctrl+C to stop the server"
echo ""

python api.py
