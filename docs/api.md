# 📚 API Reference

## 🧩 Core Components

### 🔗 Blockchain Interface
```python
from bot.blockchain import BlockchainInterface

# Initialize
blockchain = BlockchainInterface(
    rpc_url="YOUR_RPC_URL",
    private_key="YOUR_PRIVATE_KEY"
)

# Methods
balance = blockchain.get_balance(token_address)
gas_price = blockchain.get_gas_price()
```

### 💱 Trading Engine
```python
from bot.trading import TradingEngine

# Initialize
trading = TradingEngine(blockchain, config)

# Methods
tx_hash = trading.buy_token(token_address, amount_eth, slippage)
position = trading.get_position(token_address)
```

### 🍯 Honeypot Detection
```python
from bot.honeypot import HoneypotDetector

# Initialize
detector = HoneypotDetector(blockchain)

# Methods
is_safe = detector.analyze_token(token_address)
liquidity = detector.verify_liquidity(token_address)
```

### ⚙️ Configuration
```python
from bot.config import Config

# Load config
config = Config()

# Settings
profit_target = config.profit_target
stop_loss = config.stop_loss
min_liquidity = config.min_liquidity
check_honeypot = config.check_honeypot
auto_sell = config.auto_sell
gas_price_multiplier = config.gas_price_multiplier
```

### 📊 Monitoring
```python
from bot.monitoring import Monitoring

# Initialize
monitoring = Monitoring()

# Methods
monitoring.log_trade(token_address, amount, price)
monitoring.log_error("Error message")
monitoring.update_position(token_address, amount, price)
```

## 📋 Configuration Reference

| Setting | Description | Default | Required |
|---------|-------------|---------|----------|
| `RPC_URL` | RPC endpoint | - | Yes |
| `PRIVATE_KEY` | Wallet key | - | Yes |
| `ROUTER_ADDRESS` | DEX router | - | Yes |
| `FACTORY_ADDRESS` | DEX factory | - | Yes |
| `PROFIT_TARGET` | Take-profit % | 100 | No |
| `STOP_LOSS` | Stop-loss % | 50 | No |
| `MIN_LIQUIDITY` | Min liquidity | 1 | No |
| `CHECK_HONEYPOT` | Honeypot check | true | No |
| `AUTO_SELL` | Auto-sell | true | No |
| `GAS_PRICE_MULTIPLIER` | Gas multiplier | 1.1 | No |

## 💬 Support

