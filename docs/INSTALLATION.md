# Installation Guide

## System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux
- **RAM**: Minimum 512MB
- **Internet**: Stable internet connection required
- **Binance Account**: Required for trading

## Step-by-Step Installation

### 1. Prerequisites

#### Install Python

**Windows:**
- Download Python from [python.org](https://www.python.org/downloads/)
- During installation, check "Add Python to PATH"
- Verify installation:
  ```cmd
  python --version
  ```

**macOS:**
```bash
# Using Homebrew
brew install python3

# Verify
python3 --version
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv

# Verify
python3 --version
```

#### Install TA-Lib (Required for Technical Indicators)

**Windows:**
1. Download TA-Lib wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#ta-lib)
2. Install: `pip install TA_Lib-0.4.XX-cpXX-cpXX-win_amd64.whl`

Or use the binary package:
```bash
pip install talib-binary
```

**macOS:**
```bash
brew install ta-lib
pip install TA-Lib
```

**Linux:**
```bash
# Install dependencies
sudo apt-get install build-essential wget

# Download and install TA-Lib
wget http://prdownloads.sourceforge.net/ta-lib/ta-lib-0.4.0-src.tar.gz
tar -xzf ta-lib-0.4.0-src.tar.gz
cd ta-lib/
./configure --prefix=/usr
make
sudo make install

# Install Python wrapper
pip install TA-Lib
```

### 2. Clone or Download the Project

**Option A: Using Git**
```bash
git clone https://github.com/yourusername/RSI-BINANCE-BOT.git
cd RSI-BINANCE-BOT
```

**Option B: Download ZIP**
1. Download the ZIP file from GitHub
2. Extract to a folder
3. Open terminal/command prompt in that folder

### 3. Run Quick Start Script

**Linux/macOS:**
```bash
chmod +x scripts/quickstart.sh
./scripts/quickstart.sh
```

**Windows:**
```cmd
scripts\quickstart.bat
```

This script will:
- Create a virtual environment
- Install all dependencies
- Create necessary directories
- Set up configuration template

### 4. Configure API Credentials

1. **Get Binance API Keys**
   - Go to [Binance](https://www.binance.com/)
   - Login → API Management
   - Create API Key
   - Enable "Read Info" and "Enable Spot & Margin Trading"
   - **Disable** "Enable Withdrawals" for safety
   - Save your API Key and Secret

2. **Set Up Email (Optional but recommended)**
   - If using Gmail, enable 2FA
   - Generate App Password: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)

3. **Edit `.env` file**
   ```env
   # Binance API
   BINANCE_API_KEY=your_api_key_here
   BINANCE_API_SECRET=your_api_secret_here
   
   # Email Notifications
   SMTP_EMAIL=your_email@gmail.com
   SMTP_PASSWORD=your_16_char_app_password
   NOTIFICATION_EMAIL=destination@gmail.com
   
   # Bot Configuration
   SIMULATION_MODE=true
   ```

### 5. Test Installation

```bash
# Activate virtual environment
source venv/bin/activate  # Linux/macOS
# or
venv\Scripts\activate  # Windows

# Test configuration
python -c "from config.settings import AppConfig; print('✓ Configuration OK')"

# Run tests
pytest tests/

# Start bot in simulation mode
python main.py --symbol ETHUSDT --balance 1000 --simulate
```

## Manual Installation (Alternative)

If the quick start script doesn't work:

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment
```bash
# Linux/macOS
source venv/bin/activate

# Windows
venv\Scripts\activate
```

### 3. Upgrade pip
```bash
python -m pip install --upgrade pip
```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Create Directories
```bash
mkdir -p logs data/reports
```

### 6. Copy Environment Template
```bash
cp .env.example .env
```

### 7. Edit .env with your credentials

## Troubleshooting

### Common Issues

#### ImportError: No module named 'talib'

**Solution:**
```bash
pip install talib-binary
```

If that doesn't work, install TA-Lib manually (see Prerequisites section).

#### Permission Denied (Linux/macOS)

**Solution:**
```bash
chmod +x scripts/quickstart.sh
chmod +x main.py
```

#### Python not found

**Solution:**
- Ensure Python is installed
- Check it's in your PATH
- Try using `python3` instead of `python`

#### SSL Certificate Error

**Solution:**
```bash
pip install --upgrade certifi
```

Or on macOS:
```bash
/Applications/Python\ 3.X/Install\ Certificates.command
```

#### Binance API Error 401

**Solution:**
- Verify API keys are correct
- Check API key has required permissions
- Ensure system time is synchronized

#### Module 'websocket' not found

**Solution:**
```bash
pip uninstall websocket websocket-client
pip install websocket-client
```

## Verification

After installation, verify everything works:

```bash
# 1. Check Python packages
pip list | grep -E "binance|talib|flask"

# 2. Test configuration
python -c "from config.settings import AppConfig; AppConfig().initialize()"

# 3. Run tests
pytest

# 4. Test bot (simulation mode)
python main.py --symbol ETHUSDT --balance 100 --simulate
```

## Next Steps

1. **Read the Documentation**: Check `README.md` for usage instructions
2. **Test in Simulation**: Always test strategies in simulation mode first
3. **Start Small**: When going live, start with small amounts
4. **Monitor Logs**: Check `logs/trading_bot.log` regularly
5. **Use Dashboard**: Access at `http://localhost:5000`

## Getting Help

- **Documentation**: Check `docs/` folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/RSI-BINANCE-BOT/issues)
- **Logs**: Check `logs/trading_bot.log` for detailed error messages

## Uninstallation

To completely remove the bot:

```bash
# Deactivate virtual environment
deactivate

# Remove virtual environment
rm -rf venv/

# Remove log files (optional)
rm -rf logs/ data/

# Remove the project folder
cd ..
rm -rf RSI-BINANCE-BOT/
```

## Updating

To update to the latest version:

```bash
# Pull latest changes
git pull origin main

# Update dependencies
pip install -r requirements.txt --upgrade

# Run tests
pytest
```
