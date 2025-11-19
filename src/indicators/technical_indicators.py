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
    def is_rsi_oversold(rsi: float, threshold: float = 30) -> bool:
        """Check if RSI indicates oversold condition"""
        return rsi < threshold
    
    @staticmethod
    def is_rsi_overbought(rsi: float, threshold: float = 70) -> bool:
        """Check if RSI indicates overbought condition"""
        return rsi > threshold

