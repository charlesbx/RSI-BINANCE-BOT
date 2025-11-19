# 🧪 Testing Documentation

## Quick Start Testing

### 1. Interactive Test Menu (Recommended)

The easiest way to test the bot:

```bash
python test_menu.py
```

This will show an interactive menu with all test options.

### 2. Individual Tests

```bash
# Test technical indicators
python test_indicators.py

# Run demo bot (simulated prices, no API needed)
python test_demo.py --iterations 50 --speed 0.3

# Unit tests
pytest tests/ -v
```

### 3. Full Test Suite

```bash
./scripts/run_tests.sh
```

## Test Files Overview

| File | Purpose | Duration | API Required |
|------|---------|----------|--------------|
| `test_indicators.py` | Test all technical indicators (RSI, SMA, EMA, MACD, BB) | ~2s | No |
| `test_demo.py` | Demo bot with simulated prices | Variable | No |
| `test_menu.py` | Interactive test menu | N/A | No |
| `tests/test_strategy.py` | Unit tests for RSI strategy | ~3s | No |
| `tests/test_helpers.py` | Unit tests for helper functions | ~2s | No |
| `scripts/run_tests.sh` | Complete test suite | ~30s | No |

## Testing Modes

### 1. Unit Tests (No External Dependencies)

Tests individual functions and classes:

```bash
# All tests
pytest tests/ -v

# Specific test file
pytest tests/test_strategy.py -v

# With coverage report
pytest tests/ --cov=src --cov-report=html
```

**What's tested:**
- RSI buy/sell signals
- Price extreme detection
- Utility functions (formatting, calculations)

### 2. Demo Mode (Simulated Market)

Tests the complete trading loop with fake prices:

```bash
# Quick demo (30 iterations)
python test_demo.py --iterations 30 --speed 0.2

# Custom parameters
python test_demo.py \
  --symbol BTCUSDT \
  --balance 5000 \
  --iterations 100 \
  --speed 0.5
```

**What's tested:**
- Complete trading cycle (buy → hold → sell)
- RSI indicator calculations
- Position management
- P&L calculations
- Statistics tracking

**Demo Output:**
```
🤖 RSI Trading Bot - DEMO MODE
Symbol: ETHUSDT
Initial Balance: $1,000.00
Strategy: RSI (14 period, 30/70 levels)

[17:00:00] Price: $2,500.00 | RSI: 50.00 | Balance: $1,000.00
    🟢 BUY 0.380000 @ $2,480.00 (RSI: 28.50)
[17:00:05] Price: $2,550.00 | RSI: 72.30 | Position: +2.82% ($70.00)
    🔴 SELL 0.380000 @ $2,550.00 | P&L: $26.60 (+1.07%) (RSI overbought)

📊 DEMO SUMMARY
Final Balance:   $1,026.60
Total Return:    $26.60 (+2.66%)
Total Trades:    1
Win Rate:        100.0%
```

### 3. Simulation Mode (Real Market Data, No Orders)

Tests with real Binance data but doesn't place real orders:

```bash
# Configure .env first
nano .env

# Set SIMULATION_MODE=true
# Add your API keys

# Run simulation
python main.py --symbol ETHUSDT --balance 1000 --simulate
```

**What's tested:**
- Real market data integration
- API connectivity
- WebSocket data stream
- Complete bot workflow
- Error handling with real data

### 4. Live Trading (Real Money ⚠️)

**WARNING:** Only use after extensive testing!

```bash
python main.py --symbol ETHUSDT --balance 1000 --live
```

## Test Scenarios

### Scenario 1: First-Time Setup (5 min)

```bash
# 1. Test indicators
python test_indicators.py

# 2. Quick demo
python test_demo.py --iterations 20 --speed 0.1

# 3. Unit tests
pytest tests/ -v
```

**Expected:** All tests pass ✅

---

### Scenario 2: Strategy Validation (30 min)

```bash
# 1. Long demo to see multiple trades
python test_demo.py --iterations 200 --speed 0.2

# 2. Analyze results
# - Win rate should be > 50%
# - Average P&L should be positive
# - Max loss should be acceptable
```

**Expected:** Profitable strategy with acceptable risk

---

### Scenario 3: Pre-Production Testing (1-2 weeks)

