#!/bin/bash
# Launch bot with integrated dashboard

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚀 RSI Trading Bot - Lancement Complet                     ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé."
    echo "   Exécutez d'abord: ./scripts/quickstart.sh"
    exit 1
fi

# Activate venv
source venv/bin/activate

echo "🤖 Lancement du bot avec dashboard intégré..."
echo ""
echo "┌──────────────────────────────────────────────────────────────┐"
echo "│  Bot + Dashboard dans un seul processus                     │"
echo "│  Accédez au dashboard sur http://localhost:5000             │"
echo "└──────────────────────────────────────────────────────────────┘"
echo ""

# Launch bot with dashboard
python main.py --interactive --dashboard
