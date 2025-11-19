"""
Binance Exchange Client Wrapper
Supports both Spot and Futures trading
"""
import logging
from typing import Dict, List, Optional
from binance.client import Client
from binance.enums import *
from binance.exceptions import BinanceAPIException, BinanceOrderException

from config.settings import AppConfig
from src.models.trading_models import Trade, TradeType, OrderStatus


class BinanceClient:
    """
    Unified wrapper for Binance Spot and Futures API with error handling and logging.
    Automatically routes operations based on trading mode.
    """
    
    def __init__(self, api_key: str, api_secret: str, trading_mode: str = "spot", testnet: bool = False):
        """
        Initialize Binance client
        
        Args:
            api_key: Binance API key
            api_secret: Binance API secret
            trading_mode: "spot" or "futures"
            testnet: Use testnet instead of production
        """
        self.logger = logging.getLogger(__name__)
        self.api_key = api_key
        self.api_secret = api_secret
        self.trading_mode = trading_mode.lower()
        self.testnet = testnet
        
        if self.trading_mode not in ["spot", "futures"]:
            raise ValueError(f"Invalid trading_mode: {self.trading_mode}. Must be 'spot' or 'futures'")
        
        try:
            self.client = Client(
                api_key=api_key,
                api_secret=api_secret,
                tld='com'
            )
            mode_str = "FUTURES" if self.trading_mode == "futures" else "SPOT"
            self.logger.info(f"✓ Binance {mode_str} client initialized successfully")
        except Exception as e:
            self.logger.error(f"✗ Failed to initialize Binance client: {e}")
            raise
    
    def is_futures(self) -> bool:
        """Check if trading mode is Futures"""
        return self.trading_mode == "futures"
    
    def is_spot(self) -> bool:
        """Check if trading mode is Spot"""
        return self.trading_mode == "spot"
    
    def test_connection(self) -> bool:
        """
        Test connection to Binance API
        
        Returns:
            True if connection is successful
        """
        try:
            self.client.ping()
            self.logger.info("✓ Binance API connection test successful")
            return True
        except Exception as e:
            self.logger.error(f"✗ Binance API connection test failed: {e}")
            return False
    
    def get_account_balance(self, asset: str) -> Dict:
        """
        Get account balance for a specific asset (works for both Spot and Futures)
        
        Args:
            asset: Asset symbol (e.g., 'BTC', 'ETH', 'USDT')
            
        Returns:
            Balance information
        """
        try:
            if self.is_futures():
                # Get Futures account balance
                account = self.client.futures_account()
                
                # Find specific asset balance
                for balance in account.get('assets', []):
                    if balance['asset'] == asset:
                        return {
                            'asset': asset,
                            'free': float(balance['availableBalance']),
                            'locked': float(balance['initialMargin']),
                            'total': float(balance['walletBalance'])
                        }
                
                return {'asset': asset, 'free': 0.0, 'locked': 0.0, 'total': 0.0}
            else:
                # Get Spot balance
                balance = self.client.get_asset_balance(asset=asset)
                return {
                    'asset': asset,
                    'free': float(balance['free']),
                    'locked': float(balance['locked']),
                    'total': float(balance['free']) + float(balance['locked'])
                }
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to get balance for {asset}: {e}")
            return {'asset': asset, 'free': 0.0, 'locked': 0.0, 'total': 0.0}
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict]:
        """
        Get trading rules and info for a symbol (works for both Spot and Futures)
        
        Args:
            symbol: Trading pair (e.g., 'ETHUSDT')
            
        Returns:
            Symbol information or None if not found
        """
        try:
            if self.is_futures():
                exchange_info = self.client.futures_exchange_info()
            else:
                exchange_info = self.client.get_exchange_info()
            
            for s in exchange_info['symbols']:
                if s['symbol'] == symbol:
                    return s
            return None
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to get symbol info for {symbol}: {e}")
            return None
    
    def get_symbol_ticker(self, symbol: str) -> Optional[Dict]:
        """
        Get 24hr ticker price change statistics
        
        Args:
            symbol: Trading pair (e.g., 'ETHUSDT')
            
        Returns:
            Ticker information
        """
        try:
            ticker = self.client.get_ticker(symbol=symbol)
            return {
                'symbol': ticker['symbol'],
                'lastPrice': float(ticker['lastPrice']),
                'highPrice': float(ticker['highPrice']),
                'lowPrice': float(ticker['lowPrice']),
                'volume': float(ticker['volume']),
                'priceChange': float(ticker['priceChange']),
                'priceChangePercent': float(ticker['priceChangePercent'])
            }
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to get ticker for {symbol}: {e}")
            return None
    
    def get_klines(self, symbol: str, interval: str, limit: int = 500) -> List[Dict]:
        """
        Get candlestick/kline data (works for both Spot and Futures)
        
        Args:
            symbol: Trading pair
            interval: Kline interval (e.g., '1m', '5m', '1h')
            limit: Number of klines to retrieve (max 1000)
            
        Returns:
            List of kline data
        """
        try:
            if self.is_futures():
                klines = self.client.futures_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )
            else:
                klines = self.client.get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit
                )
            
            return [{
                'open_time': kline[0],
                'open': float(kline[1]),
                'high': float(kline[2]),
                'low': float(kline[3]),
                'close': float(kline[4]),
                'volume': float(kline[5]),
                'close_time': kline[6]
            } for kline in klines]
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to get klines for {symbol}: {e}")
            return []
    
    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        time_in_force: str = 'GTC',
        position_side: str = 'BOTH'
    ) -> Optional[Dict]:
        """
        Create a new order (unified for Spot and Futures)
        
        Args:
            symbol: Trading pair
            side: 'BUY' or 'SELL'
            order_type: 'MARKET', 'LIMIT', etc.
            quantity: Order quantity
            price: Order price (required for LIMIT orders)
            time_in_force: Time in force (for LIMIT orders)
            position_side: 'BOTH', 'LONG', or 'SHORT' (Futures only)
            
        Returns:
            Order response or None if failed
        """
        try:
            if self.is_futures():
                # Futures order
                if order_type == 'MARKET':
                    order = self.client.futures_create_order(
                        symbol=symbol,
                        side=side,
                        type=order_type,
                        quantity=quantity,
                        positionSide=position_side
                    )
                elif order_type == 'LIMIT':
                    if price is None:
                        raise ValueError("Price is required for LIMIT orders")
                    order = self.client.futures_create_order(
                        symbol=symbol,
                        side=side,
                        type=order_type,
                        timeInForce=time_in_force,
                        quantity=quantity,
                        price=str(price),
                        positionSide=position_side
                    )
                else:
                    raise ValueError(f"Unsupported order type: {order_type}")
            else:
                # Spot order
                if order_type == 'MARKET':
                    order = self.client.create_order(
                        symbol=symbol,
                        side=side,
                        type=order_type,
                        quantity=quantity
                    )
                elif order_type == 'LIMIT':
                    if price is None:
                        raise ValueError("Price is required for LIMIT orders")
                    order = self.client.create_order(
                        symbol=symbol,
                        side=side,
                        type=order_type,
                        timeInForce=time_in_force,
                        quantity=quantity,
                        price=str(price)
                    )
                else:
                    raise ValueError(f"Unsupported order type: {order_type}")
            
            mode_str = "Futures" if self.is_futures() else "Spot"
            self.logger.info(f"✓ {mode_str} order created: {side} {quantity} {symbol} at {order.get('price', 'MARKET')}")
            return order
            
        except (BinanceAPIException, BinanceOrderException) as e:
            self.logger.error(f"✗ Failed to create order: {e}")
            return None
    
    def create_market_buy(self, symbol: str, quantity: float) -> Optional[Dict]:
        """
        Create a market buy order
        
        Args:
            symbol: Trading pair
            quantity: Quantity to buy (in quote currency for MARKET orders)
            
        Returns:
            Order response
        """
        return self.create_order(
            symbol=symbol,
            side=SIDE_BUY,
            order_type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
    
    def create_market_sell(self, symbol: str, quantity: float) -> Optional[Dict]:
        """
        Create a market sell order
        
        Args:
            symbol: Trading pair
            quantity: Quantity to sell (in base currency)
            
        Returns:
            Order response
        """
        return self.create_order(
            symbol=symbol,
            side=SIDE_SELL,
            order_type=ORDER_TYPE_MARKET,
            quantity=quantity
        )
    
    def get_order_status(self, symbol: str, order_id: int) -> Optional[Dict]:
        """
        Get order status
        
        Args:
            symbol: Trading pair
            order_id: Order ID
            
        Returns:
            Order information
        """
        try:
            order = self.client.get_order(symbol=symbol, orderId=order_id)
            return order
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to get order status: {e}")
            return None
    
    def cancel_order(self, symbol: str, order_id: int) -> bool:
        """
        Cancel an order
        
        Args:
            symbol: Trading pair
            order_id: Order ID
            
        Returns:
            True if successful
        """
        try:
            self.client.cancel_order(symbol=symbol, orderId=order_id)
            self.logger.info(f"✓ Order {order_id} cancelled")
            return True
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to cancel order {order_id}: {e}")
            return False
    
    def get_recent_trades(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Get recent trades
        
        Args:
            symbol: Trading pair
            limit: Number of trades to retrieve
            
        Returns:
            List of recent trades
        """
        try:
            trades = self.client.get_recent_trades(symbol=symbol, limit=limit)
            return trades
        except BinanceAPIException as e:
            self.logger.error(f"✗ Failed to get recent trades: {e}")
            return []
