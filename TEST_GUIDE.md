# 🧪 Guide de Test du Projet

Ce guide vous aide à tester facilement le bot de trading RSI.

## 🚀 Tests Rapides

### 1. Test des Indicateurs Techniques

```bash
python test_indicators.py
```

**Ce test vérifie:**
- ✅ Calcul du RSI
- ✅ Moyennes mobiles (SMA, EMA)
- ✅ MACD
- ✅ Bandes de Bollinger

**Durée:** ~2 secondes

---

### 2. Demo Bot (Sans API Binance)

Le bot démo simule des prix de marché et teste la stratégie RSI **sans utiliser d'argent réel**.

```bash
# Demo rapide (30 itérations)
python test_demo.py --iterations 30 --speed 0.3

# Demo complète (100 itérations)
python test_demo.py --iterations 100 --speed 0.5

# Demo longue (personnalisée)
python test_demo.py --symbol BTCUSDT --balance 5000 --iterations 200 --speed 0.2
```

**Options disponibles:**
- `--symbol` : Paire de trading (ETHUSDT, BTCUSDT, etc.)
- `--balance` : Balance initiale en USD
- `--iterations` : Nombre de cycles de simulation
- `--speed` : Délai entre chaque cycle (en secondes)

**Ce que vous verrez:**
```
🤖 RSI Trading Bot - DEMO MODE
Symbol: ETHUSDT
Initial Balance: $1,000.00
Strategy: RSI (14 period, 30/70 levels)

[16:58:33] Price: $2,500.00 | RSI: 50.00 | Balance: $1,000.00
    🟢 BUY 0.380000 @ $2,480.00 (RSI: 28.50)
[16:58:40] Price: $2,550.00 | RSI: 72.30 | Position: +2.82% ($70.00)
    🔴 SELL 0.380000 @ $2,550.00 | P&L: $26.60 (+1.07%) (RSI overbought)
```

**Durée:** Variable selon les paramètres

---

### 3. Tests Unitaires

```bash
# Tous les tests
pytest tests/ -v

# Tests avec couverture de code
pytest tests/ --cov=src --cov-report=html

# Test spécifique
pytest tests/test_strategy.py -v
```

**Durée:** ~5 secondes

---

### 4. Suite de Tests Complète

Lance tous les tests d'un coup :

```bash
./scripts/run_tests.sh
```

**Cette suite exécute:**
1. ✅ Tests des indicateurs techniques
2. ✅ Tests unitaires avec pytest
3. ✅ Demo bot (20 itérations rapides)

**Durée:** ~30 secondes

---

## 🔧 Test en Mode Simulation (Avec API Binance)

Le mode simulation utilise les **vraies données de marché** Binance mais **ne passe PAS d'ordres réels**.

### Configuration requise:

