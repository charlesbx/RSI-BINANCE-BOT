# 🚀 Binance Futures Trading Guide

This guide explains how to use the RSI Trading Bot with Binance Futures, including leverage configuration and risk management.

## 📋 Table of Contents

- [Overview](#overview)
- [Prerequisites](#prerequisites)
- [Configuration](#configuration)
- [Leverage & Risk Management](#leverage--risk-management)
- [Trading Modes Comparison](#trading-modes-comparison)
- [Getting Started](#getting-started)
- [Risk Management Features](#risk-management-features)
- [Advanced Configuration](#advanced-configuration)
- [FAQ](#faq)
- [Safety Tips](#safety-tips)

## Overview

The bot now supports **Binance Futures** trading in addition to Spot trading, with full leverage and risk management capabilities:

- ✅ Configurable leverage (1x - 125x)
- ✅ Isolated or Cross margin modes
- ✅ Dynamic position sizing based on risk tolerance
- ✅ Maximum drawdown protection
- ✅ Risk-based order validation
- ✅ Long/short position support
- ✅ Backward compatible with Spot trading

## Prerequisites

### Binance Futures Account Setup

1. **Enable Futures Trading** on your Binance account
   - Go to Binance Futures interface
   - Complete KYC verification if required
   - Accept Futures trading agreement

2. **Create API Keys** with Futures permissions
   - Go to Account > API Management
   - Create new API key
   - **Required Permissions:**
     - ✅ Enable Reading
     - ✅ Enable Futures
     - ❌ Disable Spot & Margin Trading (optional, for Futures-only)
     - ❌ **Never enable Withdrawals** for safety

3. **Whitelist IP Address** (recommended)
   - Add your server/computer IP to API key restrictions
   - Provides additional security

4. **Fund Your Futures Account**
   - Transfer USDT (or other collateral) to your Futures wallet
   - You can transfer from Spot wallet within Binance

## Configuration

### Basic Futures Configuration

Edit your `.env` file:

```env
# Trading Mode
TRADING_MODE=futures  # Options: "spot" or "futures"

# Binance API Credentials
BINANCE_API_KEY=your_futures_api_key
BINANCE_API_SECRET=your_futures_api_secret

# Futures Settings
DEFAULT_LEVERAGE=5  # Leverage: 1-125 (start conservative!)
MARGIN_TYPE=isolated  # Options: "isolated" or "cross"

# Risk Management
MAX_RISK_PER_TRADE_PCT=2.0  # Max % of balance to risk per trade
MAX_DRAWDOWN_PCT=10.0  # Max drawdown before stopping
DYNAMIC_POSITION_SIZING=true  # Use risk-based position sizing

# Trading Configuration
DEFAULT_TRADE_SYMBOL=ETHUSDT
DEFAULT_TRADE_QUANTITY=1000  # Initial balance in USDT
SIMULATION_MODE=true  # Always start with simulation!
```

### Configuration Parameters Explained

#### `TRADING_MODE`
- **spot**: Traditional spot trading (buy and hold)
- **futures**: Futures trading with leverage

#### `DEFAULT_LEVERAGE`
- Range: 1 - 125
- **Recommended for beginners**: 2-5x
- **Experienced traders**: 5-20x
- **High risk**: 20x+
- Higher leverage = higher profits **AND** higher losses

#### `MARGIN_TYPE`
- **isolated**: Risk limited to position margin only (SAFER)
  - Each position has its own margin
  - Liquidation only affects that position
  - **Recommended for beginners**
  
- **cross**: Uses all available margin (RISKIER)
  - All positions share account balance
  - Better margin efficiency
  - Account liquidation risk

#### `MAX_RISK_PER_TRADE_PCT`
- Percentage of balance to risk per trade
- **Conservative**: 0.5-1.0%
- **Moderate**: 1.0-2.0%
- **Aggressive**: 2.0-5.0%
- Applies to position sizing calculation

#### `MAX_DRAWDOWN_PCT`
- Maximum acceptable drawdown from peak balance
- Bot stops trading when this limit is reached
- **Conservative**: 5-10%
- **Moderate**: 10-15%
- **Aggressive**: 15-20%

#### `DYNAMIC_POSITION_SIZING`
- **true**: Position size calculated based on risk parameters
- **false**: Uses full available balance (like original bot)

## Leverage & Risk Management

### How Leverage Works

With **5x leverage** and **$1,000** balance:
- You can open positions up to **$5,000**
- You only use **$1,000 / 5 = $200** as margin per $1,000 position
- **Profits are multiplied by 5x**
- **Losses are also multiplied by 5x** ⚠️

### Example Trade

**Without Leverage (Spot):**
- Balance: $1,000
- Buy ETH at $2,000
- Sell ETH at $2,100 (+5%)
- Profit: $50

**With 5x Leverage (Futures):**
- Balance: $1,000
- Buy ETH at $2,000 with 5x leverage ($5,000 position)
- Margin used: $1,000
- Sell ETH at $2,100 (+5%)
- Profit: $250 (5x more!)

**But if price drops 5%:**
- Loss: $250 (25% of your balance!)

### Risk Management Features

The bot includes several safety mechanisms:

1. **Position Sizing Calculator**
   - Calculates safe position size based on your risk tolerance
   - Factors in leverage and available balance
   - Prevents over-leveraging

2. **Pre-Trade Validation**
   - Validates every trade before execution
   - Checks available balance
   - Verifies position size is within risk limits

3. **Drawdown Monitor**
   - Tracks peak balance vs current balance
   - Automatically stops trading at max drawdown
   - Prevents emotional trading during losses

4. **Risk Status Logging**
   - Logs risk metrics after every trade
   - Shows drawdown percentage
   - Warns when approaching limits

## Trading Modes Comparison

| Feature | Spot Trading | Futures Trading |
|---------|-------------|-----------------|
| Leverage | 1x (no leverage) | 1x - 125x |
| Short Selling | ❌ No | ✅ Yes |
| Margin Type | N/A | Isolated / Cross |
| Capital Efficiency | Lower | Higher |
| Risk Level | Lower | Higher |
| Liquidation Risk | ❌ None | ✅ Yes |
| Funding Fees | ❌ None | ✅ Yes (every 8h) |
| Best For | Conservative, long-term | Active, risk-tolerant |

## Getting Started

### Step 1: Start with Simulation Mode

**ALWAYS** test with simulation mode first:

```bash
# Test Futures configuration (no real money)
python main.py --symbol ETHUSDT --balance 1000 --simulate
```

### Step 2: Monitor Risk Metrics

Watch the logs for risk status:

```
📊 RISK STATUS
Balance: $950.00 (Peak: $1000.00)
Drawdown: 5.00% (Max: 10.00%)
Total P&L: $-50.00 (-5.00%) | Win Rate: 45.0%
```

### Step 3: Go Live (When Ready)

After successful simulation testing:

```bash
# REAL trading - use caution!
python main.py --symbol ETHUSDT --balance 1000 --live --dashboard
```

## Risk Management Features

### Automatic Position Sizing

The bot calculates position size based on:
- Your current balance
- Risk per trade percentage
- Leverage setting
- Optional stop-loss distance

```
Position Sizing: Conservative sizing: 0.052000 units 
(2.0% of balance with 5x leverage)
✓ Trade validated
```

### Drawdown Protection

When max drawdown is reached:

```
❌ TRADE BLOCKED: Maximum drawdown reached (10.50% >= 10.00%). 
Peak balance: $1000.00, Current: $895.00
```

Bot automatically stops taking new trades until manual intervention.

### Trade Validation

Every trade is validated:

```
✓ Trade validated
🟢 BUY SIGNAL: Strong oversold (intensity: 12.5) | RSI bounce +5.3
Price: $2,450.00 | Quantity: 0.204082
Leverage: 5x | Position Value: $2,500.00
```

Or blocked if risks are too high:

```
❌ TRADE BLOCKED: Position size ($5,500.00) exceeds available balance ($5,000.00)
```

## Advanced Configuration

### Per-Symbol Leverage

You can set different leverage for different symbols by modifying the code:

```python
# In main.py or trading_bot.py
if symbol == "BTCUSDT":
    leverage = 3
elif symbol == "ETHUSDT":
    leverage = 5
else:
    leverage = 2
```

### Custom Risk Parameters

Adjust risk parameters per symbol or strategy:

```env
# Conservative setup for volatile markets
MAX_RISK_PER_TRADE_PCT=1.0
MAX_DRAWDOWN_PCT=8.0
DEFAULT_LEVERAGE=3

# Aggressive setup for stable markets
MAX_RISK_PER_TRADE_PCT=3.0
MAX_DRAWDOWN_PCT=15.0
DEFAULT_LEVERAGE=10
```

### Hedge Mode (Advanced)

Enable hedge mode to hold long and short positions simultaneously:

```python
# The bot supports this, but requires strategy modifications
if futures_executor:
    futures_executor.enable_hedge_mode()
```

## FAQ

### Q: What's the recommended leverage for beginners?
**A:** Start with 2-5x leverage. This provides enough benefit without extreme risk. Never start with more than 10x.

### Q: Should I use isolated or cross margin?
**A:** Use **isolated margin** as a beginner. It limits risk to each position. Cross margin is for experienced traders only.

### Q: How much should I risk per trade?
**A:** Conservative: 1-2% of balance. This allows for multiple losing trades without significant drawdown.

### Q: What happens if I reach max drawdown?
**A:** The bot stops opening new trades. Review your strategy, risk parameters, and market conditions before resuming.

### Q: Can I switch from Spot to Futures without changing strategy?
**A:** Yes! The RSI strategy logic remains identical. Only execution and risk management change.

### Q: What are funding fees?
**A:** Futures positions pay/receive funding every 8 hours based on market conditions. Factor this into holding time.

### Q: Can I manually close positions?
**A:** Yes, through Binance interface. The bot will detect and adapt, but may affect statistics.

### Q: How do I know if leverage is set correctly?
**A:** Check logs during startup:
```
✓ Leverage set for ETHUSDT: 5x
✓ Margin type set for ETHUSDT: ISOLATED
✓ Futures configured: 5x leverage, isolated margin
```

## Safety Tips

### 🚨 Critical Safety Rules

1. **Start with Simulation Mode**
   - Test thoroughly before risking real money
   - Understand how leverage affects P&L

2. **Use Conservative Leverage**
   - Don't use max leverage (125x) ever
   - Start with 2-5x, increase gradually

3. **Set Risk Limits**
   - Configure `MAX_DRAWDOWN_PCT`
   - Use `MAX_RISK_PER_TRADE_PCT`
   - Enable `DYNAMIC_POSITION_SIZING`

4. **Monitor Your Account**
   - Check liquidation prices
   - Monitor margin usage
   - Watch funding fees

5. **Use Isolated Margin**
   - Especially when learning
   - Limits risk to individual positions

6. **Never Invest More Than You Can Afford to Lose**
   - Futures trading is high risk
   - Leverage amplifies both gains and losses

7. **Keep Emergency Funds**
   - Don't use your entire balance
   - Maintain reserves for drawdown recovery

### 🛡️ Risk Mitigation

- Start small (1-10% of total capital)
- Test each configuration change in simulation
- Review logs regularly for risk warnings
- Adjust leverage based on win rate
- Take breaks after significant drawdowns

### 📊 Performance Monitoring

Watch these metrics:
- **Win Rate**: Should be >50% for profitability with leverage
- **Drawdown**: Should stay well below max limit
- **Average Trade Duration**: Minimize exposure to funding fees
- **Risk-Adjusted Returns**: Profit vs drawdown

## Support & Resources

- **Binance Futures Guide**: [https://www.binance.com/en/support/faq/futures](https://www.binance.com/en/support/faq/futures)
- **Leverage & Margin**: [https://www.binance.com/en/support/faq/leverage](https://www.binance.com/en/support/faq/leverage)
- **Funding Rates**: [https://www.binance.com/en/futures/funding-history/1](https://www.binance.com/en/futures/funding-history/1)

---

**Remember: With great leverage comes great responsibility! Trade safely.** 🚀📊
