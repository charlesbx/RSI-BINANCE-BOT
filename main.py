#!/usr/bin/env python3
"""
RSI Trading Bot - Main Entry Point
Professional Binance Trading Bot with RSI Strategy

Usage:
    python main.py --symbol ETHUSDT --balance 1000 --rsi-period 14 --rsi-overbought 70 --rsi-oversold 30
    python main.py --config config.yaml
    python main.py --interactive
"""
import sys
import argparse
import signal
import logging
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from config.settings import AppConfig
from src.core.trading_bot import TradingBot
from src.utils.helpers import setup_logger
from dashboard.backend.api import run_dashboard
import threading


def parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='RSI Trading Bot for Binance',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Run with default settings (interactive mode)
  python main.py
  
  # Run with specific parameters
  python main.py --symbol ETHUSDT --balance 1000
  
  # Run in simulation mode
  python main.py --symbol BTCUSDT --balance 5000 --simulate
  
  # Custom RSI settings
  python main.py --symbol ETHUSDT --balance 1000 --rsi-period 14 --rsi-overbought 75 --rsi-oversold 25
        """
    )
    
    # Trading parameters
    parser.add_argument(
        '--symbol', '-s',
        type=str,
        help='Trading pair symbol (e.g., ETHUSDT, BTCUSDT)'
    )
    
    parser.add_argument(
        '--balance', '-b',
        type=float,
        help='Initial trading balance in quote currency'
    )
    
    # RSI parameters
    parser.add_argument(
        '--rsi-period',
        type=int,
        help='RSI period (default: 14)'
    )
    
    parser.add_argument(
        '--rsi-overbought',
        type=int,
        help='RSI overbought level (default: 70)'
    )
    
    parser.add_argument(
        '--rsi-oversold',
        type=int,
        help='RSI oversold level (default: 30)'
    )
    
    # Mode
    parser.add_argument(
        '--simulate',
        action='store_true',
        help='Run in simulation mode (no real trades)'
    )
    
    parser.add_argument(
        '--live',
        action='store_true',
        help='Run in LIVE mode (real trades)'
    )
    
    # Other options
    parser.add_argument(
        '--interactive', '-i',
        action='store_true',
        help='Interactive mode (prompt for parameters)'
    )
    
    parser.add_argument(
        '--log-level',
        type=str,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR'],
        help='Logging level'
    )
    
    parser.add_argument(
        '--no-email',
        action='store_true',
        help='Disable email notifications'
    )
    
    parser.add_argument(
        '--dashboard',
        action='store_true',
        help='Launch dashboard server with bot'
    )
    
    return parser.parse_args()


def interactive_mode():
    """Interactive mode for parameter input"""
    print("=" * 60)
    print("RSI TRADING BOT - Interactive Configuration")
    print("=" * 60)
    
    # Trading pair
    symbol = input("\n📊 Trading Symbol (e.g., ETHUSDT): ").strip().upper()
    if not symbol:
        symbol = "ETHUSDT"
        print(f"   Using default: {symbol}")
    
    # Initial balance
    balance_input = input("\n💰 Initial Balance (USD): ").strip()
    try:
        balance = float(balance_input) if balance_input else 1000.0
    except ValueError:
        balance = 1000.0
    print(f"   Using balance: ${balance:.2f}")
    
    # RSI parameters
    print("\n⚙️  RSI Strategy Parameters")
    
    rsi_period_input = input("   RSI Period (default: 14): ").strip()
    rsi_period = int(rsi_period_input) if rsi_period_input else 14
    
    rsi_overbought_input = input("   RSI Overbought (default: 70): ").strip()
    rsi_overbought = int(rsi_overbought_input) if rsi_overbought_input else 70
    
    rsi_oversold_input = input("   RSI Oversold (default: 30): ").strip()
    rsi_oversold = int(rsi_oversold_input) if rsi_oversold_input else 30
    
    # Mode
    mode_input = input("\n🎮 Mode - [S]imulation or [L]ive? (default: S): ").strip().upper()
    simulate = mode_input != 'L'
    
    print("\n" + "=" * 60)
    print(f"Configuration Summary:")
    print(f"  Symbol: {symbol}")
    print(f"  Balance: ${balance:.2f}")
    print(f"  RSI Period: {rsi_period}")
    print(f"  RSI Overbought: {rsi_overbought}")
    print(f"  RSI Oversold: {rsi_oversold}")
    print(f"  Mode: {'🎮 SIMULATION' if simulate else '💰 LIVE TRADING'}")
    print("=" * 60)
    
    confirm = input("\n✓ Start bot with these settings? [Y/n]: ").strip().upper()
    if confirm == 'N':
        print("❌ Cancelled by user")
        sys.exit(0)
    
    return {
        'symbol': symbol,
        'balance': balance,
        'rsi_period': rsi_period,
        'rsi_overbought': rsi_overbought,
        'rsi_oversold': rsi_oversold,
        'simulate': simulate
    }


def setup_signal_handlers(bot: TradingBot):
    """Setup signal handlers for graceful shutdown"""
    def signal_handler(sig, frame):
        print("\n\n🛑 Shutdown signal received...")
        bot.stop()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)


def main():
    """Main entry point"""
    # Parse arguments
    args = parse_arguments()
    
    # Initialize configuration
    config = AppConfig()
    config.initialize()
    
    # Setup logging
    log_level = args.log_level if args.log_level else config.logging.LOG_LEVEL
    logger = setup_logger(
        name='RSI_BOT',
        log_file=str(config.logging.LOG_DIR / config.logging.LOG_FILE),
        level=log_level
    )
    
    logger.info("=" * 60)
    logger.info("🚀 RSI TRADING BOT v2.0")
    logger.info("=" * 60)
    
    # Get parameters
    if args.interactive or (not args.symbol and not args.balance):
        params = interactive_mode()
    else:
        params = {
            'symbol': args.symbol or config.trading.TRADE_SYMBOL,
            'balance': args.balance or config.trading.TRADE_QUANTITY,
            'rsi_period': args.rsi_period or config.trading.RSI_PERIOD,
            'rsi_overbought': args.rsi_overbought or config.trading.RSI_OVERBOUGHT,
            'rsi_oversold': args.rsi_oversold or config.trading.RSI_OVERSOLD,
            'simulate': args.simulate or (not args.live and config.trading.SIMULATION_MODE)
        }
    
    # Update config with parameters
    config.trading.TRADE_SYMBOL = params['symbol']
    config.trading.RSI_PERIOD = params['rsi_period']
    config.trading.RSI_OVERBOUGHT = params['rsi_overbought']
    config.trading.RSI_OVERSOLD = params['rsi_oversold']
    config.trading.SIMULATION_MODE = params['simulate']
    
    if args.no_email:
        config.notifications.ENABLE_EMAIL = False
    
    # Validate configuration
    is_valid, errors = config.validate_all()
    if not is_valid:
        logger.error("❌ Configuration validation failed:")
        for error in errors:
            logger.error(f"   - {error}")
        if not config.binance.validate():
            logger.error("\n⚠️  Please configure your Binance API credentials in .env file")
            sys.exit(1)
    
    # Create and start bot
    try:
        bot = TradingBot(
            config=config,
            symbol=params['symbol'],
            initial_balance=params['balance']
        )
        
        # Setup signal handlers for graceful shutdown
        setup_signal_handlers(bot)
        
        # Start dashboard if requested
        dashboard_thread = None
        if args.dashboard:
            logger.info("🌐 Starting dashboard server...")
            dashboard_thread = threading.Thread(
                target=run_dashboard,
                args=(config, bot),
                daemon=True
            )
            dashboard_thread.start()
            logger.info(f"✓ Dashboard accessible at http://{config.dashboard.BACKEND_HOST}:{config.dashboard.BACKEND_PORT}")
        
        # Start the bot
        if not bot.start():
            logger.error("❌ Failed to start bot")
            sys.exit(1)
        
        # Keep bot running
        logger.info("\n✓ Bot is running... Press Ctrl+C to stop\n")
        
        while bot.is_running:
            try:
                import time
                time.sleep(1)
            except KeyboardInterrupt:
                break
        
        bot.stop()
        
    except Exception as e:
        logger.exception(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
