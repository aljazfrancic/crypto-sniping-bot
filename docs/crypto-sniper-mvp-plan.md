# Crypto Sniper Bot MVP - Complete Implementation Plan

## MVP Scope Definition

### Core Features for MVP
1. **Smart Contract**: Simple sniper contract with buy/sell functionality
2. **Python Bot**: Event listener for PairCreated events and automated trading
3. **Basic Safety**: Honeypot detection and slippage protection
4. **Configuration**: Environment-based configuration
5. **Testing**: Comprehensive test suite

### Features to Exclude from MVP
- Forecasting/ML components (Phase 2)
- Multi-chain support (focus on one chain initially)
- Complex trading strategies
- UI/Dashboard
- Advanced analytics

## Project Structure

```
crypto-sniping-bot/
├── contracts/
│   ├── Sniper.sol              # Main sniper contract
│   └── interfaces/
│       ├── IUniswapV2Router.sol
│       └── IUniswapV2Pair.sol
├── bot/
│   ├── __init__.py
│   ├── sniper.py               # Main bot entry point
│   ├── blockchain.py           # Web3 interaction layer
│   ├── trading.py              # Trading logic
│   ├── honeypot.py             # Honeypot detection
│   └── config.py               # Configuration management
├── tests/
│   ├── test_contracts.js       # Solidity tests
│   └── test_bot.py             # Python tests
├── scripts/
│   ├── deploy.js               # Contract deployment
│   └── demo.sh                 # Demo script
├── .env.example
├── hardhat.config.js
├── package.json
├── requirements.txt
├── docker-compose.yml
└── README.md
```

## Implementation Details

### 1. Smart Contract (contracts/Sniper.sol)

```solidity
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "./interfaces/IUniswapV2Router.sol";
import "./interfaces/IUniswapV2Pair.sol";

contract Sniper is Ownable, ReentrancyGuard {
    IUniswapV2Router02 public immutable router;
    address public immutable WETH;
    
    uint256 public maxSlippage = 500; // 5%
    uint256 public deadline = 300; // 5 minutes
    
    event TokenBought(address token, uint256 amountIn, uint256 amountOut);
    event TokenSold(address token, uint256 amountIn, uint256 amountOut);
    
    constructor(address _router) {
        router = IUniswapV2Router02(_router);
        WETH = router.WETH();
    }
    
    function buyToken(
        address token,
        uint256 amountOutMin
    ) external payable onlyOwner nonReentrant {
        require(msg.value > 0, "No ETH sent");
        
        address[] memory path = new address[](2);
        path[0] = WETH;
        path[1] = token;
        
        uint256[] memory amounts = router.swapExactETHForTokens{value: msg.value}(
            amountOutMin,
            path,
            address(this),
            block.timestamp + deadline
        );
        
        emit TokenBought(token, msg.value, amounts[1]);
    }
    
    function sellToken(
        address token,
        uint256 amountIn,
        uint256 amountOutMin
    ) external onlyOwner nonReentrant {
        IERC20(token).approve(address(router), amountIn);
        
        address[] memory path = new address[](2);
        path[0] = token;
        path[1] = WETH;
        
        uint256[] memory amounts = router.swapExactTokensForETH(
            amountIn,
            amountOutMin,
            path,
            address(this),
            block.timestamp + deadline
        );
        
        emit TokenSold(token, amountIn, amounts[1]);
    }
    
    function withdrawETH() external onlyOwner {
        payable(owner()).transfer(address(this).balance);
    }
    
    function withdrawToken(address token) external onlyOwner {
        uint256 balance = IERC20(token).balanceOf(address(this));
        IERC20(token).transfer(owner(), balance);
    }
    
    receive() external payable {}
}
```

### 2. Python Bot Core (bot/sniper.py)

