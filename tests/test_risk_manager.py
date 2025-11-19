"""
Unit tests for Risk Manager
"""
import pytest
from datetime import datetime
from config.settings import AppConfig
from src.core.risk_manager import RiskManager
from src.models.trading_models import Position, TradingStats


@pytest.fixture
def config():
    """Create test configuration"""
    cfg = AppConfig()
    cfg.trading.MAX_RISK_PER_TRADE_PCT = 2.0
    cfg.trading.MAX_DRAWDOWN_PCT = 10.0
    cfg.trading.DYNAMIC_POSITION_SIZING = True
    return cfg


@pytest.fixture
def risk_manager(config):
    """Create risk manager instance"""
    return RiskManager(config, initial_balance=1000.0)


def test_risk_manager_initialization(risk_manager):
    """Test risk manager initializes correctly"""
    assert risk_manager.initial_balance == 1000.0
    assert risk_manager.peak_balance == 1000.0
    assert risk_manager.current_drawdown_pct == 0.0
    assert risk_manager.max_risk_per_trade_pct == 2.0
    assert risk_manager.max_drawdown_pct == 10.0


def test_calculate_position_size_fixed(config):
    """Test fixed position sizing (dynamic=False)"""
    config.trading.DYNAMIC_POSITION_SIZING = False
    rm = RiskManager(config, initial_balance=1000.0)
    
    position_size, details = rm.calculate_position_size(
        current_balance=1000.0,
        entry_price=2000.0,
        leverage=1
    )
    
    assert position_size == 0.5  # 1000 / 2000
    assert "Fixed sizing" in details


def test_calculate_position_size_dynamic_no_stop_loss(risk_manager):
    """Test dynamic position sizing without stop loss"""
    position_size, details = risk_manager.calculate_position_size(
        current_balance=1000.0,
        entry_price=2000.0,
        leverage=5
    )
    
    # With 2% risk and 5x leverage: (1000 * 5 * 0.02) / 2000 = 0.05
    assert position_size == pytest.approx(0.05, rel=0.01)
    assert "Conservative sizing" in details


def test_calculate_position_size_dynamic_with_stop_loss(risk_manager):
    """Test dynamic position sizing with stop loss"""
    position_size, details = risk_manager.calculate_position_size(
        current_balance=1000.0,
        entry_price=2000.0,
        stop_loss_price=1900.0,  # 5% stop loss
        leverage=1
    )
    
    # Risk amount: 1000 * 0.02 = $20
    # Risk per unit: 2000 - 1900 = $100
    # Position size: 20 / 100 = 0.2
    assert position_size == pytest.approx(0.2, rel=0.01)
    assert "Dynamic sizing" in details
    assert "SL at" in details


def test_validate_trade_success(risk_manager):
    """Test trade validation passes with valid parameters"""
    is_valid, reason = risk_manager.validate_trade(
        current_balance=1000.0,
        position_size=0.5,
        entry_price=2000.0
    )
    
    assert is_valid is True
    assert "validated" in reason.lower()


def test_validate_trade_insufficient_balance(risk_manager):
    """Test trade validation fails with insufficient balance"""
    is_valid, reason = risk_manager.validate_trade(
        current_balance=0.0,
        position_size=0.5,
        entry_price=2000.0
    )
    
    assert is_valid is False
    assert "Insufficient balance" in reason


def test_validate_trade_position_too_large(risk_manager):
    """Test trade validation fails when position exceeds balance"""
    is_valid, reason = risk_manager.validate_trade(
        current_balance=1000.0,
        position_size=1.0,
        entry_price=2000.0  # 1.0 * 2000 = $2000 > $1000
    )
    
    assert is_valid is False
    assert "exceeds available balance" in reason


