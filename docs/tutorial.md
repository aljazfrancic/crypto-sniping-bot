# 📚 Tutorial - Getting Started with Crypto Sniping Bot

This comprehensive tutorial will guide you through setting up and using the Crypto Sniping Bot enterprise edition, from installation to advanced trading strategies.

## 🎯 What You'll Learn

- Complete bot setup and configuration
- Security features and best practices
- Trading strategies and execution
- Performance monitoring and analytics
- Testing and validation procedures

## 🚀 Quick Start (5 Minutes)

### Step 1: Installation
```bash
# Clone the repository
git clone https://github.com/your-username/crypto-sniping-bot.git
cd crypto-sniping-bot

# Run automated setup
python setup_tests.py

# Verify installation
python test_clean.py
```

### Step 2: Basic Configuration
```bash
# Copy production config template
cp production.config.env .env

# Edit with your settings (minimum required)
nano .env
```

Add your essential settings:
```env
RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
PRIVATE_KEY=your_private_key_here
WALLET_ADDRESS=0xYourWalletAddress
WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
```

### Step 3: Test Run
```bash
# Start the bot in test mode
python -m bot.sniper --test-mode

# Check status
python -c "from bot.sniper import SniperBot; from bot.config import Config; bot = SniperBot(Config()); print(bot.get_status())"
```

## 📖 Detailed Setup Guide

### 1. Environment Preparation

#### System Requirements
- Python 3.8+ (3.10+ recommended)
- 8GB RAM minimum (16GB for production)
- Stable internet connection
- 2GB disk space

#### Create Trading Wallet
```python
# Generate a new wallet (run once)
from eth_account import Account
account = Account.create()
print(f"Address: {account.address}")
print(f"Private Key: {account.privateKey.hex()}")
# IMPORTANT: Save these securely!
```

### 2. RPC Endpoint Setup

