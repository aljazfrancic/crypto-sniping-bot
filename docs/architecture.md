# Architecture Documentation

## System Overview

The Crypto Sniping Bot is a high-performance automated trading system designed to monitor and trade newly created liquidity pools on decentralized exchanges (DEXes). The system combines smart contracts for secure trading with a Python-based monitoring and execution engine.

## Architecture Diagram

```mermaid
graph TD
    A[Python Bot] --> B[Blockchain Interface]
    A --> C[Trading Engine]
    A --> D[Honeypot Detector]
    A --> E[Configuration]
    A --> F[Monitoring]
    
    B --> G[Ethereum Network]
    C --> G
    D --> G
    
    C --> H[Sniper Contract]
    H --> G

    subgraph "Safety Layer"
        D --> I[Contract Analysis]
        D --> J[Liquidity Check]
        D --> K[Blacklist Check]
    end

    subgraph "Trading Layer"
        C --> L[Position Management]
        C --> M[Slippage Control]
        C --> N[Gas Optimization]
    end

    subgraph "Monitoring Layer"
        F --> O[Trade Logging]
        F --> P[Performance Metrics]
        F --> Q[Backup Management]
    end
```

## Core Components

### 1. Smart Contracts (`contracts/`)

#### Sniper Contract (`Sniper.sol`)
- Handles token buying and selling operations
- Implements safety checks and slippage protection
- Manages token blacklisting
- Controls withdrawals and emergency functions

#### Mock Contracts (`mocks/`)
- `MockWETH.sol`: Wrapped ETH implementation
- `MockERC20.sol`: ERC20 token implementation
- `MockUniswapV2Pair.sol`: DEX pair simulation
- `MockUniswapV2Factory.sol`: DEX factory simulation
- `MockUniswapV2Router.sol`: DEX router simulation

### 2. Python Bot (`bot/`)

#### Blockchain Interface (`blockchain.py`)
- Manages blockchain interactions
- Handles RPC communication
- Provides token and balance queries
- Manages transaction signing and sending

#### Trading Engine (`trading.py`)
- Executes buy/sell operations
- Manages position tracking
- Implements trading strategies
- Handles slippage calculations

#### Honeypot Detection (`honeypot.py`)
- Analyzes token contracts
- Checks for malicious functions
- Verifies token liquidity
- Implements blacklist checking

#### Configuration (`config.py`)
- Manages environment variables
- Validates configuration settings
- Provides network-specific parameters
- Handles private key management

#### Monitoring (`monitoring.py`)
- Logs trading activities
- Tracks performance metrics
- Manages backups
- Provides real-time statistics

## Data Flow

1. **Event Monitoring**
   - Bot monitors blockchain for new liquidity pools
   - Filters events based on configured criteria
   - Identifies potential trading opportunities

2. **Safety Checks**
   - Analyzes token contract code
   - Verifies liquidity levels
   - Checks for honeypot characteristics
   - Validates slippage parameters

3. **Trade Execution**
   - Calculates optimal trade parameters
   - Executes buy transaction via Sniper contract
   - Monitors transaction status
   - Updates position tracking

4. **Position Management**
   - Tracks token balances
   - Monitors price movements
   - Executes take-profit/stop-loss
   - Manages emergency sells

## Security Features

### Smart Contract Security
- Reentrancy protection
- Access control
- Slippage limits
- Emergency functions
- Blacklist management

### Bot Security
- Private key protection
- Transaction validation
- Honeypot detection
- Liquidity verification
- Slippage protection

## Network Support

### Supported Networks

| Network | Chain ID | Router Address | Factory Address | WETH Address |
|---------|----------|----------------|-----------------|--------------|
| Ethereum | 1 | 0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D | 0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f | 0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2 |
| BSC | 56 | 0x10ED43C718714eb63d5aA57B78B54704E256024E | 0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73 | 0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c |
| Polygon | 137 | 0xa5E0829CaCEd8fFDD4De3c43696c57F7D7A678ff | 0x5757371414417b8C6CAad45bAeF941aBc7d3Ab32 | 0x0d500B1d8E8eF31E21C99d1Db9A6444d3ADf1270 |

### Network-Specific Parameters

#### Gas Price Strategies
- Ethereum: Dynamic gas price with EIP-1559 support
- BSC: Fixed gas price with multiplier
- Polygon: Priority fee based on network congestion

#### RPC Requirements
- WebSocket connection for real-time events
- HTTP endpoint for transactions
- Backup RPC providers recommended

#### Network Limitations
- Ethereum: Higher gas costs, slower block time
- BSC: Lower gas costs, faster block time
- Polygon: Lowest gas costs, fastest block time

## Performance Considerations

### Optimization Techniques
- Efficient event filtering
- Batch transaction processing
- Gas price optimization
- Caching mechanisms
- Parallel processing

### Resource Management
- Memory usage optimization
- Connection pooling
- Error handling
- Rate limiting
- Backup strategies

## Monitoring and Maintenance

### Logging
- Transaction logs
- Error tracking
- Performance metrics
- Position updates
- System health

### Backup and Recovery
- Configuration backups
- Position state backups
- Recovery procedures
- Data consistency checks

## Development Guidelines

### Code Organization
- Modular architecture
- Clear separation of concerns
- Consistent naming conventions
- Comprehensive documentation
- Type hints and validation

### Testing Strategy
- Unit tests
- Integration tests
- Contract tests
- Performance tests
- Security audits

## Deployment Architecture

### Requirements
- Node.js environment
- Python environment
- RPC endpoint
- Funded wallet
- Storage for logs and backups

### Deployment Process
1. Contract deployment
2. Configuration setup
3. Environment preparation
4. Bot initialization
5. Monitoring setup

## Future Considerations

### Scalability
- Multi-chain support
- Advanced trading strategies
- Enhanced monitoring
- Performance optimization
- Additional safety features

### Integration
- External APIs
- Price feeds
- Trading signals
- Analytics platforms
- Alert systems 