"""
Configuration settings for the RSI Trading Bot
"""
import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Project root directory
ROOT_DIR = Path(__file__).parent.parent.absolute()

# ==================== BINANCE API CONFIGURATION ====================
class BinanceConfig:
    """Binance API configuration"""
    API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    API_SECRET: str = os.getenv("BINANCE_API_SECRET", "")
    TLD: str = os.getenv("BINANCE_TLD", "com")
    TESTNET: bool = os.getenv("BINANCE_TESTNET", "false").lower() == "true"
    
    @classmethod
    def validate(cls) -> bool:
        """Validate that required API credentials are set"""
        if not cls.API_KEY or not cls.API_SECRET:
            return False
        return True


# ==================== TRADING CONFIGURATION ====================
class TradingConfig:
    """Trading strategy configuration"""
    # RSI Settings
    RSI_PERIOD: int = int(os.getenv("DEFAULT_RSI_PERIOD", "14"))
    RSI_OVERBOUGHT: int = int(os.getenv("DEFAULT_RSI_OVERBOUGHT", "70"))
    RSI_OVERSOLD: int = int(os.getenv("DEFAULT_RSI_OVERSOLD", "30"))
    
    # Trading pair
    TRADE_SYMBOL: str = os.getenv("DEFAULT_TRADE_SYMBOL", "ETHUSDT")
    TRADE_QUANTITY: float = float(os.getenv("DEFAULT_TRADE_QUANTITY", "1000"))
    
    # Risk management
    MAX_LOSS_PERCENTAGE: float = 2.0  # Maximum loss per trade
    MIN_PROFIT_PERCENTAGE: float = 0.75  # Minimum profit to take with RSI
    BIG_PROFIT_PERCENTAGE: float = 3.0  # Big profit target without RSI
    
    # Time-based sell conditions (more adaptive)
    SELL_AT_LOSS_0_5_HOURS: float = 0.5  # Sell at -0.5% after 30 min (was 1h)
    SELL_AT_LOSS_1_0_HOURS: float = 1.5  # Sell at -1% after 1.5h (was 2h)
    SELL_AT_LOSS_2_0_HOURS: float = 2.5  # Sell at -2% after 2.5h (was 3h)
    MAX_HOLD_HOURS: float = 4.0  # Maximum hold time before aggressive exit
    
    # Buy conditions
    MIN_RSI_COUNTER: int = 3  # Minimum RSI oversold occurrences before buy
    RSI_BOUNCE_THRESHOLD: int = 3  # RSI bounce to confirm buy signal
    MIN_TIME_AFTER_SELL: int = 5  # Minutes to wait after sell before buying
    
    # Simulation mode
    SIMULATION_MODE: bool = os.getenv("SIMULATION_MODE", "true").lower() == "true"


# ==================== NOTIFICATION CONFIGURATION ====================
class NotificationConfig:
    """Email and notification settings"""
    ENABLE_EMAIL: bool = os.getenv("ENABLE_EMAIL_NOTIFICATIONS", "true").lower() == "true"
    
    SMTP_HOST: str = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "465"))
    SMTP_EMAIL: str = os.getenv("SMTP_EMAIL", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    NOTIFICATION_EMAIL: str = os.getenv("NOTIFICATION_EMAIL", "")
    
    @classmethod
    def validate(cls) -> bool:
        """Validate email configuration"""
        if cls.ENABLE_EMAIL:
            return bool(cls.SMTP_EMAIL and cls.SMTP_PASSWORD and cls.NOTIFICATION_EMAIL)
        return True


# ==================== LOGGING CONFIGURATION ====================
class LoggingConfig:
    """Logging configuration"""
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_DIR: Path = ROOT_DIR / "logs"
    LOG_FILE: str = "trading_bot.log"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_MAX_BYTES: int = 10 * 1024 * 1024  # 10MB
    LOG_BACKUP_COUNT: int = 5


# ==================== DASHBOARD CONFIGURATION ====================
class DashboardConfig:
    """Web dashboard configuration"""
    ENABLE_DASHBOARD: bool = os.getenv("ENABLE_WEB_DASHBOARD", "true").lower() == "true"
    BACKEND_HOST: str = os.getenv("DASHBOARD_HOST", "0.0.0.0")
    BACKEND_PORT: int = int(os.getenv("DASHBOARD_PORT", "5000"))
    FRONTEND_PORT: int = int(os.getenv("FRONTEND_PORT", "3000"))
    
    # WebSocket for real-time updates
    WEBSOCKET_ENABLED: bool = True
    UPDATE_INTERVAL: int = 1  # seconds


# ==================== DATA CONFIGURATION ====================
class DataConfig:
    """Data storage configuration"""
    DATA_DIR: Path = ROOT_DIR / "data"
    REPORTS_DIR: Path = DATA_DIR / "reports"
    DATABASE_URL: str = os.getenv("DATABASE_URL", f"sqlite:///{DATA_DIR}/trades.db")
    
    # Ensure directories exist
    @classmethod
    def create_directories(cls):
        """Create necessary data directories"""
        cls.DATA_DIR.mkdir(exist_ok=True)
        cls.REPORTS_DIR.mkdir(exist_ok=True)


# ==================== APPLICATION CONFIGURATION ====================
class AppConfig:
    """Main application configuration"""
    APP_NAME: str = "RSI Trading Bot"
    VERSION: str = "2.0.0"
    DEBUG: bool = os.getenv("DEBUG", "false").lower() == "true"
    
    # Configuration classes
    binance = BinanceConfig
    trading = TradingConfig
    notifications = NotificationConfig
    logging = LoggingConfig
    dashboard = DashboardConfig
    data = DataConfig
    
    @classmethod
    def validate_all(cls) -> tuple[bool, list[str]]:
        """
        Validate all configurations
        Returns: (is_valid, error_messages)
        """
        errors = []
        
        if not cls.binance.validate():
            errors.append("Binance API credentials not configured")
        
        if not cls.notifications.validate():
            errors.append("Email notification configuration incomplete")
        
        return len(errors) == 0, errors
    
    @classmethod
    def initialize(cls):
        """Initialize application configuration"""
        cls.data.create_directories()
        is_valid, errors = cls.validate_all()
        if not is_valid:
            print("⚠️  Configuration warnings:")
            for error in errors:
                print(f"  - {error}")
        return is_valid


# Initialize on import
config = AppConfig()
