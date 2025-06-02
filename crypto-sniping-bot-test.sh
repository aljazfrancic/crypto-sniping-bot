#!/bin/bash

# crypto-sniping-bot-test.sh
# Comprehensive test script for Crypto Sniping Bot

# Helper function for colored output
print_color() {
    local color=$1
    local msg=$2
    case $color in
        Cyan)   echo -e "\033[0;36m$msg\033[0m" ;;
        Green)  echo -e "\033[0;32m$msg\033[0m" ;;
        Red)    echo -e "\033[0;31m$msg\033[0m" ;;
        *)      echo "$msg" ;;
    esac
}

# 1. Environment Setup
print_color "Cyan" "[Setup] Setting up environment..."
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
pip install pytest web3  # ensure test deps (optional)

# 2. Generate Test Configuration
print_color "Cyan" "[Config] Creating test configuration..."
cat > .env << EOF
# Test configuration
BSC_NODE="wss://bsc-testnet.publicnode.com"
FLASH_SNIPER_ADDR="0x0000000000000000000000000000000000000000"
ENCRYPTION_KEY="test_encryption_key_12345"
PRIVATE_KEY="encrypted:gAAAAABmD8z5C5b5Q9X4Zz3Y2VqF7wE6lGjKpRtSxUvWnOyP3cBvR1aAeBcDdEfGhIjKlMn"
EOF

# 3. Contract Tests
print_color "Cyan" "[Contracts] Testing smart contracts..."

# Install Node.js dependencies if needed
if [ ! -d "node_modules" ]; then
    echo "Installing Node.js dependencies..."
    npm install -g truffle
    npm install @openzeppelin/contracts @truffle/hdwallet-provider
fi

# Run contract tests
truffle test --network bsc_testnet

# 4. Python Bot Tests
cd sniper-bot || exit

# Unit tests
print_color "Cyan" "Running unit tests..."
pytest ../unit

# Integration test
print_color "Cyan" "Running integration test..."
# Start bot in background
python sniping_bot.py > bot.log 2>&1 &
BOT_PID=$!

echo "Bot started in background (PID: $BOT_PID). Waiting 10 seconds..."
sleep 10

# Check if bot is running
if ps -p $BOT_PID > /dev/null; then
    print_color "Green" "[SUCCESS] Bot is running (PID: $BOT_PID)"
    kill $BOT_PID
else
    print_color "Red" "[FAIL] Bot failed to start"
    echo "Bot logs:"
    cat bot.log
fi

# 5. Security Checks
print_color "Cyan" "[Security] Running security checks..."

# Check for secrets in code
print_color "Cyan" "Scanning for exposed secrets..."
SECRETS_FOUND=$(grep -r -n -E "private_key|mnemonic|secret" ../*.py ../*.sol)
if [ -n "$SECRETS_FOUND" ]; then
    print_color "Red" "[FAIL] Potential secrets found in code:"
    echo "$SECRETS_FOUND"
else
    print_color "Green" "[SUCCESS] No secrets detected in code"
fi

# Run Slither security analysis
if command -v slither &> /dev/null; then
    echo "Running Slither security analysis..."
    slither ../contracts --exclude naming-convention
else
    echo "[WARNING] Slither not installed. Install with: pip install slither-analyzer"
fi

# 6. Performance Test
print_color "Cyan" "[Performance] Testing RPC latency..."
START_TIME=$(date +%s%3N)
python -c "from web3 import Web3; w3 = Web3(Web3.WebsocketProvider('wss://bsc-testnet.publicnode.com')); print('Connected:', w3.is_connected())" > /dev/null
END_TIME=$(date +%s%3N)
LATENCY=$((END_TIME - START_TIME))
echo "Blockchain connection latency: $LATENCY ms"

# 7. Cleanup
print_color "Cyan" "[Cleanup] Removing temporary files..."
cd ..
rm -f .env
rm -f sniper-bot/bot.log
deactivate

print_color "Green" "\nAll tests completed.\n"