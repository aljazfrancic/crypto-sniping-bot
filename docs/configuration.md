# ⚙️ Configuration Guide

This comprehensive guide covers all configuration options for the Crypto Sniping Bot enterprise edition.

## 📋 Configuration Files

The bot supports multiple configuration files for different environments:

- **`production.config.env`** - Production environment settings
- **`test_safe.config.env`** - Safe testing environment (no real funds)
- **`.env`** - Local environment (copy from production template)

## 🔧 Core Configuration

### Blockchain Settings

```env
# === BLOCKCHAIN CONFIGURATION ===

# Primary RPC endpoint
RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID

# Backup RPC endpoints (comma-separated)
BACKUP_RPC_URLS=https://eth.llamarpc.com,https://rpc.ankr.com/eth,https://ethereum.publicnode.com

# Blockchain network
CHAIN_ID=1  # 1=Mainnet, 5=Goerli, 11155111=Sepolia

# Wallet configuration
PRIVATE_KEY=your_private_key_here
WALLET_ADDRESS=0xYourWalletAddress

# Connection settings
CONNECTION_TIMEOUT=30
REQUEST_TIMEOUT=15
MAX_RETRIES=3
```

### Trading Parameters

```env
# === TRADING CONFIGURATION ===

# Liquidity requirements
MIN_LIQUIDITY_ETH=1.0          # Minimum liquidity in ETH
MIN_LIQUIDITY_USD=1000         # Minimum liquidity in USD

# Trade amounts
TRADE_AMOUNT_ETH=0.1           # Amount to trade per transaction
MAX_TRADE_AMOUNT=1.0           # Maximum trade amount
MIN_TRADE_AMOUNT=0.01          # Minimum trade amount

# Slippage and gas
SLIPPAGE_TOLERANCE=5.0         # Slippage tolerance (%)
MAX_GAS_PRICE=100              # Maximum gas price (gwei)
MIN_GAS_PRICE=10               # Minimum gas price (gwei)
GAS_PRICE_MULTIPLIER=1.1       # Gas price multiplier

# Trading limits
MAX_CONCURRENT_TRADES=3        # Maximum simultaneous trades
DAILY_TRADE_LIMIT=50           # Maximum trades per day
MAX_POSITION_SIZE=5.0          # Maximum position size in ETH
```

### DEX Configuration

```env
# === DEX SETTINGS ===

# Uniswap V2
UNISWAP_V2_ROUTER=0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
UNISWAP_V2_FACTORY=0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f

# Uniswap V3
UNISWAP_V3_ROUTER=0xE592427A0AEce92De3Edee1F18E0157C05861564
UNISWAP_V3_FACTORY=0x1F98431c8aD98523631AE4a59f267346ea31F984

# SushiSwap
SUSHISWAP_ROUTER=0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F
SUSHISWAP_FACTORY=0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac

# Common tokens
WETH_ADDRESS=0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
USDC_ADDRESS=0xA0b86991c431e6C6358a2b2e3c3d2a2c3e0b7fD14
USDT_ADDRESS=0xdAC17F958D2ee523a2206206994597C13D831ec7
```

## 🔒 Security Configuration

### Private Key Protection

```env
# === SECURITY SETTINGS ===

# Private key validation
VALIDATE_PRIVATE_KEY=true
REJECT_TEST_KEYS=true
REQUIRE_CHECKSUMMED_ADDRESS=true

# MEV Protection
ENABLE_MEV_PROTECTION=true
MEV_PROTECTION_MODE=advanced    # basic, standard, advanced
FLASHBOT_RELAY_URL=https://relay.flashbots.net
PRIVATE_MEMPOOL=true

# Honeypot detection
HONEYPOT_CHECK_ENABLED=true
HONEYPOT_API_KEY=your_honeypot_api_key
HONEYPOT_TIMEOUT=10
SIMULATE_TRADE_BEFORE_EXECUTION=true

# Contract verification
VERIFY_CONTRACT_SOURCE=true
CHECK_CONTRACT_OWNERSHIP=true
VERIFY_LIQUIDITY_LOCKS=true
CHECK_TOKEN_BLACKLIST=true
```

