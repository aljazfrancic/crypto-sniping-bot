# API Reference

## Core Components

### Blockchain Interface
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

### Trading Engine
```python
from bot.trading import TradingEngine

# Initialize
trading = TradingEngine(
    router_address="ROUTER_ADDRESS",
    factory_address="FACTORY_ADDRESS"
)

# Methods
tx_hash = trading.buy_token(token_address, amount_eth, slippage)
position = trading.get_position(token_address)
```

### Honeypot Detection
```python
from bot.honeypot import HoneypotDetector

# Initialize
detector = HoneypotDetector()

# Methods
is_safe = detector.analyze_token(token_address)
liquidity = detector.verify_liquidity(token_address)
```

### Configuration
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

### Monitoring
```python
from bot.monitoring import Monitoring

# Initialize
monitoring = Monitoring()

# Methods
monitoring.log_trade(token_address, amount, price)
monitoring.log_error("Error message")
monitoring.update_position(token_address, amount, price)
```

## Configuration Reference

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

## Support

- [Discord](https://discord.gg/bZXer5ZttK) - Community support
- GitHub Issues - Bug reports
- [Tutorial](docs/tutorial.md) - Getting started 