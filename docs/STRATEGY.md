# Strategy Guide

## RSI Trading Strategy Overview

This bot implements an advanced RSI (Relative Strength Index) trading strategy with sophisticated risk management and multiple exit strategies.

## Table of Contents

1. [Understanding RSI](#understanding-rsi)
2. [Entry Strategy (Buy Signals)](#entry-strategy-buy-signals)
3. [Exit Strategy (Sell Signals)](#exit-strategy-sell-signals)
4. [Risk Management](#risk-management)
5. [Parameter Optimization](#parameter-optimization)
6. [Best Practices](#best-practices)

## Understanding RSI

### What is RSI?

The Relative Strength Index (RSI) is a momentum oscillator that measures the speed and magnitude of recent price changes to evaluate overbought or oversold conditions.

**Formula:**
```
RSI = 100 - (100 / (1 + RS))
RS = Average Gain / Average Loss
```

### RSI Interpretation

- **RSI > 70**: Overbought (potential sell signal)
- **RSI < 30**: Oversold (potential buy signal)
- **RSI = 50**: Neutral momentum

### Default Parameters

- **Period**: 14 (standard)
- **Overbought**: 70
- **Oversold**: 30

## Entry Strategy (Buy Signals)

### Primary Buy Conditions

The bot will consider buying when **ALL** of the following conditions are met:

#### 1. RSI Oversold
```python
current_rsi < 30  # Oversold threshold
```

#### 2. Oversold Counter
```python
oversold_counter > 200  # RSI stayed oversold for 200 candles
```
This prevents buying too early during a downtrend.

#### 3. RSI Bounce Confirmation
```python
current_rsi >= lowest_rsi + 5  # RSI bounced back 5 points
```
This confirms the oversold period has ended.

#### 4. Price Condition
One of:
- Price at lowest observed price
- Price below 0.75% of highest price

#### 5. Time Restriction
```python
time_since_last_sell > 10 minutes
```
Prevents rapid buy-sell cycles.

### Buy Example

```
Current Price: $2,000
Lowest Price: $2,000
RSI: 28 → 25 → 23 → 22 → 24 → 27 → 32 (BOUNCE!)
Oversold Counter: 205 ✓
Time since sell: 15 minutes ✓

→ BUY SIGNAL at $2,000
```

## Exit Strategy (Sell Signals)

The bot has multiple sell strategies that work in parallel:

### 1. Win with RSI (Profit: 0.75%+)

**Conditions:**
- RSI reaches overbought (≥ 70)
- Profit is at least 0.75%
- RSI drops 3 points from peak

**Example:**
```
Entry: $2,000
Current: $2,020 (+1.0%)
RSI: 68 → 72 → 75 → 74 → 71 (DROP!)

→ SELL SIGNAL (Win with RSI)
P&L: +$20 (+1.0%)
```

### 2. Big Win (Profit: 3%+)

**Conditions:**
- Price rises 3% or more from entry

**Example:**
```
Entry: $2,000
Current: $2,065 (+3.25%)

→ SELL SIGNAL (Big Win)
P&L: +$65 (+3.25%)
```

### 3. Loss Prevention (Time-Based)

#### Stage 1: Sell at Buy Price (1 hour + -0.5% loss)
```
Entry: $2,000
Held for: 1.5 hours
Current: $1,990 (-0.5%)
RSI: 28 (oversold)

→ Wait for price ≥ $2,003 (+0.15%)
→ SELL SIGNAL (Minimal loss recovery)
```

#### Stage 2: Fast Sell (2 hours + -1% loss)
```
Entry: $2,000
Held for: 2.5 hours
Current: $1,980 (-1.0%)
RSI: 29 (oversold)

→ Wait for price ≥ $1,985 (-0.75%)
→ SELL SIGNAL (Reduced loss)
```

#### Stage 3: Very Fast Sell (3 hours + -2% loss)
```
Entry: $2,000
Held for: 3+ hours
Loss threshold increases over time:
  - 3-4 hours: -1.0%
  - 4-5 hours: -1.5%
  - 5-6 hours: -2.0%
  - 6+ hours: -8.0% (emergency)

→ SELL SIGNAL (Cut losses)
```

#### Stage 4: Emergency Exit (6 hours)
```
Entry: $2,000
Held for: 6+ hours
RSI: 72 (overbought)

→ SELL SIGNAL (Emergency exit regardless of price)
```

## Risk Management

### Position Sizing

```python
position_size = available_balance / current_price
```

The bot uses your entire available balance for each trade (in simulation mode).

### Stop-Loss Strategy

No fixed stop-loss. Instead, uses time-based progressive loss limits:

| Time Held | Maximum Acceptable Loss |
|-----------|------------------------|
| < 1 hour  | Unlimited (wait for signal) |
| 1-2 hours | -0.5% → +0.15% |
| 2-3 hours | -1.0% → -0.75% |
| 3-4 hours | -2.0% → -1.0% |
| 4-5 hours | -2.0% → -1.5% |
| 5-6 hours | -2.0% → -2.0% |
| 6+ hours  | Emergency exit |

### Take-Profit Strategy

Multiple profit targets:

1. **Small profit (0.75%+)**: With RSI overbought
2. **Big profit (3%+)**: Immediate exit

## Parameter Optimization

### RSI Period

**Default: 14**

- **Shorter (7-10)**: More sensitive, more signals, more false signals
- **Standard (14)**: Balanced approach
- **Longer (20-30)**: Less sensitive, fewer signals, more reliable

### RSI Overbought/Oversold

**Defaults: 70/30**

**Conservative (75/25):**
- Fewer signals
- Higher quality signals
- Lower frequency

**Aggressive (65/35):**
- More signals
- Earlier entries/exits
- Higher frequency

**Example configurations:**

```bash
# Conservative
python main.py --symbol ETHUSDT --rsi-overbought 75 --rsi-oversold 25

# Standard (default)
python main.py --symbol ETHUSDT --rsi-overbought 70 --rsi-oversold 30

# Aggressive
python main.py --symbol ETHUSDT --rsi-overbought 65 --rsi-oversold 35
```

### Oversold Counter

**Default: 200**

Controls how long RSI must stay oversold before buying:

- **Lower (50-100)**: Earlier entries, more trades
- **Standard (200)**: Balanced approach
- **Higher (300-500)**: Later entries, fewer trades, higher quality

## Best Practices

### 1. Start with Simulation

```bash
python main.py --symbol ETHUSDT --balance 1000 --simulate
```

Test the strategy for at least 24-48 hours before using real money.

### 2. Choose the Right Market

**Best for:**
- Volatile markets with clear trends
- High liquidity pairs (ETHUSDT, BTCUSDT)
- 24/7 trading availability

**Not ideal for:**
- Low volatility/sideways markets
- Low liquidity pairs
- Strong trending markets (very bullish or bearish)

### 3. Market Conditions

**Optimal conditions:**
- Moderate volatility (2-5% daily range)
- Mean-reverting behavior
- Clear support/resistance levels

**Avoid:**
- Extreme volatility (>10% daily moves)
- Strong trends (RSI stays overbought/oversold for long periods)
- Low volume periods

### 4. Time Management

**Monitor the bot:**
- Check dashboard regularly
- Review logs daily
- Analyze reports weekly

**Set alerts:**
- Large unrealized losses
- Extended holding periods
- Unusual RSI readings

### 5. Risk Management Rules

1. **Never invest more than you can afford to lose**
2. **Start with small amounts** ($100-500)
3. **Don't interfere** with the bot's decisions
4. **Review performance weekly**
5. **Adjust parameters** based on results

### 6. Performance Monitoring

Track these metrics:

- **Win Rate**: Target >60%
- **Average Profit**: Should exceed average loss
- **Max Drawdown**: Monitor largest loss
- **Trade Frequency**: 2-5 trades per day is normal

### 7. When to Stop

Stop the bot if:
- Win rate drops below 50% for extended period
- Losing more than 10% of capital
- Market conditions change dramatically
- You don't understand what's happening

## Advanced Strategies

### Multi-Pair Trading

Run multiple bots on different pairs:

```bash
# Terminal 1
python main.py --symbol ETHUSDT --balance 500

# Terminal 2
python main.py --symbol BTCUSDT --balance 500
```

### Custom Parameters for Different Markets

**High Volatility:**
```bash
python main.py --symbol ETHUSDT --rsi-period 10 --rsi-overbought 75 --rsi-oversold 25
```

**Low Volatility:**
```bash
python main.py --symbol ETHUSDT --rsi-period 20 --rsi-overbought 65 --rsi-oversold 35
```

### Backtesting

Before running live, backtest with historical data:

1. Run in simulation mode
2. Monitor for 7+ days
3. Analyze win rate and P&L
4. Adjust parameters
5. Repeat until satisfied

## Common Pitfalls

### 1. Impatience
❌ Stopping bot after first loss
✅ Let it run for at least 50+ trades

### 2. Over-optimization
❌ Constantly changing parameters
✅ Test one configuration for extended period

### 3. Ignoring Market Conditions
❌ Running in strong trending markets
✅ Use during range-bound markets

### 4. Over-leveraging
❌ Using borrowed money
✅ Only trade with disposable income

### 5. Emotional Trading
❌ Manually closing positions
✅ Trust the strategy

## Conclusion

The RSI trading strategy is a proven approach for range-bound, volatile markets. Success requires:

1. **Proper configuration** for market conditions
2. **Patience** to let the strategy work
3. **Discipline** to follow the rules
4. **Risk management** to protect capital
5. **Continuous monitoring** and adjustment

Remember: **No strategy wins 100% of the time**. The goal is consistent, positive results over many trades.

---

**Happy Trading! 📈**
