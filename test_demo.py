#!/usr/bin/env python3
"""
Demo script to test the RSI Trading Bot without real API keys
"""
import sys
import time
import random
from datetime import datetime
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.indicators.technical_indicators import TechnicalIndicators
from src.utils.helpers import format_price, format_percentage


class SimplePosition:
    """Simple position class for demo"""
    def __init__(self, entry_price, quantity):
        self.entry_price = entry_price
        self.quantity = quantity
        self.entry_time = datetime.now()


class DemoBot:
    """Demo bot with simulated market data"""
    
    def __init__(self, symbol: str = "ETHUSDT", balance: float = 1000.0):
        self.symbol = symbol
        self.balance = balance
        self.initial_balance = balance
        self.position = None
        self.trades = []
        
        # Strategy parameters
        self.rsi_period = 14
        self.rsi_overbought = 70
        self.rsi_oversold = 30
        
        # Price simulation
        self.base_price = 2500.0  # Starting price for ETH
        self.price_history = []
        
        # Stats
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        
    def generate_price(self) -> float:
        """Generate realistic price movement"""
        if not self.price_history:
            price = self.base_price
        else:
            # Random walk with trend
            last_price = self.price_history[-1]
            change_percent = random.uniform(-0.02, 0.02)  # ±2% change
            price = last_price * (1 + change_percent)
        
        self.price_history.append(price)
        return price
    
    def calculate_rsi(self) -> float:
        """Calculate RSI from price history"""
        if len(self.price_history) < 15:
            return 50.0
        
        indicators = TechnicalIndicators()
        rsi = indicators.calculate_rsi(self.price_history[-100:], period=14)
        return rsi if rsi is not None else 50.0
    
    def print_status(self, price: float, rsi: float, action: str = ""):
        """Print current status"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Status line
        status = f"[{timestamp}] Price: {format_price(price)} | RSI: {rsi:.2f}"
        
        # Add position info
        if self.position:
            pnl = (price - self.position.entry_price) * self.position.quantity
            pnl_pct = ((price / self.position.entry_price) - 1) * 100
            status += f" | Position: {format_percentage(pnl_pct)} ({format_price(pnl)})"
        else:
            status += f" | Balance: {format_price(self.balance)}"
        
        # Add action
        if action:
            status += f" | {action}"
        
        print(status)
    
    def execute_buy(self, price: float, rsi: float):
        """Execute buy order"""
        if self.position:
            return
        
        quantity = self.balance / price * 0.95  # Use 95% of balance
        cost = quantity * price
        
        self.position = SimplePosition(entry_price=price, quantity=quantity)
        self.balance -= cost
        
        print(f"    🟢 BUY {quantity:.6f} @ {format_price(price)} (RSI: {rsi:.2f})")
    
    def execute_sell(self, price: float, rsi: float, reason: str = ""):
        """Execute sell order"""
        if not self.position:
            return
        
        revenue = self.position.quantity * price
        profit = revenue - (self.position.quantity * self.position.entry_price)
        profit_pct = (profit / (self.position.quantity * self.position.entry_price)) * 100
        
        self.balance += revenue
        
        # Update stats
        self.total_trades += 1
        if profit > 0:
            self.winning_trades += 1
        else:
            self.losing_trades += 1
        
        self.trades.append({
            'entry': self.position.entry_price,
            'exit': price,
            'profit': profit,
            'profit_pct': profit_pct
        })
        
        reason_str = f" ({reason})" if reason else ""
        print(f"    🔴 SELL {self.position.quantity:.6f} @ {format_price(price)} | "
              f"P&L: {format_price(profit)} ({format_percentage(profit_pct)}){reason_str}")
        
        self.position = None
    
    def run(self, iterations: int = 100, speed: float = 0.5):
        """Run demo bot"""
        print("\n" + "="*80)
        print("🤖 RSI Trading Bot - DEMO MODE")
        print("="*80)
        print(f"Symbol: {self.symbol}")
        print(f"Initial Balance: {format_price(self.initial_balance)}")
        print(f"Strategy: RSI (14 period, 30/70 levels)")
        print("="*80 + "\n")
        
        try:
            for i in range(iterations):
                # Generate new price
                price = self.generate_price()
                rsi = self.calculate_rsi()
                
                # Simple RSI strategy
                if not self.position:
                    if rsi < self.rsi_oversold:
                        self.execute_buy(price, rsi)
                    else:
                        # Print status every 5 iterations when no position
                        if i % 5 == 0:
                            self.print_status(price, rsi)
                else:
                    # Check sell conditions
                    profit_pct = ((price / self.position.entry_price) - 1) * 100
                    
                    if rsi > self.rsi_overbought:
                        self.execute_sell(price, rsi, "RSI overbought")
                    elif profit_pct > 5.0:
                        self.execute_sell(price, rsi, "Take profit")
                    elif profit_pct < -2.0:
                        self.execute_sell(price, rsi, "Stop loss")
                    else:
                        # Print status every iteration when in position
                        self.print_status(price, rsi)
                
                time.sleep(speed)
                
        except KeyboardInterrupt:
            print("\n\n⚠️  Demo interrupted by user")
            if self.position:
                print(f"Closing position at market price...")
                self.execute_sell(price, rsi, "Manual stop")
        
        self.print_summary()
    
    def print_summary(self):
        """Print final summary"""
        final_balance = self.balance
        if self.position:
            final_balance += self.position.quantity * self.price_history[-1]
        
        total_return = final_balance - self.initial_balance
        total_return_pct = (total_return / self.initial_balance) * 100
        
        print("\n" + "="*80)
        print("📊 DEMO SUMMARY")
        print("="*80)
        print(f"Initial Balance: {format_price(self.initial_balance)}")
        print(f"Final Balance:   {format_price(final_balance)}")
        print(f"Total Return:    {format_price(total_return)} ({format_percentage(total_return_pct)})")
        print(f"\nTotal Trades:    {self.total_trades}")
        print(f"Winning Trades:  {self.winning_trades}")
        print(f"Losing Trades:   {self.losing_trades}")
        
        if self.total_trades > 0:
            win_rate = (self.winning_trades / self.total_trades) * 100
            print(f"Win Rate:        {win_rate:.1f}%")
        
        if self.trades:
            avg_profit = sum(t['profit'] for t in self.trades) / len(self.trades)
            best_trade = max(self.trades, key=lambda x: x['profit'])
            worst_trade = min(self.trades, key=lambda x: x['profit'])
            
            print(f"\nAverage P&L:     {format_price(avg_profit)}")
            print(f"Best Trade:      {format_price(best_trade['profit'])} ({best_trade['profit_pct']:+.2f}%)")
            print(f"Worst Trade:     {format_price(worst_trade['profit'])} ({worst_trade['profit_pct']:+.2f}%)")
        
        print("="*80 + "\n")


def main():
    """Main function"""
    import argparse
    
    parser = argparse.ArgumentParser(description="RSI Trading Bot - Demo Mode")
    parser.add_argument("--symbol", "-s", default="ETHUSDT", help="Trading pair symbol")
    parser.add_argument("--balance", "-b", type=float, default=1000.0, help="Initial balance")
    parser.add_argument("--iterations", "-n", type=int, default=100, help="Number of iterations")
    parser.add_argument("--speed", type=float, default=0.5, help="Speed (seconds between iterations)")
    
    args = parser.parse_args()
    
    # Create and run demo bot
    bot = DemoBot(symbol=args.symbol, balance=args.balance)
    bot.run(iterations=args.iterations, speed=args.speed)


if __name__ == "__main__":
    main()
