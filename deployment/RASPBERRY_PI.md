# 🍓 Déploiement sur Raspberry Pi

Guide complet pour faire tourner le bot 24/7 sur Raspberry Pi.

## Prérequis

- Raspberry Pi (3, 4 ou 5) avec Raspberry Pi OS
- Connexion Internet stable
- Accès SSH ou clavier/écran connecté
- ~500MB d'espace disque libre

## Installation rapide (méthode automatique)

### 1. Se connecter au Raspberry Pi

```bash
# Depuis ton PC
ssh pi@raspberrypi.local
# Mot de passe par défaut: raspberry (à changer!)
```

### 2. Télécharger et exécuter le script d'installation

```bash
# Télécharger le script
wget https://raw.githubusercontent.com/charlesbx/RSI-BINANCE-BOT/main/deployment/raspberry_pi_setup.sh

# Rendre exécutable
chmod +x raspberry_pi_setup.sh

# Exécuter
./raspberry_pi_setup.sh
```

### 3. Configurer les clés API Binance

```bash
cd ~/RSI-BINANCE-BOT
nano .env
```

Remplir :
```env
BINANCE_API_KEY=votre_clé_api
BINANCE_API_SECRET=votre_clé_secrète
```

Sauvegarder avec `Ctrl+O`, `Enter`, `Ctrl+X`

### 4. Démarrer le bot

```bash
sudo systemctl start rsi-bot
sudo systemctl status rsi-bot
```

**C'est tout !** Le bot tourne maintenant 24/7 🚀

## Accéder au Dashboard

Depuis n'importe quel appareil sur ton réseau local :

```
http://IP_DU_RASPBERRY_PI:5000
```

Pour trouver l'IP :
```bash
hostname -I
```

## Commandes utiles

### Contrôle du bot

```bash
# Démarrer
sudo systemctl start rsi-bot

# Arrêter
sudo systemctl stop rsi-bot

# Redémarrer
sudo systemctl restart rsi-bot

# Statut
sudo systemctl status rsi-bot

# Désactiver le démarrage automatique
sudo systemctl disable rsi-bot

# Réactiver le démarrage automatique
sudo systemctl enable rsi-bot
```

### Logs

```bash
# Voir les logs en temps réel
tail -f ~/RSI-BINANCE-BOT/logs/bot.log

# Voir les 100 dernières lignes
tail -n 100 ~/RSI-BINANCE-BOT/logs/bot.log

# Voir les erreurs
tail -f ~/RSI-BINANCE-BOT/logs/bot_error.log
```

### Mise à jour du bot

```bash
cd ~/RSI-BINANCE-BOT

# Arrêter le bot
sudo systemctl stop rsi-bot

# Mettre à jour le code
git pull

# Mettre à jour les dépendances si nécessaire
source venv/bin/activate
pip install -r requirements.txt

# Redémarrer le bot
sudo systemctl start rsi-bot
```

## Installation manuelle (optionnel)

Si tu préfères tout faire à la main :

### 1. Installer les dépendances système

```bash
sudo apt update && sudo apt upgrade -y
sudo apt install -y python3 python3-pip python3-venv git
```

### 2. Cloner le repository

```bash
cd ~
git clone https://github.com/charlesbx/RSI-BINANCE-BOT.git
cd RSI-BINANCE-BOT
```

### 3. Créer l'environnement virtuel

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 4. Configurer le .env

```bash
cp .env.example .env
nano .env
# Remplir les clés API
```

### 5. Test manuel

```bash
python main.py --interactive --dashboard
```

### 6. Créer le service systemd

```bash
sudo nano /etc/systemd/system/rsi-bot.service
```

Contenu :
```ini
[Unit]
Description=RSI Trading Bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=pi
WorkingDirectory=/home/pi/RSI-BINANCE-BOT
Environment="PATH=/home/pi/RSI-BINANCE-BOT/venv/bin:/usr/local/bin:/usr/bin:/bin"
ExecStart=/home/pi/RSI-BINANCE-BOT/venv/bin/python /home/pi/RSI-BINANCE-BOT/main.py --symbol ETHUSDT --balance 1000 --dashboard
Restart=always
RestartSec=10
StandardOutput=append:/home/pi/RSI-BINANCE-BOT/logs/bot.log
StandardError=append:/home/pi/RSI-BINANCE-BOT/logs/bot_error.log

[Install]
WantedBy=multi-user.target
```

