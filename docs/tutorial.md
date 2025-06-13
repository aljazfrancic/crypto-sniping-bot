# Crypto Sniping Bot Tutorial

This tutorial will guide you through setting up and using the Crypto Sniping Bot.

## Prerequisites

Before you begin, ensure you have:

1. Python 3.9+ installed (tested with 3.13)
2. Node.js 16+ and npm 7+ installed
3. A funded Ethereum wallet
4. An RPC endpoint (Alchemy, Infura, etc.)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/crypto-sniping-bot.git
   cd crypto-sniping-bot
   ```

2. Set up Python environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # Linux/Mac
   # or
   .venv\Scripts\activate  # Windows
   pip install -r requirements.txt
   ```

3. Install Node.js dependencies:
   ```bash
   npm install
   ```

4. Create `.env` file:
   ```bash
   cp .env.example .env
   ```

5. Edit `.env` with your settings:
   ```env
   RPC_URL=your_rpc_url
   CHAIN_ID=1
   ROUTER_ADDRESS=0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
   FACTORY_ADDRESS=0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f
   WETH_ADDRESS=0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
   PRIVATE_KEY=your_private_key
   BUY_AMOUNT=0.1
   SLIPPAGE=5
   ```

## Deployment

1. Deploy the Sniper contract:
   ```bash
   # For testnet
   npx hardhat run scripts/deploy.js --network goerli
   # or
   npx hardhat run scripts/deploy.js --network bscTestnet
   
   # For mainnet
   npx hardhat run scripts/deploy.js --network mainnet
   # or
   npx hardhat run scripts/deploy.js --network bsc
   ```

2. Add the deployed contract address to your `.env`:
   ```env
   SNIPER_CONTRACT=deployed_contract_address
   ```

## Running the Bot

1. Start the bot:
   ```bash
   python -m bot.sniper
   ```

2. Monitor logs:
   ```bash
   tail -f sniper_bot.log
   ```

## Basic Usage

### Buying Tokens

The bot will automatically:
1. Monitor for new liquidity pools
2. Check for honeypot characteristics
3. Verify liquidity and slippage
4. Execute trades when conditions are met

### Manual Trading

You can also trade manually:

```python
from bot.blockchain import BlockchainInterface
from bot.config import Config
from bot.trading import TradingEngine
from bot.honeypot import HoneypotDetector

# Initialize components
config = Config()
blockchain = BlockchainInterface(
    rpc_url=config.rpc_url,
    chain_id=config.chain_id,
    private_key=config.private_key
)
trading = TradingEngine(blockchain, config)
honeypot = HoneypotDetector(blockchain)

# Buy token
token_address = "0x..."  # Token address
amount = 0.1  # ETH amount

# Check for honeypot
analysis = honeypot.analyze_token(token_address)
if not analysis["is_honeypot"]:
    # Execute trade
    tx_hash = trading.buy_token(token_address, amount)
    print(f"Trade executed: {tx_hash}")
```

### Monitoring

The bot provides real-time monitoring:

```python
from bot.monitoring import BotMonitor

monitor = BotMonitor()

# Get metrics
metrics = monitor.get_metrics()
print(f"Total trades: {metrics['trades']['total']}")
print(f"Total profit: {metrics['positions']['total_profit']} ETH")

# Create backup
backup_path = monitor.create_backup()
print(f"Backup created at {backup_path}")
```

## Advanced Configuration

### Trading Parameters

Adjust trading parameters in `.env`:

```env
# Trading
BUY_AMOUNT=0.1          # ETH amount per trade
SLIPPAGE=5              # Maximum slippage percentage
PROFIT_TARGET=50        # Take profit percentage
STOP_LOSS=10           # Stop loss percentage
MIN_LIQUIDITY=5        # Minimum pool liquidity in ETH

# Safety
CHECK_HONEYPOT=true    # Enable honeypot detection
AUTO_SELL=true         # Enable automatic selling

# Network
CHAIN_ID=1             # 1: Ethereum, 56: BSC, 137: Polygon
GAS_PRICE_MULTIPLIER=1.2  # Gas price multiplier for faster transactions
```

### Network Selection

The bot supports multiple networks:

| Network | Chain ID | Router Address |
|---------|----------|----------------|
| Ethereum | 1 | 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D |
| BSC | 56 | 0x10ED43C718714eb63d5aA57B78B54704E256024E |
| Polygon | 137 | 0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff |

Set `CHAIN_ID` in `.env` to switch networks.

## Troubleshooting

### Common Issues

1. **"Insufficient funds"**
   - Check wallet balance
   - Ensure `BUY_AMOUNT` is less than balance
   - Account for gas fees

2. **"Transaction failed"**
   - Check gas price
   - Verify slippage settings
   - Ensure sufficient liquidity

3. **"Connection lost"**
   - Check RPC endpoint
   - Use reliable WebSocket provider
   - Verify network status

### Logs and Debugging

1. Check logs:
   ```bash
   tail -f sniper_bot.log
   ```

2. View metrics:
   ```bash
   cat logs/metrics_*.json
   ```

3. Restore from backup:
   ```python
   monitor.restore_from_backup("backups/backup_20240101_120000")
   ```

## Best Practices

1. **Start Small**
   - Begin with small amounts
   - Test on testnet first
   - Monitor performance

2. **Security**
   - Use dedicated wallet
   - Never share private key
   - Regular backups

3. **Monitoring**
   - Check logs regularly
   - Monitor metrics
   - Set up alerts

4. **Maintenance**
   - Update dependencies
   - Check for new features
   - Regular backups

## Next Steps

1. Explore advanced features:
   - Custom trading strategies
   - Multi-token support
   - Advanced monitoring

2. Join the community:
   - Discord server
   - GitHub discussions
   - Telegram group

3. Contribute:
   - Report bugs
   - Suggest features
   - Submit pull requests 