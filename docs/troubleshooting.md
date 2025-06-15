# 🚨 Troubleshooting Guide

This comprehensive guide helps you diagnose and resolve common issues with the Crypto Sniping Bot.

## 🔍 Quick Diagnostics

### Health Check Commands
```bash
# Verify bot configuration
python -c "from bot.config import Config; config = Config(); print('✅ Configuration valid')"

# Test database connection
python -c "from bot.analytics import TradingAnalytics; analytics = TradingAnalytics(); print('✅ Database connected')"

# Check RPC connection
python -c "from bot.blockchain import BlockchainInterface; from bot.config import Config; bi = BlockchainInterface(Config()); print('✅ Blockchain connected')"

# Run comprehensive health check
python test_clean.py
```

## 🛠️ Installation Issues

### Python Version Problems

**Error**: `Python version 3.8+ required`
```bash
# Check current Python version
python --version

# Install Python 3.8+ if needed
# Ubuntu/Debian:
sudo apt-get install python3.8 python3.8-venv python3.8-dev

# Windows: Download from python.org
# macOS: 
brew install python@3.8
```

### Package Installation Failures

**Error**: `Failed building wheel for some-package`
```bash
# Update pip and setuptools
python -m pip install --upgrade pip setuptools wheel

# Install build essentials
# Ubuntu/Debian:
sudo apt-get install build-essential python3-dev libffi-dev libssl-dev

# Windows: Install Visual Studio Build Tools
# macOS:
xcode-select --install

# Retry installation
pip install -r requirements.txt
```

### Virtual Environment Issues

**Error**: `ModuleNotFoundError` even after installation
```bash
# Ensure virtual environment is activated
# Check if you're in the right environment
which python
which pip

# If not activated:
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# Reinstall in correct environment
pip install -r requirements.txt
```

## ⚙️ Configuration Issues

### Private Key Problems

**Error**: `DangerousPrivateKeyError: This private key is known to be dangerous`
```bash
# This is a security feature - you're using a test key
# Solution: Use a real private key for production

# Generate a new wallet if needed:
python -c "
from eth_account import Account
account = Account.create()
print(f'Private Key: {account.privateKey.hex()}')
print(f'Address: {account.address}')
"
```

**Error**: `InvalidPrivateKeyError: Invalid private key format`
```bash
# Check private key format (should start with 0x and be 64 hex characters)
# Correct format: 0x1234567890abcdef...

# Validate your key:
python -c "
from bot.security import SecurityManager
from bot.config import Config
security = SecurityManager(Config())
result = security.validate_private_key('YOUR_PRIVATE_KEY_HERE')
print(f'Valid: {result}')
"
```

### RPC Connection Issues

**Error**: `ConnectionError: Unable to connect to RPC endpoint`
```bash
# Test RPC connection manually
python -c "
from web3 import Web3
w3 = Web3(Web3.HTTPProvider('YOUR_RPC_URL_HERE'))
print(f'Connected: {w3.is_connected()}')
if w3.is_connected():
    print(f'Latest block: {w3.eth.block_number}')
"

# Common solutions:
# 1. Check if RPC URL is correct
# 2. Verify API key is valid
# 3. Check network connectivity
# 4. Try backup RPC endpoints
```

**Error**: `Rate limit exceeded`
```bash
# Configure rate limiting in your .env file:
MAX_RPC_CALLS_PER_SECOND=5
MAX_BURST_REQUESTS=10

# Use backup RPC endpoints:
BACKUP_RPC_URLS=https://eth.llamarpc.com,https://rpc.ankr.com/eth
```

### Database Connection Issues

**Error**: `Database connection failed`
```bash
# For SQLite (default):
# Check if directory exists and is writable
mkdir -p data
touch data/sniper_data.db

# For PostgreSQL:
# Verify connection string format
DATABASE_URL=postgresql://user:password@localhost:5432/sniper_bot

# Test PostgreSQL connection:
python -c "
import asyncpg
import asyncio
async def test():
    conn = await asyncpg.connect('YOUR_DATABASE_URL')
    await conn.close()
    print('✅ Database connected')
asyncio.run(test())
"
```

## 🔒 Security Issues

### Private Key Security Warnings

**Warning**: `Private key security validation failed`
```bash
# Check if you're using a secure private key
python -c "
from bot.security import PrivateKeyValidator
validator = PrivateKeyValidator()
result = validator.validate('YOUR_PRIVATE_KEY')
print(f'Secure: {result}')
"

# Ensure private key is:
# 1. Not a known test key
# 2. Has proper format (0x + 64 hex chars)
# 3. Has correct checksum (if applicable)
```

### MEV Protection Issues

**Error**: `MEV protection configuration failed`
```bash
# Check MEV settings in .env:
ENABLE_MEV_PROTECTION=true
MEV_PROTECTION_MODE=advanced
FLASHBOT_RELAY_URL=https://relay.flashbots.net

# Test MEV protection:
python -c "
from bot.security import MEVProtector
from bot.config import Config
mev = MEVProtector(Config())
status = mev.get_status()
print(f'MEV Protection Active: {status.active}')
"
```

