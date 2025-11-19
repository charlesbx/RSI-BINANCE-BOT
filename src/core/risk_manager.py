"""
Risk Management Module for Trading Bot
Handles position sizing, risk validation, and drawdown monitoring
"""
import logging
from typing import Optional, Tuple
from datetime import datetime

from config.settings import AppConfig
from src.models.trading_models import Position, TradingStats


class RiskManager:
    """
    Risk management system for trading operations.
    Validates trades against risk parameters before execution.
    """
    
    def __init__(self, config: AppConfig, initial_balance: float):
        """
        Initialize risk manager
        
        Args:
            config: Application configuration
            initial_balance: Starting account balance
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # Risk parameters
        self.initial_balance = initial_balance
        self.max_risk_per_trade_pct = config.trading.MAX_RISK_PER_TRADE_PCT
        self.max_drawdown_pct = config.trading.MAX_DRAWDOWN_PCT
        self.dynamic_position_sizing = config.trading.DYNAMIC_POSITION_SIZING
        
        # State tracking
        self.peak_balance = initial_balance
        self.current_drawdown_pct = 0.0
        
        self.logger.info("✓ Risk Manager initialized")
        self.logger.info(f"  Max Risk Per Trade: {self.max_risk_per_trade_pct}%")
        self.logger.info(f"  Max Drawdown: {self.max_drawdown_pct}%")
        self.logger.info(f"  Dynamic Position Sizing: {self.dynamic_position_sizing}")
    
    def calculate_position_size(
        self,
        current_balance: float,
        entry_price: float,
        stop_loss_price: Optional[float] = None,
        leverage: int = 1
    ) -> Tuple[float, str]:
        """
        Calculate optimal position size based on risk parameters
        
        Args:
            current_balance: Current account balance
            entry_price: Planned entry price
            stop_loss_price: Optional stop loss price for risk calculation
            leverage: Leverage multiplier (1 for spot trading)
            
        Returns:
            Tuple of (position_size, calculation_details)
        """
        if not self.dynamic_position_sizing:
            # Fixed position sizing: use full balance
            position_size = current_balance / entry_price
            details = f"Fixed sizing: {position_size:.6f} units (full balance)"
            return position_size, details
        
        # Dynamic position sizing based on risk
        risk_amount = current_balance * (self.max_risk_per_trade_pct / 100)
        
        if stop_loss_price and stop_loss_price > 0:
            # Calculate position size based on stop loss distance
            risk_per_unit = abs(entry_price - stop_loss_price)
            if risk_per_unit > 0:
                position_size = risk_amount / risk_per_unit
                details = (
                    f"Dynamic sizing: {position_size:.6f} units "
                    f"(risk ${risk_amount:.2f} @ {self.max_risk_per_trade_pct}% "
                    f"with SL at ${stop_loss_price:.2f})"
                )
            else:
                # Fallback if stop loss is at entry
                position_size = risk_amount / entry_price
                details = f"Risk-based sizing: {position_size:.6f} units (SL at entry)"
        else:
            # No stop loss provided, use conservative percentage of balance
            usable_balance = current_balance * leverage * (self.max_risk_per_trade_pct / 100)
            position_size = usable_balance / entry_price
            details = (
                f"Conservative sizing: {position_size:.6f} units "
                f"({self.max_risk_per_trade_pct}% of balance with {leverage}x leverage)"
            )
        
        self.logger.debug(f"Position size calculated: {details}")
        return position_size, details
    
    def validate_trade(
        self,
        current_balance: float,
        position_size: float,
        entry_price: float,
        stats: Optional[TradingStats] = None
    ) -> Tuple[bool, str]:
        """
        Validate if a trade can be executed based on risk rules
        
        Args:
            current_balance: Current account balance
            position_size: Proposed position size
            entry_price: Entry price
            stats: Trading statistics (for drawdown calculation)
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # Check minimum balance
        if current_balance <= 0:
            return False, "❌ TRADE BLOCKED: Insufficient balance ($0)"
        
        # Check if position size is valid
        trade_value = position_size * entry_price
        if trade_value > current_balance * 1.01:  # Allow 1% tolerance
            return False, (
                f"❌ TRADE BLOCKED: Position size (${trade_value:.2f}) "
                f"exceeds available balance (${current_balance:.2f})"
            )
        
        # Check drawdown limit
        if stats:
            self._update_drawdown(current_balance)
            if self.current_drawdown_pct >= self.max_drawdown_pct:
                return False, (
                    f"❌ TRADE BLOCKED: Maximum drawdown reached "
                    f"({self.current_drawdown_pct:.2f}% >= {self.max_drawdown_pct}%). "
                    f"Peak balance: ${self.peak_balance:.2f}, Current: ${current_balance:.2f}"
                )
        
        # All checks passed
        return True, "✓ Trade validated"
    
    def validate_position_close(
        self,
        position: Position,
        current_price: float,
        reason: str
    ) -> Tuple[bool, str]:
        """
        Validate if a position can be closed
        
        Args:
            position: Current position
            current_price: Current market price
            reason: Reason for closing
            
        Returns:
            Tuple of (is_valid, reason)
        """
        # Position close is generally always valid
        # This method exists for future risk checks (e.g., circuit breakers)
        
        pnl_pct = ((current_price - position.entry_price) / position.entry_price) * 100
        self.logger.debug(f"Position close validated: {reason} (P&L: {pnl_pct:+.2f}%)")
        
        return True, "✓ Position close validated"
    
    def _update_drawdown(self, current_balance: float):
        """
        Update drawdown tracking
        
        Args:
            current_balance: Current account balance
        """
        # Update peak balance if we reached a new high
        if current_balance > self.peak_balance:
            self.peak_balance = current_balance
            self.current_drawdown_pct = 0.0
        else:
            # Calculate drawdown from peak
            self.current_drawdown_pct = (
                (self.peak_balance - current_balance) / self.peak_balance * 100
            )
    
    def get_risk_status(self, current_balance: float, stats: Optional[TradingStats] = None) -> dict:
        """
        Get current risk status
        
        Args:
            current_balance: Current account balance
            stats: Trading statistics
            
        Returns:
            Dictionary with risk metrics
        """
        self._update_drawdown(current_balance)
        
        risk_status = {
            "current_balance": current_balance,
            "initial_balance": self.initial_balance,
            "peak_balance": self.peak_balance,
            "current_drawdown_pct": round(self.current_drawdown_pct, 2),
            "max_drawdown_pct": self.max_drawdown_pct,
            "max_risk_per_trade_pct": self.max_risk_per_trade_pct,
            "drawdown_warning": self.current_drawdown_pct >= self.max_drawdown_pct * 0.8,
            "drawdown_critical": self.current_drawdown_pct >= self.max_drawdown_pct
        }
        
        if stats:
            risk_status["total_pnl"] = stats.total_profit_loss
            risk_status["total_pnl_pct"] = stats.total_profit_loss_percentage
            risk_status["win_rate"] = stats.win_rate
        
        return risk_status
    
    def log_risk_status(self, current_balance: float, stats: Optional[TradingStats] = None):
        """
        Log current risk status
        
        Args:
            current_balance: Current account balance
            stats: Trading statistics
        """
        status = self.get_risk_status(current_balance, stats)
        
        self.logger.info("=" * 60)
        self.logger.info("📊 RISK STATUS")
        self.logger.info(f"Balance: ${current_balance:.2f} (Peak: ${status['peak_balance']:.2f})")
        self.logger.info(
            f"Drawdown: {status['current_drawdown_pct']:.2f}% "
            f"(Max: {status['max_drawdown_pct']:.2f}%)"
        )
        
        if status.get('drawdown_warning') and not status.get('drawdown_critical'):
            self.logger.warning("⚠️ WARNING: Approaching maximum drawdown limit!")
        elif status.get('drawdown_critical'):
            self.logger.error("🚨 CRITICAL: Maximum drawdown reached! Trading will be blocked.")
        
        if stats:
            self.logger.info(
                f"Total P&L: ${status['total_pnl']:.2f} ({status['total_pnl_pct']:+.2f}%) "
                f"| Win Rate: {status['win_rate']:.1f}%"
            )
        
        self.logger.info("=" * 60)
