# 🤖 RSI Trading Bot - Professional Binance Trading Bot

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A professional, production-ready cryptocurrency trading bot for Binance that uses RSI (Relative Strength Index) strategy with advanced risk management and real-time monitoring.

## ✨ Features

### 🎯 Core Features
- **RSI-Based Trading Strategy**: Automated buy/sell decisions based on RSI indicators
- **Oversold Intensity System**: Advanced signal detection based on RSI depth and duration
- **Adaptive Time-Based Exits**: Smart sell timing that adjusts to price trends
- **Advanced Risk Management**: Multiple stop-loss and take-profit strategies
- **Real-Time Monitoring**: Live dashboard for tracking bot performance
- **Simulation Mode**: Test strategies without risking real funds
- **Email Notifications**: Get alerts for trades and important events
- **Comprehensive Reporting**: Detailed HTML and text reports for all trades
- **WebSocket Integration**: Real-time market data from Binance

### 📊 Dashboard Features
- **Live Price & RSI Monitoring**
- **Oversold Intensity Tracking**: Real-time signal strength visualization
- **Current Position Tracking**
- **P&L Visualization**
- **Trading Statistics**
- **Performance Metrics**

### 🔐 Security & Safety
- **API Key Protection**: Environment-based configuration
- **Simulation Mode**: Test without real money
- **Error Handling**: Robust error handling and recovery
- **Logging**: Comprehensive logging for debugging and auditing

## 📁 Project Structure

```
RSI-BINANCE-BOT/
├── src/                          # Source code
│   ├── core/                     # Core bot functionality
│   │   ├── exchange_client.py   # Binance API wrapper
│   │   ├── trading_bot.py       # Main bot orchestrator
│   │   └── websocket_handler.py # WebSocket handler
│   ├── strategies/               # Trading strategies
│   │   └── rsi_strategy.py      # RSI strategy implementation
│   ├── indicators/               # Technical indicators
│   │   └── technical_indicators.py
│   ├── services/                 # Services
│   │   ├── notification_service.py  # Email notifications
│   │   └── report_service.py    # Report generation
│   ├── models/                   # Data models
│   │   └── trading_models.py    # Trade, Position, Stats models
│   └── utils/                    # Utility functions
│       └── helpers.py
├── dashboard/                    # Web dashboard
│   ├── backend/                  # Flask API
│   │   └── api.py
│   └── frontend/                 # HTML dashboard
│       └── index.html
├── config/                       # Configuration
│   └── settings.py              # Application settings
├── tests/                        # Unit tests
├── docs/                         # Documentation
├── logs/                         # Log files
├── data/                         # Data & reports
│   └── reports/                 # Trading reports
├── main.py                       # Main entry point
├── requirements.txt              # Python dependencies
├── .env.example                  # Environment variables template
└── README.md                     # This file
```

## 🚀 Quick Start

### Prerequisites

- Python 3.8 or higher
- Binance account with API keys
- (Optional) Gmail account for email notifications

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/charlesbx/RSI-BINANCE-BOT.git
cd RSI-BINANCE-BOT
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
# Edit .env with your credentials
```

5. **Test the installation**
```bash
# Quick test (no API keys needed)
python test_menu.py

# Or run individual tests
python test_indicators.py
python test_demo.py --iterations 30
```

See [TEST_GUIDE.md](TEST_GUIDE.md) for detailed testing instructions.

### Configuration

Edit the `.env` file with your credentials:

```env
# Binance API (Required)
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here

# Email Notifications (Optional)
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_app_password
NOTIFICATION_EMAIL=destination@gmail.com

# Trading Configuration
SIMULATION_MODE=true  # Set to false for real trading
DEFAULT_TRADE_SYMBOL=ETHUSDT
DEFAULT_TRADE_QUANTITY=1000
```

## 📖 Usage

### Interactive Mode (Recommended for beginners)

```bash
python main.py --interactive
```

This will prompt you for all necessary parameters.

### Command Line Mode

```bash
# Basic usage with defaults
python main.py --symbol ETHUSDT --balance 1000

# With dashboard
python main.py --symbol ETHUSDT --balance 1000 --dashboard

# Custom RSI parameters
python main.py --symbol BTCUSDT --balance 5000 --rsi-period 14 --rsi-overbought 75 --rsi-oversold 25

# Simulation mode (default)
python main.py --symbol ETHUSDT --balance 1000 --simulate