1. **Créer un compte Binance** (si pas déjà fait)
2. **Obtenir les clés API:**
   - Allez sur [Binance API Management](https://www.binance.com/en/my/settings/api-management)
   - Créez une nouvelle API
   - ✅ Activez: "Read Info"
   - ❌ Désactivez: "Enable Trading" et "Enable Withdrawals"
   - Copiez API Key et Secret

3. **Configurer .env:**

```bash
nano .env
```

Ajoutez vos clés:

```env
BINANCE_API_KEY=votre_api_key
BINANCE_API_SECRET=votre_api_secret
SIMULATION_MODE=true
```

### Lancer le bot en mode simulation:

```bash
# Mode interactif (recommandé)
python main.py --interactive

# Mode automatique
python main.py --symbol ETHUSDT --balance 1000 --simulate
```

**Avantages:**
- 📊 Données de marché réelles
- 🔒 Aucun risque financier
- 📈 Test de la stratégie en conditions réelles

---

## 🎯 Scénarios de Test Recommandés

### Scénario 1: Test Basique
```bash
# Test rapide des indicateurs
python test_indicators.py

# Demo rapide
python test_demo.py --iterations 20 --speed 0.1
```

**Temps total:** ~5 secondes  
**Objectif:** Vérifier que tout fonctionne

---

### Scénario 2: Test de Stratégie
```bash
# Demo longue avec différents paramètres
python test_demo.py --iterations 100 --speed 0.3

# Regarder les statistiques finales
```

**Temps total:** ~30 secondes  
**Objectif:** Analyser le comportement de la stratégie RSI

---

### Scénario 3: Test Complet (Sans API)
```bash
# Suite de tests complète
./scripts/run_tests.sh
```

**Temps total:** ~30 secondes  
**Objectif:** Validation complète du code

---

### Scénario 4: Test en Conditions Réelles
```bash
# Configurer .env avec vos clés API
nano .env

# Lancer en mode simulation
python main.py --interactive
```

**Temps total:** Selon votre durée de test  
**Objectif:** Test avec vraies données de marché

---

## 📊 Interpréter les Résultats

### Demo Bot - Résumé Final

```
📊 DEMO SUMMARY
Initial Balance: $1,000.00
Final Balance:   $1,050.25
Total Return:    $50.25 (+5.02%)

Total Trades:    10
Winning Trades:  7
Losing Trades:   3
Win Rate:        70.0%

Average P&L:     $5.02
Best Trade:      $25.50 (+2.55%)
Worst Trade:     -$10.20 (-1.02%)
```

**Analyse:**
- ✅ **Win Rate > 60%** : Bonne stratégie
- ✅ **Average P&L > 0** : Rentable
- ⚠️  **Win Rate < 40%** : Ajuster les paramètres RSI
- ❌ **Total Return < 0** : Stratégie à revoir

---

## 🐛 Dépannage

### Erreur: "Module not found"
```bash
# Réinstaller les dépendances
pip install -r requirements.txt
```

### Erreur: "No module named 'pandas_ta'"
```bash
# Installer pandas-ta
pip install pandas pandas-ta
```

### Le bot demo ne trouve/vend jamais
```bash
# RSI trop restrictif, assouplir les seuils
python test_demo.py --iterations 100 --speed 0.2
# Modifiez dans test_demo.py:
# rsi_oversold = 35 (au lieu de 30)
# rsi_overbought = 65 (au lieu de 70)
```

### Tests pytest échouent
```bash
# Vérifier l'environnement
python --version  # Doit être >= 3.8
pip list | grep pytest

# Réinstaller pytest
pip install --upgrade pytest pytest-cov
```

---

## 📈 Prochaines Étapes

Après avoir testé avec succès:

1. **Optimiser les paramètres:**
   - Testez différentes valeurs de RSI (14, 21 périodes)
   - Ajustez les seuils (25/75, 30/70, 35/65)

2. **Backtesting:**
   - Téléchargez des données historiques
   - Testez sur plusieurs mois de données

3. **Paper Trading:**
   - Mode simulation avec vraies données
   - Laissez tourner 1-2 semaines

4. **Trading Réel (⚠️ ATTENTION):**
   - Commencez avec des petits montants
   - Surveillez de près
   - N'investissez que ce que vous pouvez perdre

---

## ✅ Checklist de Test

Avant de passer en mode réel:

- [ ] ✅ Tous les tests unitaires passent
- [ ] ✅ Demo bot génère des profits sur 100+ itérations
- [ ] ✅ Mode simulation testé avec vraies données (1+ semaine)
- [ ] ✅ Logs examinés et compris
- [ ] ✅ Dashboard testé et fonctionnel
- [ ] ✅ Notifications email fonctionnent (si configurées)
- [ ] ✅ Stop-loss et take-profit validés
- [ ] ✅ Stratégie documentée et comprise
- [ ] ✅ Plan de gestion des risques établi

---

## 📞 Besoin d'Aide?

- 📖 **Documentation:** Consultez `/docs`
- 🐛 **Bugs:** Ouvrez une issue sur GitHub
- 💬 **Questions:** Discussions GitHub

**Happy Testing! 🧪🚀**
