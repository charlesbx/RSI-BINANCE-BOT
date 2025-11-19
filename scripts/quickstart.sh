#!/bin/bash
# Quick Start Script for RSI Trading Bot

set -e  # Exit on error

echo "=========================================="
echo "🚀 RSI Trading Bot - Quick Start"
echo "=========================================="
echo ""

# Check Python version
echo "📌 Checking Python version..."
python3 --version || { echo "❌ Python 3 is not installed"; exit 1; }

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "📥 Installing dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Creating from template..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Please edit .env with your Binance API credentials"
    echo "   Then run this script again."
    exit 1
fi

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p logs data/reports

echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "You can now run the bot with:"
echo ""
echo "  # Interactive mode (recommended for first-time users)"
echo "  python main.py --interactive"
echo ""
echo "  # Quick start with default settings (simulation)"
echo "  python main.py --symbol ETHUSDT --balance 1000 --simulate"
echo ""
echo "  # View all options"
echo "  python main.py --help"
echo ""
echo "📊 Dashboard will be available at: http://localhost:5000"
echo ""
echo "⚠️  Remember to configure your .env file with API credentials!"
echo ""
