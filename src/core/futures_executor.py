"""
Binance Futures Executor Module
Handles Binance Futures API operations with leverage support
"""
import logging
from typing import Dict, List, Optional
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException

from config.settings import AppConfig


class FuturesExecutor:
    """
    Binance Futures execution handler with leverage and risk management.
    Supports long/short positions, dual-side mode, and advanced order types.
    """
    
    def __init__(self, client: Client, config: AppConfig):
        """
        Initialize Futures executor
        
        Args:
            client: Initialized Binance client
            config: Application configuration
        """
        self.logger = logging.getLogger(__name__)
        self.client = client
        self.config = config
        
        # Futures configuration
        self.default_leverage = config.trading.DEFAULT_LEVERAGE
        self.margin_type = config.trading.MARGIN_TYPE
        
        # Symbol-specific leverage cache
        self.leverage_cache: Dict[str, int] = {}
        
        self.logger.info("✓ Futures Executor initialized")
        self.logger.info(f"  Default Leverage: {self.default_leverage}x")
        self.logger.info(f"  Margin Type: {self.margin_type}")
    
    def set_leverage(self, symbol: str, leverage: Optional[int] = None) -> bool:
        """
        Set leverage for a symbol
        
        Args:
            symbol: Trading symbol (e.g., 'ETHUSDT')
            leverage: Leverage value (1-125), uses default if None
            
        Returns:
            True if successful
        """
        leverage = leverage or self.default_leverage
        
        # Check cache
        if symbol in self.leverage_cache and self.leverage_cache[symbol] == leverage:
            self.logger.debug(f"Leverage already set for {symbol}: {leverage}x")
            return True
        
        try:
            # Set leverage via Futures API
            response = self.client.futures_change_leverage(
                symbol=symbol,
                leverage=leverage
            )
            
            self.leverage_cache[symbol] = leverage
            self.logger.info(f"✓ Leverage set for {symbol}: {leverage}x")
            return True
            
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to set leverage for {symbol}: {e}")
            return False
    
    def set_margin_type(self, symbol: str, margin_type: Optional[str] = None) -> bool:
        """
        Set margin type for a symbol
        
        Args:
            symbol: Trading symbol
            margin_type: 'ISOLATED' or 'CROSSED', uses config default if None
            
        Returns:
            True if successful
        """
        margin_type = (margin_type or self.margin_type).upper()
        
        if margin_type not in ['ISOLATED', 'CROSSED']:
            self.logger.error(f"Invalid margin type: {margin_type}")
            return False
        
        try:
            # Set margin type via Futures API
            response = self.client.futures_change_margin_type(
                symbol=symbol,
                marginType=margin_type
            )
            
            self.logger.info(f"✓ Margin type set for {symbol}: {margin_type}")
            return True
            
        except BinanceAPIException as e:
            # Error code 4046 means margin type is already set
            if e.code == -4046:
                self.logger.debug(f"Margin type already set for {symbol}: {margin_type}")
                return True
            else:
                self.logger.error(f"✗ Failed to set margin type for {symbol}: {e}")
                return False
    
    def enable_hedge_mode(self) -> bool:
        """
        Enable hedge mode (dual-side position mode)
        Allows simultaneous long and short positions
        
        Returns:
            True if successful
        """
        try:
            # Check current position mode
            response = self.client.futures_get_position_mode()
            
            if response['dualSidePosition']:
                self.logger.debug("Hedge mode already enabled")
                return True
            
            # Enable hedge mode
            self.client.futures_change_position_mode(dualSidePosition=True)
            self.logger.info("✓ Hedge mode (dual-side) enabled")
            return True
            
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to enable hedge mode: {e}")
            return False
    
    def get_futures_balance(self) -> Dict:
        """
        Get Futures account balance
        
        Returns:
            Balance information
        """
        try:
            account = self.client.futures_account()
            
            total_balance = float(account['totalWalletBalance'])
            available_balance = float(account['availableBalance'])
            unrealized_pnl = float(account['totalUnrealizedProfit'])
            
            return {
                'total_balance': total_balance,
                'available_balance': available_balance,
                'unrealized_pnl': unrealized_pnl,
                'margin_balance': total_balance + unrealized_pnl
            }
            
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to get Futures balance: {e}")
            return {
                'total_balance': 0.0,
                'available_balance': 0.0,
                'unrealized_pnl': 0.0,
                'margin_balance': 0.0
            }
    
    def get_position(self, symbol: str) -> Optional[Dict]:
        """
        Get current position for a symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Position information or None
        """
        try:
            positions = self.client.futures_position_information(symbol=symbol)
            
            for pos in positions:
                position_amt = float(pos['positionAmt'])
                if position_amt != 0:
                    return {
                        'symbol': pos['symbol'],
                        'position_amt': position_amt,
                        'entry_price': float(pos['entryPrice']),
                        'unrealized_pnl': float(pos['unRealizedProfit']),
                        'leverage': int(pos['leverage']),
                        'position_side': pos['positionSide'],
                        'liquidation_price': float(pos['liquidationPrice']) if pos.get('liquidationPrice') else None
                    }
            
            return None
            
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to get position for {symbol}: {e}")
            return None
    
    def create_market_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        position_side: str = 'BOTH',
        reduce_only: bool = False
    ) -> Optional[Dict]:
        """
        Create a Futures market order
        
        Args:
            symbol: Trading symbol
            side: 'BUY' or 'SELL'
            quantity: Order quantity (in base asset)
            position_side: 'LONG', 'SHORT', or 'BOTH' (for hedge mode)
            reduce_only: If True, order only reduces position
            
        Returns:
            Order response or None
        """
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='MARKET',
                quantity=quantity,
                positionSide=position_side,
                reduceOnly=reduce_only
            )
            
            self.logger.info(
                f"✓ Futures {side} order created: {quantity} {symbol} "
                f"(Position: {position_side}, ReduceOnly: {reduce_only})"
            )
            
            return order
            
        except (BinanceAPIException, BinanceOrderException) as e:
            self.logger.error(f"✗ Failed to create Futures market order: {e}")
            return None
    
    def create_limit_order(
        self,
        symbol: str,
        side: str,
        quantity: float,
        price: float,
        position_side: str = 'BOTH',
        reduce_only: bool = False,
        time_in_force: str = 'GTC'
    ) -> Optional[Dict]:
        """
        Create a Futures limit order
        
        Args:
            symbol: Trading symbol
            side: 'BUY' or 'SELL'
            quantity: Order quantity
            price: Limit price
            position_side: 'LONG', 'SHORT', or 'BOTH'
            reduce_only: If True, order only reduces position
            time_in_force: Time in force ('GTC', 'IOC', 'FOK')
            
        Returns:
            Order response or None
        """
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='LIMIT',
                quantity=quantity,
                price=str(price),
                timeInForce=time_in_force,
                positionSide=position_side,
                reduceOnly=reduce_only
            )
            
            self.logger.info(
                f"✓ Futures {side} limit order created: {quantity} {symbol} @ ${price} "
                f"(Position: {position_side})"
            )
            
            return order
            
        except (BinanceAPIException, BinanceOrderException) as e:
            self.logger.error(f"✗ Failed to create Futures limit order: {e}")
            return None
    
    def create_stop_loss(
        self,
        symbol: str,
        side: str,
        quantity: float,
        stop_price: float,
        position_side: str = 'BOTH'
    ) -> Optional[Dict]:
        """
        Create a stop-loss order
        
        Args:
            symbol: Trading symbol
            side: 'BUY' or 'SELL' (opposite of position)
            quantity: Order quantity
            stop_price: Stop trigger price
            position_side: 'LONG', 'SHORT', or 'BOTH'
            
        Returns:
            Order response or None
        """
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='STOP_MARKET',
                quantity=quantity,
                stopPrice=str(stop_price),
                positionSide=position_side,
                reduceOnly=True
            )
            
            self.logger.info(
                f"✓ Stop-loss order created: {side} {quantity} {symbol} @ ${stop_price}"
            )
            
            return order
            
        except (BinanceAPIException, BinanceOrderException) as e:
            self.logger.error(f"✗ Failed to create stop-loss order: {e}")
            return None
    
    def create_take_profit(
        self,
        symbol: str,
        side: str,
        quantity: float,
        take_profit_price: float,
        position_side: str = 'BOTH'
    ) -> Optional[Dict]:
        """
        Create a take-profit order
        
        Args:
            symbol: Trading symbol
            side: 'BUY' or 'SELL' (opposite of position)
            quantity: Order quantity
            take_profit_price: Take profit trigger price
            position_side: 'LONG', 'SHORT', or 'BOTH'
            
        Returns:
            Order response or None
        """
        try:
            order = self.client.futures_create_order(
                symbol=symbol,
                side=side,
                type='TAKE_PROFIT_MARKET',
                quantity=quantity,
                stopPrice=str(take_profit_price),
                positionSide=position_side,
                reduceOnly=True
            )
            
            self.logger.info(
                f"✓ Take-profit order created: {side} {quantity} {symbol} @ ${take_profit_price}"
            )
            
            return order
            
        except (BinanceAPIException, BinanceOrderException) as e:
            self.logger.error(f"✗ Failed to create take-profit order: {e}")
            return None
    
    def close_position(
        self,
        symbol: str,
        position_side: str = 'BOTH'
    ) -> Optional[Dict]:
        """
        Close an existing position
        
        Args:
            symbol: Trading symbol
            position_side: 'LONG', 'SHORT', or 'BOTH'
            
        Returns:
            Order response or None
        """
        # Get current position
        position = self.get_position(symbol)
        
        if not position:
            self.logger.warning(f"No position to close for {symbol}")
            return None
        
        # Determine close side (opposite of position)
        position_amt = position['position_amt']
        if position_amt > 0:
            close_side = 'SELL'
            quantity = abs(position_amt)
        else:
            close_side = 'BUY'
            quantity = abs(position_amt)
        
        # Create market order to close
        return self.create_market_order(
            symbol=symbol,
            side=close_side,
            quantity=quantity,
            position_side=position_side,
            reduce_only=True
        )
    
    def cancel_all_orders(self, symbol: str) -> bool:
        """
        Cancel all open orders for a symbol
        
        Args:
            symbol: Trading symbol
            
        Returns:
            True if successful
        """
        try:
            self.client.futures_cancel_all_open_orders(symbol=symbol)
            self.logger.info(f"✓ All orders cancelled for {symbol}")
            return True
            
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to cancel orders for {symbol}: {e}")
            return False
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Get Futures symbol information and trading rules
        
        Args:
            symbol: Trading symbol
            
        Returns:
            Symbol information or None
        """
        try:
            exchange_info = self.client.futures_exchange_info()
            
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol:
                    return {
                        'symbol': s['symbol'],
                        'status': s['status'],
                        'base_asset': s['baseAsset'],
                        'quote_asset': s['quoteAsset'],
                        'price_precision': s['pricePrecision'],
                        'quantity_precision': s['quantityPrecision'],
                        'filters': s['filters']
                    }
            
            return None
            
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to get Futures symbol info: {e}")
            return None