```python
#!/usr/bin/env python3
import asyncio
import logging
from web3 import Web3
from web3.middleware import geth_poa_middleware
import json
from config import Config
from blockchain import BlockchainInterface
from trading import TradingEngine
from honeypot import HoneypotChecker

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SniperBot:
    def __init__(self, config: Config):
        self.config = config
        self.w3 = self._setup_web3()
        self.blockchain = BlockchainInterface(self.w3, config)
        self.trading = TradingEngine(self.blockchain, config)
        self.honeypot_checker = HoneypotChecker(self.w3)
        self.positions = {}
        
    def _setup_web3(self):
        if self.config.RPC_URL.startswith('ws'):
            provider = Web3.WebsocketProvider(self.config.RPC_URL)
        else:
            provider = Web3.HTTPProvider(self.config.RPC_URL)
            
        w3 = Web3(provider)
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)
        return w3
        
    async def listen_for_pairs(self):
        """Listen for PairCreated events"""
        factory_abi = self._load_abi('UniswapV2Factory.json')
        factory = self.w3.eth.contract(
            address=self.config.FACTORY_ADDRESS,
            abi=factory_abi
        )
        
        event_filter = factory.events.PairCreated.create_filter(
            fromBlock='latest'
        )
        
        logger.info("Listening for new pairs...")
        
        while True:
            try:
                for event in event_filter.get_new_entries():
                    await self._handle_new_pair(event)
                await asyncio.sleep(1)
            except Exception as e:
                logger.error(f"Error in event loop: {e}")
                await asyncio.sleep(5)
                
    async def _handle_new_pair(self, event):
        """Handle new pair creation event"""
        token0 = event['args']['token0']
        token1 = event['args']['token1']
        pair = event['args']['pair']
        
        # Determine which token is not WETH
        weth = self.config.WETH_ADDRESS
        target_token = token0 if token1.lower() == weth.lower() else token1
        
        logger.info(f"New pair detected: {pair}")
        logger.info(f"Target token: {target_token}")
        
        # Check if token is safe
        if await self._is_token_safe(target_token):
            await self._execute_buy(target_token)
        else:
            logger.warning(f"Token {target_token} failed safety checks")
            
    async def _is_token_safe(self, token_address):
        """Perform safety checks on token"""
        try:
            # Basic honeypot check
            is_honeypot = await self.honeypot_checker.check(token_address)
            if is_honeypot:
                logger.warning(f"Token {token_address} detected as honeypot")
                return False
                
            # Additional checks can be added here
            # - Liquidity check
            # - Contract verification
            # - Ownership check
            
            return True
        except Exception as e:
            logger.error(f"Error checking token safety: {e}")
            return False
            
    async def _execute_buy(self, token_address):
        """Execute buy transaction"""
        try:
            tx_hash = await self.trading.buy_token(
                token_address,
                self.config.BUY_AMOUNT
            )
            
            if tx_hash:
                logger.info(f"Buy transaction sent: {tx_hash}")
                self.positions[token_address] = {
                    'buy_tx': tx_hash,
                    'amount': self.config.BUY_AMOUNT,
                    'status': 'bought'
                }
                
                # Start monitoring for sell conditions
                asyncio.create_task(self._monitor_position(token_address))
        except Exception as e:
            logger.error(f"Error executing buy: {e}")
            
    async def _monitor_position(self, token_address):
        """Monitor position for sell conditions"""
        # Implement profit target and stop loss logic
        pass
        
    def _load_abi(self, filename):
        with open(f'abi/{filename}', 'r') as f:
            return json.load(f)
            
    async def run(self):
        """Main bot loop"""
        logger.info("Starting Sniper Bot...")
        await self.listen_for_pairs()

async def main():
    config = Config()
    bot = SniperBot(config)
    await bot.run()

if __name__ == "__main__":
    asyncio.run(main())
```

### 3. Configuration (bot/config.py)

```python
import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Network settings
    RPC_URL = os.getenv('RPC_URL', 'ws://localhost:8545')
    CHAIN_ID = int(os.getenv('CHAIN_ID', '1'))
    
    # Contract addresses
    ROUTER_ADDRESS = os.getenv('ROUTER_ADDRESS')
    FACTORY_ADDRESS = os.getenv('FACTORY_ADDRESS')
    WETH_ADDRESS = os.getenv('WETH_ADDRESS')
    SNIPER_CONTRACT = os.getenv('SNIPER_CONTRACT')
    
    # Wallet settings
    PRIVATE_KEY = os.getenv('PRIVATE_KEY')
    
    # Trading settings
    BUY_AMOUNT = float(os.getenv('BUY_AMOUNT', '0.1'))  # in ETH
    SLIPPAGE = float(os.getenv('SLIPPAGE', '5'))  # percentage
    GAS_PRICE_MULTIPLIER = float(os.getenv('GAS_PRICE_MULTIPLIER', '1.5'))
    
    # Sell settings
    PROFIT_TARGET = float(os.getenv('PROFIT_TARGET', '50'))  # percentage
    STOP_LOSS = float(os.getenv('STOP_LOSS', '10'))  # percentage
    AUTO_SELL = os.getenv('AUTO_SELL', 'true').lower() == 'true'
    
    # Safety settings
    MIN_LIQUIDITY = float(os.getenv('MIN_LIQUIDITY', '5'))  # in ETH
    CHECK_HONEYPOT = os.getenv('CHECK_HONEYPOT', 'true').lower() == 'true'
```

