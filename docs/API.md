# API Documentation

## Overview

The RSI Trading Bot provides a REST API and WebSocket interface for real-time monitoring and control.

## Base URL

```
http://localhost:5000/api
```

## Endpoints

### GET /api/health

Health check endpoint to verify the API is running.

**Response:**
```json
{
  "status": "healthy",
  "timestamp": "2024-01-01T12:00:00",
  "bot_running": true
}
```

### GET /api/status

Get complete bot status including current price, RSI, position, and statistics.

**Response:**
```json
{
  "is_running": true,
  "is_simulation": true,
  "symbol": "ETHUSDT",
  "current_price": 2500.50,
  "current_rsi": 45.32,
  "current_balance": 1050.25,
  "position": {
    "symbol": "ETHUSDT",
    "quantity": 0.5,
    "entry_price": 2450.00,
    "entry_time": "2024-01-01T10:00:00",
    "entry_rsi": 35.0,
    "current_price": 2500.50,
    "current_rsi": 45.32,
    "unrealized_pnl": 25.25,
    "unrealized_pnl_percentage": 2.06,
    "time_held_minutes": 120.5
  },
  "stats": {
    "total_trades": 10,
    "winning_trades": 7,
    "losing_trades": 3,
    "total_profit_loss": 50.25,
    "total_profit_loss_percentage": 5.03,
    "win_rate": 70.0,
    "average_profit": 15.50,
    "average_loss": -8.25,
    "average_trade_duration": 45.3,
    "largest_win": 35.00,
    "largest_loss": -15.00,
    "start_balance": 1000.00,
    "current_balance": 1050.25,
    "runtime_hours": 2.5,
    "trades_per_hour": 4.0
  },
  "strategy_status": "🔍 Waiting for BUY | RSI: 45.32"
}
```

### GET /api/stats

Get trading statistics only.

**Response:**
```json
{
  "total_trades": 10,
  "winning_trades": 7,
  "losing_trades": 3,
  "total_profit_loss": 50.25,
  "total_profit_loss_percentage": 5.03,
  "win_rate": 70.0,
  "average_profit": 15.50,
  "average_loss": -8.25,
  "average_trade_duration": 45.3,
  "largest_win": 35.00,
  "largest_loss": -15.00,
  "start_balance": 1000.00,
  "current_balance": 1050.25,
  "runtime_hours": 2.5,
  "trades_per_hour": 4.0
}
```

### GET /api/position

Get current position details.

**Response (with position):**
```json
{
  "symbol": "ETHUSDT",
  "quantity": 0.5,
  "entry_price": 2450.00,
  "entry_time": "2024-01-01T10:00:00",
  "entry_rsi": 35.0,
  "current_price": 2500.50,
  "current_rsi": 45.32,
  "unrealized_pnl": 25.25,
  "unrealized_pnl_percentage": 2.06,
  "time_held_minutes": 120.5
}
```

**Response (no position):**
```json
null
```

### GET /api/config

Get bot configuration.

**Response:**
```json
{
  "symbol": "ETHUSDT",
  "rsi_period": 14,
  "rsi_overbought": 70,
  "rsi_oversold": 30,
  "simulation_mode": true,
  "initial_balance": 1000.00
}
```

## WebSocket Events

### Connection

Connect to WebSocket:
```javascript
const socket = io('http://localhost:5000');
```

### Events

#### connected
Fired when successfully connected to the server.

**Payload:**
```json
{
  "data": "Connected to RSI Trading Bot"
}
```

#### bot_update
Real-time bot status updates (broadcast periodically).

**Payload:** Same as `/api/status` response

### Example Usage

```javascript
const socket = io('http://localhost:5000');

socket.on('connected', (data) => {
  console.log('Connected:', data);
});

socket.on('bot_update', (status) => {
  console.log('Bot Update:', status);
  // Update UI with new data
  updateDashboard(status);
});

socket.on('disconnect', () => {
  console.log('Disconnected from server');
});
```

## Error Responses

All endpoints may return the following error responses:

### 503 Service Unavailable
```json
{
  "error": "Bot not initialized"
}
```

### 500 Internal Server Error
```json
{
  "error": "Error message describing the issue"
}
```

## Rate Limiting

Currently, no rate limiting is implemented. However, it's recommended to:
- Poll status endpoints no more than once per second
- Use WebSocket for real-time updates instead of polling

## Authentication

Currently, no authentication is required. For production use, consider implementing:
- API keys
- JWT tokens
- IP whitelisting
- HTTPS/TLS

## CORS

CORS is enabled for all origins (`*`). In production, restrict to specific origins:

```python
CORS(app, origins=['https://yourdomain.com'])
```

## Examples

### Python Example

```python
import requests

# Get bot status
response = requests.get('http://localhost:5000/api/status')
status = response.json()
print(f"Current RSI: {status['current_rsi']}")

# Get statistics
response = requests.get('http://localhost:5000/api/stats')
stats = response.json()
print(f"Win Rate: {stats['win_rate']}%")
```

### JavaScript Example

```javascript
// Fetch bot status
fetch('http://localhost:5000/api/status')
  .then(response => response.json())
  .then(data => {
    console.log('Current Price:', data.current_price);
    console.log('Current RSI:', data.current_rsi);
  });

// Get position
fetch('http://localhost:5000/api/position')
  .then(response => response.json())
  .then(position => {
    if (position) {
      console.log('Unrealized P&L:', position.unrealized_pnl);
    } else {
      console.log('No active position');
    }
  });
```

### cURL Examples

```bash
# Health check
curl http://localhost:5000/api/health

# Get status
curl http://localhost:5000/api/status

# Get statistics
curl http://localhost:5000/api/stats

# Get position
curl http://localhost:5000/api/position

# Get configuration
curl http://localhost:5000/api/config
```

## Integration Examples

### Custom Dashboard

```html
<!DOCTYPE html>
<html>
<head>
    <title>Custom Dashboard</title>
    <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
</head>
<body>
    <div id="status"></div>
    <script>
        const socket = io('http://localhost:5000');
        
        socket.on('bot_update', (data) => {
            document.getElementById('status').innerHTML = `
                <p>Price: $${data.current_price}</p>
                <p>RSI: ${data.current_rsi}</p>
                <p>Balance: $${data.current_balance}</p>
            `;
        });
    </script>
</body>
</html>
```

### Monitoring Script

```python
import requests
import time

def monitor_bot():
    while True:
        try:
            response = requests.get('http://localhost:5000/api/status')
            data = response.json()
            
            print(f"Price: ${data['current_price']:.2f} | "
                  f"RSI: {data['current_rsi']:.2f} | "
                  f"Balance: ${data['current_balance']:.2f}")
            
            # Alert on high/low RSI
            if data['current_rsi'] > 75:
                print("⚠️  High RSI - Consider selling")
            elif data['current_rsi'] < 25:
                print("⚠️  Low RSI - Consider buying")
            
        except Exception as e:
            print(f"Error: {e}")
        
        time.sleep(5)

if __name__ == '__main__':
    monitor_bot()
```

## Future Enhancements

Planned API enhancements:
- [ ] Historical trade data endpoint
- [ ] Configuration update endpoint
- [ ] Manual trade triggering
- [ ] Strategy parameter adjustment
- [ ] Multiple timeframe data
- [ ] Performance metrics graphs
