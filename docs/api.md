# 📖 API Reference

Comprehensive API documentation for the Crypto Sniping Bot enterprise edition. This guide covers all modules, classes, and methods available in the bot.

## 🎯 Overview

The bot is organized into several key modules:

- **[Core Bot](#-core-bot-api)**: Main bot orchestration
- **[Blockchain Interface](#-blockchain-interface-api)**: Blockchain interactions
- **[Trading Engine](#-trading-engine-api)**: Trade execution
- **[Security Module](#-security-module-api)**: Security and risk management
- **[Analytics Engine](#-analytics-engine-api)**: Performance tracking
- **[Utilities](#-utilities-api)**: Production-ready utilities
- **[Configuration](#-configuration-api)**: Configuration management
- **[Notifications](#-notifications-api)**: Alert and notification system

## 🤖 Core Bot API

### `SniperBot`

Main bot orchestrator class that coordinates all trading operations.

#### Constructor

```python
class SniperBot:
    def __init__(self, config: Config) -> None:
        """
        Initialize the sniping bot with configuration.
        
        Args:
            config: Bot configuration object
        """
```

#### Methods

##### `start() -> None`
```python
async def start(self) -> None:
    """
    Start the sniping bot and begin monitoring for opportunities.
    
    Raises:
        SniperBotError: If bot fails to start
        ConfigurationError: If configuration is invalid
    """
```

##### `stop() -> None`
```python
async def stop(self) -> None:
    """
    Gracefully stop the bot and cleanup resources.
    """
```

##### `get_status() -> BotStatus`
```python
def get_status(self) -> BotStatus:
    """
    Get current bot status and metrics.
    
    Returns:
        BotStatus: Current status including health, active trades, performance
    """
```

#### Example Usage

```python
from bot.sniper import SniperBot
from bot.config import Config

config = Config()
bot = SniperBot(config)

# Start the bot
await bot.start()

# Check status
status = bot.get_status()
print(f"Bot is {status.state}, active trades: {status.active_trades}")

# Stop the bot
await bot.stop()
```

## 📊 Blockchain Interface API

### `BlockchainInterface`

Handles all blockchain interactions with reliability and performance optimization.

#### Constructor

```python
class BlockchainInterface:
    def __init__(self, config: Config) -> None:
        """
        Initialize blockchain interface with configuration.
        
        Args:
            config: Configuration containing RPC settings
        """
```

#### Methods

##### `get_latest_block() -> int`
```python
async def get_latest_block(self) -> int:
    """
    Get the latest block number from the blockchain.
    
    Returns:
        int: Latest block number
        
    Raises:
        ConnectionError: If unable to connect to RPC
        BlockchainError: If blockchain query fails
    """
```

##### `get_token_info(token_address: str) -> TokenInfo`
```python
async def get_token_info(self, token_address: str) -> TokenInfo:
    """
    Get comprehensive token information.
    
    Args:
        token_address: ERC-20 token contract address
        
    Returns:
        TokenInfo: Token details including name, symbol, decimals, total supply
        
    Raises:
        InvalidTokenError: If token address is invalid
        ContractError: If unable to read token contract
    """
```

##### `get_pair_info(pair_address: str) -> PairInfo`
```python
async def get_pair_info(self, pair_address: str) -> PairInfo:
    """
    Get liquidity pair information.
    
    Args:
        pair_address: Uniswap pair contract address
        
    Returns:
        PairInfo: Pair details including reserves, price, liquidity
        
    Raises:
        InvalidPairError: If pair address is invalid
        LiquidityError: If unable to read pair data
    """
```

##### `estimate_gas(transaction: dict) -> int`
```python
async def estimate_gas(self, transaction: dict) -> int:
    """
    Estimate gas required for transaction.
    
    Args:
        transaction: Transaction parameters
        
    Returns:
        int: Estimated gas units
        
    Raises:
        GasEstimationError: If gas estimation fails
    """
```

#### Health Monitoring

##### `get_health_status() -> HealthStatus`
```python
def get_health_status(self) -> HealthStatus:
    """
    Get blockchain connection health status.
    
    Returns:
        HealthStatus: Connection health metrics
    """
```

## 💰 Trading Engine API

### `TradingEngine`

Executes trades with sophisticated order management and risk controls.

#### Constructor

```python
class TradingEngine:
    def __init__(self, config: Config) -> None:
        """
        Initialize trading engine with configuration.
        
        Args:
            config: Trading configuration parameters
        """
```

#### Trading Methods

##### `execute_buy_order(token_address: str, amount_eth: float) -> TradeResult`
```python
async def execute_buy_order(
    self, 
    token_address: str, 
    amount_eth: float,
    slippage_tolerance: Optional[float] = None
) -> TradeResult:
    """
    Execute a buy order for the specified token.
    
    Args:
        token_address: Token contract address to buy
        amount_eth: Amount of ETH to spend
        slippage_tolerance: Optional slippage override
        
    Returns:
        TradeResult: Trade execution result with transaction hash and details
        
    Raises:
        InsufficientFundsError: If insufficient ETH balance
        SlippageExceededError: If slippage exceeds tolerance
        TradeExecutionError: If trade fails to execute
    """
```

##### `execute_sell_order(token_address: str, amount_tokens: float) -> TradeResult`
```python
async def execute_sell_order(
    self, 
    token_address: str, 
    amount_tokens: float,
    slippage_tolerance: Optional[float] = None
) -> TradeResult:
    """
    Execute a sell order for the specified token.
    
    Args:
        token_address: Token contract address to sell
        amount_tokens: Amount of tokens to sell
        slippage_tolerance: Optional slippage override
        
    Returns:
        TradeResult: Trade execution result
        
    Raises:
        InsufficientTokensError: If insufficient token balance
        SlippageExceededError: If slippage exceeds tolerance
        TradeExecutionError: If trade fails to execute
    """
```

##### `get_quote(token_address: str, amount_eth: float) -> Quote`
```python
async def get_quote(
    self, 
    token_address: str, 
    amount_eth: float
) -> Quote:
    """
    Get price quote for a potential trade.
    
    Args:
        token_address: Token to get quote for
        amount_eth: Amount of ETH to trade
        
    Returns:
        Quote: Price quote with expected output amount and price impact
        
    Raises:
        QuoteError: If unable to get quote
    """
```

#### Position Management

##### `get_positions() -> List[Position]`
```python
def get_positions(self) -> List[Position]:
    """
    Get all current token positions.
    
    Returns:
        List[Position]: List of all held positions
    """
```

##### `get_position(token_address: str) -> Optional[Position]`
```python
def get_position(self, token_address: str) -> Optional[Position]:
    """
    Get position for specific token.
    
    Args:
        token_address: Token contract address
        
    Returns:
        Optional[Position]: Position details if held, None otherwise
    """
```

## 🛡️ Security Module API

### `SecurityManager`

Comprehensive security framework protecting against various threats.

#### Constructor

```python
class SecurityManager:
    def __init__(self, config: Config) -> None:
        """
        Initialize security manager with configuration.
        
        Args:
            config: Security configuration settings
        """
```

#### Token Security

##### `validate_token(token_address: str) -> SecurityReport`
```python
async def validate_token(self, token_address: str) -> SecurityReport:
    """
    Perform comprehensive token security analysis.
    
    Args:
        token_address: Token contract address to analyze
        
    Returns:
        SecurityReport: Detailed security analysis report
        
    Raises:
        SecurityValidationError: If validation fails
    """
```

##### `check_honeypot(token_address: str) -> HoneypotResult`
```python
async def check_honeypot(self, token_address: str) -> HoneypotResult:
    """
    Check if token is a honeypot scam.
    
    Args:
        token_address: Token contract address
        
    Returns:
        HoneypotResult: Honeypot analysis results
        
    Raises:
        HoneypotCheckError: If honeypot check fails
    """
```

#### MEV Protection

##### `enable_mev_protection() -> None`
```python
def enable_mev_protection(self) -> None:
    """
    Enable MEV (Maximal Extractable Value) protection.
    """
```

##### `get_mev_protection_status() -> MEVStatus`
```python
def get_mev_protection_status(self) -> MEVStatus:
    """
    Get current MEV protection status.
    
    Returns:
        MEVStatus: MEV protection configuration and status
    """
```

#### Private Key Security

##### `validate_private_key(private_key: str) -> bool`
```python
def validate_private_key(self, private_key: str) -> bool:
    """
    Validate private key security and format.
    
    Args:
        private_key: Private key to validate
        
    Returns:
        bool: True if key is valid and safe
        
    Raises:
        DangerousPrivateKeyError: If key is known to be dangerous
        InvalidPrivateKeyError: If key format is invalid
    """
```

## 📈 Analytics Engine API

### `TradingAnalytics`

Advanced performance tracking and reporting system.

#### Constructor

```python
class TradingAnalytics:
    def __init__(self, config: Config) -> None:
        """
        Initialize analytics engine with configuration.
        
        Args:
            config: Analytics configuration including database settings
        """
```

#### Performance Metrics

##### `calculate_performance_metrics() -> PerformanceMetrics`
```python
def calculate_performance_metrics(self) -> PerformanceMetrics:
    """
    Calculate comprehensive performance metrics.
    
    Returns:
        PerformanceMetrics: Performance statistics including win rate, PnL, etc.
    """
```

##### `get_trade_history(limit: int = 100) -> List[TradeRecord]`
```python
async def get_trade_history(
    self, 
    limit: int = 100,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> List[TradeRecord]:
    """
    Get trading history with optional filtering.
    
    Args:
        limit: Maximum number of trades to return
        start_date: Optional start date filter
        end_date: Optional end date filter
        
    Returns:
        List[TradeRecord]: List of trade records
    """
```

#### Reporting

##### `generate_report(days: int = 7) -> AnalyticsReport`
```python
async def generate_report(self, days: int = 7) -> AnalyticsReport:
    """
    Generate analytics report for specified period.
    
    Args:
        days: Number of days to include in report
        
    Returns:
        AnalyticsReport: Comprehensive analytics report
    """
```

##### `export_data(format: str = 'csv') -> str`
```python
async def export_data(
    self, 
    format: str = 'csv',
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> str:
    """
    Export trading data in specified format.
    
    Args:
        format: Export format ('csv', 'json', 'excel')
        start_date: Optional start date
        end_date: Optional end date
        
    Returns:
        str: Path to exported file
        
    Raises:
        ExportError: If export fails
    """
```

## ⚙️ Utilities API

### `RateLimiter`

Token bucket rate limiting implementation.

#### Constructor

```python
class RateLimiter:
    def __init__(self, max_calls: int, time_window: int) -> None:
        """
        Initialize rate limiter.
        
        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
        """
```

#### Usage

```python
async with rate_limiter:
    # Rate-limited operation
    result = await some_api_call()
```

### `CircuitBreaker`

Fault tolerance mechanism with automatic recovery.

#### Constructor

```python
class CircuitBreaker:
    def __init__(
        self, 
        failure_threshold: int = 5, 
        recovery_timeout: int = 60
    ) -> None:
        """
        Initialize circuit breaker.
        
        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before attempting recovery
        """
```

#### Methods

##### `call(func, *args, **kwargs) -> Any`
```python
async def call(self, func, *args, **kwargs) -> Any:
    """
    Execute function with circuit breaker protection.
    
    Args:
        func: Function to execute
        *args: Function arguments
        **kwargs: Function keyword arguments
        
    Returns:
        Any: Function result
        
    Raises:
        CircuitBreakerOpenError: If circuit is open
    """
```

### `RetryLogic`

Exponential backoff retry mechanism.

#### Constructor

```python
class RetryLogic:
    def __init__(self, config: RetryConfig) -> None:
        """
        Initialize retry logic with configuration.
        
        Args:
            config: Retry configuration parameters
        """
```

#### Methods

##### `execute(func, *args, **kwargs) -> Any`
```python
async def execute(self, func, *args, **kwargs) -> Any:
    """
    Execute function with retry logic.
    
    Args:
        func: Function to execute
        *args: Function arguments  
        **kwargs: Function keyword arguments
        
    Returns:
        Any: Function result
        
    Raises:
        MaxRetriesExceededError: If all retries are exhausted
    """
```

## 📋 Configuration API

### `Config`

Configuration management with validation and security.

#### Configuration Properties

```python
class Config(BaseSettings):
    # Blockchain Settings
    rpc_url: str
    backup_rpc_urls: List[str] = []
    chain_id: int = 1
    private_key: str
    wallet_address: str
    
    # Trading Settings
    min_liquidity_eth: float = 1.0
    max_gas_price: int = 100
    slippage_tolerance: float = 5.0
    trade_amount_eth: float = 0.1
    max_trade_amount: float = 1.0
    
    # Security Settings
    enable_mev_protection: bool = True
    honeypot_check_enabled: bool = True
    verify_contract_source: bool = True
    
    # Performance Settings
    max_rpc_calls_per_second: int = 10
    max_concurrent_trades: int = 3
    
    # Monitoring Settings
    webhook_url: Optional[str] = None
    database_url: str = "sqlite:///sniper_data.db"
    log_level: str = "INFO"
```

#### Methods

##### `validate() -> bool`
```python
def validate(self) -> bool:
    """
    Validate configuration settings.
    
    Returns:
        bool: True if configuration is valid
        
    Raises:
        ConfigurationError: If configuration is invalid
    """
```

## 🔔 Notifications API

### `NotificationSystem`

Multi-channel notification system with reliability features.

#### Constructor

```python
class NotificationSystem:
    def __init__(self, config: Config) -> None:
        """
        Initialize notification system.
        
        Args:
            config: Notification configuration
        """
```

#### Methods

##### `send_trade_notification(trade: TradeData) -> None`
```python
async def send_trade_notification(self, trade: TradeData) -> None:
    """
    Send trade notification to configured channels.
    
    Args:
        trade: Trade data to include in notification
        
    Raises:
        NotificationError: If notification fails to send
    """
```

##### `send_alert(alert: Alert) -> None`
```python
async def send_alert(self, alert: Alert) -> None:
    """
    Send alert notification.
    
    Args:
        alert: Alert to send
        
    Raises:
        NotificationError: If alert fails to send
    """
```

## 📊 Data Models

### Core Data Types

#### `TradeResult`
```python
@dataclass
class TradeResult:
    success: bool
    transaction_hash: str
    amount_in: float
    amount_out: float
    gas_used: int
    gas_price: int
    timestamp: datetime
    error_message: Optional[str] = None
```

#### `TokenInfo`
```python
@dataclass
class TokenInfo:
    address: str
    name: str
    symbol: str
    decimals: int
    total_supply: int
    verified: bool
```

#### `SecurityReport`
```python
@dataclass
class SecurityReport:
    token_address: str
    is_honeypot: bool
    has_transfer_restrictions: bool
    liquidity_locked: bool
    contract_verified: bool
    security_score: int  # 0-100
    risk_level: RiskLevel
    warnings: List[str]
```

#### `PerformanceMetrics`
```python
@dataclass
class PerformanceMetrics:
    total_trades: int
    successful_trades: int
    win_rate: float
    total_profit_loss: float
    average_trade_size: float
    average_gas_cost: float
    max_drawdown: float
    sharpe_ratio: float
```

## 🚨 Exception Classes

### Core Exceptions

```python
class SniperBotError(Exception):
    """Base exception for all bot errors"""
    pass

class ConfigurationError(SniperBotError):
    """Configuration-related errors"""
    pass

class TradingError(SniperBotError):
    """Trading execution errors"""
    pass

class SecurityError(SniperBotError):
    """Security validation errors"""
    pass

class BlockchainError(SniperBotError):
    """Blockchain interaction errors"""
    pass

class ConnectionError(SniperBotError):
    """Network connection errors"""
    pass
```

## 💡 Usage Examples

### Basic Bot Setup

```python
from bot.sniper import SniperBot
from bot.config import Config

# Load configuration
config = Config()

# Initialize bot
bot = SniperBot(config)

# Start trading
await bot.start()
```

### Manual Trading

```python
from bot.trading import TradingEngine
from bot.config import Config

config = Config()
trading_engine = TradingEngine(config)

# Execute a buy order
result = await trading_engine.execute_buy_order(
    token_address="0x...",
    amount_eth=0.1,
    slippage_tolerance=5.0
)

print(f"Trade result: {result.success}, TX: {result.transaction_hash}")
```

### Security Analysis

```python
from bot.security import SecurityManager
from bot.config import Config

config = Config()
security = SecurityManager(config)

# Analyze token security
report = await security.validate_token("0x...")

print(f"Security score: {report.security_score}/100")
print(f"Risk level: {report.risk_level}")
for warning in report.warnings:
    print(f"Warning: {warning}")
```

### Analytics and Reporting

```python
from bot.analytics import TradingAnalytics
from bot.config import Config

config = Config()
analytics = TradingAnalytics(config)

# Get performance metrics
metrics = analytics.calculate_performance_metrics()
print(f"Win rate: {metrics.win_rate:.2f}%")
print(f"Total P&L: {metrics.total_profit_loss:.4f} ETH")

# Generate weekly report
report = await analytics.generate_report(days=7)
print(report.summary)
```

## 🔧 Advanced Configuration

### Custom Rate Limiting

```python
from bot.utils import RateLimiter

# Create custom rate limiter (10 calls per 5 seconds)
rate_limiter = RateLimiter(max_calls=10, time_window=5)

async def rate_limited_function():
    async with rate_limiter:
        # Your API call here
        result = await some_api_call()
        return result
```

### Circuit Breaker Pattern

```python
from bot.utils import CircuitBreaker

# Create circuit breaker (open after 3 failures, recover in 30 seconds)
circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)

async def protected_function():
    return await circuit_breaker.call(unreliable_function)
```

## 📞 Support

For API questions and support:

- 📖 **Documentation**: [GitHub Wiki](https://github.com/your-username/crypto-sniping-bot/wiki)
- 🐛 **Issues**: [GitHub Issues](https://github.com/your-username/crypto-sniping-bot/issues)  
- 💬 **Discussions**: [GitHub Discussions](https://github.com/your-username/crypto-sniping-bot/discussions)
- 🔒 **Security**: Report security issues to security@yourproject.com

---

**📖 This API reference covers all major components. For implementation details, see the source code and additional documentation.**