### 7. Activer le service

```bash
sudo systemctl daemon-reload
sudo systemctl enable rsi-bot
sudo systemctl start rsi-bot
```

## Optimisations pour Raspberry Pi

### Réduire la consommation de RAM

Éditer `config/settings.py` pour réduire le buffer de données :

```python
# Au lieu de stocker 1000 prix, stocker 200
MAX_PRICE_HISTORY = 200
```

### Désactiver l'interface graphique (optionnel)

Si tu utilises uniquement SSH :

```bash
sudo systemctl set-default multi-user.target
sudo reboot
```

Pour réactiver :
```bash
sudo systemctl set-default graphical.target
```

### Accès depuis l'extérieur (optionnel)

Pour accéder au dashboard depuis Internet :

1. **Configurer le port forwarding sur ta box** :
   - Port externe : 8080
   - Port interne : 5000
   - IP : celle du Raspberry Pi

2. **Utiliser Tailscale (recommandé)** :
```bash
curl -fsSL https://tailscale.com/install.sh | sh
sudo tailscale up
```

Accès sécurisé depuis n'importe où : `http://raspberry-pi-tailscale-ip:5000`

## Monitoring

### Surveiller la performance

```bash
# CPU et RAM
htop

# Température du Raspberry Pi
vcgencmd measure_temp

# Espace disque
df -h
```

### Alertes par email

Le bot envoie déjà des emails configurés dans `.env` :

```env
ENABLE_EMAIL_NOTIFICATIONS=true
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_EMAIL=votre_email@gmail.com
SMTP_PASSWORD=votre_mot_de_passe_app
EMAIL_TO=votre_email@gmail.com
```

## Sauvegarde automatique

Créer un script de backup :

```bash
nano ~/backup_bot.sh
```

Contenu :
```bash
#!/bin/bash
tar -czf ~/bot_backup_$(date +%Y%m%d).tar.gz \
    ~/RSI-BINANCE-BOT/.env \
    ~/RSI-BINANCE-BOT/logs/ \
    ~/RSI-BINANCE-BOT/data/
```

Ajouter à crontab (backup quotidien à 3h du matin) :
```bash
crontab -e
# Ajouter :
0 3 * * * ~/backup_bot.sh
```

## Dépannage

### Le bot ne démarre pas

```bash
# Vérifier les logs
sudo journalctl -u rsi-bot -n 50

# Vérifier les permissions
ls -la ~/RSI-BINANCE-BOT/

# Tester manuellement
cd ~/RSI-BINANCE-BOT
source venv/bin/activate
python main.py --interactive
```

### Problèmes de connexion Binance

```bash
# Vérifier la connexion Internet
ping -c 3 api.binance.com

# Vérifier les clés API dans .env
cat .env | grep BINANCE
```

### Le dashboard ne s'affiche pas

```bash
# Vérifier que le port 5000 est ouvert
sudo netstat -tuln | grep 5000

# Vérifier le firewall
sudo ufw status
sudo ufw allow 5000/tcp
```

## Consommation électrique

- Raspberry Pi 4 : ~3-5W
- Coût annuel : ~3-5€ (0,20€/kWh)
- ✅ Très économique pour un bot 24/7 !

## Sécurité

1. **Changer le mot de passe par défaut** :
```bash
passwd
```

2. **Configurer un pare-feu** :
```bash
sudo apt install ufw
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow ssh
sudo ufw allow 5000/tcp
sudo ufw enable
```

3. **Mettre à jour régulièrement** :
```bash
sudo apt update && sudo apt upgrade -y
```

4. **Utiliser des clés SSH au lieu du mot de passe**

---

**Besoin d'aide ?** Ouvre une issue sur GitHub !