### Risk Management

```env
# === RISK MANAGEMENT ===

# Price manipulation protection
ENABLE_PRICE_MANIPULATION_DETECTION=true
MAX_PRICE_IMPACT=10.0          # Maximum acceptable price impact (%)
MIN_TIME_BETWEEN_TRADES=30     # Minimum seconds between trades

# Gas protection
MAX_GAS_LIMIT=500000           # Maximum gas limit
GAS_ESTIMATION_MULTIPLIER=1.2  # Gas estimation safety multiplier
ENABLE_GAS_PRICE_ALERTS=true

# Stop loss and take profit
ENABLE_STOP_LOSS=true
STOP_LOSS_PERCENTAGE=20.0      # Stop loss at 20% loss
ENABLE_TAKE_PROFIT=true
TAKE_PROFIT_PERCENTAGE=50.0    # Take profit at 50% gain

# Portfolio limits
MAX_PORTFOLIO_RISK=10.0        # Maximum portfolio risk (%)
MAX_SINGLE_POSITION_RISK=2.0   # Maximum single position risk (%)
```

## 📊 Analytics & Monitoring

### Database Configuration

```env
# === DATABASE SETTINGS ===

# SQLite (default)
DATABASE_URL=sqlite:///sniper_data.db
DATABASE_POOL_SIZE=10
DATABASE_TIMEOUT=30

# PostgreSQL (production)
# DATABASE_URL=postgresql://user:password@localhost:5432/sniper_bot
# DATABASE_POOL_SIZE=20
# DATABASE_TIMEOUT=60

# MySQL
# DATABASE_URL=mysql://user:password@localhost:3306/sniper_bot
```

### Performance Monitoring

```env
# === MONITORING CONFIGURATION ===

# Performance tracking
ENABLE_PERFORMANCE_MONITORING=true
TRACK_TRADE_ANALYTICS=true
CALCULATE_PROFIT_LOSS=true
MONITOR_GAS_USAGE=true

# Metrics collection
COLLECT_BLOCKCHAIN_METRICS=true
MONITOR_RPC_PERFORMANCE=true
TRACK_ERROR_RATES=true
PERFORMANCE_SAMPLE_RATE=1.0

# Analytics reporting
GENERATE_DAILY_REPORTS=true
GENERATE_WEEKLY_REPORTS=true
AUTO_CLEANUP_OLD_DATA=true
DATA_RETENTION_DAYS=90
```

## 🔔 Notifications & Alerts

### Webhook Configuration

```env
# === NOTIFICATION SETTINGS ===

# Primary webhook (Slack/Discord)
WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
WEBHOOK_AUTH_TOKEN=your_auth_token

# Backup webhook
BACKUP_WEBHOOK_URL=https://discord.com/api/webhooks/your/webhook/url

# Notification settings
ENABLE_TRADE_NOTIFICATIONS=true
ENABLE_ERROR_NOTIFICATIONS=true
ENABLE_PERFORMANCE_NOTIFICATIONS=true
ENABLE_SECURITY_ALERTS=true

# Alert thresholds
PROFIT_ALERT_THRESHOLD=100.0   # Alert on profits > $100
LOSS_ALERT_THRESHOLD=50.0      # Alert on losses > $50
ERROR_RATE_THRESHOLD=5.0       # Alert on error rate > 5%
```

### Logging Configuration

```env
# === LOGGING SETTINGS ===

# Log levels: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL=INFO
LOG_FORMAT=detailed            # simple, detailed, json

# Log files
LOG_FILE=logs/sniper_bot.log
ERROR_LOG_FILE=logs/errors.log
TRADE_LOG_FILE=logs/trades.log

# Log rotation
ENABLE_LOG_ROTATION=true
MAX_LOG_SIZE=10MB
BACKUP_COUNT=5

# Remote logging (optional)
# REMOTE_LOG_URL=https://your-log-service.com/endpoint
# LOG_SERVICE_API_KEY=your_api_key
```

