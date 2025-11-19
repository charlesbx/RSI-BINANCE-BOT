"""
Data models for the trading bot
"""
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Optional


class TradeType(Enum):
    """Trade type enumeration"""
    BUY = "BUY"
    SELL = "SELL"


class TradeResult(Enum):
    """Trade result enumeration"""
    WIN = "WIN"
    LOSS = "LOSS"
    PENDING = "PENDING"


class OrderStatus(Enum):
    """Order status enumeration"""
    NEW = "NEW"
    FILLED = "FILLED"
    PARTIALLY_FILLED = "PARTIALLY_FILLED"
    CANCELED = "CANCELED"
    PENDING_CANCEL = "PENDING_CANCEL"
    REJECTED = "REJECTED"
    EXPIRED = "EXPIRED"


@dataclass
class Trade:
    """Trade information"""
    id: str
    symbol: str
    trade_type: TradeType
    quantity: float
    price: float
    timestamp: datetime
    rsi_value: float
    status: OrderStatus = OrderStatus.NEW
    is_simulation: bool = True
    
    # Additional metadata
    buy_price: Optional[float] = None
    sell_price: Optional[float] = None
    profit_loss: Optional[float] = None
    profit_loss_percentage: Optional[float] = None
    result: TradeResult = TradeResult.PENDING
    time_held: Optional[float] = None  # in minutes
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "id": self.id,
            "symbol": self.symbol,
            "trade_type": self.trade_type.value,
            "quantity": self.quantity,
            "price": self.price,
            "timestamp": self.timestamp.isoformat(),
            "rsi_value": self.rsi_value,
            "status": self.status.value,
            "is_simulation": self.is_simulation,
            "buy_price": self.buy_price,
            "sell_price": self.sell_price,
            "profit_loss": self.profit_loss,
            "profit_loss_percentage": self.profit_loss_percentage,
            "result": self.result.value,
            "time_held": self.time_held
        }


@dataclass
class Position:
    """Current trading position"""
    symbol: str
    quantity: float
    entry_price: float
    entry_time: datetime
    entry_rsi: float
    current_price: float = 0.0
    current_rsi: float = 0.0
    unrealized_pnl: float = 0.0
    unrealized_pnl_percentage: float = 0.0
    
    def update(self, current_price: float, current_rsi: float):
        """Update current position values"""
        self.current_price = current_price
        self.current_rsi = current_rsi
        self.unrealized_pnl = (current_price - self.entry_price) * self.quantity
        self.unrealized_pnl_percentage = ((current_price / self.entry_price) - 1) * 100
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "quantity": self.quantity,
            "entry_price": self.entry_price,
            "entry_time": self.entry_time.isoformat(),
            "entry_rsi": self.entry_rsi,
            "current_price": self.current_price,
            "current_rsi": self.current_rsi,
            "unrealized_pnl": self.unrealized_pnl,
            "unrealized_pnl_percentage": self.unrealized_pnl_percentage,
            "time_held_minutes": (datetime.now() - self.entry_time).total_seconds() / 60
        }


@dataclass
class TradingStats:
    """Trading statistics"""
    total_trades: int = 0
    winning_trades: int = 0
    losing_trades: int = 0
    total_profit_loss: float = 0.0
    total_profit_loss_percentage: float = 0.0
    win_rate: float = 0.0
    average_profit: float = 0.0
    average_loss: float = 0.0
    average_trade_duration: float = 0.0  # in minutes
    largest_win: float = 0.0
    largest_loss: float = 0.0
    start_balance: float = 0.0
    current_balance: float = 0.0
    start_time: datetime = field(default_factory=datetime.now)
    
    def update(self, trade: Trade):
        """Update statistics with a new trade"""
        self.total_trades += 1
        
        if trade.result == TradeResult.WIN:
            self.winning_trades += 1
            if trade.profit_loss:
                self.average_profit = (
                    (self.average_profit * (self.winning_trades - 1) + trade.profit_loss) 
                    / self.winning_trades
                )
                if trade.profit_loss > self.largest_win:
                    self.largest_win = trade.profit_loss
        
        elif trade.result == TradeResult.LOSS:
            self.losing_trades += 1
            if trade.profit_loss:
                self.average_loss = (
                    (self.average_loss * (self.losing_trades - 1) + trade.profit_loss) 
                    / self.losing_trades
                )
                if trade.profit_loss < self.largest_loss:
                    self.largest_loss = trade.profit_loss
        
        if trade.profit_loss:
            self.total_profit_loss += trade.profit_loss
        
        if self.total_trades > 0:
            self.win_rate = (self.winning_trades / self.total_trades) * 100
        
        if trade.time_held:
            self.average_trade_duration = (
                (self.average_trade_duration * (self.total_trades - 1) + trade.time_held) 
                / self.total_trades
            )
        
        if self.start_balance > 0:
            self.total_profit_loss_percentage = (
                (self.current_balance / self.start_balance - 1) * 100
            )
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "total_trades": self.total_trades,
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "total_profit_loss": round(self.total_profit_loss, 2),
            "total_profit_loss_percentage": round(self.total_profit_loss_percentage, 2),
            "win_rate": round(self.win_rate, 2),
            "average_profit": round(self.average_profit, 2),
            "average_loss": round(self.average_loss, 2),
            "average_trade_duration": round(self.average_trade_duration, 2),
            "largest_win": round(self.largest_win, 2),
            "largest_loss": round(self.largest_loss, 2),
            "start_balance": round(self.start_balance, 2),
            "current_balance": round(self.current_balance, 2),
            "runtime_hours": round((datetime.now() - self.start_time).total_seconds() / 3600, 2),
            "trades_per_hour": round(
                self.total_trades / max((datetime.now() - self.start_time).total_seconds() / 3600, 0.01),
                2
            )
        }


@dataclass
class MarketData:
    """Market data snapshot"""
    symbol: str
    timestamp: datetime
    open_price: float
    high_price: float
    low_price: float
    close_price: float
    volume: float
    rsi: Optional[float] = None
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {
            "symbol": self.symbol,
            "timestamp": self.timestamp.isoformat(),
            "open": self.open_price,
            "high": self.high_price,
            "low": self.low_price,
            "close": self.close_price,
            "volume": self.volume,
            "rsi": self.rsi
        }
