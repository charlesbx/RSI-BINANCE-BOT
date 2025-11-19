"""
Main Trading Bot Implementation
"""
import logging
import time
from datetime import datetime
from typing import List, Optional
import uuid

from config.settings import AppConfig
from src.core.exchange_client import BinanceClient
from src.core.websocket_handler import WebSocketHandler
from src.strategies.rsi_strategy import RSIStrategy
from src.indicators.technical_indicators import TechnicalIndicators
from src.models.trading_models import (
    Trade, Position, TradingStats, TradeType, TradeResult, OrderStatus, MarketData
)
from src.services.notification_service import NotificationService
from src.services.report_service import ReportService
from src.utils.helpers import format_currency, format_percentage


class TradingBot:
    """
    Main Trading Bot - Orchestrates all components
    """
    
    def __init__(self, config: AppConfig, symbol: str, initial_balance: float):
        """
        Initialize trading bot
        
        Args:
            config: Application configuration
            symbol: Trading symbol (e.g., 'ETHUSDT')
            initial_balance: Initial trading balance
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.symbol = symbol.upper()
        self.initial_balance = initial_balance
        
        # Trading state
        self.current_balance = initial_balance
        self.position: Optional[Position] = None
        self.stats = TradingStats(
            start_balance=initial_balance,
            current_balance=initial_balance
        )
        
        # Price data
        self.closes: List[float] = [0.0]  # Start with dummy value
        self.current_price: float = 0.0
        self.current_rsi: Optional[float] = None
        
        # Initialize components
        self.exchange = BinanceClient(
            api_key=config.binance.API_KEY,
            api_secret=config.binance.API_SECRET,
            testnet=config.binance.TESTNET
        )
        
        self.strategy = RSIStrategy(config)
        self.indicators = TechnicalIndicators()
        
        # Services
        self.notifier = NotificationService(config)
        self.reporter = ReportService(config, self.symbol)
        
        # WebSocket
        self.ws_handler = WebSocketHandler(
            symbol=self.symbol,
            on_message_callback=self._on_market_data
        )
        
        # Control flags
        self.is_running = False
        self.is_simulation = config.trading.SIMULATION_MODE
        self.last_candle_closed = False
        
        self.logger.info(f"{'🎮 SIMULATION' if self.is_simulation else '💰 LIVE'} Trading Bot initialized")
        self.logger.info(f"Symbol: {self.symbol} | Initial Balance: {format_currency(initial_balance)}")
    
    def start(self):
        """Start the trading bot"""
        self.logger.info("=" * 60)
        self.logger.info("🚀 STARTING RSI TRADING BOT")
        self.logger.info("=" * 60)
        
        # Test exchange connection
        if not self.exchange.test_connection():
            self.logger.error("❌ Failed to connect to exchange")
            return False
        
        # Get initial market data
        self._initialize_market_data()
        
        # Start WebSocket
        self.ws_handler.start()
        time.sleep(2)  # Wait for connection
        
        if not self.ws_handler.is_connected():
            self.logger.error("❌ Failed to connect to WebSocket")
            return False
        
        self.is_running = True
        self.stats.start_time = datetime.now()
        
        # Send start notification
        self.notifier.send_start_notification(
            symbol=self.symbol,
            balance=self.current_balance,
            strategy_params={
                'RSI_PERIOD': self.config.trading.RSI_PERIOD,
                'RSI_OVERBOUGHT': self.config.trading.RSI_OVERBOUGHT,
                'RSI_OVERSOLD': self.config.trading.RSI_OVERSOLD
            }
        )
        
        self.logger.info("✓ Bot started successfully")
        self.logger.info("=" * 60)
        
        return True
    
    def stop(self):
        """Stop the trading bot"""
        self.logger.info("=" * 60)
        self.logger.info("🛑 STOPPING RSI TRADING BOT")
        self.logger.info("=" * 60)
        
        self.is_running = False
        
        # Close any open position
        if self.position:
            self.logger.warning("⚠ Closing open position before shutdown...")
            self._execute_sell(
                position=self.position,
                price=self.current_price,
                reason="Bot shutdown"
            )
        
        # Stop WebSocket
        self.ws_handler.stop()
        
        # Generate final report
        self.reporter.generate_final_report(self.stats, self.position)
        
        # Send final notification
        self.notifier.send_final_report(self.stats)
        
        self.logger.info("✓ Bot stopped successfully")
        self.logger.info("=" * 60)
    
    def _initialize_market_data(self):
        """Initialize historical market data"""
        self.logger.info("📊 Loading historical data...")
        
        # Get last 500 candles for RSI calculation
        klines = self.exchange.get_klines(
            symbol=self.symbol,
            interval='1m',
            limit=500
        )
        
        if not klines:
            self.logger.error("❌ Failed to load historical data")
            return
        
        # Extract closing prices
        self.closes = [kline['close'] for kline in klines]
        self.current_price = self.closes[-1]
        
        # Calculate initial RSI
        self.current_rsi = self.indicators.calculate_rsi(
            self.closes,
            self.config.trading.RSI_PERIOD
        )
        
        self.logger.info(f"✓ Loaded {len(self.closes)} candles")
        self.logger.info(f"Current Price: {format_currency(self.current_price)}")
        if self.current_rsi:
            self.logger.info(f"Current RSI: {self.current_rsi:.2f}")
    
    def _on_market_data(self, candle_data: dict):
        """
        Process incoming market data from WebSocket
        
        Args:
            candle_data: Candle data from WebSocket
        """
        if not self.is_running:
            return
        
        # Update current price
        self.current_price = candle_data['close']
        is_closed = candle_data['is_closed']
        
        # Update closes array
        if self.last_candle_closed:
            # New candle started
            self.closes.append(self.current_price)
        else:
            # Update current candle
            self.closes[-1] = self.current_price
        
        self.last_candle_closed = is_closed
        
        # Calculate RSI
        if len(self.closes) > self.config.trading.RSI_PERIOD:
            self.current_rsi = self.indicators.calculate_rsi(
                self.closes,
                self.config.trading.RSI_PERIOD
            )
            
            if self.current_rsi is None:
                return
            
            # Update strategy extremes
            self.strategy.update_price_extremes(self.current_price, self.current_rsi)
            
            # Process trading logic
            self._process_trading_logic()
            
            # Log status periodically (every closed candle)
            if is_closed:
                self._log_status()
    
    def _process_trading_logic(self):
        """Process trading logic based on current market conditions"""
        if self.position:
            # Check for sell signal
            should_sell, reason, result_type = self.strategy.should_sell(
                position=self.position,
                current_price=self.current_price,
                current_rsi=self.current_rsi
            )
            
            if should_sell:
                self._execute_sell(self.position, self.current_price, reason)
        else:
            # Check for buy signal
            should_buy, reason = self.strategy.should_buy(
                current_price=self.current_price,
                current_rsi=self.current_rsi,
                closes=self.closes,
                in_position=False
            )
            
            if should_buy:
                self._execute_buy(self.current_price, reason)
    
    def _execute_buy(self, price: float, reason: str):
        """
        Execute a buy order
        
        Args:
            price: Buy price
            reason: Buy reason
        """
        quantity = self.current_balance / price
        
        self.logger.info("=" * 60)
        self.logger.info(f"🟢 BUY SIGNAL: {reason}")
        self.logger.info(f"Price: {format_currency(price)} | Quantity: {quantity:.6f}")
        self.logger.info(f"RSI: {self.current_rsi:.2f}")
        
        # Create position
        self.position = Position(
            symbol=self.symbol,
            quantity=quantity,
            entry_price=price,
            entry_time=datetime.now(),
            entry_rsi=self.current_rsi,
            current_price=price,
            current_rsi=self.current_rsi
        )
        
        # Execute order (simulation or real)
        if not self.is_simulation:
            order = self.exchange.create_market_buy(
                symbol=self.symbol,
                quantity=quantity
            )
            if not order:
                self.logger.error("❌ Failed to execute buy order")
                self.position = None
                return
        
        # Update balance
        self.current_balance = 0.0
        self.stats.current_balance = 0.0
        
        # Send notification
        self.notifier.send_trade_notification(
            trade_type=TradeType.BUY,
            symbol=self.symbol,
            price=price,
            quantity=quantity,
            rsi=self.current_rsi,
            reason=reason
        )
        
        # Add to report
        self.reporter.log_buy(self.position, reason)
        
        self.logger.info("=" * 60)
    
    def _execute_sell(self, position: Position, price: float, reason: str):
        """
        Execute a sell order
        
        Args:
            position: Current position
            price: Sell price
            reason: Sell reason
        """
        # Calculate P&L
        sell_value = position.quantity * price
        profit_loss = sell_value - (position.quantity * position.entry_price)
        profit_loss_pct = (profit_loss / (position.quantity * position.entry_price)) * 100
        
        # Determine result
        result = TradeResult.WIN if profit_loss >= 0 else TradeResult.LOSS
        
        time_held = (datetime.now() - position.entry_time).total_seconds() / 60
        
        self.logger.info("=" * 60)
        
        if result == TradeResult.WIN:
            self.logger.info(f"🟢 SELL SIGNAL (WIN): {reason}")
        else:
            self.logger.warning(f"🔴 SELL SIGNAL (LOSS): {reason}")
        
        self.logger.info(f"Entry: {format_currency(position.entry_price)} | Exit: {format_currency(price)}")
        self.logger.info(f"P&L: {format_currency(profit_loss)} ({format_percentage(profit_loss_pct)})")
        self.logger.info(f"Time Held: {time_held:.1f} minutes")
        self.logger.info(f"RSI: {self.current_rsi:.2f}")
        
        # Execute order (simulation or real)
        if not self.is_simulation:
            order = self.exchange.create_market_sell(
                symbol=self.symbol,
                quantity=position.quantity
            )
            if not order:
                self.logger.error("❌ Failed to execute sell order")
                return
        
        # Update balance
        self.current_balance = sell_value
        self.stats.current_balance = sell_value
        
        # Create trade record
        trade = Trade(
            id=str(uuid.uuid4()),
            symbol=self.symbol,
            trade_type=TradeType.SELL,
            quantity=position.quantity,
            price=price,
            timestamp=datetime.now(),
            rsi_value=self.current_rsi,
            is_simulation=self.is_simulation,
            buy_price=position.entry_price,
            sell_price=price,
            profit_loss=profit_loss,
            profit_loss_percentage=profit_loss_pct,
            result=result,
            time_held=time_held
        )
        
        # Update stats
        self.stats.update(trade)
        
        # Send notification
        self.notifier.send_trade_notification(
            trade_type=TradeType.SELL,
            symbol=self.symbol,
            price=price,
            quantity=position.quantity,
            rsi=self.current_rsi,
            reason=reason,
            profit_loss=profit_loss,
            profit_loss_pct=profit_loss_pct
        )
        
        # Add to report
        self.reporter.log_sell(position, price, profit_loss, profit_loss_pct, reason, result)
        
        # Clear position
        self.position = None
        
        # Reset strategy flags
        self.strategy.reset_extremes()
        
        self.logger.info("=" * 60)
    
    def _log_status(self):
        """Log current bot status"""
        status_msg = self.strategy.get_status_message(self.position, self.current_rsi)
        
        balance_info = f"💰 Balance: {format_currency(self.current_balance)}"
        if self.position:
            balance_info += f" (in position: {format_currency(self.position.quantity * self.current_price)})"
        
        self.logger.info(f"{status_msg} | {balance_info}")
    
    def get_status(self) -> dict:
        """
        Get current bot status (for dashboard/API)
        
        Returns:
            Status dictionary
        """
        return {
            'is_running': self.is_running,
            'is_simulation': self.is_simulation,
            'symbol': self.symbol,
            'current_price': self.current_price,
            'current_rsi': self.current_rsi,
            'current_balance': self.current_balance,
            'position': self.position.to_dict() if self.position else None,
            'stats': self.stats.to_dict(),
            'strategy_status': self.strategy.get_status_message(self.position, self.current_rsi),
            'oversold_intensity': round(self.strategy.oversold_intensity, 2),
            'oversold_counter': self.strategy.oversold_counter
        }
