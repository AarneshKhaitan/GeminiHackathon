#!/bin/bash
# Quick start script for IHEE backend and frontend

echo "🚀 Starting IHEE Investigation Engine..."
echo ""

# Check if backend port is free
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 8000 is already in use. Killing existing process..."
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    sleep 1
fi

# Check if frontend port is free
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Port 5173 is already in use. Killing existing process..."
    lsof -ti:5173 | xargs kill -9 2>/dev/null
    sleep 1
fi

# Start backend
echo "📡 Starting backend server (port 8000)..."
cd backend
source ../venv/bin/activate
python3 main.py > /tmp/ihee-backend.log 2>&1 &
BACKEND_PID=$!
cd ..

sleep 2

# Check if backend started successfully
if curl -s http://localhost:8000/docs > /dev/null 2>&1; then
    echo "✓ Backend running (PID: $BACKEND_PID)"
else
    echo "✗ Backend failed to start. Check /tmp/ihee-backend.log"
    exit 1
fi

# Start frontend
echo "🎨 Starting frontend dev server (port 5173)..."
cd frontend
npm run dev > /tmp/ihee-frontend.log 2>&1 &
FRONTEND_PID=$!
cd ..

sleep 3

# Check if frontend started successfully
if curl -s http://localhost:5173 > /dev/null 2>&1; then
    echo "✓ Frontend running (PID: $FRONTEND_PID)"
else
    echo "✗ Frontend failed to start. Check /tmp/ihee-frontend.log"
    kill $BACKEND_PID 2>/dev/null
    exit 1
fi

echo ""
echo "✅ IHEE is running!"
echo ""
echo "📍 URLs:"
echo "   Frontend: http://localhost:5173"
echo "   Backend:  http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "📊 Available triggers:"
echo "   • Silicon Valley Bank (SIVB) - 4.2σ"
echo "   • Credit Suisse (CS) - 3.8σ ✓ Recommended"
echo "   • First Republic Bank (FRC) - 5.1σ"
echo ""
echo "🎮 Frontend modes:"
echo "   • MOCK: Instant playback (pre-recorded)"
echo "   • LIVE: Real-time investigation (8-12 min)"
echo ""
echo "📝 Process IDs:"
echo "   Backend: $BACKEND_PID"
echo "   Frontend: $FRONTEND_PID"
echo ""
echo "🛑 To stop:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo ""
echo "📜 Logs:"
echo "   Backend:  /tmp/ihee-backend.log"
echo "   Frontend: /tmp/ihee-frontend.log"
echo ""
