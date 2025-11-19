# Strategy Guide

## RSI Trading Strategy Overview

This bot implements an advanced RSI (Relative Strength Index) trading strategy with sophisticated risk management and multiple exit strategies.

**Trading Modes:**
- **Spot Trading**: Traditional buy and hold
- **Futures Trading**: Leverage trading (1x-125x) with advanced risk management

📖 **For Futures-specific features, see [Futures Trading Guide](FUTURES_GUIDE.md)**

## Table of Contents

1. [Understanding RSI](#understanding-rsi)
2. [Entry Strategy (Buy Signals)](#entry-strategy-buy-signals)
3. [Exit Strategy (Sell Signals)](#exit-strategy-sell-signals)
4. [Risk Management](#risk-management)
5. [Futures Trading Considerations](#futures-trading-considerations)
6. [Parameter Optimization](#parameter-optimization)
7. [Best Practices](#best-practices)

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

### Oversold Intensity System

The bot uses an advanced **intensity-based system** instead of simple counter-based logic. This makes the bot more responsive to strong oversold conditions.

#### How Intensity Works

**Accumulation:**
```python
# Each candle in oversold zone:
if RSI < 30:
    depth = (30 - RSI) / 30  # 0.0 to 1.0
    intensity += depth * 2.0  # Stronger when deeper
    
    # Duration bonus (after 5+ minutes)
    if oversold_duration >= 5_minutes:
        intensity += 0.5  # Extra accumulation
```

**Decay (Smart fade-out):**
```python
if RSI >= 30:
    if RSI < 35:  # Buffer zone
        intensity *= 0.95  # Slow fade (5% per candle)
    else:
        intensity *= 0.85  # Faster fade (15% per candle)
```

#### Buy Triggers (Dual System)

The bot will buy when **ONE** of these conditions is met:

##### Trigger 1: Strong Intensity
```python
oversold_intensity >= 10.0  # Strong accumulated signal
```

##### Trigger 2: Traditional Counter
```python
oversold_counter >= 3  # 3 consecutive oversold candles
```

#### Additional Confirmations

All buy signals must also satisfy:

##### 1. RSI Bounce Confirmation
```python
current_rsi >= lowest_rsi + 3  # RSI bounced back 3 points (was 5)
```
This confirms the oversold period is ending.

##### 2. Price Condition
One of:
- Price at lowest observed price
- Price below 0.75% of highest price

##### 3. Time Restriction
```python
time_since_last_sell >= 5 minutes  # Reduced from 10 minutes
```
Prevents rapid buy-sell cycles.

### Buy Example

```
Scenario 1: Strong Intensity Buy
================================
Time  | Price  | RSI  | Intensity | Counter | Action
------|--------|------|-----------|---------|-------
10:00 | $2000  | 35   | 0.0       | 0       | -
10:01 | $1995  | 29   | 1.4       | 1       | Accumulating
10:02 | $1990  | 26   | 3.1       | 2       | Accumulating
10:03 | $1985  | 23   | 5.3       | 3       | Accumulating  
10:04 | $1982  | 22   | 7.8       | 4       | Accumulating
10:05 | $1980  | 21   | 10.5      | 5       | 🔥 STRONG SIGNAL!
10:06 | $1985  | 24   | 10.5      | 6       | RSI bounce +3

→ BUY SIGNAL at $1985 (Intensity: 10.5)
Reason: Strong intensity + RSI bounce confirmed

Scenario 2: Quick Counter Buy
=============================
Time  | Price  | RSI  | Intensity | Counter | Action
------|--------|------|-----------|---------|-------
11:00 | $2000  | 35   | 0.0       | 0       | -
11:01 | $1998  | 29   | 1.4       | 1       | Accumulating
11:02 | $1996  | 28   | 2.9       | 2       | Accumulating
11:03 | $1994  | 27   | 4.5       | 3       | ⚡ Counter = 3
11:04 | $1997  | 31   | 4.3       | 0       | RSI bounce +4

→ BUY SIGNAL at $1997 (Counter: 3, Intensity: 4.3)
Reason: Counter threshold + RSI bounce confirmed
```

### Intensity Status Messages

The bot shows different status based on intensity:

- **💤 Fading (0 < intensity < 5)**: Signal weakening
- **⚡ Building (5 ≤ intensity < 10)**: Signal strengthening  
- **🔥 STRONG SIGNAL (intensity ≥ 10)**: Ready to buy

### Configuration

**Default Settings:**
```python
MIN_RSI_COUNTER = 3           # Minimum cycles (was 200)
RSI_BOUNCE_THRESHOLD = 3      # Bounce confirmation (was 5)
MIN_TIME_AFTER_SELL = 5       # Minutes (was 10)
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

### 3. Adaptive Loss Prevention (Time-Based)

The bot now uses an **adaptive system** that analyzes price trends and adjusts sell timing accordingly.

#### Price Trend Detection

```python
# Calculate recent price movement
recent_change = (current_price - price_5min_ago) / entry_price * 100

if recent_change > 0.3:
    trend = "recovering"      # Price trending up
elif recent_change < -0.3:
    trend = "deteriorating"  # Price trending down  
else:
    trend = "neutral"        # Price stable
```

#### Adaptive Threshold Modifiers

Based on the detected trend, the bot adjusts when to activate sell modes:

```python
if trend == "deteriorating":
    multiplier = 0.7   # Activate 30% FASTER
elif trend == "recovering":
    multiplier = 1.3   # Activate 30% SLOWER
else:
    multiplier = 1.0   # Normal timing
```

#### Stage 1: Sell at Buy Price (30 min + -0.5% loss)
```python
# Base threshold: 0.5 hours (30 minutes)
threshold = 0.5 * multiplier

Entry: $2,000
Held for: 0.35 hours (21 minutes)
Current: $1,990 (-0.5%)
Trend: deteriorating
Adjusted threshold: 0.5 * 0.7 = 0.35 hours ✓

→ Wait for price ≥ $2,003 (+0.15%)
→ SELL SIGNAL (Minimal loss recovery)
```

#### Stage 2: Fast Sell (1.5 hours + -1% loss)
```python
# Base threshold: 1.5 hours  
threshold = 1.5 * multiplier

Entry: $2,000
Held for: 1.2 hours
Current: $1,980 (-1.0%)
Trend: recovering
Adjusted threshold: 1.5 * 1.3 = 1.95 hours ✗

→ Not activated yet (price recovering, give it time)
```

#### Stage 3: Progressive Very Fast (2.5+ hours + -2% loss)
```python
# Base threshold: 2.5 hours
threshold = 2.5 * multiplier

# Progressive targets based on time held:
if held < 1.0h:  target = -1.0%
if held < 1.5h:  target = -1.5%  
else:            target = -2.0%

Entry: $2,000
Held for: 2.0 hours
Current: $1,970 (-1.5%)
Trend: neutral
Adjusted threshold: 2.5 * 1.0 = 2.5 hours ✗

→ Not activated yet

Held for: 2.5 hours
Trend: deteriorating
Adjusted threshold: 2.5 * 0.7 = 1.75 hours ✓

→ SELL SIGNAL at $1,970 (-1.5%)
```

#### Stage 4: Emergency Exit (4 hours maximum)
```python
# Hard limit: 4 hours
MAX_HOLD_HOURS = 4.0

Entry: $2,000
Held for: 4+ hours
Current: $1,985 (-0.75%)

→ SELL SIGNAL (Emergency exit with any loss)

# Also force sell if RSI overbought:
if held >= 4.0h and RSI >= 70:
    → SELL SIGNAL (Regardless of profit/loss)
```

### Comparison: Old vs New

| Condition | Old System | New Adaptive System |
|-----------|------------|---------------------|
| Stage 1 | 1.0 hour fixed | 0.5h × (0.7-1.3) = 21-39 min |
| Stage 2 | 2.0 hours fixed | 1.5h × (0.7-1.3) = 63-117 min |
| Stage 3 | 3.0 hours fixed | 2.5h × (0.7-1.3) = 105-195 min |
| Max Hold | 6.0 hours | 4.0 hours (stricter) |
| Very Fast | Fixed -2% | Progressive: -1%, -1.5%, -2% |
| Adaptation | None | Adjusts to price trend |

### Benefits of Adaptive System

1. **Faster exits** when price is deteriorating (cut losses sooner)
2. **More patience** when price is recovering (give trades time to work)
3. **Progressive targets** that get stricter over time
4. **Stricter max hold** prevents very long losing trades
5. **Market-responsive** rather than rigid time-based rules

## Risk Management

### Position Sizing

**Spot Trading:**
```python
position_size = available_balance / current_price
```

The bot uses your entire available balance for each trade (in simulation mode).

**Futures Trading:**
```python
# Dynamic position sizing based on risk parameters
position_size = calculate_position_size(
    balance=current_balance,
    risk_per_trade_pct=MAX_RISK_PER_TRADE_PCT,
    leverage=DEFAULT_LEVERAGE,
    entry_price=current_price
)
```

The bot calculates safe position sizes considering leverage and risk tolerance.

📖 **See [Futures Trading Guide](FUTURES_GUIDE.md#risk-management-features) for details**

### Stop-Loss Strategy

No fixed stop-loss. Instead, uses **adaptive time-based** progressive loss limits:

| Time Held | Maximum Acceptable Loss | Adaptive Range |
|-----------|------------------------|----------------|
| < 0.5h    | Unlimited (wait for signal) | - |
| 0.5-1.5h  | -0.5% → +0.15% | 21-39 min (deteriorating) |
| 1.5-2.5h  | -1.0% → -0.75% | 63-117 min (deteriorating) |
| 2.5-4.0h  | Progressive: -1.0% → -1.5% → -2.0% | 105-195 min (deteriorating) |
| 4.0+ hours | Emergency exit | Force sell any loss |

**Note**: Thresholds adjust based on price trend (±30% activation time)

### Take-Profit Strategy

Multiple profit targets:

1. **Small profit (0.75%+)**: With RSI overbought
2. **Big profit (3%+)**: Immediate exit

**Note**: In Futures trading, these percentages apply to leveraged positions, meaning actual returns are multiplied by leverage.

## Futures Trading Considerations

### Leverage Impact on Strategy

When using Futures with leverage, the RSI strategy remains the same, but execution differs:

#### Leverage Multiplies Returns
With 5x leverage:
- A 1% price move = 5% gain/loss on your margin
- Risk management becomes critical
- Drawdown limits prevent over-leveraging

#### Margin and Liquidation
- **Isolated Margin** (recommended): Risk limited per position
- **Cross Margin**: Uses full account balance
- The bot monitors margin usage to prevent liquidation

#### Risk-Based Position Sizing
```python
# Bot calculates safe position size
position_value = balance * leverage * (risk_per_trade_pct / 100)
# Example: $1000 * 5x * (2% / 100) = $100 position max risk
```

#### Drawdown Protection
```python
if current_drawdown >= MAX_DRAWDOWN_PCT:
    # Bot stops trading automatically
    # Prevents emotional over-trading
```

### Strategy Adjustments for Futures

**Same Strategy Elements:**
- ✅ RSI thresholds (30/70)
- ✅ Oversold intensity system
- ✅ Buy/sell signal logic
- ✅ Adaptive time-based exits

**Additional Considerations:**
- 💰 Funding fees (every 8 hours)
- ⚡ Faster position sizing calculations
- 🛡️ Pre-trade risk validation
- 📊 Enhanced risk monitoring

**Example: 5x Leverage Trade**
```
Entry Signal: RSI 28, Strong intensity
Entry Price: $2,000
Position Size: 0.5 ETH (with 5x leverage = $5,000 position)
Margin Used: $1,000

Exit Signal: RSI 72, Overbought
Exit Price: $2,100 (+5% price move)
Profit: $250 (25% on margin!)

Without leverage same trade: $50 profit (5%)
```

### Risk Management in Futures

**Critical Settings:**
- `MAX_RISK_PER_TRADE_PCT`: 1-2% recommended
- `MAX_DRAWDOWN_PCT`: 10-15% recommended  
- `DEFAULT_LEVERAGE`: Start with 2-5x
- `MARGIN_TYPE`: Use `isolated` for safety

**The bot automatically:**
- Validates every trade before execution
- Monitors drawdown continuously
- Stops trading at max drawdown
- Calculates safe position sizes

📖 **Complete Futures guide: [Futures Trading Guide](FUTURES_GUIDE.md)**

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

**Default: 3** (changed from 200)

This now works alongside the intensity system as a secondary trigger:

- **Lower (1-2)**: Very quick entries, relies more on intensity
- **Standard (3)**: Balanced dual-trigger approach (recommended)
- **Higher (5-10)**: More conservative, requires both triggers

**Note**: The intensity system (≥10.0) can trigger buys even faster than the counter.

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
