# 🧪 Testnet Deployment Guide

This comprehensive guide covers deploying and testing the crypto sniping bot on various testnets. Includes advanced testing procedures, security validation, and performance benchmarking. Testing on testnet is crucial before mainnet deployment to ensure all components work correctly without risking real funds.

## 📋 Prerequisites

Before deploying on testnet, ensure you have:

1. **Test Environment Passing**: All local tests should pass
   ```bash
   npm run test:all
   ```

2. **Required Accounts**: Test accounts with testnet tokens
3. **Environment Configuration**: Properly configured `.env` file
4. **Network Access**: RPC endpoints for your chosen testnet

## 🌐 Supported Testnets

### BSC Testnet (Recommended)
- **Chain ID**: 97
- **Native Token**: tBNB
- **Block Explorer**: https://testnet.bscscan.com
- **Faucet**: https://testnet.binance.org/faucet-smart

### Ethereum Sepolia
- **Chain ID**: 11155111
- **Native Token**: SepoliaETH
- **Block Explorer**: https://sepolia.etherscan.io
- **Faucet**: https://sepoliafaucet.com

### Polygon Mumbai
- **Chain ID**: 80001
- **Native Token**: MATIC
- **Block Explorer**: https://mumbai.polygonscan.com
- **Faucet**: https://faucet.polygon.technology

## 🛠️ Step 1: Environment Setup

### 1.1 Create Testnet Configuration

Create a separate `.env.testnet` file for testnet deployment:

```env
# Testnet Environment Configuration
# BSC Testnet Example

# Network Configuration
RPC_URL=https://data-seed-prebsc-1-s1.binance.org:8545
CHAIN_ID=97
PRIVATE_KEY=your_testnet_private_key_here

# Contract Addresses (BSC Testnet)
ROUTER_ADDRESS=0xD99D1c33F9fC3444f8101754aBC46c52416550D1  # PancakeSwap Testnet Router
FACTORY_ADDRESS=0x6725F303b657a9451d8BA641348b6761A6CC7a17  # PancakeSwap Testnet Factory
WETH_ADDRESS=0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd   # WBNB Testnet

# Trading Configuration (Conservative for Testing)
BUY_AMOUNT=0.01          # Small amount for testing
SLIPPAGE=10.0            # Higher slippage for testnet
PROFIT_TARGET=50.0       # Higher target for testing
STOP_LOSS=20.0           # Higher stop loss for testing
MIN_LIQUIDITY=0.1        # Lower minimum for testnet
GAS_PRICE_MULTIPLIER=1.5 # Higher multiplier for faster execution

# Security Configuration
CHECK_HONEYPOT=true
AUTO_SELL=false          # Manual selling for testing
WAIT_FOR_CONFIRMATION=true

# Monitoring Configuration
LOG_LEVEL=DEBUG          # Verbose logging for testing
ENABLE_MONITORING=true
```

### 1.2 Update Hardhat Configuration

Ensure your `hardhat.config.js` includes the testnet:

```javascript
// Add to networks section if not present
sepolia: {
  url: process.env.ETHEREUM_RPC || "https://rpc.sepolia.org",
  accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
  chainId: 11155111,
},
mumbai: {
  url: process.env.POLYGON_RPC || "https://rpc-mumbai.maticvigil.com",
  accounts: process.env.PRIVATE_KEY ? [process.env.PRIVATE_KEY] : [],
  chainId: 80001,
}
```

## 💰 Step 2: Get Testnet Tokens

### 2.1 Fund Your Test Wallet

Get native tokens for gas fees:

**BSC Testnet (tBNB)**:
1. Visit https://testnet.binance.org/faucet-smart
2. Enter your wallet address
3. Request tBNB tokens

**Ethereum Sepolia (SepoliaETH)**:
1. Visit https://sepoliafaucet.com
2. Enter your wallet address
3. Complete any required tasks

**Polygon Mumbai (MATIC)**:
1. Visit https://faucet.polygon.technology
2. Select Mumbai network
3. Enter your wallet address

### 2.2 Verify Token Balance

Check your balance before proceeding:

```bash
# Using cast (foundry)
cast balance YOUR_ADDRESS --rpc-url YOUR_TESTNET_RPC

# Using hardhat console
npx hardhat console --network bscTestnet
# Then: (await ethers.provider.getBalance("YOUR_ADDRESS")).toString()
```

## 🚀 Step 3: Deploy Smart Contracts

### 3.1 Deploy to BSC Testnet

```bash
# Set environment variables
export $(cat .env.testnet | xargs)

# Deploy smart contracts
npm run deploy:bscTestnet
```

### 3.2 Deploy to Other Testnets

```bash
# Ethereum Sepolia
npm run deploy:sepolia

# Polygon Mumbai
npm run deploy:mumbai
```

### 3.3 Verify Deployment

After deployment, you should see output similar to:

```
✅ Sniper deployed to: 0x1234567890123456789012345678901234567890
Router: 0xD99D1c33F9fC3444f8101754aBC46c52416550D1
WETH: 0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd
Owner: 0xYourAddress
```

**Important**: Add the contract address to your `.env.testnet`:
```env
SNIPER_CONTRACT=0x1234567890123456789012345678901234567890
```

## 🧪 Step 4: Testing Strategy

