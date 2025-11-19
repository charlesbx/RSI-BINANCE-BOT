"""
Notification Service for Email Alerts
"""
import logging
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional, Dict
from datetime import datetime

from config.settings import AppConfig
from src.models.trading_models import TradeType, TradingStats
from src.utils.helpers import format_currency, format_percentage


class NotificationService:
    """
    Handle email notifications for trading events
    """
    
    def __init__(self, config: AppConfig):
        """
        Initialize notification service
        
        Args:
            config: Application configuration
        """
        self.logger = logging.getLogger(__name__)
        self.config = config
        self.enabled = config.notifications.ENABLE_EMAIL
        
        if self.enabled:
            self.smtp_host = config.notifications.SMTP_HOST
            self.smtp_port = config.notifications.SMTP_PORT
            self.smtp_email = config.notifications.SMTP_EMAIL
            self.smtp_password = config.notifications.SMTP_PASSWORD
            self.notification_email = config.notifications.NOTIFICATION_EMAIL
            
            self.logger.info("✓ Notification service initialized")
        else:
            self.logger.info("ℹ Email notifications disabled")
    
    def _send_email(self, subject: str, html_content: str) -> bool:
        """
        Send an email
        
        Args:
            subject: Email subject
            html_content: HTML content
            
        Returns:
            True if successful
        """
        if not self.enabled:
            return True
        
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = self.smtp_email
            msg['To'] = self.notification_email
            
            # Attach HTML content
            html_part = MIMEText(html_content, 'html')
            msg.attach(html_part)
            
            # Send email
            with smtplib.SMTP_SSL(self.smtp_host, self.smtp_port) as server:
                server.login(self.smtp_email, self.smtp_password)
                server.send_message(msg)
            
            self.logger.debug(f"✓ Email sent: {subject}")
            return True
            
        except Exception as e:
            self.logger.error(f"✗ Failed to send email: {e}")
            return False
    
    def send_start_notification(
        self,
        symbol: str,
        balance: float,
        strategy_params: Dict
    ):
        """
        Send bot start notification
        
        Args:
            symbol: Trading symbol
            balance: Initial balance
            strategy_params: Strategy parameters
        """
        subject = f"🚀 Trading Bot Started - {symbol}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: #4CAF50;">🚀 Trading Bot Started</h2>
                <p><strong>Symbol:</strong> {symbol}</p>
                <p><strong>Initial Balance:</strong> {format_currency(balance)}</p>
                <p><strong>Start Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                
                <h3>Strategy Parameters</h3>
                <ul>
                    <li><strong>RSI Period:</strong> {strategy_params.get('RSI_PERIOD', 14)}</li>
                    <li><strong>RSI Overbought:</strong> {strategy_params.get('RSI_OVERBOUGHT', 70)}</li>
                    <li><strong>RSI Oversold:</strong> {strategy_params.get('RSI_OVERSOLD', 30)}</li>
                </ul>
                
                <p style="color: #666; font-size: 12px; margin-top: 20px;">
                    This is an automated notification from RSI Trading Bot
                </p>
            </body>
        </html>
        """
        
        self._send_email(subject, html_content)
    
    def send_trade_notification(
        self,
        trade_type: TradeType,
        symbol: str,
        price: float,
        quantity: float,
        rsi: float,
        reason: str,
        profit_loss: Optional[float] = None,
        profit_loss_pct: Optional[float] = None
    ):
        """
        Send trade execution notification
        
        Args:
            trade_type: BUY or SELL
            symbol: Trading symbol
            price: Execution price
            quantity: Trade quantity
            rsi: RSI at execution
            reason: Trade reason
            profit_loss: P&L (for sell orders)
            profit_loss_pct: P&L percentage (for sell orders)
        """
        is_buy = trade_type == TradeType.BUY
        emoji = "🟢" if is_buy else ("🟢" if profit_loss and profit_loss >= 0 else "🔴")
        color = "#4CAF50" if is_buy or (profit_loss and profit_loss >= 0) else "#f44336"
        
        subject = f"{emoji} {trade_type.value} - {symbol}"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: {color};">{emoji} {trade_type.value} Order Executed</h2>
                <p><strong>Symbol:</strong> {symbol}</p>
                <p><strong>Price:</strong> {format_currency(price)}</p>
                <p><strong>Quantity:</strong> {quantity:.6f}</p>
                <p><strong>RSI:</strong> {rsi:.2f}</p>
                <p><strong>Reason:</strong> {reason}</p>
                <p><strong>Time:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        """
        
        if not is_buy and profit_loss is not None:
            html_content += f"""
                <h3 style="color: {color};">Trade Result</h3>
                <p><strong>P&L:</strong> {format_currency(profit_loss)} ({format_percentage(profit_loss_pct)})</p>
            """
        
        html_content += """
                <p style="color: #666; font-size: 12px; margin-top: 20px;">
                    This is an automated notification from RSI Trading Bot
                </p>
            </body>
        </html>
        """
        
        self._send_email(subject, html_content)
    
    def send_final_report(self, stats: TradingStats):
        """
        Send final trading report
        
        Args:
            stats: Trading statistics
        """
        total_pnl = stats.current_balance - stats.start_balance
        total_pnl_pct = (total_pnl / stats.start_balance) * 100
        color = "#4CAF50" if total_pnl >= 0 else "#f44336"
        emoji = "🎉" if total_pnl >= 0 else "📉"
        
        subject = f"{emoji} Final Trading Report"
        
        html_content = f"""
        <html>
            <body style="font-family: Arial, sans-serif;">
                <h2 style="color: {color};">{emoji} Final Trading Report</h2>
                
                <h3>Overall Performance</h3>
                <p><strong>Start Balance:</strong> {format_currency(stats.start_balance)}</p>
                <p><strong>Final Balance:</strong> {format_currency(stats.current_balance)}</p>
                <p style="font-size: 18px;"><strong>Total P&L:</strong> 
                    <span style="color: {color};">{format_currency(total_pnl)} ({format_percentage(total_pnl_pct)})</span>
                </p>
                
                <h3>Trading Statistics</h3>
                <table style="border-collapse: collapse; width: 100%;">
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Total Trades:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{stats.total_trades}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Winning Trades:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd; color: #4CAF50;">{stats.winning_trades}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Losing Trades:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd; color: #f44336;">{stats.losing_trades}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Win Rate:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{stats.win_rate:.2f}%</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Average Profit:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd; color: #4CAF50;">{format_currency(stats.average_profit)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Average Loss:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd; color: #f44336;">{format_currency(stats.average_loss)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Largest Win:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd; color: #4CAF50;">{format_currency(stats.largest_win)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Largest Loss:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd; color: #f44336;">{format_currency(stats.largest_loss)}</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Avg Trade Duration:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{stats.average_trade_duration:.1f} minutes</td>
                    </tr>
                    <tr>
                        <td style="padding: 8px; border: 1px solid #ddd;"><strong>Runtime:</strong></td>
                        <td style="padding: 8px; border: 1px solid #ddd;">{(datetime.now() - stats.start_time).total_seconds() / 3600:.2f} hours</td>
                    </tr>
                </table>
                
                <p style="color: #666; font-size: 12px; margin-top: 20px;">
                    Trading session ended at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
                </p>
            </body>
        </html>
        """
        
        self._send_email(subject, html_content)
