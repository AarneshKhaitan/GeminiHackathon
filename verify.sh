#!/bin/bash
# Comprehensive integration verification script

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  IHEE Integration Verification"
echo "  Iterative Hypothesis Elimination Engine"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

PASS=0
FAIL=0

# Helper functions
check_pass() {
    echo "✅ $1"
    PASS=$((PASS + 1))
}

check_fail() {
    echo "❌ $1"
    FAIL=$((FAIL + 1))
}

# 1. Check virtual environment
echo "📦 Checking Python environment..."
if [ -d "venv" ]; then
    check_pass "Virtual environment exists"
else
    check_fail "Virtual environment missing (run: python3 -m venv venv)"
fi

# 2. Check backend dependencies
echo ""
echo "🐍 Checking backend dependencies..."
source venv/bin/activate 2>/dev/null
if python3 -c "import fastapi, uvicorn, google.generativeai" 2>/dev/null; then
    check_pass "Backend dependencies installed"
else
    check_fail "Backend dependencies missing"
fi

# 3. Check frontend dependencies
echo ""
echo "📦 Checking frontend dependencies..."
if [ -d "frontend/node_modules" ]; then
    check_pass "Frontend dependencies installed"
else
    check_fail "Frontend dependencies missing (run: cd frontend && npm install)"
fi

# 4. Check environment configuration
echo ""
echo "⚙️  Checking configuration..."
if [ -f ".env" ]; then
    check_pass ".env file exists"
    if grep -q "GEMINI_API_KEY" .env; then
        check_pass "GEMINI_API_KEY configured"
    else
        check_fail "GEMINI_API_KEY not found in .env"
    fi
else
    check_fail ".env file missing"
fi

# 5. Check evidence corpus
echo ""
echo "📚 Checking evidence corpus..."
if [ -d "evidence/credit-suisse/structural" ]; then
    STRUCTURAL_COUNT=$(ls evidence/credit-suisse/structural/*.md 2>/dev/null | wc -l | tr -d ' ')
    check_pass "Credit Suisse structural evidence ($STRUCTURAL_COUNT files)"
else
    check_fail "Credit Suisse structural evidence missing"
fi

if [ -d "evidence/credit-suisse/empirical" ]; then
    EMPIRICAL_COUNT=$(ls evidence/credit-suisse/empirical/*.md 2>/dev/null | wc -l | tr -d ' ')
    check_pass "Credit Suisse empirical evidence ($EMPIRICAL_COUNT files)"
else
    check_fail "Credit Suisse empirical evidence missing"
fi

# 6. Check backend imports
echo ""
echo "🔍 Checking backend code..."
cd backend
if python3 -c "from main import app; print('OK')" 2>/dev/null | grep -q "OK"; then
    check_pass "Backend imports successfully"
else
    check_fail "Backend import errors"
fi
cd ..

# 7. Check if ports are available
echo ""
echo "🔌 Checking port availability..."
if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    check_pass "Port 8000 available (backend)"
else
    echo "⚠️  Port 8000 in use (will be cleared on start)"
fi

if ! lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    check_pass "Port 5173 available (frontend)"
else
    echo "⚠️  Port 5173 in use (will be cleared on start)"
fi

# 8. Check helper scripts
echo ""
echo "📜 Checking helper scripts..."
if [ -x "start.sh" ]; then
    check_pass "start.sh is executable"
else
    check_fail "start.sh not executable (run: chmod +x start.sh)"
fi

if [ -x "stop.sh" ]; then
    check_pass "stop.sh is executable"
else
    check_fail "stop.sh not executable (run: chmod +x stop.sh)"
fi

# Summary
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "  Results: $PASS passed, $FAIL failed"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 All checks passed! Ready to run."
    echo ""
    echo "To start the application:"
    echo "  ./start.sh"
    echo ""
    echo "Then open: http://localhost:5173"
    echo ""
    exit 0
else
    echo "⚠️  Some checks failed. Fix the issues above and try again."
    echo ""
    exit 1
fi
