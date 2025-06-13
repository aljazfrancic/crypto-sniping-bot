# 🚀 Installation Guide

This guide will help you set up the Crypto Sniping Bot on your system.

## 📋 System Requirements

- Python 3.8 or higher
- Node.js 16 or higher
- Git
- 4GB RAM minimum
- Stable internet connection
- Windows 10/11, macOS, or Linux

## 🔧 Installation Steps

### 1. Clone Repository

```bash
git clone https://github.com/yourusername/crypto-sniping-bot.git
cd crypto-sniping-bot
```

### 2. Python Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Node.js Setup

```bash
# Install dependencies
npm install
```

### 4. Configuration

1. Create `.env` file:
```bash
cp .env.example .env
```

2. Edit `.env` with your settings:
```env
# Network
NETWORK=ethereum
RPC_URL=your-rpc-url
CHAIN_ID=1

# Wallet
PRIVATE_KEY=your-private-key
WALLET_ADDRESS=your-wallet-address

# Trading
MAX_SLIPPAGE=2.5
GAS_LIMIT=300000
MIN_LIQUIDITY=10

# Security
MEV_PROTECTION=true
HONEYPOT_DETECTION=true
SLIPPAGE_PROTECTION=true
```

## ✅ Verification

### 1. Check Installation

```bash
# Check Python version
python --version

# Check Node.js version
node --version

# Check dependencies
pip list
npm list
```

### 2. Run Tests

```bash
# Run Python tests
pytest

# Run JavaScript tests
npm test
```

## 🔒 Security Considerations

1. **Private Key Security**
   - Never share your private key
   - Use environment variables
   - Keep `.env` file secure
   - Don't commit sensitive data

2. **Network Security**
   - Use secure RPC endpoints
   - Enable HTTPS
   - Use VPN if needed
   - Monitor connections

3. **Trading Security**
   - Start with small amounts
   - Test on testnet first
   - Monitor transactions
   - Use security features

## 🚨 Common Issues

1. **Python Issues**
   - Virtual environment not activated
   - Missing dependencies
   - Version conflicts
   - Path issues

2. **Node.js Issues**
   - NPM errors
   - Version conflicts
   - Permission issues
   - Path issues

3. **Configuration Issues**
   - Invalid RPC URL
   - Wrong network
   - Invalid private key
   - Missing variables

## 📚 Additional Resources

- [Python Documentation](https://docs.python.org)
- [Node.js Documentation](https://nodejs.org/docs)
- [Web3.py Documentation](https://web3py.readthedocs.io)
- [Ethereum Documentation](https://ethereum.org/developers)

## 🆘 Need Help?

- Check [Troubleshooting Guide](troubleshooting.md)
- Join [Discord Community](https://discord.gg/your-server)
- Open [GitHub Issues](https://github.com/yourusername/crypto-sniping-bot/issues)
- Read [Documentation](https://docs.your-bot.com) 