# Live trading (CAUTION: Real money!)
python main.py --symbol ETHUSDT --balance 1000 --live --dashboard
```

### Available Options

```
Options:
  -h, --help            Show help message
  --symbol SYMBOL       Trading pair (e.g., ETHUSDT, BTCUSDT)
  --balance BALANCE     Initial balance in quote currency
  --rsi-period N        RSI period (default: 14)
  --rsi-overbought N    RSI overbought level (default: 70)
  --rsi-oversold N      RSI oversold level (default: 30)
  --simulate            Run in simulation mode
  --live                Run in LIVE mode (real trades)
  --interactive         Interactive mode
  --dashboard           Launch dashboard server with bot
  --no-email            Disable email notifications
  --log-level LEVEL     Set logging level (DEBUG, INFO, WARNING, ERROR)
```

## 🌐 Dashboard

The bot includes a beautiful web dashboard for real-time monitoring.

### Starting the Dashboard

The dashboard can be started in two ways:

**Option 1: Launch with bot (recommended)**
```bash
python main.py --symbol ETHUSDT --balance 1000 --dashboard
```

**Option 2: Separate process**
```bash
# Terminal 1: Start bot
python main.py --symbol ETHUSDT --balance 1000

# Terminal 2: Start dashboard
python run_dashboard.py
```

Access at:
```
http://localhost:5000
```

For remote access (e.g., Raspberry Pi deployment):
```
http://YOUR_PI_IP:5000
```

Or open the HTML file directly:

```bash
# Open in browser
open dashboard/frontend/index.html  # macOS
xdg-open dashboard/frontend/index.html  # Linux
start dashboard/frontend/index.html  # Windows
```

### Dashboard Features

- **Real-time Updates**: Auto-refreshes every 2 seconds
- **Current Price & RSI**: Live market data
- **Position Tracking**: Current position with unrealized P&L
- **Trading Statistics**: Win rate, average profit/loss, etc.
- **Performance Metrics**: Total trades, runtime, trades per hour

## 📊 Trading Strategy

### RSI Strategy Overview

The bot uses a sophisticated RSI-based strategy with multiple entry and exit conditions:

#### Buy Signals
- **Oversold Intensity System**: Accumulates signal strength based on:
  - RSI depth below 30 (deeper = stronger)
  - Duration in oversold zone (longer = stronger)
  - 5-minute+ duration bonus for persistent signals
- **Dual Trigger**: Buy when intensity ≥ 10.0 OR counter ≥ 3 cycles
- **RSI Bounce**: Confirms exit from oversold (RSI + 3 points)
- **Price Validation**: Near lowest or below 0.75% of highest price
- **Timing**: Minimum 5 minutes after previous sell

#### Sell Signals (Multiple Strategies)

1. **Win with RSI** (0.75%+ profit)
   - RSI reaches overbought (70+)
   - RSI drops 3 points from peak
   - Minimum 0.75% profit achieved

2. **Big Win** (3%+ profit)
   - Price rises 3% or more
   - Immediate sell regardless of RSI

3. **Adaptive Loss Prevention** (Time-based)
   - **30 min + (-0.5% loss)**: Sell at buy price +0.15%
   - **1.5 hours + (-1.0% loss)**: Sell at -0.75% loss
   - **2.5 hours + (-2.0% loss)**: Progressive sell (-1%, -1.5%, -2%)
   - **4 hours maximum**: Emergency exit with any loss
   - **Adaptive Thresholds**: Activates 30% faster if price deteriorating, 30% slower if recovering

### Risk Management

- **Maximum Loss**: Progressive stop-loss based on holding time
- **Take Profit**: Multiple profit targets
- **Position Sizing**: Based on available balance
- **Emergency Exits**: Automatic exit after extended holding periods

## 📧 Email Notifications

The bot can send email notifications for important events:

- **Bot Start**: Confirmation when bot starts
- **Buy Orders**: Entry price, quantity, RSI
- **Sell Orders**: Exit price, P&L, duration
- **Final Report**: Complete trading summary

### Setting Up Gmail Notifications

1. Enable 2-factor authentication on your Gmail account
2. Generate an App Password: [https://myaccount.google.com/apppasswords](https://myaccount.google.com/apppasswords)
3. Use the App Password in `.env`:

```env
SMTP_EMAIL=your_email@gmail.com
SMTP_PASSWORD=your_16_char_app_password
NOTIFICATION_EMAIL=destination@gmail.com
```

## 📈 Reports

The bot generates comprehensive reports:

### Text Reports
Located in `data/reports/`, includes:
- All buy/sell trades
- Entry and exit prices
- P&L for each trade
- RSI values
- Trade duration
- Final statistics

### HTML Reports
Beautiful HTML reports with:
- Performance summary
- Trading statistics table
- Complete trade history
- Visual indicators for wins/losses

## 🔒 Security Best Practices

### API Keys
- **Never** commit API keys to version control
- Use environment variables (`.env` file)
- Enable IP whitelist on Binance
- Use read-only API keys for testing

### Binance API Permissions
Required permissions:
- ✅ Read Info
- ✅ Enable Spot & Margin Trading (for live mode)
- ❌ Enable Withdrawals (NOT required - disable for safety)

### Testing
- **Always test in simulation mode first**
- Start with small amounts in live mode
- Monitor closely for the first few hours
- Review logs regularly

## 🐛 Troubleshooting

### Common Issues

**Bot won't start**
```bash
# Check Python version
python --version  # Should be 3.8+