## 🚀 Performance Configuration

### Rate Limiting

```env
# === PERFORMANCE SETTINGS ===

# RPC rate limiting
MAX_RPC_CALLS_PER_SECOND=10
MAX_BURST_REQUESTS=20
RPC_COOLDOWN_PERIOD=1.0

# API rate limiting
MAX_API_CALLS_PER_MINUTE=100
API_RATE_LIMIT_WINDOW=60

# Concurrent operations
MAX_CONCURRENT_REQUESTS=5
MAX_CONCURRENT_TRADES=3
MAX_CONCURRENT_ANALYTICS=2
```

### Circuit Breaker

```env
# === CIRCUIT BREAKER SETTINGS ===

# RPC circuit breaker
ENABLE_RPC_CIRCUIT_BREAKER=true
RPC_FAILURE_THRESHOLD=5
RPC_RECOVERY_TIMEOUT=60
RPC_SUCCESS_THRESHOLD=3

# Trading circuit breaker
ENABLE_TRADING_CIRCUIT_BREAKER=true
TRADING_FAILURE_THRESHOLD=3
TRADING_RECOVERY_TIMEOUT=300

# Notification circuit breaker
NOTIFICATION_FAILURE_THRESHOLD=5
NOTIFICATION_RECOVERY_TIMEOUT=120
```

### Caching

```env
# === CACHING CONFIGURATION ===

# Enable caching
ENABLE_CONTRACT_CACHING=true
ENABLE_PRICE_CACHING=true
ENABLE_ABI_CACHING=true

# Cache timeouts (seconds)
CONTRACT_CACHE_TTL=3600        # 1 hour
PRICE_CACHE_TTL=30             # 30 seconds
ABI_CACHE_TTL=86400            # 24 hours

# Cache sizes
MAX_CONTRACT_CACHE_SIZE=1000
MAX_PRICE_CACHE_SIZE=500
MAX_ABI_CACHE_SIZE=100
```

## 🧪 Testing Configuration

### Test Environment

```env
# === TEST CONFIGURATION ===

# Test mode settings
ENABLE_TEST_MODE=false
USE_TESTNET=false
PAPER_TRADING=false

# Test RPC endpoints
TESTNET_RPC_URL=https://goerli.infura.io/v3/YOUR_PROJECT_ID
SEPOLIA_RPC_URL=https://sepolia.infura.io/v3/YOUR_PROJECT_ID

# Test amounts
TEST_TRADE_AMOUNT=0.001
TEST_MAX_GAS_PRICE=20

# Mock settings
MOCK_BLOCKCHAIN_CALLS=false
MOCK_WEBHOOK_CALLS=false
ENABLE_DRY_RUN=false
```

## 📱 Advanced Features

### Machine Learning (Optional)

```env
# === ML CONFIGURATION ===

# Enable ML features
ENABLE_ML_PREDICTIONS=false
ML_MODEL_PATH=models/price_predictor.pkl
ML_CONFIDENCE_THRESHOLD=0.8

# Feature engineering
ENABLE_TECHNICAL_INDICATORS=true
LOOKBACK_PERIOD=100
UPDATE_MODEL_FREQUENCY=daily
```

### Custom Strategies

```env
# === STRATEGY CONFIGURATION ===

# Strategy selection
DEFAULT_STRATEGY=liquidity_sniper
ENABLE_MULTIPLE_STRATEGIES=true

# Strategy-specific settings
LIQUIDITY_SNIPER_MIN_AMOUNT=1.0
NEW_PAIR_DETECTOR_DELAY=5
ARBITRAGE_MIN_PROFIT=0.5

# Strategy weights (for multi-strategy mode)
STRATEGY_WEIGHTS=liquidity:0.4,new_pairs:0.3,arbitrage:0.3
```

## 🌐 Network-Specific Settings

### Ethereum Mainnet

