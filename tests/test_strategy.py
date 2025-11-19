"""
Unit tests for RSI Strategy
"""
import pytest
from datetime import datetime, timedelta
from src.strategies.rsi_strategy import RSIStrategy
from src.models.trading_models import Position
from config.settings import AppConfig


@pytest.fixture
def config():
    """Create test configuration"""
    return AppConfig()


@pytest.fixture
def strategy(config):
    """Create RSI strategy instance"""
    return RSIStrategy(config)


def test_strategy_initialization(strategy):
    """Test strategy initialization"""
    assert strategy.rsi_period == 14
    assert strategy.rsi_overbought == 70
    assert strategy.rsi_oversold == 30
    assert strategy.oversold_counter == 0


def test_update_price_extremes(strategy):
    """Test price extreme tracking"""
    strategy.update_price_extremes(2000.0, 45.0)
    assert strategy.highest_price == 2000.0
    assert strategy.lowest_rsi == 45.0
    assert strategy.highest_rsi == 45.0
    
    strategy.update_price_extremes(1950.0, 35.0)
    assert strategy.highest_price == 2000.0
    assert strategy.lowest_rsi == 35.0
    
    strategy.update_price_extremes(2100.0, 55.0)
    assert strategy.highest_price == 2100.0
    assert strategy.highest_rsi == 55.0


def test_should_buy_not_in_position(strategy):
    """Test buy signal when not in position"""
    closes = [2000.0] * 500  # Dummy price history
    
    # Test RSI oversold
    should_buy, reason = strategy.should_buy(
        current_price=1950.0,
        current_rsi=25.0,
        closes=closes,
        in_position=False
    )
    
    # Should not buy immediately (counter not met)
    assert not should_buy


def test_should_buy_already_in_position(strategy):
    """Test buy signal when already in position"""
    closes = [2000.0] * 500
    
    should_buy, reason = strategy.should_buy(
        current_price=1950.0,
        current_rsi=25.0,
        closes=closes,
        in_position=True
    )
    
    assert not should_buy
    assert reason == "Already in position"


def test_reset_extremes(strategy):
    """Test resetting price extremes"""
    strategy.update_price_extremes(2000.0, 45.0)
    strategy.reset_extremes()
    
    assert strategy.highest_price == 0.0
    assert strategy.lowest_rsi == 100.0
    assert strategy.highest_rsi == 0.0


def test_sell_no_position(strategy):
    """Test sell signal with no position"""
    should_sell, reason, result = strategy.should_sell(
        position=None,
        current_price=2000.0,
        current_rsi=75.0
    )
    
    assert not should_sell
    assert reason == "No position"


def test_sell_big_profit(strategy):
    """Test sell signal with big profit"""
    position = Position(
        symbol="ETHUSDT",
        quantity=1.0,
        entry_price=2000.0,
        entry_time=datetime.now() - timedelta(hours=1),
        entry_rsi=35.0
    )
    
    # 3% profit
    should_sell, reason, result = strategy.should_sell(
        position=position,
        current_price=2060.0,  # 3% profit
        current_rsi=55.0
    )
    
    assert should_sell
    assert result == "win"
    assert "Big profit" in reason
