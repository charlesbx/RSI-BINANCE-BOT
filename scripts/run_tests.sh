#!/bin/bash
# Run all tests for the RSI Trading Bot

echo "========================================"
echo "🧪 RSI Trading Bot - Test Suite"
echo "========================================"
echo ""

# Activate virtual environment
if [ -d "venv" ]; then
    echo "📦 Activating virtual environment..."
    source venv/bin/activate
else
    echo "⚠️  Virtual environment not found. Run quickstart.sh first!"
    exit 1
fi

# Test 1: Technical Indicators
echo ""
echo "========================================"
echo "Test 1: Technical Indicators"
echo "========================================"
python test_indicators.py
if [ $? -ne 0 ]; then
    echo "❌ Technical indicators test failed!"
    exit 1
fi

# Test 2: Unit Tests
echo ""
echo "========================================"
echo "Test 2: Unit Tests"
echo "========================================"
pytest tests/ -v --color=yes
if [ $? -ne 0 ]; then
    echo "❌ Unit tests failed!"
    exit 1
fi

# Test 3: Demo Bot
echo ""
echo "========================================"
echo "Test 3: Demo Bot (Quick Run)"
echo "========================================"
echo "Running 20 iterations with 0.1s delay..."
python test_demo.py --iterations 20 --speed 0.1
if [ $? -ne 0 ]; then
    echo "❌ Demo bot test failed!"
    exit 1
fi

# Summary
echo ""
echo "========================================"
echo "✅ ALL TESTS PASSED!"
echo "========================================"
echo ""
echo "Next steps:"
echo "1. Test full demo: python test_demo.py"
echo "2. Configure API keys in .env"
echo "3. Run bot: python main.py --interactive"
echo ""
