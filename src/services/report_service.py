"""
Report Service for Generating Trading Reports
"""
import logging
from datetime import datetime
from pathlib import Path
from typing import Optional

from config.settings import AppConfig
from src.models.trading_models import Position, TradingStats, TradeResult
from src.utils.helpers import format_currency, format_percentage


class ReportService:
    """
    Generate and manage trading reports
    """
    
    def __init__(self, config: AppConfig, symbol: str):
        """
        Initialize report service
        
        Args:
            config: Application configuration
            symbol: Trading symbol
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.symbol = symbol
        
        # Create report file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.report_file = config.data.REPORTS_DIR / f"trade_log_{symbol}_{timestamp}.txt"
        self.html_file = config.data.REPORTS_DIR / f"report_{symbol}_{timestamp}.html"
        
        # Initialize files
        self._init_report_file()
        self._init_html_report()
        
        self.logger.info(f"✓ Report service initialized: {self.report_file.name}")
    
    def _init_report_file(self):
        """Initialize text report file"""
        with open(self.report_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write(f"RSI TRADING BOT - TRADE LOG\n")
            f.write(f"Symbol: {self.symbol}\n")
            f.write(f"Start Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
    
    def _init_html_report(self):
        """Initialize HTML report"""
        self.html_trades = []
    
    def log_buy(self, position: Position, reason: str):
        """
        Log a buy trade
        
        Args:
            position: Position that was opened
            reason: Buy reason
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Text log
        log_entry = f"""
[{timestamp}] BUY EXECUTED
{'='*60}
Price: {format_currency(position.entry_price)}
Quantity: {position.quantity:.6f} {self.symbol}
RSI: {position.entry_rsi:.2f}
Reason: {reason}
{'='*60}

"""
        
        with open(self.report_file, 'a') as f:
            f.write(log_entry)
        
        # HTML log
        self.html_trades.append({
            'type': 'buy',
            'timestamp': timestamp,
            'price': position.entry_price,
            'quantity': position.quantity,
            'rsi': position.entry_rsi,
            'reason': reason
        })
    
    def log_sell(
        self,
        position: Position,
        sell_price: float,
        profit_loss: float,
        profit_loss_pct: float,
        reason: str,
        result: TradeResult
    ):
        """
        Log a sell trade
        
        Args:
            position: Position that was closed
            sell_price: Sell price
            profit_loss: Profit/loss amount
            profit_loss_pct: Profit/loss percentage
            reason: Sell reason
            result: Trade result (WIN/LOSS)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        time_held = (datetime.now() - position.entry_time).total_seconds() / 60
        
        result_emoji = "🟢 WIN" if result == TradeResult.WIN else "🔴 LOSS"
        
        # Text log
        log_entry = f"""
[{timestamp}] SELL EXECUTED - {result_emoji}
{'='*60}
Entry Price: {format_currency(position.entry_price)}
Exit Price: {format_currency(sell_price)}
Quantity: {position.quantity:.6f} {self.symbol}
P&L: {format_currency(profit_loss)} ({format_percentage(profit_loss_pct)})
Time Held: {time_held:.1f} minutes
RSI: {position.current_rsi:.2f}
Reason: {reason}
{'='*60}

"""
        
        with open(self.report_file, 'a') as f:
            f.write(log_entry)
        
        # HTML log
        self.html_trades.append({
            'type': 'sell',
            'timestamp': timestamp,
            'entry_price': position.entry_price,
            'exit_price': sell_price,
            'quantity': position.quantity,
            'profit_loss': profit_loss,
            'profit_loss_pct': profit_loss_pct,
            'time_held': time_held,
            'rsi': position.current_rsi,
            'reason': reason,
            'result': result.value
        })
    
    def generate_final_report(self, stats: TradingStats, current_position: Optional[Position] = None):
        """
        Generate final trading report
        
        Args:
            stats: Trading statistics
            current_position: Current open position (if any)
        """
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        runtime = (datetime.now() - stats.start_time).total_seconds() / 3600
        total_pnl = stats.current_balance - stats.start_balance
        total_pnl_pct = (total_pnl / stats.start_balance) * 100
        
        # Text report
        final_report = f"""
{'='*80}
FINAL TRADING REPORT
{'='*80}
End Time: {timestamp}
Runtime: {runtime:.2f} hours

PERFORMANCE SUMMARY
{'='*80}
Start Balance: {format_currency(stats.start_balance)}
Final Balance: {format_currency(stats.current_balance)}
Total P&L: {format_currency(total_pnl)} ({format_percentage(total_pnl_pct)})

TRADING STATISTICS
{'='*80}
Total Trades: {stats.total_trades}
Winning Trades: {stats.winning_trades}
Losing Trades: {stats.losing_trades}
Win Rate: {stats.win_rate:.2f}%

Average Profit: {format_currency(stats.average_profit)}
Average Loss: {format_currency(stats.average_loss)}
Largest Win: {format_currency(stats.largest_win)}
Largest Loss: {format_currency(stats.largest_loss)}

Average Trade Duration: {stats.average_trade_duration:.1f} minutes
Trades Per Hour: {stats.total_trades / max(runtime, 0.01):.2f}

