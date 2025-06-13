# API Documentation

## Core Components

### Blockchain Interface (`bot/blockchain.py`)

The blockchain interface handles all interactions with the Ethereum blockchain.

#### `BlockchainInterface`

```python
class BlockchainInterface:
    def __init__(self, rpc_url: str, chain_id: int, private_key: str):
        """
        Initialize blockchain interface.
        
        Args:
            rpc_url: Ethereum RPC endpoint URL
            chain_id: Network chain ID
            private_key: Wallet private key
        """
```

#### Methods

- `get_balance(address: str) -> float`
  - Get ETH balance for an address
  - Returns: Balance in ETH

- `get_token_balance(token_address: str, wallet_address: str) -> float`
  - Get token balance for a wallet
  - Returns: Token balance

- `get_token_price(token_address: str) -> float`
  - Get current token price in ETH
  - Returns: Price in ETH

- `get_liquidity(token_address: str) -> float`
  - Get token liquidity in ETH
  - Returns: Liquidity amount in ETH

### Trading Engine (`bot/trading.py`)

The trading engine handles all trading operations.

#### `TradingEngine`

```python
class TradingEngine:
    def __init__(self, blockchain: BlockchainInterface, config: Config):
        """
        Initialize trading engine.
        
        Args:
            blockchain: Blockchain interface instance
            config: Configuration instance
        """
```

#### Methods

- `buy_token(token_address: str, amount: float) -> str`
  - Buy tokens with ETH
  - Returns: Transaction hash

- `sell_token(token_address: str, amount: float) -> str`
  - Sell tokens for ETH
  - Returns: Transaction hash

- `check_slippage(token_address: str, amount: float) -> float`
  - Calculate expected slippage
  - Returns: Slippage percentage

### Honeypot Detection (`bot/honeypot.py`)

The honeypot detection module analyzes tokens for potential scams.

#### `HoneypotDetector`

```python
class HoneypotDetector:
    def __init__(self, blockchain: BlockchainInterface):
        """
        Initialize honeypot detector.
        
        Args:
            blockchain: Blockchain interface instance
        """
```

#### Methods

- `analyze_token(token_address: str) -> Dict[str, Any]`
  - Analyze token for honeypot characteristics
  - Returns: Analysis results

- `check_blacklist(token_address: str) -> bool`
  - Check if token is blacklisted
  - Returns: True if blacklisted

### Configuration (`bot/config.py`)

The configuration module manages bot settings.

#### `Config`

```python
class Config:
    def __init__(self, env_file: str = ".env"):
        """
        Initialize configuration.
        
        Args:
            env_file: Path to environment file
        """
```

#### Properties

- `rpc_url: str`
  - Ethereum RPC endpoint

- `chain_id: int`
  - Network chain ID

- `private_key: str`
  - Wallet private key

- `buy_amount: float`
  - Amount to spend per trade

- `slippage: float`
  - Maximum allowed slippage

### Monitoring (`bot/monitoring.py`)

The monitoring module handles logging and metrics.

#### `BotMonitor`

```python
class BotMonitor:
    def __init__(self, log_dir: str = "logs"):
        """
        Initialize bot monitor.
        
        Args:
            log_dir: Directory for log files
        """
```

#### Methods

- `log_trade(trade_type: str, token_address: str, amount: float, price: float, status: str, tx_hash: Optional[str] = None)`
  - Log a trade event

- `log_error(error_type: str, message: str, details: Optional[Dict] = None)`
  - Log an error event

- `update_position(token_address: str, status: str, profit: float = 0.0)`
  - Update position metrics

- `create_backup() -> Path`
  - Create backup of important files
  - Returns: Backup directory path

- `restore_from_backup(backup_path: str)`
  - Restore from backup

## Usage Examples

### Basic Setup

```python
from bot.blockchain import BlockchainInterface
from bot.config import Config
from bot.trading import TradingEngine
from bot.honeypot import HoneypotDetector
from bot.monitoring import BotMonitor

# Initialize components
config = Config()
blockchain = BlockchainInterface(
    rpc_url=config.rpc_url,
    chain_id=config.chain_id,
    private_key=config.private_key
)
trading = TradingEngine(blockchain, config)
honeypot = HoneypotDetector(blockchain)
monitor = BotMonitor()

# Buy token
token_address = "0x..."
amount = 0.1  # ETH

# Check for honeypot
analysis = honeypot.analyze_token(token_address)
if not analysis["is_honeypot"]:
    # Execute trade
    tx_hash = trading.buy_token(token_address, amount)
    monitor.log_trade("buy", token_address, amount, analysis["price"], "success", tx_hash)
```

### Monitoring and Backup

```python
# Get metrics
metrics = monitor.get_metrics()
print(f"Total trades: {metrics['trades']['total']}")
print(f"Total profit: {metrics['positions']['total_profit']} ETH")

# Create backup
backup_path = monitor.create_backup()
print(f"Backup created at {backup_path}")

# Restore from backup
monitor.restore_from_backup(backup_path)
```

## Error Handling

The bot uses a comprehensive error handling system:

```python
try:
    # Trading operation
    tx_hash = trading.buy_token(token_address, amount)
except Exception as e:
    # Log error
    monitor.log_error(
        "trade_failed",
        str(e),
        {
            "token": token_address,
            "amount": amount,
            "operation": "buy"
        }
    )
```

## Configuration Reference

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `RPC_URL` | Ethereum RPC endpoint | Required |
| `CHAIN_ID` | Network chain ID | Required |
| `PRIVATE_KEY` | Wallet private key | Required |
| `BUY_AMOUNT` | Amount to spend per trade | 0.1 |
| `SLIPPAGE` | Maximum allowed slippage | 5 |
| `PROFIT_TARGET` | Take profit percentage | 50 |
| `STOP_LOSS` | Stop loss percentage | 10 |
| `MIN_LIQUIDITY` | Minimum pool liquidity | 5 |
| `CHECK_HONEYPOT` | Enable honeypot detection | true |
| `AUTO_SELL` | Enable automatic selling | true | 