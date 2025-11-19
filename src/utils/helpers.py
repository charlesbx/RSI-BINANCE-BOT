"""
Utility functions for the trading bot
"""
import logging
from typing import Union


def calculate_percentage(percentage: float, value: float) -> float:
    """
    Calculate percentage of a value
    
    Args:
        percentage: Percentage to calculate (e.g., 1.5 for 1.5%)
        value: Base value
        
    Returns:
        Calculated percentage value
    """
    return (percentage / 100) * value


def percentage_difference(start_value: float, end_value: float) -> float:
    """
    Calculate percentage difference between two values
    
    Args:
        start_value: Initial value
        end_value: Final value
        
    Returns:
        Percentage difference
    """
    if start_value == 0:
        return 0.0
    return ((end_value - start_value) / start_value) * 100


def format_currency(value: float, decimals: int = 2) -> str:
    """
    Format value as currency
    
    Args:
        value: Value to format
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    return f"${value:,.{decimals}f}"


def format_price(value: float, decimals: int = 2) -> str:
    """
    Alias for format_currency
    
    Args:
        value: Value to format
        decimals: Number of decimal places
        
    Returns:
        Formatted string
    """
    return format_currency(value, decimals)


def format_percentage(value: float, decimals: int = 2) -> str:
    """
    Format value as percentage
    
    Args:
        value: Value to format (e.g., 5.5 for 5.5%)
        decimals: Number of decimal places
        
    Returns:
        Formatted string with % sign
    """
    return f"{value:+.{decimals}f}%"


def round_to_precision(value: float, precision: int) -> float:
    """
    Round value to specified precision
    
    Args:
        value: Value to round
        precision: Number of decimal places
        
    Returns:
        Rounded value
    """
    return round(value, precision)


def validate_symbol(symbol: str) -> bool:
    """
    Validate trading symbol format
    
    Args:
        symbol: Trading symbol (e.g., ETHUSDT)
        
    Returns:
        True if valid, False otherwise
    """
    if not symbol or len(symbol) < 6:
        return False
    return symbol.isalpha() and symbol.isupper()


def setup_logger(name: str, log_file: str, level: Union[str, int] = logging.INFO) -> logging.Logger:
    """
    Setup a logger with file and console handlers
    
    Args:
        name: Logger name
        log_file: Path to log file
        level: Logging level
        
    Returns:
        Configured logger
    """
    # Convert string level to logging constant
    if isinstance(level, str):
        level = getattr(logging, level.upper(), logging.INFO)
    
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Remove existing handlers
    logger.handlers.clear()
    
    # Create formatters
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    console_formatter = logging.Formatter(
        '%(levelname)s: %(message)s'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(level)
    file_handler.setFormatter(file_formatter)
    logger.addHandler(file_handler)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    return logger


def validate_rsi_value(rsi: float) -> bool:
    """
    Validate RSI value is within correct range
    
    Args:
        rsi: RSI value to validate
        
    Returns:
        True if valid, False otherwise
    """
    return 0 <= rsi <= 100


def clamp(value: float, min_value: float, max_value: float) -> float:
    """
    Clamp a value between min and max
    
    Args:
        value: Value to clamp
        min_value: Minimum value
        max_value: Maximum value
        
    Returns:
        Clamped value
    """
    return max(min_value, min(value, max_value))