- [Discord](https://discord.gg/bZXer5ZttK) - Community support
- GitHub Issues - Bug reports
- [Tutorial](docs/tutorial.md) - Getting started

# 📡 API Documentation

This document describes the REST API endpoints available in the Crypto Sniping Bot.

## 🔑 Authentication

All API requests require authentication using an API key. Include the API key in the request header:

```http
Authorization: Bearer YOUR_API_KEY
```

## 📊 Endpoints

### 1. Bot Status

#### Get Bot Status
```http
GET /api/v1/status
```

**Response**
```json
{
    "status": "running",
    "uptime": "2h 30m",
    "version": "1.0.0",
    "network": "ethereum",
    "balance": {
        "eth": "1.5",
        "usd": "3000"
    }
}
```

### 2. Trading

#### Start Trading
```http
POST /api/v1/trading/start
```

**Request Body**
```json
{
    "strategy": "quick_flip",
    "max_slippage": 2.5,
    "gas_limit": 300000,
    "min_liquidity": 10
}
```

**Response**
```json
{
    "status": "success",
    "message": "Trading started",
    "strategy": "quick_flip"
}
```

#### Stop Trading
```http
POST /api/v1/trading/stop
```

**Response**
```json
{
    "status": "success",
    "message": "Trading stopped"
}
```

### 3. Positions

#### Get Open Positions
```http
GET /api/v1/positions
```

**Response**
```json
{
    "positions": [
        {
            "token": "0x123...",
            "amount": "1000",
            "entry_price": "0.001",
            "current_price": "0.0012",
            "profit_loss": "20%"
        }
    ]
}
```

#### Close Position
```http
POST /api/v1/positions/{token_address}/close
```

**Response**
```json
{
    "status": "success",
    "tx_hash": "0xabc...",
    "profit_loss": "20%"
}
```

### 4. Configuration

#### Get Configuration
```http
GET /api/v1/config
```

**Response**
```json
{
    "network": "ethereum",
    "rpc_url": "https://eth-mainnet.alchemyapi.io/v2/...",
    "max_slippage": 2.5,
    "gas_limit": 300000,
    "min_liquidity": 10
}
```

#### Update Configuration
```http
PUT /api/v1/config
```

**Request Body**
```json
{
    "max_slippage": 3.0,
    "gas_limit": 350000,
    "min_liquidity": 15
}
```

**Response**
```json
{
    "status": "success",
    "message": "Configuration updated"
}
```

### 5. Monitoring

#### Get Recent Trades
```http
GET /api/v1/trades
```

**Query Parameters**
- `limit`: Number of trades to return (default: 10)
- `offset`: Offset for pagination (default: 0)

**Response**
```json
{
    "trades": [
        {
            "token": "0x123...",
            "type": "buy",
            "amount": "1.5",
            "price": "0.001",
            "timestamp": "2024-02-20T10:30:00Z",
            "tx_hash": "0xabc..."
        }
    ],
    "total": 100,
    "limit": 10,
    "offset": 0
}
```

#### Get Performance Metrics
```http
GET /api/v1/metrics
```

**Response**
```json
{
    "total_trades": 100,
    "successful_trades": 95,
    "failed_trades": 5,
    "total_profit": "2.5",
    "average_profit": "0.025",
    "win_rate": "95%"
}
```

### 6. Security

#### Get Security Status
```http
GET /api/v1/security
```

**Response**
```json
{
    "mev_protection": true,
    "honeypot_detection": true,
    "slippage_protection": true,
    "last_check": "2024-02-20T10:30:00Z",
    "alerts": []
}
```

#### Update Security Settings
```http
PUT /api/v1/security
```

**Request Body**
```json
{
    "mev_protection": true,
    "honeypot_detection": true,
    "slippage_protection": true
}
```

**Response**
```json
{
    "status": "success",
    "message": "Security settings updated"
}
```

## 🔄 WebSocket API

### 1. Connection

Connect to the WebSocket endpoint:
```javascript
const ws = new WebSocket('ws://your-bot-address/ws');
```

### 2. Events

#### Subscribe to Events
```javascript
ws.send(JSON.stringify({
    "action": "subscribe",
    "events": ["new_pair", "trade", "position"]
}));
```

#### Event Types

1. **New Pair**
```json
{
    "event": "new_pair",
    "data": {
        "pair": "0x123...",
        "token0": "0xabc...",
        "token1": "0xdef...",
        "timestamp": "2024-02-20T10:30:00Z"
    }
}
```

2. **Trade**
```json
{
    "event": "trade",
    "data": {
        "token": "0x123...",
        "type": "buy",
        "amount": "1.5",
        "price": "0.001",
        "timestamp": "2024-02-20T10:30:00Z",
        "tx_hash": "0xabc..."
    }
}
```

3. **Position**
```json
{
    "event": "position",
    "data": {
        "token": "0x123...",
        "amount": "1000",
        "entry_price": "0.001",
        "current_price": "0.0012",
        "profit_loss": "20%"
    }
}
```

## 🚨 Error Handling

### Error Response Format
```json
{
    "error": {
        "code": "ERROR_CODE",
        "message": "Error description",
        "details": {}
    }
}
```

### Common Error Codes

- `AUTH_ERROR`: Authentication failed
- `INVALID_REQUEST`: Invalid request parameters
- `TRADING_ERROR`: Trading operation failed
- `NETWORK_ERROR`: Network connection error
- `CONFIG_ERROR`: Configuration error
- `SECURITY_ERROR`: Security check failed

## 📚 Rate Limits

- REST API: 100 requests per minute
- WebSocket: 1000 messages per minute

## 🔒 Security Considerations

1. **API Key Security**
   - Keep API keys secure
   - Rotate keys regularly
   - Use IP whitelisting

2. **Request Security**
   - Use HTTPS
   - Validate all inputs
   - Implement rate limiting

3. **Data Security**
   - Encrypt sensitive data
   - Implement request signing
   - Use secure WebSocket connections

## 📈 Best Practices

1. **Error Handling**
   - Implement retry logic
   - Handle rate limits
   - Log errors properly

2. **Performance**
   - Use WebSocket for real-time data
   - Implement caching
   - Optimize request frequency

3. **Monitoring**
   - Monitor API usage
   - Track error rates
   - Set up alerts

## 🔧 SDK Examples

### Python
```python
import requests

class CryptoSnipingBot:
    def __init__(self, api_key, base_url):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            'Authorization': f'Bearer {api_key}',
            'Content-Type': 'application/json'
        }
    
    def get_status(self):
        response = requests.get(
            f'{self.base_url}/api/v1/status',
            headers=self.headers
        )
        return response.json()
    
    def start_trading(self, strategy):
        response = requests.post(
            f'{self.base_url}/api/v1/trading/start',
            headers=self.headers,
            json={'strategy': strategy}
        )
        return response.json()
```

### JavaScript
```javascript
class CryptoSnipingBot {
    constructor(apiKey, baseUrl) {
        this.apiKey = apiKey;
        this.baseUrl = baseUrl;
        this.headers = {
            'Authorization': `Bearer ${apiKey}`,
            'Content-Type': 'application/json'
        };
    }
    
    async getStatus() {
        const response = await fetch(
            `${this.baseUrl}/api/v1/status`,
            { headers: this.headers }
        );
        return response.json();
    }
    
    async startTrading(strategy) {
        const response = await fetch(
            `${this.baseUrl}/api/v1/trading/start`,
            {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify({ strategy })
            }
        );
        return response.json();
    }
}
``` 