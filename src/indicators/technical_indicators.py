"""
Technical indicators calculation
"""
import pandas as pd
import numpy as np
from typing import List, Optional


class TechnicalIndicators:
    """Technical indicators calculator"""
    
    @staticmethod
    def calculate_rsi(prices: List[float], period: int = 14) -> Optional[float]:
        """
        Calculate RSI (Relative Strength Index) manually
        
        Args:
            prices: List of prices
            period: RSI period
            
        Returns:
            RSI value or None if insufficient data
        """
        if len(prices) < period + 1:
            return None
        
        prices_series = pd.Series(prices, dtype=float)
        
        # Calculate price changes
        delta = prices_series.diff()
        
        # Separate gains and losses
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        # Calculate RS and RSI
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        # Return the last RSI value
        last_rsi = rsi.iloc[-1]
        return float(last_rsi) if not pd.isna(last_rsi) else None
    
    @staticmethod
    def calculate_sma(prices: List[float], period: int) -> Optional[float]:
        """
        Calculate Simple Moving Average
        
        Args:
            prices: List of prices
            period: SMA period
            
        Returns:
            SMA value or None if insufficient data
        """
        if len(prices) < period:
            return None
        
        prices_series = pd.Series(prices, dtype=float)
        sma_values = ta.sma(prices_series, length=period)
        
        if sma_values is None or sma_values.empty:
            return None
        
        last_sma = sma_values.iloc[-1]
        return float(last_sma) if not pd.isna(last_sma) else None
    
    @staticmethod
    def calculate_ema(prices: List[float], period: int) -> Optional[float]:
        """
        Calculate Exponential Moving Average
        
        Args:
            prices: List of prices
            period: EMA period
            
        Returns:
            EMA value or None if insufficient data
        """
        if len(prices) < period:
            return None
        
        prices_series = pd.Series(prices, dtype=float)
        ema_values = ta.ema(prices_series, length=period)
        
        if ema_values is None or ema_values.empty:
            return None
        
        last_ema = ema_values.iloc[-1]
        return float(last_ema) if not pd.isna(last_ema) else None
    
    @staticmethod
    def calculate_macd(prices: List[float], 
                       fast_period: int = 12, 
                       slow_period: int = 26, 
                       signal_period: int = 9) -> Optional[tuple]:
        """
        Calculate MACD (Moving Average Convergence Divergence)
        
        Args:
            prices: List of prices
            fast_period: Fast EMA period
            slow_period: Slow EMA period
            signal_period: Signal line period
            
        Returns:
            Tuple of (MACD, signal, histogram) or None if insufficient data
        """
        if len(prices) < slow_period + signal_period:
            return None
        
        prices_series = pd.Series(prices, dtype=float)
        macd_df = ta.macd(prices_series, fast=fast_period, slow=slow_period, signal=signal_period)
        
        if macd_df is None or macd_df.empty:
            return None
        
        macd_val = macd_df[f'MACD_{fast_period}_{slow_period}_{signal_period}'].iloc[-1]
        signal_val = macd_df[f'MACDs_{fast_period}_{slow_period}_{signal_period}'].iloc[-1]
        hist_val = macd_df[f'MACDh_{fast_period}_{slow_period}_{signal_period}'].iloc[-1]
        
        if pd.isna(macd_val) or pd.isna(signal_val) or pd.isna(hist_val):
            return None
        
        return float(macd_val), float(signal_val), float(hist_val)
    
    @staticmethod
    def calculate_bollinger_bands(prices: List[float], 
                                   period: int = 20, 
                                   std_dev: int = 2) -> Optional[tuple]:
        """
        Calculate Bollinger Bands
        
        Args:
            prices: List of prices
            period: MA period
            std_dev: Number of standard deviations
            
        Returns:
            Tuple of (upper, middle, lower) bands or None if insufficient data
        """
        if len(prices) < period:
            return None
        
        prices_series = pd.Series(prices, dtype=float)
        bbands = ta.bbands(prices_series, length=period, std=std_dev)
        
        if bbands is None or bbands.empty:
            return None
        
        # Get column names (pandas-ta uses format BBL_20_2.0, BBM_20_2.0, BBU_20_2.0)
        columns = bbands.columns.tolist()
        
        # Find the upper, middle, lower columns
        upper_col = [c for c in columns if c.startswith('BBU_')][0]
        middle_col = [c for c in columns if c.startswith('BBM_')][0]
        lower_col = [c for c in columns if c.startswith('BBL_')][0]
        
        upper = bbands[upper_col].iloc[-1]
        middle = bbands[middle_col].iloc[-1]
        lower = bbands[lower_col].iloc[-1]
        
        if pd.isna(upper) or pd.isna(middle) or pd.isna(lower):
            return None
        
        return float(upper), float(middle), float(lower)
    
    @staticmethod
    def is_rsi_oversold(rsi: float, threshold: float = 30) -> bool:
        """Check if RSI indicates oversold condition"""
        return rsi < threshold
    
    @staticmethod
    def is_rsi_overbought(rsi: float, threshold: float = 70) -> bool:
        """Check if RSI indicates overbought condition"""
        return rsi > threshold
    
    @staticmethod
    def rsi_divergence(rsi_values: List[float], 
                       prices: List[float], 
                       lookback: int = 5) -> Optional[str]:
        """
        Detect RSI divergence
        
        Args:
            rsi_values: List of RSI values
            prices: List of prices
            lookback: Number of periods to look back
            
        Returns:
            'bullish', 'bearish', or None
        """
        if len(rsi_values) < lookback or len(prices) < lookback:
            return None
        
        recent_rsi = rsi_values[-lookback:]
        recent_prices = prices[-lookback:]
        
        # Bullish divergence: price makes lower low, RSI makes higher low
        if recent_prices[-1] < recent_prices[0] and recent_rsi[-1] > recent_rsi[0]:
            return 'bullish'
        
        # Bearish divergence: price makes higher high, RSI makes lower high
        if recent_prices[-1] > recent_prices[0] and recent_rsi[-1] < recent_rsi[0]:
            return 'bearish'
        
        return None
