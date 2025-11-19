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
        Calculate RSI (Relative Strength Index) manually, robust to edge cases
        """
        if len(prices) < period + 1:
            return None

        prices_series = pd.Series(prices, dtype=float)
        delta = prices_series.diff()

        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()

        last_gain = gain.iloc[-1]
        last_loss = loss.iloc[-1]

        # Cas extrêmes : marché plat ou haussier/baisser extrême
        if last_loss == 0 and last_gain == 0:
            return 50.0  # RSI neutre si aucun mouvement
        elif last_loss == 0:
            return 100.0  # RSI max si aucune perte
        elif last_gain == 0:
            return 0.0    # RSI min si aucun gain

        rs = last_gain / last_loss
        rsi = 100 - (100 / (1 + rs))
        return float(rsi) if not pd.isna(rsi) else None
    
    @staticmethod
    def is_rsi_oversold(rsi: float, threshold: float = 30) -> bool:
        """Check if RSI indicates oversold condition"""
        return rsi < threshold
    
    @staticmethod
    def is_rsi_overbought(rsi: float, threshold: float = 70) -> bool:
        """Check if RSI indicates overbought condition"""
        return rsi > threshold