```env
# === ETHEREUM MAINNET ===
CHAIN_ID=1
RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
BLOCK_CONFIRMATION_COUNT=2
```

### Binance Smart Chain

```env
# === BSC CONFIGURATION ===
CHAIN_ID=56
RPC_URL=https://bsc-dataseed.binance.org/
PANCAKESWAP_ROUTER=0x10ED43C718714eb63d5aA57B78B54704E256024E
```

### Polygon

```env
# === POLYGON CONFIGURATION ===
CHAIN_ID=137
RPC_URL=https://polygon-rpc.com/
QUICKSWAP_ROUTER=0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff
```

## 🔄 Environment-Specific Configurations

### Development Environment

```env
# === DEVELOPMENT SETTINGS ===
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
ENABLE_HOT_RELOAD=true
DISABLE_SECURITY_CHECKS=false  # Never disable in production!
```

### Staging Environment

```env
# === STAGING SETTINGS ===
ENVIRONMENT=staging
USE_TESTNET=true
REDUCED_TRADE_AMOUNTS=true
ENABLE_ALL_LOGGING=true
```

### Production Environment

```env
# === PRODUCTION SETTINGS ===
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=INFO
ENABLE_ALL_SECURITY_FEATURES=true
```

## 📚 Configuration Examples

### Conservative Trading Setup

```env
# Conservative configuration for beginners
TRADE_AMOUNT_ETH=0.01
MAX_GAS_PRICE=50
SLIPPAGE_TOLERANCE=2.0
ENABLE_STOP_LOSS=true
STOP_LOSS_PERCENTAGE=10.0
MAX_CONCURRENT_TRADES=1
```

### Aggressive Trading Setup

```env
# Aggressive configuration for experienced traders
TRADE_AMOUNT_ETH=0.5
MAX_GAS_PRICE=200
SLIPPAGE_TOLERANCE=10.0
MAX_CONCURRENT_TRADES=5
ENABLE_MEV_PROTECTION=true
```

### High-Frequency Trading Setup

```env
# High-frequency trading configuration
MAX_RPC_CALLS_PER_SECOND=50
MAX_CONCURRENT_TRADES=10
MIN_TIME_BETWEEN_TRADES=1
ENABLE_PRICE_CACHING=true
PRICE_CACHE_TTL=5
```

## 🔍 Configuration Validation

The bot automatically validates configuration on startup:

```bash
# Validate configuration
python -c "from bot.config import Config; config = Config(); print('✅ Configuration valid')"

# Check specific settings
python -c "from bot.config import Config; config = Config(); print(f'RPC URL: {config.rpc_url}')"

# Test database connection
python -c "from bot.analytics import TradingAnalytics; analytics = TradingAnalytics(); print('✅ Database connected')"
```

## 🚨 Security Best Practices

### Environment Variables

```bash
# Use environment variables for sensitive data
export PRIVATE_KEY="your_private_key_here"
export RPC_URL="your_rpc_url_here"
export WEBHOOK_URL="your_webhook_url_here"
```

### File Permissions

```bash
# Secure configuration files
chmod 600 .env
chmod 600 production.config.env
```

### Git Security

```gitignore
# Add to .gitignore
.env
*.config.env
secrets/
```

## 🔧 Configuration Management

### Multiple Environments

```bash
# Switch between environments
cp production.config.env .env     # Production
cp staging.config.env .env        # Staging
cp development.config.env .env    # Development
```

### Configuration Backup

```bash
# Backup configurations
tar -czf config_backup_$(date +%Y%m%d).tar.gz *.config.env .env
```

### Automated Deployment

```bash
# Deploy with specific config
python -m bot.sniper --config production.config.env
```

## 📞 Support

For configuration assistance:

- 📖 **Documentation**: [troubleshooting.md](troubleshooting.md)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/crypto-sniping-bot/issues)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/crypto-sniping-bot/discussions)

---

**⚙️ Proper configuration is crucial for successful trading. Take time to understand each setting before going live.**
