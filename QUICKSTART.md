# 🚀 Quick Start Guide

Get your RSI Trading Bot up and running in 5 minutes!

## ⚡ Super Quick Start

```bash
# 1. Clone & navigate
git clone https://github.com/yourusername/RSI-BINANCE-BOT.git
cd RSI-BINANCE-BOT

# 2. Run quick start script
./scripts/quickstart.sh  # Linux/macOS
# OR
scripts\quickstart.bat   # Windows

# 3. Configure API keys
nano .env  # or use any text editor

# 4. Start bot
python main.py --interactive
```

## 📋 Step-by-Step Guide

### Step 1: Installation (2 minutes)

**Prerequisites:**
- Python 3.8+ installed
- Git installed (optional)

**Install:**

```bash
# Download the project
git clone https://github.com/yourusername/RSI-BINANCE-BOT.git
cd RSI-BINANCE-BOT

# Run setup script
./scripts/quickstart.sh
```

### Step 2: Configuration (2 minutes)

**Get Binance API Keys:**

1. Go to [Binance.com](https://www.binance.com/) → Login
2. Navigate to: Profile → API Management
3. Create new API Key
4. ✅ Enable: "Read Info" and "Enable Trading"
5. ❌ Disable: "Enable Withdrawals" (for safety!)
6. Copy API Key and Secret

**Configure .env file:**

```bash
# Edit .env file
nano .env
```

Add your credentials:

```env
BINANCE_API_KEY=your_api_key_here
BINANCE_API_SECRET=your_api_secret_here
SIMULATION_MODE=true
```

### Step 3: Run Bot (1 minute)

**Start in interactive mode:**

```bash
python main.py --interactive
```

**Or use command-line:**

```bash
# Simulation mode (safe, no real money)
python main.py --symbol ETHUSDT --balance 1000 --simulate
```

### Step 4: Monitor

**Open Dashboard:**

```
http://localhost:5000
```

**Or open HTML file:**

```bash
open dashboard/frontend/index.html
```

## 🎯 Common Use Cases

### 1. Test Strategy (Simulation)

```bash
python main.py \
  --symbol ETHUSDT \
  --balance 1000 \
  --rsi-period 14 \
  --rsi-overbought 70 \
  --rsi-oversold 30 \
  --simulate
```

### 2. Live Trading (Real Money)

⚠️ **CAUTION**: Use at your own risk!

```bash
python main.py \
  --symbol ETHUSDT \
  --balance 1000 \
  --live
```

### 3. Conservative Strategy

```bash
python main.py \
  --symbol BTCUSDT \
  --balance 5000 \
  --rsi-overbought 75 \
  --rsi-oversold 25 \
  --simulate
```

### 4. Aggressive Strategy

```bash
python main.py \
  --symbol ETHUSDT \
  --balance 2000 \
  --rsi-overbought 65 \
  --rsi-oversold 35 \
  --simulate
```

## 📊 Dashboard Overview

### What You'll See:

```
┌─────────────────────────────────────┐
│  📊 RSI Trading Bot Dashboard       │
├─────────────────────────────────────┤
│                                     │
│  Current Price:    $2,500.50        │
│  RSI:             45.32             │
│  Balance:         $1,050.25         │
│  Total Trades:    10                │
│                                     │
│  📈 CURRENT POSITION                │
│  Entry: $2,450  →  Current: $2,500  │
│  P&L: +$25.25 (+2.06%)             │
│                                     │
│  📊 STATISTICS                      │
│  Win Rate:        70%               │
│  Avg Profit:      $15.50            │
│  Largest Win:     $35.00            │
│                                     │
└─────────────────────────────────────┘
```

## 🔍 Monitoring

### Check Logs:

```bash
# Follow logs in real-time
tail -f logs/trading_bot.log

# Search for errors
grep ERROR logs/trading_bot.log

# View recent trades
grep "BUY\|SELL" logs/trading_bot.log | tail -20
```

### View Reports:

```bash
# Text reports
ls -lh data/reports/*.txt

# HTML reports
open data/reports/*.html
```

## 🛑 Stopping the Bot

**Graceful shutdown:**

```
Press Ctrl+C
```

The bot will:
1. Close any open positions
2. Generate final report
3. Send summary email (if configured)
4. Save all logs

## ⚙️ Configuration Options

### All Available Options:

```bash
python main.py --help
```

### Key Parameters:

| Parameter | Default | Description |
|-----------|---------|-------------|
| `--symbol` | ETHUSDT | Trading pair |
| `--balance` | 1000 | Initial balance |
| `--rsi-period` | 14 | RSI calculation period |
| `--rsi-overbought` | 70 | Overbought threshold |
| `--rsi-oversold` | 30 | Oversold threshold |
| `--simulate` | true | Simulation mode |
| `--live` | false | Live trading mode |
| `--no-email` | false | Disable emails |
| `--log-level` | INFO | Logging level |

## 🎓 Learning Path

**Day 1-2: Learn**
- Read [README.md](README.md)
- Understand [STRATEGY.md](docs/STRATEGY.md)
- Review dashboard

**Day 3-7: Test**
- Run in simulation for 1 week
- Try different parameters
- Analyze results

**Week 2: Optimize**
- Adjust RSI thresholds
- Test different symbols
- Review win rate

**Week 3+: Go Live**
- Start with small amounts
- Monitor closely
- Scale up gradually

## ❓ Troubleshooting

### Bot won't start?

```bash
# Check Python version
python --version

# Reinstall dependencies
pip install -r requirements.txt

# Check configuration
python -c "from config.settings import AppConfig; AppConfig().initialize()"
```

### No trades executing?

- Check RSI thresholds match market conditions
- Verify sufficient balance
- Review logs for specific reasons
- Ensure market is suitable (volatile, range-bound)

### Dashboard not loading?

- Check port 5000 is not in use
- Try: `http://127.0.0.1:5000`
- Check firewall settings
- View browser console for errors

### API errors?

- Verify API keys are correct
- Check API permissions
- Ensure IP whitelist if enabled
- Check system time is synchronized

## 📚 Next Steps

1. **Read Full Documentation**
   - [README.md](README.md) - Complete guide
   - [INSTALLATION.md](docs/INSTALLATION.md) - Detailed setup
   - [STRATEGY.md](docs/STRATEGY.md) - Strategy deep dive
   - [API.md](docs/API.md) - API documentation

2. **Join Community**
   - GitHub Discussions
   - Report issues
   - Share strategies

3. **Contribute**
   - Fork the project
   - Submit improvements
   - Share backtesting results

## 🔒 Security Reminders

✅ **DO:**
- Use API keys with minimal permissions
- Start with simulation mode
- Test thoroughly before live trading
- Monitor bot regularly
- Keep API keys secret
- Use small amounts initially

❌ **DON'T:**
- Share API keys
- Enable withdrawal permissions
- Invest more than you can afford to lose
- Run unmonitored in live mode
- Commit .env file to git

## 📞 Getting Help

- **Documentation**: Check `/docs` folder
- **Issues**: [GitHub Issues](https://github.com/yourusername/RSI-BINANCE-BOT/issues)
- **Logs**: Check `logs/trading_bot.log`
- **Email**: your.email@example.com

## 🎉 You're Ready!

Your bot is now configured and ready to trade!

```bash
# Start trading (simulation)
python main.py --interactive

# Open dashboard
open http://localhost:5000

# Monitor logs
tail -f logs/trading_bot.log
```

**Happy Trading! 📈🚀**

---

*Remember: Past performance doesn't guarantee future results. Always trade responsibly!*
