# 📦 Installation Guide

This guide will walk you through setting up the Crypto Sniping Bot with all dependencies, configurations, and testing infrastructure.

## 🖥️ System Requirements

### Minimum Requirements
- **Python**: 3.8 or higher
- **Node.js**: 16.0 or higher
- **Memory**: 4GB RAM minimum, 8GB recommended
- **Storage**: 2GB free disk space
- **Network**: Stable internet connection

### Supported Operating Systems
- ✅ Windows 10/11
- ✅ macOS 10.15+
- ✅ Ubuntu 18.04+
- ✅ Debian 10+
- ✅ CentOS 7+

## 🚀 Quick Installation (Recommended)

### Option 1: Automated Setup
```bash
# Clone the repository
git clone https://github.com/aljazfrancic/crypto-sniping-bot.git
cd crypto-sniping-bot

# Run automated setup (installs everything)
python tests/scripts/setup_tests.py

# Verify installation
python run_tests.py
```

The automated setup script will:
- ✅ Verify Python version compatibility
- ✅ Install all required Python packages
- ✅ Create necessary directories and files
- ✅ Set up ABI files for smart contracts
- ✅ Configure testing environment
- ✅ Create safe test configuration

### Option 2: Manual Installation

#### 1. Clone Repository
```bash
git clone https://github.com/aljazfrancic/crypto-sniping-bot.git
cd crypto-sniping-bot
```

#### 2. Create Virtual Environment (Recommended)
```bash
# Create virtual environment
python -m venv .venv

# Activate virtual environment
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
```

#### 3. Install Python Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Install Node.js Dependencies
```bash
npm install
```

#### 5. Setup Configuration
```bash
# Copy production config template
cp production.config.env .env

# Copy test config for development/testing
cp tests/config/test.config.env test.env

# Or use safe test config (recommended for development)
cp tests/config/test_safe.config.env .env
```

## 🔧 Configuration Setup

### 1. Environment Configuration

Edit your `.env` file with your settings:

```env
# === BLOCKCHAIN SETTINGS ===
RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID
BACKUP_RPC_URLS=https://eth.llamarpc.com,https://rpc.ankr.com/eth
CHAIN_ID=1
PRIVATE_KEY=your_actual_private_key_here
WALLET_ADDRESS=0xYourWalletAddress

# === TRADING PARAMETERS ===
MIN_LIQUIDITY_ETH=1.0
MAX_GAS_PRICE=100
SLIPPAGE_TOLERANCE=5.0
MAX_TRADE_AMOUNT=1.0
TRADE_AMOUNT_ETH=0.1

# === SECURITY SETTINGS ===
ENABLE_MEV_PROTECTION=true
HONEYPOT_CHECK_ENABLED=true
CHECK_LIQUIDITY_LOCKS=true
VERIFY_CONTRACT_SOURCE=true

# === PERFORMANCE SETTINGS ===
MAX_RPC_CALLS_PER_SECOND=10
MAX_CONCURRENT_TRADES=3
CONNECTION_TIMEOUT=30
REQUEST_TIMEOUT=15

# === MONITORING & ALERTS ===
WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
DATABASE_URL=sqlite:///sniper_data.db
LOG_LEVEL=INFO
ENABLE_PERFORMANCE_MONITORING=true
```

### 2. Smart Contract Deployment (Optional)

For enhanced features, deploy the smart contracts:

```bash
# Compile contracts
npx hardhat compile

# Deploy to mainnet (requires ETH for gas)
npx hardhat run scripts/deploy.js --network mainnet

# Or deploy to testnet first
npx hardhat run scripts/deploy.js --network sepolia
```

### 3. Verify Installation

```bash
# Run all 72 tests
python run_tests.py

# Run with coverage report (48% coverage)
python run_tests.py --coverage

# Run specific test categories
python -m pytest tests/unit/ -v        # Unit tests
python -m pytest tests/integration/ -v # Integration tests
```

## 🛠️ Development Setup

### IDE Setup

#### VS Code (Recommended)
Install these extensions:
- Python
- Pylance
- Black Formatter
- MyPy Type Checker

#### PyCharm
Configure:
- Python interpreter: `./venv/bin/python`
- Code formatter: Black
- Type checker: MyPy

### Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

### Code Quality Tools
```bash
# Format code
black bot/ tests/

# Type checking
mypy bot/

# Linting
pylint bot/

# Security scan
bandit -r bot/
```

## 🧪 Testing Infrastructure

### Test Structure

The bot includes 72 comprehensive tests organized by category:

```
tests/
├── unit/              # Unit tests (33 tests)
│   ├── test_exceptions.py
│   └── test_security.py  
├── integration/       # Integration tests (39 tests)
│   ├── test_sniper.py
│   ├── test_clean.py
│   └── test_improvements.py
├── config/           # Test configurations
│   ├── test.config.env
│   └── test_safe.config.env
└── scripts/          # Test utilities
    ├── run_tests.py
    └── setup_tests.py
```

### Running Tests

#### 1. All Tests
```bash
# Run all 72 tests
python run_tests.py

# With coverage report (48% coverage)
python run_tests.py --coverage
```

