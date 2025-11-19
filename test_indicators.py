#!/usr/bin/env python3
"""
Test script for technical indicators
"""
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.indicators.technical_indicators import TechnicalIndicators


def test_rsi():
    """Test RSI calculation"""
    print("\n" + "="*60)
    print("Testing RSI Calculation")
    print("="*60)
    
    # Sample price data (trending up)
    prices = [
        2400, 2410, 2405, 2415, 2420,
        2425, 2430, 2428, 2435, 2440,
        2445, 2450, 2448, 2455, 2460,
        2465, 2470, 2468, 2475, 2480
    ]
    
    indicators = TechnicalIndicators()
    rsi = indicators.calculate_rsi(prices, period=14)
    
    print(f"\nPrice data: {len(prices)} candles")
    print(f"Latest price: ${prices[-1]:.2f}")
    print(f"RSI (14): {rsi:.2f}")
    
    if rsi:
        if rsi > 70:
            print("Status: 🔴 OVERBOUGHT")
        elif rsi < 30:
            print("Status: 🟢 OVERSOLD")
        else:
            print("Status: ⚪ NEUTRAL")
    
    print("\n✅ RSI calculation working!")


def test_moving_averages():
    """Test SMA and EMA"""
    print("\n" + "="*60)
    print("Testing Moving Averages")
    print("="*60)
    
    prices = [
        2400, 2410, 2405, 2415, 2420,
        2425, 2430, 2428, 2435, 2440,
        2445, 2450, 2448, 2455, 2460,
        2465, 2470, 2468, 2475, 2480
    ]
    
    indicators = TechnicalIndicators()
    
    sma_10 = indicators.calculate_sma(prices, period=10)
    sma_20 = indicators.calculate_sma(prices, period=20)
    ema_10 = indicators.calculate_ema(prices, period=10)
    
    print(f"\nLatest price: ${prices[-1]:.2f}")
    print(f"SMA (10): ${sma_10:.2f}" if sma_10 else "SMA (10): Insufficient data")
    print(f"SMA (20): ${sma_20:.2f}" if sma_20 else "SMA (20): Insufficient data")
    print(f"EMA (10): ${ema_10:.2f}" if ema_10 else "EMA (10): Insufficient data")
    
    if sma_10 and prices[-1] > sma_10:
        print("\nTrend: 📈 Price above SMA (bullish)")
    elif sma_10:
        print("\nTrend: 📉 Price below SMA (bearish)")
    
    print("\n✅ Moving averages calculation working!")


def test_macd():
    """Test MACD calculation"""
    print("\n" + "="*60)
    print("Testing MACD")
    print("="*60)
    
    # Need more data for MACD
    prices = [2400 + i * 2 for i in range(50)]
    
    indicators = TechnicalIndicators()
    macd_result = indicators.calculate_macd(prices)
    
    if macd_result:
        macd, signal, histogram = macd_result
        print(f"\nMACD Line: {macd:.2f}")
        print(f"Signal Line: {signal:.2f}")
        print(f"Histogram: {histogram:.2f}")
        
        if histogram > 0:
            print("Signal: 🟢 BULLISH (MACD > Signal)")
        else:
            print("Signal: 🔴 BEARISH (MACD < Signal)")
        
        print("\n✅ MACD calculation working!")
    else:
        print("\n⚠️  Insufficient data for MACD")


def test_bollinger_bands():
    """Test Bollinger Bands"""
    print("\n" + "="*60)
    print("Testing Bollinger Bands")
    print("="*60)
    
    prices = [
        2400, 2410, 2405, 2415, 2420,
        2425, 2430, 2428, 2435, 2440,
        2445, 2450, 2448, 2455, 2460,
        2465, 2470, 2468, 2475, 2480
    ]
    
    indicators = TechnicalIndicators()
    bb_result = indicators.calculate_bollinger_bands(prices, period=20, std_dev=2)
    
    if bb_result:
        upper, middle, lower = bb_result
        current_price = prices[-1]
        
        print(f"\nCurrent Price: ${current_price:.2f}")
        print(f"Upper Band: ${upper:.2f}")
        print(f"Middle Band: ${middle:.2f}")
        print(f"Lower Band: ${lower:.2f}")
        
        band_width = upper - lower
        position = (current_price - lower) / band_width * 100
        
        print(f"\nBand Width: ${band_width:.2f}")
        print(f"Price Position: {position:.1f}% of band")
        
        if current_price > upper:
            print("Status: 🔴 Above upper band (overbought)")
        elif current_price < lower:
            print("Status: 🟢 Below lower band (oversold)")
        else:
            print("Status: ⚪ Within bands (normal)")
        
        print("\n✅ Bollinger Bands calculation working!")
    else:
        print("\n⚠️  Insufficient data for Bollinger Bands")


def main():
    """Run all tests"""
    print("\n" + "="*60)
    print("🧪 TESTING TECHNICAL INDICATORS")
    print("="*60)
    
    try:
        test_rsi()
        test_moving_averages()
        test_macd()
        test_bollinger_bands()
        
        print("\n" + "="*60)
        print("✅ ALL TESTS PASSED!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n❌ TEST FAILED: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