### 4.1 Create Test Tokens

For comprehensive testing, create test tokens:

```bash
# Deploy test tokens (optional)
npx hardhat run scripts/deploy-test-tokens.js --network bscTestnet
```

### 4.2 Test Scenarios

#### Basic Functionality Test
1. **Bot Initialization**
   ```bash
   # Use testnet configuration
   cp .env.testnet .env
   python bot/sniper.py --dry-run
   ```

2. **Security Checks**
   - Honeypot detection on known scam tokens
   - Liquidity verification
   - Price manipulation detection

3. **Trading Functions**
   - Monitor new pairs
   - Execute test buys (small amounts)
   - Verify sell functionality

#### Advanced Testing
1. **MEV Protection**
   - Test front-running protection
   - Verify EIP-1559 transaction handling

2. **Gas Optimization**
   - Monitor gas usage patterns
   - Test different gas multipliers

3. **Error Handling**
   - Test with insufficient balance
   - Test with failed transactions
   - Test network connectivity issues

### 4.3 Monitoring and Logging

Enable comprehensive logging during testing:

```bash
# Set debug logging
export LOG_LEVEL=DEBUG

# Run with monitoring
python bot/sniper.py --monitor --testnet
```

## 📊 Step 5: Performance Testing

### 5.1 Speed Tests

Test transaction execution speed:

```python
# Example speed test
import time
from bot.trading import TradingEngine

start_time = time.time()
# Execute test transaction
execution_time = time.time() - start_time
print(f"Transaction execution time: {execution_time:.2f}s")
```

### 5.2 Reliability Tests

Run extended testing sessions:

```bash
# 24-hour test run (monitor mode)
timeout 86400 python bot/sniper.py --testnet --monitor-only
```

### 5.3 Load Testing

Test with high-frequency trading:

```bash
# Simulate high-frequency environment
python tests/load_test.py --network testnet --duration 3600
```

## 🔍 Step 6: Verification and Validation

### 6.1 Transaction Verification

Check all transactions on the block explorer:

```bash
# Example: Check transaction on BSC Testnet
echo "https://testnet.bscscan.com/tx/YOUR_TX_HASH"
```

### 6.2 Contract Verification

Verify your contract on the block explorer:

```bash
# BSC Testnet verification
npx hardhat verify --network bscTestnet DEPLOYED_CONTRACT_ADDRESS \
  "0xD99D1c33F9fC3444f8101754aBC46c52416550D1" \
  "0x6725F303b657a9451d8BA641348b6761A6CC7a17" \
  "0xae13d989daC2f0dEbFf460aC112a837C89BAa7cd"
```

### 6.3 Security Audit

Run security checks on testnet:

```bash
# Check for common vulnerabilities
python -m bot.security --audit --testnet

# Verify honeypot detection
python -m bot.honeypot --test-known-scams --testnet
```

## 📈 Step 7: Performance Metrics

### 7.1 Key Metrics to Track

- **Transaction Success Rate**: >95%
- **Average Execution Time**: <3 seconds
- **Gas Efficiency**: Within expected ranges
- **Security Detection Rate**: 100% for known threats
- **Uptime**: >99% during testing period

### 7.2 Monitoring Dashboard

Create a simple monitoring setup:

```bash
# Start monitoring dashboard
python bot/monitoring.py --dashboard --testnet
```

## 🚨 Common Issues and Solutions

### Issue: Insufficient Gas
```
Error: insufficient funds for gas * price + value
```
**Solution**: Increase gas price multiplier or get more testnet tokens

### Issue: Nonce Too Low
```
Error: nonce too low
```
**Solution**: Reset account nonce or wait for pending transactions

### Issue: Contract Not Verified
```
Error: Contract source code not verified
```
**Solution**: Manual verification on block explorer

### Issue: RPC Timeout
```
Error: request timeout
```
**Solution**: Switch to alternative RPC endpoint or increase timeout

## ✅ Testnet Checklist

Before moving to mainnet, ensure:

- [ ] All local tests pass
- [ ] Smart contracts deployed successfully
- [ ] Contract verified on block explorer
- [ ] Bot connects to testnet correctly
- [ ] Security features working (honeypot detection, etc.)
- [ ] Trading functions execute properly
- [ ] Gas optimization working
- [ ] Error handling functioning
- [ ] Monitoring system operational
- [ ] Performance metrics within acceptable ranges
- [ ] 24-hour stability test completed
- [ ] All team members tested the setup

## 🔄 Next Steps

After successful testnet deployment:

1. **Document Lessons Learned**: Update configurations based on testing
2. **Optimize Parameters**: Fine-tune based on testnet performance
3. **Security Review**: Final security audit
4. **Mainnet Preparation**: Prepare mainnet deployment configurations
5. **Go-Live Planning**: Plan mainnet deployment timing and monitoring

## ⚠️ Important Reminders

- **Never use mainnet private keys** on testnet
- **Always use small amounts** for testing
- **Test all features thoroughly** before mainnet
- **Monitor gas costs** and optimize accordingly
- **Document all issues** encountered and solutions
- **Test fail-safe mechanisms** like emergency stops
- **Verify all contract addresses** before trading

---

**Happy Testing! 🚀**

Remember: Thorough testnet testing prevents mainnet disasters. Take your time and test every feature comprehensively. 