### 4. Testing Suite (tests/test_contracts.js)

```javascript
const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("Sniper Contract", function () {
    let sniper, router, owner, addr1;
    
    beforeEach(async function () {
        [owner, addr1] = await ethers.getSigners();
        
        // Deploy mock router
        const MockRouter = await ethers.getContractFactory("MockUniswapV2Router");
        router = await MockRouter.deploy();
        
        // Deploy sniper
        const Sniper = await ethers.getContractFactory("Sniper");
        sniper = await Sniper.deploy(router.address);
    });
    
    describe("Buying tokens", function () {
        it("Should buy tokens with ETH", async function () {
            // Test implementation
        });
        
        it("Should revert if no ETH sent", async function () {
            await expect(
                sniper.buyToken(addr1.address, 0)
            ).to.be.revertedWith("No ETH sent");
        });
    });
    
    describe("Selling tokens", function () {
        it("Should sell tokens for ETH", async function () {
            // Test implementation
        });
    });
});
```

### 5. Environment Configuration (.env.example)

```env
# Network Configuration
RPC_URL=wss://eth-mainnet.g.alchemy.com/v2/YOUR_API_KEY
CHAIN_ID=1

# Contract Addresses (Ethereum Mainnet)
ROUTER_ADDRESS=0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
FACTORY_ADDRESS=0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f
WETH_ADDRESS=0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2

# Wallet Configuration
PRIVATE_KEY=your_private_key_here

# Trading Configuration
BUY_AMOUNT=0.1
SLIPPAGE=5
GAS_PRICE_MULTIPLIER=1.5

# Sell Configuration
PROFIT_TARGET=50
STOP_LOSS=10
AUTO_SELL=true

# Safety Configuration
MIN_LIQUIDITY=5
CHECK_HONEYPOT=true
```

### 6. Package.json

```json
{
  "name": "crypto-sniping-bot",
  "version": "1.0.0",
  "description": "Lightning-fast crypto sniping bot for DEX trading",
  "scripts": {
    "test": "hardhat test",
    "compile": "hardhat compile",
    "deploy": "hardhat run scripts/deploy.js",
    "node": "hardhat node",
    "lint": "eslint . --ext .js,.ts",
    "format": "prettier --write \"**/*.{js,ts,sol}\""
  },
  "dependencies": {
    "@openzeppelin/contracts": "^4.9.0",
    "dotenv": "^16.0.3",
    "ethers": "^5.7.2"
  },
  "devDependencies": {
    "@nomicfoundation/hardhat-toolbox": "^2.0.0",
    "chai": "^4.3.7",
    "eslint": "^8.40.0",
    "hardhat": "^2.14.0",
    "prettier": "^2.8.8",
    "prettier-plugin-solidity": "^1.1.3"
  }
}
```

### 7. Requirements.txt

```txt
web3==6.5.0
python-dotenv==1.0.0
asyncio==3.4.3
aiohttp==3.8.4
eth-account==0.9.0
eth-utils==2.1.0
requests==2.31.0
pytest==7.3.1
pytest-asyncio==0.21.0
black==23.3.0
flake8==6.0.0
```

## Next Steps

1. **Implement core components** following the structure above
2. **Write comprehensive tests** for both contracts and Python code
3. **Set up local development environment** with Hardhat
4. **Deploy to testnet** for integration testing
5. **Add monitoring and logging** for production readiness
6. **Security audit** before mainnet deployment

## Key Refactoring Points

1. **Separation of Concerns**: Each module has a single responsibility
2. **Configuration Management**: All settings in one place
3. **Error Handling**: Proper try-catch blocks and logging
4. **Async Architecture**: Non-blocking operations for performance
5. **Testing**: Comprehensive test coverage
6. **Security**: ReentrancyGuard, ownership controls, slippage protection

This MVP provides a solid foundation that can be extended with additional features once the core functionality is working reliably.