{'='*80}
"""
        
        with open(self.report_file, 'a') as f:
            f.write(final_report)
        
        # Generate HTML report
        self._generate_html_report(stats, runtime, total_pnl, total_pnl_pct)
        
        self.logger.info(f"✓ Final report generated: {self.report_file.name}")
        self.logger.info(f"✓ HTML report generated: {self.html_file.name}")
    
    def _generate_html_report(self, stats: TradingStats, runtime: float, total_pnl: float, total_pnl_pct: float):
        """Generate HTML report"""
        color = "#4CAF50" if total_pnl >= 0 else "#f44336"
        
        # Build trades table
        trades_html = ""
        for i, trade in enumerate(self.html_trades, 1):
            if trade['type'] == 'buy':
                trades_html += f"""
                <tr style="background-color: #e8f5e9;">
                    <td style="padding: 8px; border: 1px solid #ddd;">{i}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">🟢 BUY</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{trade['timestamp']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{format_currency(trade['price'])}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{trade['quantity']:.6f}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{trade['rsi']:.2f}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;" colspan="2">{trade['reason']}</td>
                </tr>
                """
            else:
                result_color = "#4CAF50" if trade['result'] == 'WIN' else "#f44336"
                trades_html += f"""
                <tr style="background-color: {('#fff3e0' if trade['result'] == 'WIN' else '#ffebee')};">
                    <td style="padding: 8px; border: 1px solid #ddd;">{i}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">🔴 SELL</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{trade['timestamp']}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{format_currency(trade['exit_price'])}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{trade['quantity']:.6f}</td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{trade['rsi']:.2f}</td>
                    <td style="padding: 8px; border: 1px solid #ddd; color: {result_color}; font-weight: bold;">
                        {format_currency(trade['profit_loss'])} ({format_percentage(trade['profit_loss_pct'])})
                    </td>
                    <td style="padding: 8px; border: 1px solid #ddd;">{trade['time_held']:.1f} min</td>
                </tr>
                """
        
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>RSI Trading Bot Report - {self.symbol}</title>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background-color: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background-color: white; padding: 30px; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); }}
        h1 {{ color: {color}; border-bottom: 3px solid {color}; padding-bottom: 10px; }}
        h2 {{ color: #333; margin-top: 30px; }}
        .summary {{ background-color: #f9f9f9; padding: 20px; border-radius: 5px; margin: 20px 0; }}
        .summary-item {{ margin: 10px 0; font-size: 16px; }}
        .summary-item strong {{ display: inline-block; width: 200px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th {{ background-color: #333; color: white; padding: 12px; text-align: left; }}
        td {{ padding: 8px; border: 1px solid #ddd; }}
        .metric {{ display: inline-block; margin: 10px 20px 10px 0; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: {color}; }}
        .metric-label {{ font-size: 14px; color: #666; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 RSI Trading Bot Report</h1>
        <p><strong>Symbol:</strong> {self.symbol}</p>
        <p><strong>Report Generated:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p><strong>Runtime:</strong> {runtime:.2f} hours</p>
        
        <h2>💰 Performance Summary</h2>
        <div class="summary">
            <div class="metric">
                <div class="metric-label">Total P&L</div>
                <div class="metric-value">{format_currency(total_pnl)}</div>
                <div class="metric-label">({format_percentage(total_pnl_pct)})</div>
            </div>
            <div class="metric">
                <div class="metric-label">Win Rate</div>
                <div class="metric-value">{stats.win_rate:.1f}%</div>
            </div>
            <div class="metric">
                <div class="metric-label">Total Trades</div>
                <div class="metric-value">{stats.total_trades}</div>
            </div>
        </div>
        
        <h2>📈 Statistics</h2>
        <table>
            <tr>
                <th>Metric</th>
                <th>Value</th>
            </tr>
            <tr>
                <td>Start Balance</td>
                <td>{format_currency(stats.start_balance)}</td>
            </tr>
            <tr>
                <td>Final Balance</td>
                <td style="color: {color}; font-weight: bold;">{format_currency(stats.current_balance)}</td>
            </tr>
            <tr>
                <td>Winning Trades</td>
                <td style="color: #4CAF50;">{stats.winning_trades}</td>
            </tr>
            <tr>
                <td>Losing Trades</td>
                <td style="color: #f44336;">{stats.losing_trades}</td>
            </tr>
            <tr>
                <td>Average Profit</td>
                <td style="color: #4CAF50;">{format_currency(stats.average_profit)}</td>
            </tr>
            <tr>
                <td>Average Loss</td>
                <td style="color: #f44336;">{format_currency(stats.average_loss)}</td>
            </tr>
            <tr>
                <td>Largest Win</td>
                <td style="color: #4CAF50;">{format_currency(stats.largest_win)}</td>
            </tr>
            <tr>
                <td>Largest Loss</td>
                <td style="color: #f44336;">{format_currency(stats.largest_loss)}</td>
            </tr>
            <tr>
                <td>Average Trade Duration</td>
                <td>{stats.average_trade_duration:.1f} minutes</td>
            </tr>
        </table>
        
        <h2>📝 Trade History</h2>
        <table>
            <tr>
                <th>#</th>
                <th>Type</th>
                <th>Time</th>
                <th>Price</th>
                <th>Quantity</th>
                <th>RSI</th>
                <th>P&L</th>
                <th>Duration</th>
            </tr>
            {trades_html}
        </table>
        
        <p style="color: #666; font-size: 12px; margin-top: 40px; text-align: center;">
            Generated by RSI Trading Bot v2.0
        </p>
    </div>
</body>
</html>
"""
        
        with open(self.html_file, 'w') as f:
            f.write(html_content)
