"""
RSI Trading Strategy Implementation
"""
import logging
from datetime import datetime, timedelta
from typing import Optional, List
from src.models.trading_models import Position, TradeType
from src.indicators.technical_indicators import TechnicalIndicators
from src.utils.helpers import calculate_percentage
from config.settings import AppConfig


class RSIStrategy:
    """
    RSI-based trading strategy with multiple exit conditions
    """
    
    def __init__(self, config: AppConfig):
        """
        Initialize RSI strategy
        
        Args:
            config: Application configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        
        # RSI settings
        self.rsi_period = config.trading.RSI_PERIOD
        self.rsi_overbought = config.trading.RSI_OVERBOUGHT
        self.rsi_oversold = config.trading.RSI_OVERSOLD
        
        # Profit/Loss targets
        self.min_profit_pct = config.trading.MIN_PROFIT_PERCENTAGE
        self.big_profit_pct = config.trading.BIG_PROFIT_PERCENTAGE
        self.max_loss_pct = config.trading.MAX_LOSS_PERCENTAGE
        
        # Price tracking
        self.highest_price: float = 0.0
        self.lowest_rsi: float = 100.0
        self.highest_rsi: float = 0.0
        
        # Buy condition tracking
        self.oversold_counter: int = 0
        self.oversold_intensity: float = 0.0  # Accumulated oversold strength
        self.oversold_start_time: Optional[datetime] = None
        self.last_sell_time: Optional[datetime] = None
        
        # State flags
        self.sell_at_buyprice: bool = False
        self.sell_fast: bool = False
        self.sell_very_fast: bool = False
        self.very_fast_lose_amt: float = 1.0
        self.sell_very_fast_time: Optional[datetime] = None
        
        self.logger.info(f"✓ RSI Strategy initialized: Period={self.rsi_period}, "
                        f"Overbought={self.rsi_overbought}, Oversold={self.rsi_oversold}")
    
    def update_price_extremes(self, current_price: float, current_rsi: float):
        """
        Update tracked price and RSI extremes
        
        Args:
            current_price: Current price
            current_rsi: Current RSI value
        """
        if current_price > self.highest_price:
            self.highest_price = current_price
        if current_rsi < self.lowest_rsi:
            self.lowest_rsi = current_rsi
        if current_rsi > self.highest_rsi:
            self.highest_rsi = current_rsi
    
    def reset_extremes(self):
        """Reset price and RSI extremes"""
        self.highest_price = 0.0
        self.lowest_rsi = 100.0
        self.highest_rsi = 0.0
    
    def should_buy(
        self, 
        current_price: float, 
        current_rsi: float,
        closes: List[float],
        in_position: bool
    ) -> tuple[bool, str]:
        """
        Determine if a buy signal is present
        
        Args:
            current_price: Current price
            current_rsi: Current RSI
            closes: List of closing prices
            in_position: Whether currently in a position
            
        Returns:
            Tuple of (should_buy, reason)
        """
        if in_position:
            return False, "Already in position"
        
        # Check if enough time has passed since last sell
        if self.last_sell_time:
            time_since_sell = (datetime.now() - self.last_sell_time).total_seconds() / 60
            if time_since_sell < self.config.trading.MIN_TIME_AFTER_SELL:
                return False, f"Too soon after sell ({time_since_sell:.1f} min)"
        
        # Update price tracking
        self.update_price_extremes(current_price, current_rsi)
        
        # Calculate dynamic thresholds
        top_price_threshold = self.highest_price - calculate_percentage(0.75, self.highest_price)
        
        # === SYSTÈME D'INTENSITÉ OVERSOLD ===
        # Plus le RSI est bas et longtemps, plus l'intensité augmente
        if current_rsi < self.rsi_oversold:
            # Marquer le début de la période oversold
            if self.oversold_start_time is None:
                self.oversold_start_time = datetime.now()
            
            # Calculer l'intensité : plus le RSI est bas, plus ça compte
            # RSI à 20 = intensité 2x, RSI à 10 = intensité 3x
            intensity_multiplier = (self.rsi_oversold - current_rsi) / 10
            self.oversold_intensity += 1.0 + intensity_multiplier
            
            self.oversold_counter += 1
            
            # Durée en oversold (bonus après 5 minutes)
            if self.oversold_start_time:
                oversold_duration = (datetime.now() - self.oversold_start_time).total_seconds() / 60
                if oversold_duration > 5:
                    self.oversold_intensity += 0.5  # Bonus durée
            
            self.logger.debug(f"Oversold: RSI={current_rsi:.1f}, Intensity={self.oversold_intensity:.1f}, Count={self.oversold_counter}")
        
        elif current_rsi < self.rsi_oversold + 5:
            # Zone tampon : RSI proche oversold, maintien partiel
            self.oversold_intensity = max(0, self.oversold_intensity - 0.2)
        
        elif current_rsi < 45:
            # RSI bas mais pas oversold : décroissance lente
            self.oversold_intensity = max(0, self.oversold_intensity - 0.5)
            if self.oversold_counter > 0:
                self.oversold_counter = max(0, self.oversold_counter - 1)
        
        else:
            # RSI neutre/haut : reset progressif
            if self.oversold_intensity > 5:
                # Reset fort si on avait une bonne intensité
                self.oversold_intensity = max(0, self.oversold_intensity - 2.0)
            else:
                # Reset complet si faible intensité
                self.oversold_intensity = 0
                self.oversold_counter = 0
                self.oversold_start_time = None
            
            if self.oversold_intensity == 0:
                self.logger.debug(f"Oversold signals reset (RSI: {current_rsi:.1f})")
        
        # Buy conditions améliorées
        # Soit le compteur basique (3+ cycles), soit une forte intensité (10+)
        rsi_counter_met = (
            self.oversold_counter >= self.config.trading.MIN_RSI_COUNTER or
            self.oversold_intensity >= 10.0
        )
        price_condition_met = current_price <= top_price_threshold
        
        # RSI bounce confirmation
        rsi_bounced = False
        if self.lowest_rsi < self.rsi_oversold:
            rsi_bounce = current_rsi - self.lowest_rsi
            if rsi_bounce >= self.config.trading.RSI_BOUNCE_THRESHOLD:
                rsi_bounced = True
                self.logger.debug(f"RSI bounced: {rsi_bounce:.2f} from {self.lowest_rsi:.2f}")
        
        # Buy signal logic
        if rsi_counter_met and price_condition_met and rsi_bounced:
            reason = []
            if self.oversold_intensity >= 10.0:
                reason.append(f"Strong oversold (intensity: {self.oversold_intensity:.1f})")
            elif self.oversold_counter >= self.config.trading.MIN_RSI_COUNTER:
                reason.append(f"RSI oversold x{self.oversold_counter}")
            if rsi_bounced:
                reason.append(f"RSI bounce +{current_rsi - self.lowest_rsi:.1f}")
            
            # Reset counters
            self.oversold_counter = 0
            self.oversold_intensity = 0.0
            self.oversold_start_time = None
            self.lowest_rsi = 100.0
            
            return True, " | ".join(reason)
        
        return False, "Conditions not met"
    
    def should_sell(
        self,
        position: Position,
        current_price: float,
        current_rsi: float
    ) -> tuple[bool, str, str]:
        """
        Determine if a sell signal is present
        
        Args:
            position: Current position
            current_price: Current price
            current_rsi: Current RSI
            
        Returns:
            Tuple of (should_sell, reason, result_type)
            result_type can be: 'win', 'loss', 'neutral'
        """
        if not position:
            return False, "No position", "neutral"
        
        # Update position
        position.update(current_price, current_rsi)
        
        # Track RSI for overbought sell
        if current_rsi > self.highest_rsi:
            self.highest_rsi = current_rsi
        
        # Time held
        time_held = datetime.now() - position.entry_time
        hours_held = time_held.total_seconds() / 3600
        
        # === ADAPTIVE LOSS PREVENTION STRATEGIES ===
        
        # Calculate trend: is price recovering or deteriorating?
        price_trend = "neutral"
        if hasattr(position, 'entry_price'):
            recent_change = (current_price - position.entry_price) / position.entry_price * 100
            if recent_change > -0.3:
                price_trend = "recovering"
            elif recent_change < -1.5:
                price_trend = "deteriorating"
        
        # Activate sell flags based on time, loss, and trend
        loss_0_5_pct = calculate_percentage(0.5, position.entry_price)
        loss_1_0_pct = calculate_percentage(1.0, position.entry_price)
        loss_2_0_pct = calculate_percentage(2.0, position.entry_price)
        
        # Mode 1: Sell at buy price (early warning)
        # Activate earlier if deteriorating, later if recovering
        threshold_0_5 = self.config.trading.SELL_AT_LOSS_0_5_HOURS
        if price_trend == "deteriorating":
            threshold_0_5 *= 0.7  # 30% faster activation
        elif price_trend == "recovering":
            threshold_0_5 *= 1.3  # 30% slower activation
            
        if (not self.sell_at_buyprice and 
            current_price <= position.entry_price - loss_0_5_pct and 
            hours_held >= threshold_0_5):
            self.sell_at_buyprice = True
            self.logger.warning(f"⚠ Activated: Sell at buy price mode (held {hours_held:.1f}h, trend: {price_trend})")
        
        # Mode 2: Fast sell (moderate urgency)
        threshold_1_0 = self.config.trading.SELL_AT_LOSS_1_0_HOURS
        if price_trend == "deteriorating":
            threshold_1_0 *= 0.75
        elif price_trend == "recovering":
            threshold_1_0 *= 1.2
            
        if (not self.sell_fast and 
            current_price <= position.entry_price - loss_1_0_pct and 
            hours_held >= threshold_1_0):
            self.sell_fast = True
            self.logger.warning(f"⚠ Activated: Fast sell mode (held {hours_held:.1f}h, trend: {price_trend})")
        
        # Mode 3: Very fast sell (high urgency)
        threshold_2_0 = self.config.trading.SELL_AT_LOSS_2_0_HOURS
        if price_trend == "deteriorating":
            threshold_2_0 *= 0.8
            
        if (not self.sell_very_fast and 
            current_price <= position.entry_price - loss_2_0_pct and 
            hours_held >= threshold_2_0):
            self.sell_very_fast = True
            self.sell_very_fast_time = datetime.now()
            self.very_fast_lose_amt = 1.0
            self.logger.error(f"🚨 Activated: VERY FAST sell mode (held {hours_held:.1f}h, trend: {price_trend})")
        
        # Progressive loss thresholds in very fast mode
        if self.sell_very_fast and self.sell_very_fast_time:
            vf_hours = (datetime.now() - self.sell_very_fast_time).total_seconds() / 3600
            if vf_hours >= 0.5:
                self.very_fast_lose_amt = 1.5
            if vf_hours >= 1.0:
                self.very_fast_lose_amt = 2.0
            if vf_hours >= 1.5:
                self.very_fast_lose_amt = 3.0  # Aggressive exit
        
        # Emergency sell - held too long regardless of RSI
        max_hold = self.config.trading.MAX_HOLD_HOURS
        if hours_held >= max_hold:
            # Force sell if held max time with any loss
            if position.unrealized_pnl < 0:
                self.logger.error(f"🚨 MAX HOLD TIME: Selling at {position.unrealized_pnl_percentage:.2f}% after {hours_held:.1f}h")
                self._reset_sell_flags()
                self.last_sell_time = datetime.now()
                return True, f"Max hold time exceeded ({hours_held:.1f}h)", "loss"
            # Or if RSI overbought
            elif current_rsi > self.rsi_overbought:
                self.logger.warning(f"⏰ Max hold time + overbought: {position.unrealized_pnl_percentage:.2f}%")
                self._reset_sell_flags()
                self.last_sell_time = datetime.now()
                return True, f"Max hold + RSI overbought", "win" if position.unrealized_pnl > 0 else "neutral"
        
        # Sell with RSI oversold at reduced loss/small profit
        if current_rsi < self.rsi_oversold:
            # Sell at buy price mode: +0.15% or better
            if self.sell_at_buyprice:
                target = position.entry_price + calculate_percentage(0.15, position.entry_price)
                if current_price >= target:
                    self.logger.info(f"✓ Selling at buy price mode: +{position.unrealized_pnl_percentage:.2f}%")
                    self._reset_sell_flags()
                    self.last_sell_time = datetime.now()
                    return True, "RSI oversold + buy price recovery", "win"
            
            # Fast sell mode: -0.75% or better
            if self.sell_fast:
                target = position.entry_price - calculate_percentage(0.75, position.entry_price)
                if current_price >= target:
                    self.logger.warning(f"⚠ Fast sell: {position.unrealized_pnl_percentage:.2f}%")
                    self._reset_sell_flags()
                    self.last_sell_time = datetime.now()
                    return True, "RSI oversold + fast sell", "loss"
            
            # Very fast sell mode: variable loss threshold
            if self.sell_very_fast:
                target = position.entry_price - calculate_percentage(
                    self.very_fast_lose_amt, 
                    position.entry_price
                )
                if current_price >= target:
                    self.logger.error(f"🚨 Very fast sell: {position.unrealized_pnl_percentage:.2f}%")
                    self._reset_sell_flags()
                    self.last_sell_time = datetime.now()
                    return True, f"RSI oversold + very fast sell (-{self.very_fast_lose_amt}%)", "loss"
        
        # === PROFIT TAKING STRATEGIES ===
        
        # Big profit without RSI (3%)
        profit_3_pct = position.entry_price + calculate_percentage(
            self.big_profit_pct, 
            position.entry_price
        )
        if current_price >= profit_3_pct:
            self.logger.info(f"🎉 BIG WIN: +{position.unrealized_pnl_percentage:.2f}%")
            self._reset_sell_flags()
            self.last_sell_time = datetime.now()
            return True, f"Big profit target (+{self.big_profit_pct}%)", "win"
        
        # RSI overbought sell (0.75% minimum profit)
        if current_rsi >= self.rsi_overbought:
            profit_target = position.entry_price + calculate_percentage(
                self.min_profit_pct, 
                position.entry_price
            )
            
            if current_price >= profit_target:
                # Confirm RSI peaked (dropped by 3 points from highest)
                if current_rsi + 3 <= self.highest_rsi:
                    self.logger.success(f"✓ RSI sell: +{position.unrealized_pnl_percentage:.2f}% (RSI peaked at {self.highest_rsi:.1f})")
                    self._reset_sell_flags()
                    self.highest_rsi = 0.0
                    self.last_sell_time = datetime.now()
                    return True, f"RSI overbought peak (+{self.min_profit_pct}%+)", "win"
        
        return False, "No sell condition met", "neutral"
    
    def _reset_sell_flags(self):
        """Reset all sell condition flags"""
        self.sell_at_buyprice = False
        self.sell_fast = False
        self.sell_very_fast = False
        self.very_fast_lose_amt = 1.0
        self.sell_very_fast_time = None
    
    def get_status_message(self, position: Optional[Position], current_rsi: float) -> str:
        """
        Get current strategy status message
        
        Args:
            position: Current position (if any)
            current_rsi: Current RSI value
            
        Returns:
            Status message
        """
        if not position:
            status = f"🔍 Waiting for BUY | RSI: {current_rsi:.1f}"
            if current_rsi < self.rsi_oversold:
                if self.oversold_intensity >= 10.0:
                    status += f" 🔥 (Intensity: {self.oversold_intensity:.1f})"
                else:
                    status += f" ⚡ (x{self.oversold_counter}, Int: {self.oversold_intensity:.1f})"
            elif self.oversold_intensity > 0:
                status += f" 💤 (Fading: {self.oversold_intensity:.1f})"
            return status
        
        # In position
        pnl_symbol = "📈" if position.unrealized_pnl >= 0 else "📉"
        status = f"{pnl_symbol} In Position | RSI: {current_rsi:.1f} | " \
                f"P&L: {position.unrealized_pnl_percentage:+.2f}%"
        
        # Add active flags
        flags = []
        if self.sell_at_buyprice:
            flags.append("⚠️BuyPrice")
        if self.sell_fast:
            flags.append("⚡Fast")
        if self.sell_very_fast:
            flags.append("🚨VeryFast")
        
        if flags:
            status += " | " + " ".join(flags)
        
        return status