# Check dependencies
pip install -r requirements.txt

# Check configuration
python -c "from config.settings import AppConfig; AppConfig().validate_all()"
```

**Connection errors**
- Verify API keys are correct
- Check internet connection
- Ensure Binance is not blocked in your region
- Try using a VPN if needed

**No trades executing**
- Verify RSI thresholds are appropriate for market conditions
- Check that oversold counter requirements are being met
- Review logs for detailed information
- Ensure sufficient balance

**Dashboard not loading**
- Check if port 5000 is available
- Try accessing via `http://127.0.0.1:5000`
- Check firewall settings
- Review browser console for errors

## 📝 Logging

Logs are stored in `logs/trading_bot.log` and include:

- Bot start/stop events
- All buy/sell decisions
- Strategy signals
- Error messages
- WebSocket connection status
- API calls

### Log Levels
- **DEBUG**: Detailed information for debugging
- **INFO**: General information about bot operation
- **WARNING**: Important warnings (e.g., sell flags activated)
- **ERROR**: Errors that need attention

## 🍓 Raspberry Pi Deployment

For 24/7 operation, deploy the bot on a Raspberry Pi:

```bash
# 1. Clone repository on Raspberry Pi
git clone https://github.com/charlesbx/RSI-BINANCE-BOT.git
cd RSI-BINANCE-BOT

# 2. Run automated setup
chmod +x deployment/raspberry_pi_setup.sh
./deployment/raspberry_pi_setup.sh

# 3. Configure environment
cp .env.example .env
nano .env  # Edit with your credentials

# 4. Start bot as systemd service
sudo systemctl start rsi-bot
sudo systemctl enable rsi-bot  # Auto-start on boot

# 5. Monitor
sudo systemctl status rsi-bot
tail -f logs/bot.log
```

See [deployment/RASPBERRY_PI.md](deployment/RASPBERRY_PI.md) for complete instructions.

## 🧪 Testing

Run tests with:

```bash
# Install test dependencies
pip install pytest pytest-cov

# Run all tests
pytest

# Run with coverage
pytest --cov=src tests/

# Run specific test file
pytest tests/test_strategy.py
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

**IMPORTANT**: This bot is for educational purposes only. Cryptocurrency trading carries significant risk. 

- Past performance does not guarantee future results
- Never invest more than you can afford to lose
- The developers are not responsible for any financial losses
- Use at your own risk
- Always test thoroughly in simulation mode first
- Understand the strategy before using real money

## 📞 Support

- **Issues**: [GitHub Issues](https://github.com/charlesbx/RSI-BINANCE-BOT/issues)
- **Discussions**: [GitHub Discussions](https://github.com/charlesbx/RSI-BINANCE-BOT/discussions)

## 🙏 Acknowledgments

- [python-binance](https://github.com/sammchardy/python-binance) - Binance API wrapper
- [pandas](https://pandas.pydata.org/) - Data analysis and RSI calculation
- [Flask](https://flask.palletsprojects.com/) - Web framework
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/) - Real-time dashboard updates

## 🗺️ Roadmap

- [ ] Support for multiple trading pairs
- [ ] Additional technical indicators (MACD, Bollinger Bands)
- [ ] Machine learning integration
- [ ] Telegram bot integration
- [ ] Mobile app
- [ ] Backtesting framework
- [ ] Advanced charting

---

**Happy Trading! 🚀📈**
