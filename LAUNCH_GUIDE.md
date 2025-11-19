# 🚀 Guide: Lancer Bot + Dashboard

## Problème Résolu

Quand vous lancez le bot, il occupe le terminal et vous ne pouvez plus accéder au menu. Voici les solutions :

## 🎯 Solution 1: Scripts Séparés (Recommandé)

### Terminal 1 - Lancer le Bot
```bash
python main.py --interactive
```

### Terminal 2 - Lancer le Dashboard
```bash
python run_dashboard.py
```

### Accéder au Dashboard
Ouvrez votre navigateur: **http://localhost:5000**

---

## 🎯 Solution 2: Script Automatique

Lance bot + dashboard dans 2 terminaux automatiquement:

```bash
./launch_all.sh
```

Ce script:
- ✅ Lance le bot dans le terminal actuel
- ✅ Ouvre un nouveau terminal pour le dashboard
- ✅ Configure tout automatiquement

---

## 🎯 Solution 3: Menu Interactif Mis à Jour

```bash
python test_menu.py
```

**Nouvelles options:**
- **Option 7** : Lance SEULEMENT le bot (terminal bloqué)
- **Option 8** : Lance bot + dashboard (2 terminaux)
- **Option 9** : Lance SEULEMENT le dashboard (bot doit tourner ailleurs)

### Scénario typique:

1. **Première utilisation:**
   - Choisir option 8 → Lance tout automatiquement

2. **Dashboard seul:**
   - Bot déjà lancé dans un autre terminal
   - Choisir option 9 → Lance juste le dashboard

---

## 📊 Workflow Recommandé

### Pour le Développement / Test

```bash
# Terminal 1
python test_demo.py --iterations 100 --speed 0.5

# Terminal 2  
python run_dashboard.py

# Navigateur
http://localhost:5000
```

### Pour le Trading Réel

```bash
# Terminal 1 - Bot
python main.py --interactive

# Terminal 2 - Dashboard
python run_dashboard.py

# Terminal 3 - Logs (optionnel)
tail -f logs/trading_bot.log
```

---

## 🔧 Dépannage

### Dashboard ne se lance pas
```bash
# Vérifier que le port 5000 est libre
lsof -i:5000

# Si occupé, tuer le processus
kill -9 <PID>

# Ou changer le port dans .env
DASHBOARD_PORT=5001
```

### Bot ne se lance pas
```bash
# Vérifier les clés API
cat .env | grep BINANCE

# Tester en mode simulation
SIMULATION_MODE=true python main.py --interactive
```

### Nouveau terminal ne s'ouvre pas (launch_all.sh)
```bash
# Vérifier les terminaux disponibles
which gnome-terminal konsole xterm

# Ou lancer manuellement dans 2 terminaux séparés
```

---

## 💡 Astuces

### Utiliser tmux (recommandé pour serveurs)
```bash
# Installer tmux
sudo apt install tmux

# Créer une session
tmux new -s trading

# Terminal 1 (bot)
python main.py --interactive

# Créer nouveau panel (Ctrl+B puis ")
# Terminal 2 (dashboard)
python run_dashboard.py

# Détacher: Ctrl+B puis D
# Réattacher: tmux attach -t trading
```

### Utiliser screen
```bash
# Terminal 1
screen -S bot
python main.py --interactive
# Détacher: Ctrl+A puis D

# Terminal 2
screen -S dashboard
python run_dashboard.py
# Détacher: Ctrl+A puis D

# Réattacher
screen -r bot
screen -r dashboard
```

---

## 📋 Checklist Avant de Lancer

- [ ] ✅ Environnement virtuel activé
- [ ] ✅ Clés API configurées dans `.env`
- [ ] ✅ Port 5000 libre (ou PORT changé dans .env)
- [ ] ✅ Mode simulation testé d'abord
- [ ] ✅ 2 terminaux ouverts (ou tmux/screen)

---

## 🎉 C'est Parti !

**Méthode la plus simple:**
```bash
./launch_all.sh
```

**Ou manuellement:**
```bash
# Terminal 1
python main.py --interactive

# Terminal 2
python run_dashboard.py
```

**Dashboard:**
http://localhost:5000

**Happy Trading! 📈🚀**