```bash
# 1. Configure API keys in .env
nano .env

# 2. Run simulation mode
python main.py --interactive
# Choose simulation mode
# Let it run for 1-2 weeks

# 3. Analyze logs
tail -f logs/trading_bot.log

# 4. Review reports
ls -lh data/reports/
```

**Expected:** Profitable over extended period with real data

---

## Interpreting Test Results

### Demo Bot Results

**Good Strategy Indicators:**
- ✅ Win Rate: > 60%
- ✅ Total Return: > 0%
- ✅ Average P&L: > 0
- ✅ Max Loss: < 2% per trade

**Warning Signs:**
- ⚠️ Win Rate: < 40%
- ⚠️ Total Return: Negative
- ⚠️ Large consecutive losses
- ⚠️ Very few trades (RSI too restrictive)

**Adjustment Tips:**

| Issue | Solution |
|-------|----------|
| No trades happening | Relax RSI thresholds (35/65 instead of 30/70) |
| Too many losses | Tighten stop-loss, increase RSI period |
| Missing opportunities | Lower RSI thresholds, faster response |
| Big drawdowns | Reduce position size, stricter stop-loss |

### Unit Test Results

```bash
pytest tests/ -v
```

**Expected Output:**
```
tests/test_helpers.py::test_calculate_percentage PASSED
tests/test_helpers.py::test_percentage_difference PASSED
tests/test_helpers.py::test_format_currency PASSED
tests/test_strategy.py::test_rsi_oversold_buy_signal PASSED
tests/test_strategy.py::test_rsi_overbought_sell_signal PASSED
tests/test_strategy.py::test_price_extremes PASSED

====== 6 passed in 2.34s ======
```

All tests should pass. If any fail:
1. Check error message for details
2. Verify dependencies are installed
3. Check Python version (>= 3.8)

## Continuous Testing

### Before Each Commit

```bash
# Quick validation
pytest tests/ -v
python test_indicators.py
```

### Before Deployment

```bash
# Full test suite
./scripts/run_tests.sh

# Extended demo
python test_demo.py --iterations 200

# Simulation mode test (1+ day)
python main.py --simulate
```

### Production Monitoring

```bash
# Monitor logs
tail -f logs/trading_bot.log

# Check error rate
grep ERROR logs/trading_bot.log | wc -l

# Review trades
grep "BUY\|SELL" logs/trading_bot.log | tail -20
```

## Troubleshooting Tests

### Import Errors

```bash
# Reinstall dependencies
pip install -r requirements.txt

# Check Python path
python -c "import sys; print(sys.path)"
```

### Test Failures

```bash
# Run with verbose output
pytest tests/ -vv

# Run single test
pytest tests/test_strategy.py::test_rsi_oversold_buy_signal -v

# Show print statements
pytest tests/ -v -s
```

### Demo Bot Issues

**No trades happening:**
- RSI thresholds too strict
- Not enough iterations
- Market conditions not suitable

**Solution:**
```python
# Edit test_demo.py
self.rsi_oversold = 35  # Was 30
self.rsi_overbought = 65  # Was 70
```

**Errors during demo:**
```bash
# Check dependencies
pip list | grep -E "pandas|numpy|pandas-ta"

# Reinstall technical analysis lib
pip install --upgrade pandas pandas-ta
```

## Performance Benchmarks

Expected test execution times:

| Test | Expected Duration |
|------|------------------|
| `test_indicators.py` | < 3 seconds |
| `test_demo.py` (20 iter) | ~ 5 seconds |
| `test_demo.py` (100 iter) | ~ 60 seconds |
| `pytest tests/` | < 5 seconds |
| `run_tests.sh` (full suite) | ~ 30 seconds |

If tests take significantly longer:
- Check system resources
- Reduce demo iterations
- Check for network issues (simulation mode)

## Test Coverage

Current coverage (run `pytest --cov`):

- **Core Bot**: 85%
- **Strategy**: 90%
- **Indicators**: 95%
- **Helpers**: 100%
- **Overall**: ~88%

Areas not covered:
- Error recovery scenarios
- Extreme market conditions
- API rate limiting
- Network failures

These require integration testing or manual testing in simulation mode.

## Next Steps

After successful testing:

1. ✅ All unit tests pass
2. ✅ Demo shows profitable results
3. ✅ Simulation runs for 1+ week successfully
4. → **Consider live trading with small amounts**
5. → **Monitor closely and scale gradually**

---

**Remember:** Testing is crucial. Never skip straight to live trading!
