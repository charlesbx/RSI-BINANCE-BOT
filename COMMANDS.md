# 🎯 Commandes Rapides

## 🧪 Tests (Sans API)

```bash
# Menu interactif de test
python test_menu.py

# Tests individuels
python test_indicators.py              # ~2s
python test_demo.py --iterations 30    # ~6s
pytest tests/ -v                       # ~3s

# Suite complète
./scripts/run_tests.sh                 # ~30s
```

## 🚀 Lancer le Bot

```bash
# Mode interactif (recommandé)
python main.py --interactive

# Mode simulation
python main.py --symbol ETHUSDT --balance 1000 --simulate

# Mode live (⚠️ argent réel)
python main.py --symbol ETHUSDT --balance 1000 --live
```

## 📊 Surveillance

```bash
# Dashboard web
http://localhost:5000

# Logs en temps réel
tail -f logs/trading_bot.log

# Rapports
ls -lh data/reports/
```

## 🛠️ Configuration

```bash
# Éditer configuration
nano .env

# Variables importantes
BINANCE_API_KEY=votre_clé
BINANCE_API_SECRET=votre_secret
SIMULATION_MODE=true
```

## 📚 Documentation

- [README.md](README.md) - Guide complet
- [TEST_GUIDE.md](TEST_GUIDE.md) - Guide de test détaillé
- [QUICKSTART.md](QUICKSTART.md) - Démarrage rapide
- [docs/TESTING.md](docs/TESTING.md) - Documentation tests
- [docs/INSTALLATION.md](docs/INSTALLATION.md) - Installation détaillée
- [docs/STRATEGY.md](docs/STRATEGY.md) - Explication stratégie
- [docs/API.md](docs/API.md) - Documentation API

## 🔧 Dépannage Rapide

```bash
# Réinstaller dépendances
pip install -r requirements.txt

# Vérifier Python
python --version  # Doit être >= 3.8

# Nettoyer et recréer venv
rm -rf venv
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Tester sans API
python test_demo.py --iterations 20 --speed 0.1
```

## ⚡ Raccourcis Utiles

```bash
# Test rapide complet
python test_indicators.py && python test_demo.py --iterations 20 --speed 0.1

# Monitoring rapide
tail -f logs/trading_bot.log | grep -E "BUY|SELL|ERROR"

# Statistiques des trades
grep -E "BUY|SELL" logs/trading_bot.log | wc -l

# Derniers trades
grep -E "BUY|SELL" logs/trading_bot.log | tail -10
```

## 📋 Checklist Avant Production

- [ ] ✅ Tests unitaires passent (`pytest tests/`)
- [ ] ✅ Demo bot profitable (`python test_demo.py --iterations 100`)
- [ ] ✅ Clés API configurées dans `.env`
- [ ] ✅ Mode simulation testé 1+ semaine
- [ ] ✅ Dashboard vérifié
- [ ] ✅ Logs compris et analysés
- [ ] ✅ Petit montant pour premiers trades réels
