#!/bin/bash

# Crypto Sniper Bot Demo Script
# This script demonstrates the bot setup and execution
# Make executable with: chmod +x scripts/demo.sh

set -e  # Exit on error

echo "🚀 Crypto Sniper Bot Demo"
echo "========================"
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js v16+"
    exit 1
fi
echo "✅ Node.js: $(node --version)"

# Check Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 not found. Please install Python 3.8+"
    exit 1
fi
echo "✅ Python: $(python3 --version)"

# Check if .env exists
if [ ! -f .env ]; then
    echo ""
    echo "⚠️  No .env file found. Creating from template..."
    cp .env.example .env
    echo "✅ Created .env file"
    echo ""
    echo "⚡ Please edit .env with your configuration:"
    echo "   - Add your RPC_URL"
    echo "   - Add your PRIVATE_KEY"
    echo "   - Configure your preferred network"
    echo ""
    echo "Then run this script again."
    exit 1
fi

# Install dependencies
echo ""
echo "📦 Installing dependencies..."

# Node dependencies
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install
else
    echo "✅ Node.js dependencies already installed"
fi

# Python virtual environment
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate || source venv/Scripts/activate

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt --quiet

echo ""
echo "🔨 Compiling smart contracts..."
npx hardhat compile

echo ""
echo "🧪 Running tests..."
echo "Running Solidity tests..."
npx hardhat test

echo ""
echo "Running Python tests..."
pytest tests/test_bot.py -v

# Check if contract is deployed
source .env
if [ -z "$SNIPER_CONTRACT" ]; then
    echo ""
    echo "📝 No sniper contract deployed yet."
    echo ""
    echo "To deploy the contract, run:"
    echo "  npx hardhat run scripts/deploy.js --network <network>"
    echo ""
    echo "Available networks:"
    echo "  - localhost (local node)"
    echo "  - goerli (Ethereum testnet)"
    echo "  - bscTestnet (BSC testnet)"
    echo "  - mumbai (Polygon testnet)"
    echo ""
    echo "After deployment, add the contract address to your .env file."
    exit 0
fi

echo ""
echo "✅ All checks passed!"
echo ""
echo "🎯 Ready to run the bot!"
echo ""
echo "To start the bot, run:"
echo "  python bot/sniper.py"
echo ""
echo "⚠️  Safety reminders:"
echo "  - Always test on testnet first"
echo "  - Start with small amounts"
echo "  - Monitor the bot actively"
echo "  - Never share your private key"
echo ""
echo "Good luck and happy sniping! 🎯"