#### Option A: Infura (Recommended)
1. Go to [infura.io](https://infura.io)
2. Create free account
3. Create new project
4. Copy project ID
5. Use URL: `https://mainnet.infura.io/v3/YOUR_PROJECT_ID`

#### Option B: Alchemy
1. Go to [alchemy.com](https://alchemy.com)
2. Create account and app
3. Copy API key
4. Use URL: `https://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY`

#### Option C: Public Endpoints (Backup)
```env
BACKUP_RPC_URLS=https://eth.llamarpc.com,https://rpc.ankr.com/eth,https://ethereum.publicnode.com
```

### 3. Security Configuration

#### Private Key Protection
```env
# ✅ SECURE: Use environment variables
PRIVATE_KEY=0xYourActualPrivateKeyHere

# ❌ INSECURE: Never hard-code keys
# ❌ INSECURE: Never use test keys in production
```

#### Enable All Security Features
```env
# Private key validation
VALIDATE_PRIVATE_KEY=true
REJECT_TEST_KEYS=true

# MEV Protection
ENABLE_MEV_PROTECTION=true
MEV_PROTECTION_MODE=advanced

# Honeypot detection
HONEYPOT_CHECK_ENABLED=true
SIMULATE_TRADE_BEFORE_EXECUTION=true

# Contract verification
VERIFY_CONTRACT_SOURCE=true
CHECK_LIQUIDITY_LOCKS=true
```

### 4. Trading Configuration

#### Conservative Setup (Beginners)
```env
# Trading amounts
TRADE_AMOUNT_ETH=0.01
MAX_TRADE_AMOUNT=0.1

# Risk management
SLIPPAGE_TOLERANCE=2.0
MAX_GAS_PRICE=50
ENABLE_STOP_LOSS=true
STOP_LOSS_PERCENTAGE=10.0

# Limits
MAX_CONCURRENT_TRADES=1
DAILY_TRADE_LIMIT=10
```

#### Aggressive Setup (Experienced)
```env
# Trading amounts
TRADE_AMOUNT_ETH=0.1
MAX_TRADE_AMOUNT=1.0

# Risk management
SLIPPAGE_TOLERANCE=10.0
MAX_GAS_PRICE=200
ENABLE_STOP_LOSS=true
STOP_LOSS_PERCENTAGE=20.0

# Limits
MAX_CONCURRENT_TRADES=5
DAILY_TRADE_LIMIT=100
```

## 🛡️ Security Tutorial

### Understanding Security Features

#### 1. Private Key Protection
```python
# The bot automatically validates your private key
from bot.security import SecurityManager
from bot.config import Config

security = SecurityManager(Config())

# This will pass for real keys
try:
    security.validate_private_key("0x" + "a" * 64)
    print("✅ Key is valid")
except Exception as e:
    print(f"❌ Key validation failed: {e}")

# This will fail for test keys
try:
    dangerous_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
    security.validate_private_key(dangerous_key)
except Exception as e:
    print(f"🛡️ Dangerous key rejected: {e}")
```

#### 2. Token Security Analysis
```python
# Analyze a token before trading
from bot.security import SecurityManager
from bot.config import Config

async def analyze_token(token_address):
    security = SecurityManager(Config())
    
    # Comprehensive security analysis
    report = await security.validate_token(token_address)
    
    print(f"Security Score: {report.security_score}/100")
    print(f"Risk Level: {report.risk_level}")
    print(f"Is Honeypot: {report.is_honeypot}")
    print(f"Contract Verified: {report.contract_verified}")
    
    if report.warnings:
        print("⚠️ Warnings:")
        for warning in report.warnings:
            print(f"  - {warning}")
    
    return report.security_score >= 70  # Safe threshold

# Usage
token_safe = await analyze_token("0x...")
if token_safe:
    print("✅ Token appears safe to trade")
else:
    print("❌ Token has security concerns")
```

#### 3. MEV Protection
```python
# MEV protection is automatic, but you can check status
from bot.security import MEVProtector
from bot.config import Config

mev_protector = MEVProtector(Config())
status = mev_protector.get_status()

print(f"MEV Protection: {'✅ Active' if status.active else '❌ Inactive'}")
print(f"Protection Mode: {status.mode}")
print(f"Flashbot Relay: {status.flashbot_enabled}")
```

## 💰 Trading Tutorial

### Basic Trading Operations

#### 1. Manual Buy Order
```python
from bot.trading import TradingEngine
from bot.config import Config

async def execute_manual_buy():
    trading = TradingEngine(Config())
    
    token_address = "0x..."  # Token you want to buy
    amount_eth = 0.1  # Amount in ETH
    
    try:
        # Execute buy order with security checks
        result = await trading.execute_buy_order(
            token_address=token_address,
            amount_eth=amount_eth,
            slippage_tolerance=5.0  # 5% slippage
        )
        
        if result.success:
            print(f"✅ Buy successful!")
            print(f"Transaction: {result.transaction_hash}")
            print(f"Tokens received: {result.amount_out}")
            print(f"Gas used: {result.gas_used}")
        else:
            print(f"❌ Buy failed: {result.error_message}")
            
    except Exception as e:
        print(f"💥 Error: {e}")

# Run the buy order
await execute_manual_buy()
```

#### 2. Get Price Quote
```python
async def get_price_quote():
    trading = TradingEngine(Config())
    
    # Get quote without executing
    quote = await trading.get_quote(
        token_address="0x...",
        amount_eth=0.1
    )
    
    print(f"Expected tokens: {quote.amount_out}")
    print(f"Price per token: {quote.price}")
    print(f"Price impact: {quote.price_impact}%")
    print(f"Minimum received: {quote.minimum_received}")

await get_price_quote()
```

#### 3. Portfolio Management
```python
async def check_portfolio():
    trading = TradingEngine(Config())
    
    # Get all positions
    positions = trading.get_positions()
    
    print(f"📊 Portfolio Summary ({len(positions)} positions)")
    print("-" * 50)
    
    total_value = 0
    for position in positions:
        current_value = await trading.get_position_value(position)
        profit_loss = current_value - position.initial_value
        profit_percent = (profit_loss / position.initial_value) * 100
        
        print(f"Token: {position.symbol}")
        print(f"  Amount: {position.amount:.4f}")
        print(f"  Initial Value: ${position.initial_value:.2f}")
        print(f"  Current Value: ${current_value:.2f}")
        print(f"  P&L: ${profit_loss:.2f} ({profit_percent:+.2f}%)")
        print()
        
        total_value += current_value
    
    print(f"Total Portfolio Value: ${total_value:.2f}")

await check_portfolio()
```

### Automated Trading

#### 1. Start the Bot
```python
from bot.sniper import SniperBot
from bot.config import Config

async def start_automated_trading():
    config = Config()
    bot = SniperBot(config)
    
    print("🚀 Starting automated trading...")
    
    # Start the bot
    await bot.start()
    
    # Bot will now monitor for opportunities automatically
    print("✅ Bot is now running and monitoring...")

# Start in background
import asyncio
asyncio.create_task(start_automated_trading())
```

#### 2. Monitor Bot Status
```python
def monitor_bot_status():
    bot = SniperBot(Config())
    status = bot.get_status()
    
    print(f"Bot Status: {status.state}")
    print(f"Active Trades: {status.active_trades}")
    print(f"Total Trades Today: {status.trades_today}")
    print(f"Success Rate: {status.success_rate:.2f}%")
    print(f"Uptime: {status.uptime}")

# Check status periodically
import time
while True:
    monitor_bot_status()
    time.sleep(60)  # Check every minute
```

## 📊 Analytics Tutorial

### Performance Tracking

#### 1. Basic Performance Metrics
```python
from bot.analytics import TradingAnalytics
from bot.config import Config

def get_performance_summary():
    analytics = TradingAnalytics(Config())
    metrics = analytics.calculate_performance_metrics()
    
    print("📈 Performance Summary")
    print("=" * 30)
    print(f"Total Trades: {metrics.total_trades}")
    print(f"Successful Trades: {metrics.successful_trades}")
    print(f"Win Rate: {metrics.win_rate:.2f}%")
    print(f"Total P&L: {metrics.total_profit_loss:.4f} ETH")
    print(f"Average Trade Size: {metrics.average_trade_size:.4f} ETH")
    print(f"Average Gas Cost: {metrics.average_gas_cost:.6f} ETH")
    print(f"Sharpe Ratio: {metrics.sharpe_ratio:.2f}")

get_performance_summary()
```

#### 2. Detailed Trade Analysis
```python
async def analyze_recent_trades():
    analytics = TradingAnalytics(Config())
    
    # Get last 50 trades
    trades = await analytics.get_trade_history(limit=50)
    
    print(f"📋 Recent Trades ({len(trades)} total)")
    print("-" * 80)
    
    for trade in trades[-10:]:  # Show last 10
        status = "✅" if trade.profitable else "❌"
        print(f"{status} {trade.timestamp.strftime('%Y-%m-%d %H:%M')} | "
              f"{trade.token_symbol:8} | "
              f"P&L: {trade.profit_loss:+.4f} ETH | "
              f"Gas: {trade.gas_cost:.6f} ETH")

await analyze_recent_trades()
```

#### 3. Generate Reports
```python
async def generate_weekly_report():
    analytics = TradingAnalytics(Config())
    
    # Generate comprehensive weekly report
    report = await analytics.generate_report(days=7)
    
    print("📊 Weekly Trading Report")
    print("=" * 40)
    print(report.summary)
    print()
    print("Key Metrics:")
    print(f"  • Total Volume: {report.total_volume:.2f} ETH")
    print(f"  • Net Profit: {report.net_profit:.4f} ETH")
    print(f"  • Best Trade: +{report.best_trade:.4f} ETH")
    print(f"  • Worst Trade: {report.worst_trade:.4f} ETH")
    print(f"  • Gas Costs: {report.total_gas_costs:.6f} ETH")

await generate_weekly_report()
```

### Data Export

#### 1. Export Trading Data
```python
async def export_trading_data():
    analytics = TradingAnalytics(Config())
    
    # Export to CSV
    csv_file = await analytics.export_data(
        format='csv',
        start_date=datetime.now() - timedelta(days=30)
    )
    print(f"📁 Data exported to: {csv_file}")
    
    # Export to Excel
    excel_file = await analytics.export_data(
        format='excel',
        start_date=datetime.now() - timedelta(days=30)
    )
    print(f"📊 Excel report: {excel_file}")

await export_trading_data()
```

## 🧪 Testing Tutorial

### Validating Your Setup

#### 1. Run Comprehensive Tests
```bash
# Complete system validation
python test_clean.py

# This test validates:
# ✅ Configuration security
# ✅ All bot components
# ✅ Security features
# ✅ Database connectivity
# ✅ RPC connections
# ✅ Analytics systems
```

#### 2. Security-Specific Tests
```bash
# Run 18 security tests
python run_tests.py security

# Test categories:
# • Private key protection (3 tests)
# • MEV protection (3 tests)  
# • Honeypot detection (4 tests)
# • Gas protection (2 tests)
# • Contract security (3 tests)
# • Price manipulation (3 tests)
```

#### 3. Custom Validation
```python
# Test your specific configuration
from bot.config import Config
from bot.security import SecurityManager

async def validate_my_setup():
    print("🔍 Validating your configuration...")
    
    # Test configuration
    try:
        config = Config()
        print("✅ Configuration loaded successfully")
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False
    
    # Test security
    try:
        security = SecurityManager(config)
        security.validate_private_key(config.private_key)
        print("✅ Private key validation passed")
    except Exception as e:
        print(f"❌ Security validation failed: {e}")
        return False
    
    # Test RPC connection
    try:
        from bot.blockchain import BlockchainInterface
        blockchain = BlockchainInterface(config)
        block = await blockchain.get_latest_block()
        print(f"✅ RPC connection working (block: {block})")
    except Exception as e:
        print(f"❌ RPC connection failed: {e}")
        return False
    
    print("🎉 All validations passed!")
    return True

# Run validation
await validate_my_setup()
```

## 🚀 Advanced Usage

### Custom Trading Strategies

#### 1. Liquidity Sniping
```bash
# Focus on new liquidity pairs
python -m bot.sniper --strategy liquidity --min-liquidity 2.0
```

#### 2. New Token Detection
```bash
# Snipe newly created tokens
python -m bot.sniper --strategy new-pairs --delay 5
```

#### 3. Arbitrage Opportunities
```bash
# Look for price differences across DEXes
python -m bot.sniper --strategy arbitrage --min-profit 0.5
```

### Monitoring and Alerts

#### 1. Slack Integration
```env
WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
ENABLE_TRADE_NOTIFICATIONS=true
ENABLE_PERFORMANCE_NOTIFICATIONS=true
PROFIT_ALERT_THRESHOLD=100.0
```

#### 2. Discord Integration
```env
WEBHOOK_URL=https://discord.com/api/webhooks/000000000000000000/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Performance Optimization

#### 1. RPC Configuration
```env
# Multiple RPC endpoints for reliability
RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
BACKUP_RPC_URLS=https://eth.llamarpc.com,https://rpc.ankr.com/eth

# Rate limiting
MAX_RPC_CALLS_PER_SECOND=20
MAX_BURST_REQUESTS=50
```

#### 2. Caching Options
```env
# Enable caching for better performance
ENABLE_CONTRACT_CACHING=true
ENABLE_PRICE_CACHING=true
CONTRACT_CACHE_TTL=3600
PRICE_CACHE_TTL=30
```

## 🆘 Troubleshooting

### Common Issues

#### 1. "Private key validation failed"
```bash
# Check if you're using a test key
python -c "
from bot.security import SecurityManager
security = SecurityManager()
try:
    security.validate_private_key('YOUR_PRIVATE_KEY')
    print('✅ Key is valid')
except Exception as e:
    print(f'❌ {e}')
"
```

#### 2. "RPC connection failed"
```bash
# Test RPC manually
python -c "
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('YOUR_RPC_URL'))
print(f'Connected: {w3.is_connected()}')
if w3.is_connected():
    print(f'Latest block: {w3.eth.block_number}')
"
```

#### 3. "Insufficient funds"
```bash
# Check wallet balance
python -c "
from bot.blockchain import BlockchainInterface
from bot.config import Config
bi = BlockchainInterface(Config())
balance = await bi.get_eth_balance()
print(f'ETH Balance: {balance} ETH')
"
```

## 📚 Next Steps

### 1. Paper Trading
Start with test mode to familiarize yourself:
```bash
python -m bot.sniper --test-mode --paper-trading
```

### 2. Small Amounts
Begin with minimal trade sizes:
```env
TRADE_AMOUNT_ETH=0.001
MAX_TRADE_AMOUNT=0.01
```

### 3. Monitor and Learn
- Check analytics regularly
- Review trade history
- Adjust parameters based on performance
- Stay informed about market conditions

### 4. Scale Gradually
- Increase trade sizes slowly
- Add more concurrent trades
- Optimize gas settings
- Implement custom strategies

## 🎓 Best Practices

1. **Always Test First**: Run tests before live trading
2. **Start Small**: Begin with minimal amounts
3. **Monitor Actively**: Check bot status regularly
4. **Set Limits**: Use stop-losses and position sizing
5. **Stay Secure**: Never share private keys
6. **Keep Learning**: Markets change, adapt accordingly

---

**🎉 Congratulations! You're ready to start crypto sniping. Remember to trade responsibly and never invest more than you can afford to lose.**
