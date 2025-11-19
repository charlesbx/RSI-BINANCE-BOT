#!/bin/bash
# Quick demo script - Show all features in 1 minute

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🚀 RSI Trading Bot - DÉMONSTRATION RAPIDE (1 minute)       ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Check if venv exists
if [ ! -d "venv" ]; then
    echo "❌ Environnement virtuel non trouvé."
    echo "   Exécutez d'abord: ./scripts/quickstart.sh"
    exit 1
fi

# Activate venv
echo "📦 Activation de l'environnement virtuel..."
source venv/bin/activate

echo ""
echo "┌──────────────────────────────────────────────────────────────┐"
echo "│  1/3 - Test des Indicateurs Techniques (3 secondes)         │"
echo "└──────────────────────────────────────────────────────────────┘"
echo ""
sleep 1
python test_indicators.py

echo ""
echo "┌──────────────────────────────────────────────────────────────┐"
echo "│  2/3 - Demo Bot avec Prix Simulés (10 secondes)             │"
echo "└──────────────────────────────────────────────────────────────┘"
echo ""
sleep 1
python test_demo.py --iterations 15 --speed 0.5

echo ""
echo "┌──────────────────────────────────────────────────────────────┐"
echo "│  3/3 - Aperçu de la Structure du Projet                     │"
echo "└──────────────────────────────────────────────────────────────┘"
echo ""
sleep 1

echo "📁 Structure du projet:"
tree -L 2 -I 'venv|__pycache__|*.pyc|.git' 2>/dev/null || find . -maxdepth 2 -type d -not -path '*/venv/*' -not -path '*/.git/*' -not -path '*/__pycache__/*' | head -20

echo ""
echo "📊 Fichiers de test créés:"
ls -lh test_*.py 2>/dev/null | awk '{print "   ", $9, "-", $5}'

echo ""
echo "📚 Documentation disponible:"
ls -1 *.md 2>/dev/null | awk '{print "   •", $1}'

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║                  ✅ DÉMONSTRATION TERMINÉE                   ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "🎯 Prochaines étapes:"
echo ""
echo "   1. Tests interactifs:"
echo "      → python test_menu.py"
echo ""
echo "   2. Lire la documentation:"
echo "      → cat TESTING_SUMMARY.txt"
echo "      → cat TEST_GUIDE.md"
echo ""
echo "   3. Configurer et tester avec API:"
echo "      → nano .env"
echo "      → python main.py --interactive"
echo ""
echo "   4. Dashboard web:"
echo "      → http://localhost:5000"
echo ""
echo "📖 Documentation complète: README.md"
echo ""
