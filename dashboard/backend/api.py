"""
Dashboard API Backend
Flask API for real-time bot monitoring
"""
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_socketio import SocketIO, emit
import logging
from datetime import datetime
from typing import Optional
from pathlib import Path

from config.settings import AppConfig
from src.core.trading_bot import TradingBot


# Initialize Flask app
app = Flask(__name__)
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")

# Get paths
DASHBOARD_DIR = Path(__file__).parent.parent
FRONTEND_DIR = DASHBOARD_DIR / "frontend"

# Global bot instance (will be set by main)
bot_instance: Optional[TradingBot] = None

logger = logging.getLogger(__name__)


def set_bot_instance(bot: TradingBot):
    """Set the bot instance for the API"""
    global bot_instance
    bot_instance = bot


@app.route('/')
def index():
    """Serve the main dashboard page"""
    return send_from_directory(FRONTEND_DIR, 'index.html')


@app.route('/<path:path>')
def serve_static(path):
    """Serve static files from frontend directory"""
    return send_from_directory(FRONTEND_DIR, path)


@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current bot status"""
    if not bot_instance:
        return jsonify({'error': 'Bot not initialized'}), 503
    
    try:
        status = bot_instance.get_status()
        return jsonify(status)
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
def get_stats():
    """Get trading statistics"""
    if not bot_instance:
        return jsonify({'error': 'Bot not initialized'}), 503
    
    try:
        stats = bot_instance.stats.to_dict()
        return jsonify(stats)
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/position', methods=['GET'])
def get_position():
    """Get current position"""
    if not bot_instance:
        return jsonify({'error': 'Bot not initialized'}), 503
    
    try:
        if bot_instance.position:
            return jsonify(bot_instance.position.to_dict())
        return jsonify(None)
    except Exception as e:
        logger.error(f"Error getting position: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/config', methods=['GET'])
def get_config():
    """Get bot configuration"""
    if not bot_instance:
        return jsonify({'error': 'Bot not initialized'}), 503
    
    try:
        config_data = {
            'symbol': bot_instance.symbol,
            'rsi_period': bot_instance.config.trading.RSI_PERIOD,
            'rsi_overbought': bot_instance.config.trading.RSI_OVERBOUGHT,
            'rsi_oversold': bot_instance.config.trading.RSI_OVERSOLD,
            'simulation_mode': bot_instance.is_simulation,
            'initial_balance': bot_instance.initial_balance
        }
        return jsonify(config_data)
    except Exception as e:
        logger.error(f"Error getting config: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'bot_running': bot_instance.is_running if bot_instance else False
    })


@socketio.on('connect')
def handle_connect():
    """Handle client connection"""
    logger.info('Client connected to WebSocket')
    emit('connected', {'data': 'Connected to RSI Trading Bot'})


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection"""
    logger.info('Client disconnected from WebSocket')


def broadcast_update():
    """Broadcast bot status update to all connected clients"""
    if bot_instance:
        try:
            status = bot_instance.get_status()
            socketio.emit('bot_update', status)
        except Exception as e:
            logger.error(f"Error broadcasting update: {e}")


def run_dashboard(config: AppConfig, bot: TradingBot):
    """
    Run the dashboard server
    
    Args:
        config: Application configuration
        bot: Trading bot instance
    """
    set_bot_instance(bot)
    
    host = config.dashboard.BACKEND_HOST
    port = config.dashboard.BACKEND_PORT
    
    logger.info(f"🌐 Starting dashboard API on http://{host}:{port}")
    socketio.run(app, host=host, port=port, debug=False, allow_unsafe_werkzeug=True)


if __name__ == '__main__':
    # For testing only
    app.run(debug=True, port=5000)
