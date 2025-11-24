#!/bin/bash
# Simple HTTP server for the dashboard

cd "$(dirname "$0")/../dashboard"

echo "🚀 Starting Market Research Dashboard..."
echo "📊 Dashboard will be available at: http://localhost:3000"
echo "🔧 Make sure the API is running at: http://localhost:8000"
echo ""
echo "Press Ctrl+C to stop"
echo ""

python3 -m http.server 3000
