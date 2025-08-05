#!/bin/bash

# Frontend startup script for PlagHunt

echo "🚀 Starting PlagHunt Frontend..."

# Check if we're in the right directory
if [ ! -f "package.json" ]; then
    echo "❌ Error: Please run this script from the frontend directory"
    exit 1
fi

# Install dependencies if node_modules doesn't exist
if [ ! -d "node_modules" ]; then
    echo "📦 Installing dependencies..."
    npm install
fi

# Check if React 19 is installed
REACT_VERSION=$(npm list react --depth=0 2>/dev/null | grep react@ | sed 's/.*react@//' | sed 's/ .*//')
echo "📱 React version: $REACT_VERSION"

echo "✅ Frontend setup complete!"
echo "🌟 Starting development server..."

# Start the development server
npm run dev
