#!/bin/bash
# Script de déploiement automatique pour Raspberry Pi
# À exécuter sur le Raspberry Pi

set -e

echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  🤖 RSI Trading Bot - Setup Raspberry Pi                    ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""

# Mise à jour du système
echo "📦 Mise à jour du système..."
sudo apt update && sudo apt upgrade -y

# Installation Python 3 et pip
echo "🐍 Installation de Python 3..."
sudo apt install -y python3 python3-pip python3-venv git

# Clone du repo (si pas déjà fait)
REPO_DIR="$HOME/RSI-BINANCE-BOT"
if [ ! -d "$REPO_DIR" ]; then
    echo "📥 Clone du repository..."
    cd $HOME
    git clone https://github.com/charlesbx/RSI-BINANCE-BOT.git
    cd $REPO_DIR
else
    echo "📂 Repository déjà présent, mise à jour..."
    cd $REPO_DIR
    git pull
fi

# Création de l'environnement virtuel
echo "🔧 Création de l'environnement virtuel..."
python3 -m venv venv
source venv/bin/activate

# Installation des dépendances
echo "📚 Installation des dépendances..."
pip install --upgrade pip
pip install -r requirements.txt

# Configuration du .env
if [ ! -f ".env" ]; then
    echo "⚙️  Configuration du fichier .env..."
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Éditez le fichier .env avec vos clés API Binance:"
    echo "   nano .env"
    echo ""
    read -p "Appuyez sur Entrée pour continuer après avoir configuré .env..."
fi

# Création du service systemd
echo "🔄 Création du service systemd pour auto-démarrage..."
sudo tee /etc/systemd/system/rsi-bot.service > /dev/null <<EOF
[Unit]
Description=RSI Trading Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$REPO_DIR
Environment="PATH=$REPO_DIR/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=$REPO_DIR/venv/bin/python $REPO_DIR/main.py --symbol ETHUSDT --balance 1000 --dashboard
Restart=always
RestartSec=10
StandardOutput=append:$REPO_DIR/logs/bot.log
StandardError=append:$REPO_DIR/logs/bot_error.log

[Install]
WantedBy=multi-user.target
EOF

# Création du répertoire logs
mkdir -p logs

# Activation du service
echo "✅ Activation du service..."
sudo systemctl daemon-reload
sudo systemctl enable rsi-bot.service

echo ""
echo "╔══════════════════════════════════════════════════════════════╗"
echo "║  ✅ Installation terminée !                                  ║"
echo "╚══════════════════════════════════════════════════════════════╝"
echo ""
echo "📋 Commandes utiles:"
echo ""
echo "  Démarrer le bot:"
echo "    sudo systemctl start rsi-bot"
echo ""
echo "  Arrêter le bot:"
echo "    sudo systemctl stop rsi-bot"
echo ""
echo "  Redémarrer le bot:"
echo "    sudo systemctl restart rsi-bot"
echo ""
echo "  Voir le status:"
echo "    sudo systemctl status rsi-bot"
echo ""
echo "  Voir les logs en temps réel:"
echo "    tail -f logs/bot.log"
echo ""
echo "  Dashboard accessible sur:"
echo "    http://$(hostname -I | awk '{print $1}'):5000"
echo ""
echo "💡 Le bot démarrera automatiquement au démarrage du Raspberry Pi"
echo ""
