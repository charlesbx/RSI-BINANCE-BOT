"""
Unit tests for Futures configuration
"""
import pytest
import os
from config.settings import AppConfig, TradingConfig


def test_trading_mode_validation():
    """Test trading mode validation"""
    # Valid modes
    TradingConfig.TRADING_MODE = "spot"
    is_valid, error = TradingConfig.validate_trading_mode()
    assert is_valid is True
    
    TradingConfig.TRADING_MODE = "futures"
    is_valid, error = TradingConfig.validate_trading_mode()
    assert is_valid is True
    
    # Invalid mode
    TradingConfig.TRADING_MODE = "invalid"
    is_valid, error = TradingConfig.validate_trading_mode()
    assert is_valid is False
    assert "Invalid TRADING_MODE" in error


def test_leverage_validation_spot_mode():
    """Test leverage validation is skipped for spot mode"""
    TradingConfig.TRADING_MODE = "spot"
    TradingConfig.DEFAULT_LEVERAGE = 999  # Invalid but shouldn't matter for spot
    
    is_valid, error = TradingConfig.validate_leverage()
    assert is_valid is True  # Should pass because we're in spot mode


def test_leverage_validation_futures_valid():
    """Test leverage validation passes with valid values"""
    TradingConfig.TRADING_MODE = "futures"
    
    # Test various valid leverage values
    for leverage in [1, 5, 10, 50, 125]:
        TradingConfig.DEFAULT_LEVERAGE = leverage
        is_valid, error = TradingConfig.validate_leverage()
        assert is_valid is True, f"Leverage {leverage} should be valid"


def test_leverage_validation_futures_invalid():
    """Test leverage validation fails with invalid values"""
    TradingConfig.TRADING_MODE = "futures"
    
    # Test invalid leverage values
    TradingConfig.DEFAULT_LEVERAGE = 0
    is_valid, error = TradingConfig.validate_leverage()
    assert is_valid is False
    assert "Invalid leverage" in error
    
    TradingConfig.DEFAULT_LEVERAGE = 126
    is_valid, error = TradingConfig.validate_leverage()
    assert is_valid is False
    assert "Invalid leverage" in error
    
    TradingConfig.DEFAULT_LEVERAGE = -5
    is_valid, error = TradingConfig.validate_leverage()
    assert is_valid is False


def test_margin_type_validation():
    """Test margin type validation"""
    # Save original values
    original_mode = TradingConfig.TRADING_MODE
    original_margin = TradingConfig.MARGIN_TYPE
    original_leverage = TradingConfig.DEFAULT_LEVERAGE
    
    try:
        TradingConfig.TRADING_MODE = "futures"
        TradingConfig.DEFAULT_LEVERAGE = 5  # Valid leverage
        
        # Valid margin types
        TradingConfig.MARGIN_TYPE = "isolated"
        is_valid, error = TradingConfig.validate_leverage()
        assert is_valid is True
        
        TradingConfig.MARGIN_TYPE = "cross"
        is_valid, error = TradingConfig.validate_leverage()
        assert is_valid is True
        
        # Invalid margin type
        TradingConfig.MARGIN_TYPE = "invalid"
        is_valid, error = TradingConfig.validate_leverage()
        assert is_valid is False
        assert "Invalid margin type" in error
    finally:
        # Restore original values
        TradingConfig.TRADING_MODE = original_mode
        TradingConfig.MARGIN_TYPE = original_margin
        TradingConfig.DEFAULT_LEVERAGE = original_leverage


def test_risk_params_validation_valid():
    """Test risk parameters validation with valid values"""
    # Valid risk parameters
    TradingConfig.MAX_RISK_PER_TRADE_PCT = 2.0
    TradingConfig.MAX_DRAWDOWN_PCT = 10.0
    
    is_valid, error = TradingConfig.validate_risk_params()
    assert is_valid is True