### Honeypot Detection Issues

**Error**: `Honeypot check failed`
```bash
# Check honeypot service configuration:
HONEYPOT_CHECK_ENABLED=true
HONEYPOT_TIMEOUT=10

# Test honeypot detection manually:
python -c "
from bot.security import HoneypotDetector  
from bot.config import Config
detector = HoneypotDetector(Config())
result = await detector.check('TOKEN_ADDRESS_HERE')
print(f'Is Honeypot: {result.is_honeypot}')
"
```

## 💼 Trading Issues

### Insufficient Balance Errors

**Error**: `InsufficientFundsError: Not enough ETH for trade`
```bash
# Check wallet balance:
python -c "
from bot.blockchain import BlockchainInterface
from bot.config import Config
bi = BlockchainInterface(Config())
balance = await bi.get_eth_balance()
print(f'ETH Balance: {balance} ETH')
"

# Ensure you have enough ETH for:
# 1. Trade amount
# 2. Gas fees
# 3. Safety buffer (recommended 10-20%)
```

### High Gas Price Issues

**Error**: `Gas price too high`
```bash
# Check current gas prices:
python -c "
from bot.blockchain import BlockchainInterface
from bot.config import Config
bi = BlockchainInterface(Config())
gas_price = await bi.get_gas_price()
print(f'Current gas price: {gas_price} gwei')
"

# Adjust gas settings in .env:
MAX_GAS_PRICE=150  # Increase if network is congested
GAS_PRICE_MULTIPLIER=1.2
```

### Slippage Exceeded Errors

**Error**: `SlippageExceededError: Price impact too high`
```bash
# Check current slippage settings:
SLIPPAGE_TOLERANCE=5.0  # 5%

# For volatile tokens, you may need higher slippage:
SLIPPAGE_TOLERANCE=10.0  # 10%

# Check token liquidity before trading:
python -c "
from bot.blockchain import BlockchainInterface
from bot.config import Config
bi = BlockchainInterface(Config())
pair_info = await bi.get_pair_info('PAIR_ADDRESS')
print(f'Liquidity: {pair_info.liquidity_eth} ETH')
"
```

## 📊 Analytics Issues

### Database Migration Problems

**Error**: `Database schema mismatch`
```bash
# Reset database (WARNING: This deletes all data)
rm data/sniper_data.db

# Or run migrations:
python -c "
from bot.analytics import TradingAnalytics
from bot.config import Config
analytics = TradingAnalytics(Config())
await analytics.initialize_database()
print('✅ Database initialized')
"
```

### Performance Tracking Issues

**Error**: `Analytics calculation failed`
```bash
# Check if there's trade data:
python -c "
from bot.analytics import TradingAnalytics
from bot.config import Config
analytics = TradingAnalytics(Config())
trades = await analytics.get_trade_history(limit=1)
print(f'Trade count: {len(trades)}')
"

# If no trades, analytics may fail
# Wait for some trades or use mock data for testing
```

## 🔔 Notification Issues

### Webhook Connection Problems

**Error**: `Notification failed to send`
```bash
# Test webhook URL manually:
curl -X POST -H "Content-Type: application/json" \
  -d '{"text":"Test message"}' \
  YOUR_WEBHOOK_URL_HERE

# Check webhook configuration:
WEBHOOK_URL=https://hooks.slack.com/services/your/webhook/url
ENABLE_TRADE_NOTIFICATIONS=true
```

### Rate Limiting Issues

**Error**: `Notification rate limit exceeded`
```bash
# Adjust notification rate limits:
NOTIFICATION_RATE_LIMIT=30  # messages per minute
NOTIFICATION_BURST_LIMIT=5

# Enable notification circuit breaker:
NOTIFICATION_CIRCUIT_BREAKER=true
NOTIFICATION_FAILURE_THRESHOLD=5
```

## 🧪 Testing Issues

### Test Failures

**Error**: Tests failing unexpectedly
```bash
# Run tests with verbose output:
python run_tests.py -v

# Run specific test categories:
python run_tests.py security  # Security tests only
python run_tests.py unit      # Unit tests only

# Check test environment:
python -c "
import sys
import os
print(f'Python: {sys.version}')
print(f'Working directory: {os.getcwd()}')
print(f'PATH: {os.environ.get(\"PATH\", \"Not set\")}')
"
```

### Mock Service Issues

**Error**: `Mock services not responding`
```bash
# Reset test environment:
python cleanup.py

# Recreate test environment:
python setup_tests.py

# Run clean test:
python test_clean.py
```

## ⚡ Performance Issues

### Slow Response Times

**Symptoms**: Bot responding slowly to opportunities
```bash
# Check RPC response times:
python -c "
import time
from bot.blockchain import BlockchainInterface
from bot.config import Config

bi = BlockchainInterface(Config())
start = time.time()
block = await bi.get_latest_block()
end = time.time()
print(f'RPC response time: {(end-start)*1000:.2f}ms')
"

# Solutions:
# 1. Use faster RPC endpoints
# 2. Increase connection pool size
# 3. Enable caching
# 4. Reduce rate limiting if possible
```