def test_validate_trade_max_drawdown_reached(risk_manager):
    """Test trade validation fails at max drawdown"""
    # Create stats with loss
    stats = TradingStats(
        start_balance=1000.0,
        current_balance=850.0  # 15% drawdown
    )
    
    # Simulate drawdown by updating peak
    risk_manager.peak_balance = 1000.0
    risk_manager._update_drawdown(850.0)
    
    is_valid, reason = risk_manager.validate_trade(
        current_balance=850.0,
        position_size=0.4,
        entry_price=2000.0,
        stats=stats
    )
    
    assert is_valid is False
    assert "Maximum drawdown reached" in reason


def test_drawdown_calculation(risk_manager):
    """Test drawdown is calculated correctly"""
    # Start at peak
    assert risk_manager.current_drawdown_pct == 0.0
    
    # Lose 10%
    risk_manager._update_drawdown(900.0)
    assert risk_manager.current_drawdown_pct == pytest.approx(10.0, rel=0.01)
    
    # Recover partially
    risk_manager._update_drawdown(950.0)
    assert risk_manager.current_drawdown_pct == pytest.approx(5.0, rel=0.01)
    
    # New peak
    risk_manager._update_drawdown(1100.0)
    assert risk_manager.current_drawdown_pct == 0.0
    assert risk_manager.peak_balance == 1100.0


def test_validate_position_close(risk_manager):
    """Test position close validation always passes"""
    position = Position(
        symbol="ETHUSDT",
        quantity=0.5,
        entry_price=2000.0,
        entry_time=datetime.now(),
        entry_rsi=30.0
    )
    
    is_valid, reason = risk_manager.validate_position_close(
        position=position,
        current_price=2100.0,
        reason="Take profit"
    )
    
    assert is_valid is True


def test_get_risk_status(risk_manager):
    """Test risk status report"""
    # Create some trading stats
    stats = TradingStats(
        start_balance=1000.0,
        current_balance=950.0,
        total_trades=10,
        winning_trades=6,
        total_profit_loss=-50.0
    )
    stats.win_rate = 60.0
    stats.total_profit_loss_percentage = -5.0
    
    risk_manager._update_drawdown(950.0)
    status = risk_manager.get_risk_status(950.0, stats)
    
    assert status['current_balance'] == 950.0
    assert status['initial_balance'] == 1000.0
    assert status['peak_balance'] == 1000.0
    assert status['current_drawdown_pct'] == 5.0
    assert status['max_drawdown_pct'] == 10.0
    assert status['drawdown_warning'] is False
    assert status['drawdown_critical'] is False
    assert status['win_rate'] == 60.0


def test_risk_status_warning(risk_manager):
    """Test risk status shows warning at 80% of max drawdown"""
    risk_manager._update_drawdown(920.0)  # 8% drawdown
    status = risk_manager.get_risk_status(920.0)
    
    assert status['drawdown_warning'] is True  # 8% >= 80% of 10%
    assert status['drawdown_critical'] is False


def test_risk_status_critical(risk_manager):
    """Test risk status shows critical at max drawdown"""
    risk_manager._update_drawdown(900.0)  # 10% drawdown
    status = risk_manager.get_risk_status(900.0)
    
    assert status['drawdown_warning'] is True
    assert status['drawdown_critical'] is True


def test_position_sizing_with_leverage(risk_manager):
    """Test position sizing accounts for leverage correctly"""
    # With 5x leverage, position value can be 5x balance
    position_size, details = risk_manager.calculate_position_size(
        current_balance=1000.0,
        entry_price=2000.0,
        leverage=5
    )
    
    # Conservative: (1000 * 5 * 0.02) / 2000 = 0.05
    assert position_size == pytest.approx(0.05, rel=0.01)
    assert "5x leverage" in details


def test_risk_manager_with_zero_balance(risk_manager):
    """Test risk manager handles zero balance gracefully"""
    position_size, details = risk_manager.calculate_position_size(
        current_balance=0.0,
        entry_price=2000.0,
        leverage=1
    )
    
    assert position_size == 0.0
    
    is_valid, reason = risk_manager.validate_trade(
        current_balance=0.0,
        position_size=0.0,
        entry_price=2000.0
    )
    
    assert is_valid is False
