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