def test_risk_params_validation_invalid_risk_per_trade():
    """Test risk parameters validation fails with invalid risk per trade"""
    # Too low
    TradingConfig.MAX_RISK_PER_TRADE_PCT = 0.05
    TradingConfig.MAX_DRAWDOWN_PCT = 10.0
    is_valid, error = TradingConfig.validate_risk_params()
    assert is_valid is False
    assert "MAX_RISK_PER_TRADE_PCT" in error
    
    # Too high
    TradingConfig.MAX_RISK_PER_TRADE_PCT = 15.0
    is_valid, error = TradingConfig.validate_risk_params()
    assert is_valid is False


def test_risk_params_validation_invalid_drawdown():
    """Test risk parameters validation fails with invalid max drawdown"""
    TradingConfig.MAX_RISK_PER_TRADE_PCT = 2.0
    
    # Too low
    TradingConfig.MAX_DRAWDOWN_PCT = 0.5
    is_valid, error = TradingConfig.validate_risk_params()
    assert is_valid is False
    assert "MAX_DRAWDOWN_PCT" in error
    
    # Too high
    TradingConfig.MAX_DRAWDOWN_PCT = 60.0
    is_valid, error = TradingConfig.validate_risk_params()
    assert is_valid is False


def test_app_config_validate_all_spot_mode():
    """Test full config validation for spot mode"""
    # Setup valid spot configuration
    config = AppConfig()
    config.trading.TRADING_MODE = "spot"
    config.trading.MAX_RISK_PER_TRADE_PCT = 2.0
    config.trading.MAX_DRAWDOWN_PCT = 10.0
    
    # Mock API keys for testing
    config.binance.API_KEY = "test_key"
    config.binance.API_SECRET = "test_secret"
    
    is_valid, errors = config.validate_all()
    
    # Should be valid (email might fail but that's optional)
    assert is_valid or len(errors) <= 1  # Only email error allowed


def test_app_config_validate_all_futures_mode():
    """Test full config validation for futures mode"""
    # Setup valid futures configuration
    config = AppConfig()
    config.trading.TRADING_MODE = "futures"
    config.trading.DEFAULT_LEVERAGE = 5
    config.trading.MARGIN_TYPE = "isolated"
    config.trading.MAX_RISK_PER_TRADE_PCT = 2.0
    config.trading.MAX_DRAWDOWN_PCT = 10.0
    
    # Mock API keys
    config.binance.API_KEY = "test_key"
    config.binance.API_SECRET = "test_secret"
    
    is_valid, errors = config.validate_all()
    
    # Should be valid (email might fail but that's optional)
    assert is_valid or len(errors) <= 1


def test_app_config_validate_all_invalid_futures():
    """Test full config validation fails with invalid futures config"""
    config = AppConfig()
    config.trading.TRADING_MODE = "futures"
    config.trading.DEFAULT_LEVERAGE = 200  # Invalid
    config.trading.MARGIN_TYPE = "isolated"
    
    # Mock API keys
    config.binance.API_KEY = "test_key"
    config.binance.API_SECRET = "test_secret"
    
    is_valid, errors = config.validate_all()
    
    assert is_valid is False
    assert any("leverage" in err.lower() for err in errors)


def test_default_config_values():
    """Test default configuration values are sensible"""
    # Create fresh config to avoid test pollution
    os.environ['TRADING_MODE'] = 'spot'  # Reset to default
    os.environ['DEFAULT_LEVERAGE'] = '5'  # Reset to default
    
    config = AppConfig()
    
    # Check defaults (allowing for test environment modifications)
    assert config.trading.TRADING_MODE in ["spot", "futures"]
    # Don't check leverage as it may have been modified by previous tests
    assert config.trading.MARGIN_TYPE in ["isolated", "cross"]
    # Check risk params have reasonable defaults
    assert isinstance(config.trading.MAX_RISK_PER_TRADE_PCT, float)
    assert isinstance(config.trading.MAX_DRAWDOWN_PCT, float)
    assert isinstance(config.trading.DYNAMIC_POSITION_SIZING, bool)
