# ⚙️ Configuration Guide

This guide explains all configuration options available in the Crypto Sniping Bot.

## 📁 Configuration Files

### 1. Environment Variables (.env)
```env
# Required Settings
PRIVATE_KEY=your_private_key_here
RPC_URL=your_rpc_url_here
CHAIN_ID=1  # 1 for Ethereum, 56 for BSC

# Trading Settings
SLIPPAGE=5  # Maximum slippage tolerance in percentage
MIN_LIQUIDITY=1  # Minimum liquidity in ETH
MAX_GAS_PRICE=100  # Maximum gas price in gwei
GAS_PRICE_MULTIPLIER=1.2  # Multiplier for base gas price

# Security Settings
CHECK_HONEYPOT=true  # Enable honeypot detection
VERIFY_CONTRACT=true  # Enable contract verification
CHECK_RESTRICTIONS=true  # Enable trading restrictions check
MAX_PRICE_DEVIATION=5  # Maximum price deviation in percentage

# DEX Settings
DEX_ROUTER=0x...  # DEX router address
DEX_FACTORY=0x...  # DEX factory address
WETH_ADDRESS=0x...  # Wrapped ETH address

# Monitoring Settings
LOG_LEVEL=INFO  # DEBUG, INFO, WARNING, ERROR
TELEGRAM_BOT_TOKEN=your_token_here  # Optional: Telegram notifications
TELEGRAM_CHAT_ID=your_chat_id_here  # Optional: Telegram chat ID
```

### 2. Configuration File (config.json)
```json
{
  "trading": {
    "slippage": 5,
    "min_liquidity": 1,
    "max_gas_price": 100,
    "gas_price_multiplier": 1.2
  },
  "security": {
    "check_honeypot": true,
    "verify_contract": true,
    "check_restrictions": true,
    "max_price_deviation": 5
  },
  "dex": {
    "router": "0x...",
    "factory": "0x...",
    "weth": "0x..."
  },
  "monitoring": {
    "log_level": "INFO",
    "telegram": {
      "enabled": true,
      "bot_token": "your_token_here",
      "chat_id": "your_chat_id_here"
    }
  }
}
```

## 🔧 Configuration Options

### Trading Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `SLIPPAGE` | int | 5 | Maximum allowed slippage in percentage |
| `MIN_LIQUIDITY` | float | 1 | Minimum required liquidity in ETH |
| `MAX_GAS_PRICE` | int | 100 | Maximum gas price in gwei |
| `GAS_PRICE_MULTIPLIER` | float | 1.2 | Multiplier for base gas price |

### Security Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `CHECK_HONEYPOT` | bool | true | Enable honeypot detection |
| `VERIFY_CONTRACT` | bool | true | Enable contract verification |
| `CHECK_RESTRICTIONS` | bool | true | Enable trading restrictions check |
| `MAX_PRICE_DEVIATION` | int | 5 | Maximum price deviation in percentage |

### DEX Settings

| Setting | Type | Description |
|---------|------|-------------|
| `DEX_ROUTER` | address | DEX router contract address |
| `DEX_FACTORY` | address | DEX factory contract address |
| `WETH_ADDRESS` | address | Wrapped ETH contract address |

### Monitoring Settings

| Setting | Type | Default | Description |
|---------|------|---------|-------------|
| `LOG_LEVEL` | string | INFO | Logging level (DEBUG, INFO, WARNING, ERROR) |
| `TELEGRAM_BOT_TOKEN` | string | - | Telegram bot token for notifications |
| `TELEGRAM_CHAT_ID` | string | - | Telegram chat ID for notifications |

## 🔄 Configuration Loading

The bot loads configuration in the following order:

1. Environment variables (.env)
2. Configuration file (config.json)
3. Command-line arguments
4. Default values

## 📝 Example Configurations

### Basic Configuration
```env
PRIVATE_KEY=your_private_key
RPC_URL=https://mainnet.infura.io/v3/your_project_id
CHAIN_ID=1
SLIPPAGE=5
MIN_LIQUIDITY=1
```

### Advanced Configuration
```env
# Required
PRIVATE_KEY=your_private_key
RPC_URL=https://mainnet.infura.io/v3/your_project_id
CHAIN_ID=1

# Trading
SLIPPAGE=3
MIN_LIQUIDITY=2
MAX_GAS_PRICE=50
GAS_PRICE_MULTIPLIER=1.5

# Security
CHECK_HONEYPOT=true
VERIFY_CONTRACT=true
CHECK_RESTRICTIONS=true
MAX_PRICE_DEVIATION=3

# DEX
DEX_ROUTER=0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
DEX_FACTORY=0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f
WETH_ADDRESS=0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2

# Monitoring
LOG_LEVEL=DEBUG
TELEGRAM_BOT_TOKEN=your_token
TELEGRAM_CHAT_ID=your_chat_id
```

## 🔒 Security Considerations

1. **Private Key Security**
   - Never commit private keys to version control
   - Use environment variables for sensitive data
   - Consider using a hardware wallet for large amounts

2. **RPC URL Security**
   - Use HTTPS endpoints
   - Consider using private RPC nodes
   - Monitor RPC usage and rate limits

3. **Gas Price Settings**
   - Set reasonable gas price limits
   - Monitor network conditions
   - Adjust gas price multiplier based on network load

## 🚀 Best Practices

1. **Configuration Management**
   - Use version control for config files
   - Document all configuration changes
   - Test configurations in testnet first

2. **Security Settings**
   - Enable all security checks in production
   - Set conservative slippage limits
   - Monitor price deviations

3. **Monitoring Setup**
   - Enable detailed logging
   - Set up notifications
   - Monitor bot performance

## ⚠️ Common Issues

1. **Configuration Errors**
   - Invalid private key format
   - Incorrect RPC URL
   - Invalid contract addresses

2. **Security Warnings**
   - High slippage settings
   - Disabled security checks
   - Unverified contracts

3. **Performance Issues**
   - High gas prices
   - Network congestion
   - RPC node issues

## 📚 Additional Resources

- [Ethereum Networks](https://ethereum.org/en/developers/docs/networks/)
- [Gas Optimization](https://ethereum.org/en/developers/docs/gas/)
- [Security Best Practices](https://consensys.github.io/smart-contract-best-practices/) 