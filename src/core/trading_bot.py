"""
Main Trading Bot Implementation
Supports both Spot and Futures trading with leverage and risk management
"""
import logging
import time
from datetime import datetime
from typing import List, Optional
import uuid

from config.settings import AppConfig
from src.core.exchange_client import BinanceClient
from src.core.risk_manager import RiskManager
from src.core.futures_executor import FuturesExecutor
from src.core.websocket_handler import WebSocketHandler
from src.strategies.rsi_strategy import RSIStrategy
from src.indicators.technical_indicators import TechnicalIndicators
from src.models.trading_models import (
    Trade, Position, TradingStats, TradeType, TradeResult, OrderStatus, MarketData, PositionSide
)
from src.services.notification_service import NotificationService
from src.services.report_service import ReportService
from src.utils.helpers import format_currency, format_percentage


class TradingBot:
    """
    Main Trading Bot - Orchestrates all components
    Supports both Spot and Futures trading with full risk management
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
        
        # Trading mode
        self.trading_mode = config.trading.TRADING_MODE
        self.is_futures = self.trading_mode == "futures"
        self.leverage = config.trading.DEFAULT_LEVERAGE if self.is_futures else 1
        
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
            trading_mode=self.trading_mode,
            testnet=config.binance.TESTNET
        )
        
        # Initialize Futures executor if needed
        self.futures_executor: Optional[FuturesExecutor] = None
        if self.is_futures:
            self.futures_executor = FuturesExecutor(self.exchange.client, config)
        
        # Initialize Risk Manager
        self.risk_manager = RiskManager(config, initial_balance)
        
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
        
        mode_emoji = "🎮" if self.is_simulation else "💰"
        mode_type = "FUTURES" if self.is_futures else "SPOT"
        self.logger.info(f"{mode_emoji} {mode_type} Trading Bot initialized")
        self.logger.info(f"Symbol: {self.symbol} | Initial Balance: {format_currency(initial_balance)}")
        if self.is_futures:
            self.logger.info(f"Leverage: {self.leverage}x | Margin: {config.trading.MARGIN_TYPE}")
    
    def start(self):
        """Start the trading bot"""
        self.logger.info("=" * 60)
        mode_type = "FUTURES" if self.is_futures else "SPOT"
        self.logger.info(f"🚀 STARTING RSI {mode_type} TRADING BOT")
        self.logger.info("=" * 60)
        
        # Test exchange connection (skip in simulation mode with invalid keys)
        if not self.is_simulation:
            if not self.exchange.test_connection():
                self.logger.error("❌ Failed to connect to exchange")
                return False
        else:
            # In simulation mode, try to connect but don't fail if it doesn't work
            if self.exchange.test_connection():
                self.logger.info("✓ Connected to exchange (market data)")
            else:
                self.logger.warning("⚠️ Could not connect to exchange API, will use mock data for simulation")
        
        # Setup Futures if needed (only in live mode)
        if self.is_futures and self.futures_executor and not self.is_simulation:
            self.logger.info(f"⚙️ Configuring Futures for {self.symbol}...")
            
            # Set leverage
            if not self.futures_executor.set_leverage(self.symbol, self.leverage):
                self.logger.error("❌ Failed to set leverage")
                return False
            
            # Set margin type
            if not self.futures_executor.set_margin_type(self.symbol):
                self.logger.warning("⚠️ Failed to set margin type (may already be set)")
            
            self.logger.info(f"✓ Futures configured: {self.leverage}x leverage, {self.config.trading.MARGIN_TYPE} margin")
        elif self.is_futures and self.is_simulation:
            self.logger.info(f"🎮 Futures SIMULATION mode: using {self.leverage}x leverage (virtual only)")
        
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
                self.position,
                self.current_price,
                "Bot shutdown"
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
            # Check for sell/cover signal
            should_sell, reason, result_type = self.strategy.should_sell(
                position=self.position,
                current_price=self.current_price,
                current_rsi=self.current_rsi
            )
            
            if should_sell:
                if self.position.side == PositionSide.LONG:
                    self._execute_sell(self.position, self.current_price, reason)
                else:  # SHORT
                    self._execute_cover(self.position, self.current_price, reason)
        else:
            # Check for LONG signal
            should_buy, reason = self.strategy.should_buy(
                current_price=self.current_price,
                current_rsi=self.current_rsi,
                closes=self.closes,
                in_position=False
            )
            
            if should_buy:
                self._execute_buy(self.current_price, reason)
            
            # Check for SHORT signal (only in Futures mode)
            if self.is_futures:
                should_short, reason = self.strategy.should_short(
                    current_price=self.current_price,
                    current_rsi=self.current_rsi,
                    closes=self.closes,
                    in_position=False
                )
                
                if should_short:
                    self._execute_short(self.current_price, reason)
    
    def _execute_buy(self, price: float, reason: str):
        """
        Execute a buy order with risk management
        
        Args:
            price: Buy price
            reason: Buy reason
        """
        # Calculate position size with risk management
        quantity, sizing_details = self.risk_manager.calculate_position_size(
            current_balance=self.current_balance,
            entry_price=price,
            stop_loss_price=None,  # Can be enhanced with actual stop loss
            leverage=self.leverage
        )
        
        # Validate trade against risk rules
        is_valid, validation_msg = self.risk_manager.validate_trade(
            current_balance=self.current_balance,
            position_size=quantity,
            entry_price=price,
            leverage=self.leverage,
            stats=self.stats
        )
        
        if not is_valid:
            self.logger.error(validation_msg)
            return
        
        self.logger.info("=" * 60)
        self.logger.info(f"🟢 BUY SIGNAL: {reason}")
        self.logger.info(f"Price: {format_currency(price)} | Quantity: {quantity:.6f}")
        self.logger.info(f"RSI: {self.current_rsi:.2f}")
        if self.is_futures:
            self.logger.info(f"Leverage: {self.leverage}x | Position Value: {format_currency(quantity * price * self.leverage)}")
        self.logger.info(f"Position Sizing: {sizing_details}")
        self.logger.info(validation_msg)
        
        # Create position
        self.position = Position(
            symbol=self.symbol,
            quantity=quantity,
            entry_price=price,
            entry_time=datetime.now(),
            entry_rsi=self.current_rsi,
            side=PositionSide.LONG,
            current_price=price,
            current_rsi=self.current_rsi
        )
        
        # Execute order (simulation or real)
        if not self.is_simulation:
            if self.is_futures and self.futures_executor:
                # Futures order execution
                order = self.futures_executor.create_market_order(
                    symbol=self.symbol,
                    side='BUY',
                    quantity=quantity,
                    position_side='BOTH'  # Can be changed to 'LONG' for hedge mode
                )
            else:
                # Spot order execution
                order = self.exchange.create_market_buy(
                    symbol=self.symbol,
                    quantity=quantity
                )
            
            if not order:
                self.logger.error("❌ Failed to execute buy order")
                self.position = None
                return
        
        # Update balance (for Futures, this is margin used)
        if self.is_futures:
            # In Futures, we only use margin, not full balance
            margin_used = (quantity * price) / self.leverage
            self.current_balance -= margin_used
        else:
            # In Spot, we use full balance
            self.current_balance = 0.0
        
        self.stats.current_balance = self.current_balance
        
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
    
    def _execute_short(self, price: float, reason: str):
        """
        Execute a SHORT order (Futures only)
        
        Args:
            price: Entry price
            reason: Short reason
        """
        if not self.is_futures:
            self.logger.error("❌ SHORT positions only available in Futures mode")
            return
        
        # Calculate position size with risk management
        quantity, sizing_details = self.risk_manager.calculate_position_size(
            current_balance=self.current_balance,
            entry_price=price,
            stop_loss_price=None,
            leverage=self.leverage
        )
        
        # Validate trade against risk rules
        is_valid, validation_msg = self.risk_manager.validate_trade(
            current_balance=self.current_balance,
            position_size=quantity,
            entry_price=price,
            leverage=self.leverage,
            stats=self.stats
        )
        
        if not is_valid:
            self.logger.error(validation_msg)
            return
        
        self.logger.info("=" * 60)
        self.logger.info(f"🔴 SHORT SIGNAL: {reason}")
        self.logger.info(f"Price: {format_currency(price)} | Quantity: {quantity:.6f}")
        self.logger.info(f"RSI: {self.current_rsi:.2f}")
        self.logger.info(f"Leverage: {self.leverage}x | Position Value: {format_currency(quantity * price * self.leverage)}")
        self.logger.info(f"Position Sizing: {sizing_details}")
        self.logger.info(validation_msg)
        
        # Create SHORT position
        self.position = Position(
            symbol=self.symbol,
            quantity=quantity,
            entry_price=price,
            entry_time=datetime.now(),
            entry_rsi=self.current_rsi,
            side=PositionSide.SHORT,
            current_price=price,
            current_rsi=self.current_rsi
        )
        
        # Execute order (simulation or real)
        if not self.is_simulation:
            if self.futures_executor:
                # Futures SHORT order execution
                order = self.futures_executor.create_market_order(
                    symbol=self.symbol,
                    side='SELL',
                    quantity=quantity,
                    position_side='BOTH'  # Can be changed to 'SHORT' for hedge mode
                )
            
                if not order:
                    self.logger.error("❌ Failed to execute SHORT order")
                    self.position = None
                    return
        
        # Update balance (margin used)
        margin_used = (quantity * price) / self.leverage
        self.current_balance -= margin_used
        self.stats.current_balance = self.current_balance
        
        # Send notification
        self.notifier.send_trade_notification(
            trade_type=TradeType.SELL,  # SHORT is a SELL to open
            symbol=self.symbol,
            price=price,
            quantity=quantity,
            rsi=self.current_rsi,
            reason=f"SHORT: {reason}"
        )
        
        # Add to report
        self.reporter.log_buy(self.position, f"SHORT: {reason}")
        
        self.logger.info("=" * 60)
    
    def _execute_sell(self, position: Position, price: float, reason: str):
        """
        Execute a sell order with risk validation
        
        Args:
            position: Current position
            price: Sell price
            reason: Sell reason
        """
        # Validate position close
        is_valid, validation_msg = self.risk_manager.validate_position_close(
            position=position,
            current_price=price,
            reason=reason
        )
        
        if not is_valid:
            self.logger.error(f"❌ Position close blocked: {validation_msg}")
            return
        
        # Calculate P&L
        if self.is_futures:
            # For Futures, P&L is calculated with leverage
            entry_value = position.quantity * position.entry_price
            exit_value = position.quantity * price
            profit_loss = exit_value - entry_value
        else:
            # For Spot, standard calculation
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
        if self.is_futures:
            self.logger.info(f"Leverage: {self.leverage}x")
        
        # Execute order (simulation or real)
        if not self.is_simulation:
            if self.is_futures and self.futures_executor:
                # Futures order execution
                order = self.futures_executor.create_market_order(
                    symbol=self.symbol,
                    side='SELL',
                    quantity=position.quantity,
                    position_side='BOTH',
                    reduce_only=True
                )
            else:
                # Spot order execution
                order = self.exchange.create_market_sell(
                    symbol=self.symbol,
                    quantity=position.quantity
            )
            if not order:
                self.logger.error("❌ Failed to execute sell order")
                return
        
        # Update balance
        if self.is_futures:
            # For Futures, return margin and add P&L
            margin_used = (position.quantity * position.entry_price) / self.leverage
            self.current_balance += margin_used + profit_loss
        else:
            # For Spot, receive sell value
            sell_value = position.quantity * price
            self.current_balance = sell_value
        
        self.stats.current_balance = self.current_balance
        
        # Log risk status after trade
        self.risk_manager.log_risk_status(self.current_balance, self.stats)
        
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
    
    def _execute_cover(self, position: Position, price: float, reason: str):
        """
        Execute a COVER order to close SHORT position (Futures only)
        
        Args:
            position: Current SHORT position
            price: Cover price
            reason: Cover reason
        """
        # Validate position close
        is_valid, validation_msg = self.risk_manager.validate_position_close(
            position=position,
            current_price=price,
            reason=reason
        )
        
        if not is_valid:
            self.logger.error(f"❌ Position cover blocked: {validation_msg}")
            return
        
        # Calculate P&L for SHORT (profit when price goes DOWN)
        entry_value = position.quantity * position.entry_price
        exit_value = position.quantity * price
        profit_loss = entry_value - exit_value  # INVERSE for SHORT
        
        profit_loss_pct = (profit_loss / (position.quantity * position.entry_price)) * 100
        
        # Determine result
        result = TradeResult.WIN if profit_loss >= 0 else TradeResult.LOSS
        
        time_held = (datetime.now() - position.entry_time).total_seconds() / 60
        
        self.logger.info("=" * 60)
        
        if result == TradeResult.WIN:
            self.logger.info(f"🟢 COVER (WIN): {reason}")
        else:
            self.logger.warning(f"🔴 COVER (LOSS): {reason}")
        
        self.logger.info(f"Entry: {format_currency(position.entry_price)} | Cover: {format_currency(price)}")
        self.logger.info(f"P&L: {format_currency(profit_loss)} ({format_percentage(profit_loss_pct)})")
        self.logger.info(f"Time Held: {time_held:.1f} minutes")
        self.logger.info(f"RSI: {self.current_rsi:.2f}")
        self.logger.info(f"Leverage: {self.leverage}x")
        
        # Execute order (simulation or real)
        if not self.is_simulation:
            if self.futures_executor:
                # Futures COVER order (BUY to close SHORT)
                order = self.futures_executor.create_market_order(
                    symbol=self.symbol,
                    side='BUY',
                    quantity=position.quantity,
                    position_side='BOTH',
                    reduce_only=True
                )
                
                if not order:
                    self.logger.error("❌ Failed to execute cover order")
                    return
        
        # Update balance (return margin and add P&L)
        margin_used = (position.quantity * position.entry_price) / self.leverage
        self.current_balance += margin_used + profit_loss
        self.stats.current_balance = self.current_balance
        
        # Log risk status after trade
        self.risk_manager.log_risk_status(self.current_balance, self.stats)
        
        # Create trade record
        trade = Trade(
            id=str(uuid.uuid4()),
            symbol=self.symbol,
            trade_type=TradeType.BUY,  # COVER is a BUY to close
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
            trade_type=TradeType.BUY,  # COVER
            symbol=self.symbol,
            price=price,
            quantity=position.quantity,
            rsi=self.current_rsi,
            reason=f"COVER SHORT: {reason}",
            profit_loss=profit_loss,
            profit_loss_pct=profit_loss_pct
        )
        
        # Add to report
        self.reporter.log_sell(position, price, profit_loss, profit_loss_pct, f"COVER: {reason}", result)
        
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
        status = {
            'is_running': self.is_running,
            'is_simulation': self.is_simulation,
            'trading_mode': self.trading_mode,
            'is_futures': self.is_futures,
            'symbol': self.symbol,
            'current_price': self.current_price,
            'current_rsi': self.current_rsi,
            'current_balance': self.current_balance,
            'position': self.position.to_dict() if self.position else None,
            'stats': self.stats.to_dict(),
            'strategy_status': self.strategy.get_status_message(self.position, self.current_rsi),
            'oversold_intensity': round(self.strategy.oversold_intensity, 2),
            'oversold_counter': self.strategy.oversold_counter,
            'overbought_intensity': round(self.strategy.overbought_intensity, 2),
            'overbought_counter': self.strategy.overbought_counter
        }
        
        # Add Futures-specific information
        if self.is_futures:
            status['leverage'] = self.leverage
            status['margin_type'] = self.config.trading.MARGIN_TYPE
        
        # Add risk management status
        status['risk_status'] = self.risk_manager.get_risk_status(
            self.current_balance,
            self.stats
        )
        
        return status
