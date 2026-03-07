#!/bin/bash
# Stop script for IHEE backend and frontend

echo "🛑 Stopping IHEE Investigation Engine..."
echo ""

# Stop backend (port 8000)
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "Stopping backend (port 8000)..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    echo "✓ Backend stopped"
else
    echo "• Backend not running"
fi

# Stop frontend (port 5173)
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo "Stopping frontend (port 5173)..."
    lsof -ti:5173 | xargs kill -9 2>/dev/null
    echo "✓ Frontend stopped"
else
    echo "• Frontend not running"
fi

# Clean up any Python processes running main.py
pkill -f "python3 main.py" 2>/dev/null

# Clean up any npm processes
pkill -f "vite" 2>/dev/null

echo ""
echo "✅ IHEE stopped"
echo ""
