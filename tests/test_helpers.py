"""
Unit tests for utility helpers
"""
import pytest
from src.utils.helpers import (
    calculate_percentage,
    percentage_difference,
    format_currency,
    format_percentage,
    round_to_precision,
    validate_symbol,
    validate_rsi_value,
    clamp
)


def test_calculate_percentage():
    """Test percentage calculation"""
    assert calculate_percentage(10, 100) == 10.0
    assert calculate_percentage(5, 200) == 10.0
    assert calculate_percentage(0, 100) == 0.0


def test_percentage_difference():
    """Test percentage difference calculation"""
    assert percentage_difference(100, 110) == 10.0
    assert percentage_difference(100, 90) == -10.0
    assert percentage_difference(0, 10) == 0.0


def test_format_currency():
    """Test currency formatting"""
    assert format_currency(1234.56) == "$1,234.56"
    assert format_currency(0.99) == "$0.99"
    assert format_currency(1234.567, 3) == "$1,234.567"


def test_format_percentage():
    """Test percentage formatting"""
    assert format_percentage(5.67) == "+5.67%"
    assert format_percentage(-3.45) == "-3.45%"
    assert format_percentage(0) == "+0.00%"


def test_round_to_precision():
    """Test precision rounding"""
    assert round_to_precision(1.23456, 2) == 1.23
    assert round_to_precision(1.23456, 4) == 1.2346
    assert round_to_precision(1.5, 0) == 2.0


def test_validate_symbol():
    """Test symbol validation"""
    assert validate_symbol("ETHUSDT")
    assert validate_symbol("BTCUSDT")
    assert not validate_symbol("eth")
    assert not validate_symbol("ETH")
    assert not validate_symbol("")
    assert not validate_symbol("123")


def test_validate_rsi_value():
    """Test RSI validation"""
    assert validate_rsi_value(50)
    assert validate_rsi_value(0)
    assert validate_rsi_value(100)
    assert not validate_rsi_value(-1)
    assert not validate_rsi_value(101)


def test_clamp():
    """Test value clamping"""
    assert clamp(5, 0, 10) == 5
    assert clamp(-5, 0, 10) == 0
    assert clamp(15, 0, 10) == 10