### High Memory Usage

**Symptoms**: Bot consuming too much memory
```bash
# Check memory usage:
python -c "
import psutil
import os
process = psutil.Process(os.getpid())
memory = process.memory_info()
print(f'Memory usage: {memory.rss / 1024 / 1024:.2f} MB')
"

# Solutions:
# 1. Reduce cache sizes
# 2. Enable cache cleanup
# 3. Limit concurrent operations
```

### CPU Usage Issues

**Symptoms**: High CPU usage
```bash
# Profile CPU usage:
python -c "
import asyncio
import time
from bot.sniper import SniperBot
from bot.config import Config

# Monitor CPU during operation
import psutil
cpu_percent = psutil.cpu_percent(interval=1)
print(f'CPU usage: {cpu_percent}%')
"

# Solutions:
# 1. Optimize async operations
# 2. Reduce polling frequency
# 3. Enable efficient algorithms
```

## 🌐 Network Issues

### Blockchain Network Problems

**Error**: `Network congestion detected`
```bash
# Check network status:
python -c "
from bot.blockchain import BlockchainInterface
from bot.config import Config
bi = BlockchainInterface(Config())
health = bi.get_health_status()
print(f'Network health: {health.status}')
print(f'Block time: {health.average_block_time}s')
print(f'Gas price: {health.current_gas_price} gwei')
"

# Solutions:
# 1. Increase gas price multiplier
# 2. Use backup RPC endpoints
# 3. Implement retry logic
# 4. Wait for network to stabilize
```

### Firewall Issues

**Error**: `Connection timeout`
```bash
# Test connectivity:
ping google.com
nslookup ethereum.org

# Check if ports are blocked:
telnet api.infura.io 443

# Solutions:
# 1. Configure firewall rules
# 2. Use VPN if necessary
# 3. Try different RPC endpoints
# 4. Check corporate proxy settings
```

## 🔧 Advanced Troubleshooting

### Debug Mode

Enable debug logging for detailed troubleshooting:
```bash
# Set debug mode in .env:
LOG_LEVEL=DEBUG
DEBUG=true

# Run with debug output:
python -m bot.sniper --debug

# Or run specific component with debug:
python -c "
import logging
logging.basicConfig(level=logging.DEBUG)
from bot.security import SecurityManager
from bot.config import Config
# Your debug code here
"
```

### Log Analysis

```bash
# View recent logs:
tail -f logs/sniper_bot.log

# Search for errors:
grep -i error logs/sniper_bot.log

# Search for specific issues:
grep -i "connection" logs/sniper_bot.log
grep -i "gas" logs/sniper_bot.log
grep -i "slippage" logs/sniper_bot.log
```

### System Resource Monitoring

```bash
# Monitor system resources:
python -c "
import psutil
import time

while True:
    cpu = psutil.cpu_percent()
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('.')
    
    print(f'CPU: {cpu}% | Memory: {memory.percent}% | Disk: {disk.percent}%')
    time.sleep(5)
"
```

## 📞 Getting Help

### Self-Help Resources

1. **Check Logs**: Always check logs first
2. **Run Diagnostics**: Use built-in health checks
3. **Test Components**: Test individual components
4. **Review Configuration**: Verify all settings

### Community Support

- 📖 **Documentation**: [GitHub Wiki](https://github.com/your-username/crypto-sniping-bot/wiki)
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/crypto-sniping-bot/discussions)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/crypto-sniping-bot/issues)

### Professional Support

For professional support:
- 📧 **Email**: support@yourproject.com
- 🔒 **Security Issues**: security@yourproject.com
- 💼 **Professional Support**: support@yourproject.com

## 📋 Troubleshooting Checklist

Before seeking help, please:

- [ ] Check system requirements (Python 3.8+)
- [ ] Verify all dependencies are installed
- [ ] Run comprehensive tests (`python test_clean.py`)
- [ ] Check configuration file for errors
- [ ] Review recent log files for errors
- [ ] Test individual components
- [ ] Try with minimal configuration
- [ ] Check network connectivity
- [ ] Verify wallet balance and permissions

## 🚨 Emergency Procedures

### Bot Won't Stop

```bash
# Find bot process:
ps aux | grep python

# Kill gracefully:
kill -TERM <process_id>

# Force kill if necessary:
kill -KILL <process_id>
```

### Funds at Risk

```bash
# Emergency stop all trading:
python -c "
from bot.sniper import SniperBot
from bot.config import Config
bot = SniperBot(Config())
await bot.emergency_stop()
"

# Move funds to safe wallet:
# (Manual transaction through wallet interface)
```

### Data Recovery

```bash
# Backup current data:
cp -r data/ backup_$(date +%Y%m%d_%H%M%S)/

# Restore from backup:
cp -r backup_YYYYMMDD_HHMMSS/ data/
```

---

**🚨 When in doubt, stop the bot and seek help. It's better to miss opportunities than risk funds.**