#### 2. Specific Categories
```bash
# Unit tests only
python -m pytest tests/unit/ -v

# Integration tests only 
python -m pytest tests/integration/ -v

# Specific test file
python -m pytest tests/unit/test_security.py -v
```

#### 3. Test Configuration
```bash
# Set up test environment
cp tests/config/test.config.env .env

# Verify test setup
python -c "import os; print('RPC_URL:', os.getenv('RPC_URL', 'Not set'))"
```

## 🔒 Security Setup

### Private Key Security

**⚠️ NEVER commit private keys to version control!**

```bash
# Use environment variables
export PRIVATE_KEY="your_private_key_here"

# Or use .env file (add to .gitignore)
echo "PRIVATE_KEY=your_private_key_here" >> .env
```

### Test Key Protection

The bot includes automatic detection of dangerous test keys:
- Common test private keys are rejected
- Prevents accidental use of example keys
- Validates key format and checksum

### Network Security

```env
# Use secure RPC endpoints
RPC_URL=https://mainnet.infura.io/v3/YOUR_PROJECT_ID

# Configure backup endpoints
BACKUP_RPC_URLS=https://eth.llamarpc.com,https://rpc.ankr.com/eth

# Enable SSL verification
VERIFY_SSL=true
```

## 📊 Database Setup

### SQLite (Default)
No additional setup required. Database file is created automatically.

### PostgreSQL (Production)
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database
sudo -u postgres createdb sniper_bot

# Update configuration
DATABASE_URL=postgresql://user:password@localhost/sniper_bot
```

### MySQL
```bash
# Install MySQL
sudo apt-get install mysql-server

# Create database
mysql -u root -p -e "CREATE DATABASE sniper_bot;"

# Update configuration
DATABASE_URL=mysql://user:password@localhost/sniper_bot
```

## 🔔 Notification Setup

### Slack Integration
1. Create a Slack app at https://api.slack.com/apps
2. Enable Incoming Webhooks
3. Copy webhook URL to configuration:
```env
WEBHOOK_URL=https://hooks.slack.com/services/T00000000/B00000000/XXXXXXXXXXXXXXXXXXXXXXXX
```

### Discord Integration
1. Create a Discord webhook in your server
2. Copy webhook URL:
```env
WEBHOOK_URL=https://discord.com/api/webhooks/000000000000000000/xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

### Custom Webhooks
```env
WEBHOOK_URL=https://your-custom-endpoint.com/webhook
WEBHOOK_AUTH_TOKEN=your_auth_token_here
```

## 🚨 Troubleshooting

### Common Issues

#### Python Version Error
```bash
# Check Python version
python --version

# Install Python 3.8+ if needed
# Ubuntu/Debian:
sudo apt-get install python3.8 python3.8-venv python3.8-dev

# Windows: Download from python.org
# macOS: brew install python@3.8
```

#### Package Installation Errors
```bash
# Update pip
python -m pip install --upgrade pip

# Install build tools
# Ubuntu/Debian:
sudo apt-get install build-essential python3-dev

# Windows: Install Visual Studio Build Tools
# macOS: xcode-select --install
```

#### RPC Connection Issues
```bash
# Test RPC connection
python -c "from web3 import Web3; w3 = Web3(Web3.HTTPProvider('YOUR_RPC_URL')); print('Connected:', w3.is_connected())"

# Check firewall settings
# Verify API key/project ID
# Try different RPC endpoint
```

#### Smart Contract Compilation Errors
```bash
# Clear cache
npx hardhat clean

# Reinstall dependencies
rm -rf node_modules package-lock.json
npm install

# Update Hardhat
npm install --save-dev hardhat@latest
```

### Getting Help

- 📖 **Documentation**: Check [troubleshooting.md](troubleshooting.md)
- 🐛 **Issues**: Report bugs on [GitHub Issues](https://github.com/aljazfrancic/crypto-sniping-bot/issues)

## ✅ Verification Checklist

After installation, verify everything is working:

- [ ] Python 3.8+ installed and accessible
- [ ] Virtual environment created and activated
- [ ] All Python dependencies installed (`pip list`)
- [ ] Node.js dependencies installed (`npm list`)
- [ ] Configuration files created (`.env`)
- [ ] ABI files generated (`ls abis/`)
- [ ] Database connection working
- [ ] RPC endpoint accessible
- [ ] All tests passing (`python test_clean.py`)
- [ ] Bot can start (`python -m bot.sniper --help`)

## 🚀 Next Steps

Once installation is complete:

1. **Configure Trading Parameters**: Edit your `.env` file
2. **Test on Testnet**: Use testnet configuration first
3. **Run Security Tests**: Ensure all security features work
4. **Start with Small Amounts**: Begin with minimal trade sizes
5. **Monitor Performance**: Check logs and analytics
6. **Set up Alerts**: Configure webhook notifications

---

**🎉 Congratulations! Your Crypto Sniping Bot is ready to use.**

For usage instructions, see the [Tutorial](tutorial.md) and [Configuration Guide](configuration.md).
