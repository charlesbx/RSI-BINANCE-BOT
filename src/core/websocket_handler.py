"""
WebSocket Handler for Real-Time Market Data
"""
import json
import logging
import threading
from typing import Callable, Optional
import websocket
from datetime import datetime


class WebSocketHandler:
    """
    Handle Binance WebSocket connections for real-time market data
    """
    
    def __init__(self, symbol: str, on_message_callback: Callable):
        """
        Initialize WebSocket handler
        
        Args:
            symbol: Trading symbol (e.g., 'ETHUSDT')
            on_message_callback: Callback function for messages
        """
        self.logger = logging.getLogger(__name__)
        self.symbol = symbol.lower()
        self.on_message_callback = on_message_callback
        
        # WebSocket URL for kline data (1-minute candles)
        self.socket_url = f"wss://stream.binance.com:9443/ws/{self.symbol}@kline_1m"
        
        self.ws: Optional[websocket.WebSocketApp] = None
        self.ws_thread: Optional[threading.Thread] = None
        self.is_running = False
        
        self.logger.info(f"✓ WebSocket handler initialized for {symbol}")
    
    def on_open(self, ws):
        """Called when WebSocket connection is opened"""
        self.logger.info(f"📡 WebSocket connection opened for {self.symbol.upper()}")
        self.is_running = True
    
    def on_close(self, ws, close_status_code, close_msg):
        """Called when WebSocket connection is closed"""
        self.logger.warning(f"📡 WebSocket connection closed: {close_status_code} - {close_msg}")
        self.is_running = False
    
    def on_error(self, ws, error):
        """Called when WebSocket encounters an error"""
        self.logger.error(f"❌ WebSocket error: {error}")
    
    def on_message(self, ws, message):
        """
        Called when WebSocket receives a message
        
        Args:
            ws: WebSocket instance
            message: Raw message string
        """
        try:
            data = json.loads(message)
            
            # Extract kline data
            if 'k' in data:
                kline = data['k']
                candle_data = {
                    'symbol': kline['s'],
                    'timestamp': datetime.fromtimestamp(kline['t'] / 1000),
                    'open': float(kline['o']),
                    'high': float(kline['h']),
                    'low': float(kline['l']),
                    'close': float(kline['c']),
                    'volume': float(kline['v']),
                    'is_closed': kline['x']  # True when candle is closed
                }
                
                # Call the registered callback
                self.on_message_callback(candle_data)
            
        except json.JSONDecodeError as e:
            self.logger.error(f"❌ Failed to parse WebSocket message: {e}")
        except Exception as e:
            self.logger.error(f"❌ Error processing WebSocket message: {e}")
    
    def start(self):
        """Start WebSocket connection in a separate thread"""
        if self.is_running:
            self.logger.warning("WebSocket is already running")
            return
        
        self.logger.info(f"🚀 Starting WebSocket connection for {self.symbol.upper()}")
        
        # Create WebSocket app
        self.ws = websocket.WebSocketApp(
            self.socket_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close
        )
        
        # Run WebSocket in a separate thread
        self.ws_thread = threading.Thread(
            target=self._run_websocket,
            daemon=True
        )
        self.ws_thread.start()
    
    def _run_websocket(self):
        """Run WebSocket connection (called in separate thread)"""
        try:
            self.ws.run_forever()
        except Exception as e:
            self.logger.error(f"❌ WebSocket thread error: {e}")
            self.is_running = False
    
    def stop(self):
        """Stop WebSocket connection"""
        if not self.is_running:
            self.logger.warning("WebSocket is not running")
            return
        
        self.logger.info(f"🛑 Stopping WebSocket connection for {self.symbol.upper()}")
        
        if self.ws:
            self.ws.close()
        
        if self.ws_thread and self.ws_thread.is_alive():
            self.ws_thread.join(timeout=5)
        
        self.is_running = False
        self.logger.info("✓ WebSocket connection stopped")
    
    def is_connected(self) -> bool:
        """Check if WebSocket is connected"""
        return self.is_running
