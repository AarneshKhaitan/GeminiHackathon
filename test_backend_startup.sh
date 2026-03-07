#!/bin/bash
cd "/Users/I772786/Desktop/gemini hackathon/backend"
source ../venv/bin/activate
python3 main.py > /tmp/backend.log 2>&1 &
BACKEND_PID=$!
sleep 3
curl -s http://localhost:8000/docs > /dev/null && echo "✓ Backend server is running" || echo "✗ Backend server failed to start"
echo ""
echo "=== Backend logs ==="
cat /tmp/backend.log
kill $BACKEND_PID 2>/dev/null || true
