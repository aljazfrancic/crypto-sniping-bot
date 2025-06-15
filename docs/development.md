# 👨‍💻 Development Guide

This guide covers development practices, testing procedures, and contribution guidelines for the Crypto Sniping Bot.

## 🚀 Getting Started

### Development Environment Setup

#### 1. Clone and Setup
```bash
git clone https://github.com/your-username/crypto-sniping-bot.git
cd crypto-sniping-bot

# Run automated setup
python setup_tests.py

# Or manual setup
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

#### 2. IDE Configuration

**VS Code (Recommended)**
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./.venv/bin/python",
    "python.formatting.provider": "black",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.linting.mypyEnabled": true,
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": ["tests/"]
}
```

**PyCharm**
- Set Python interpreter to `.venv/bin/python`
- Configure Black as code formatter
- Enable MyPy type checking
- Set pytest as test runner

#### 3. Pre-commit Hooks
```bash
# Install pre-commit
pip install pre-commit

# Setup hooks
pre-commit install

# Run on all files
pre-commit run --all-files
```

## 🏗️ Project Structure

```
crypto-sniping-bot/
├── bot/                    # Main bot modules
│   ├── __init__.py
│   ├── sniper.py          # Main bot orchestration
│   ├── blockchain.py      # Blockchain interface
│   ├── trading.py         # Trading engine
│   ├── security.py        # Security module
│   ├── analytics.py       # Analytics engine
│   ├── config.py          # Configuration management
│   ├── utils.py           # Utilities (rate limiter, circuit breaker)
│   ├── exceptions.py      # Custom exceptions
│   └── notifications.py   # Notification system
├── tests/                 # Test suite
│   ├── test_security.py   # Security tests (18 tests)
│   ├── test_exceptions.py # Exception tests (15 tests)
│   ├── test_analytics.py  # Analytics tests
│   ├── test_trading.py    # Trading tests
│   └── conftest.py        # Test configuration
├── docs/                  # Documentation
├── scripts/               # Utility scripts
├── abis/                  # Smart contract ABIs
├── logs/                  # Log files
├── data/                  # Database and data files
├── test_clean.py          # Comprehensive integration test
├── setup_tests.py         # Test environment setup
├── run_tests.py           # Test runner
└── requirements.txt       # Dependencies
```

## 🧪 Testing Strategy

### Test Categories

#### 1. Unit Tests
Test individual components in isolation:
```bash
# Run unit tests
python run_tests.py unit
pytest tests/test_*.py -v -k "not integration"
```

#### 2. Integration Tests
Test component interactions:
```bash
# Run integration tests
python run_tests.py integration
pytest tests/test_integration.py -v
```

#### 3. Security Tests
Comprehensive security validation:
```bash
# Run security tests (18 tests)
python run_tests.py security
pytest tests/test_security.py -v
```

#### 4. Clean Environment Test
Full system test in clean environment:
```bash
# Run comprehensive clean test
python test_clean.py
```

### Writing Tests

#### Test Structure
```python
# tests/test_example.py
import pytest
from unittest.mock import AsyncMock, patch
from bot.security import SecurityManager
from bot.config import Config

class TestSecurityManager:
    @pytest.fixture
    def security_manager(self):
        config = Config()
        return SecurityManager(config)
    
    async def test_private_key_validation(self, security_manager):
        """Test private key validation"""
        # Test valid key
        valid_key = "0x" + "a" * 64
        result = security_manager.validate_private_key(valid_key)
        assert result is True
        
        # Test dangerous key
        # Known Hardhat test key - should be blocked by security
        dangerous_key = "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80"
        with pytest.raises(DangerousPrivateKeyError):
            security_manager.validate_private_key(dangerous_key)
    
    @patch('bot.security.aiohttp.ClientSession.post')
    async def test_honeypot_detection(self, mock_post, security_manager):
        """Test honeypot detection with mocked API"""
        # Mock API response
        mock_response = AsyncMock()
        mock_response.json.return_value = {"isHoneypot": False}
        mock_post.return_value.__aenter__.return_value = mock_response
        
        # Test honeypot check
        result = await security_manager.check_honeypot("0x123...")
        assert result.is_honeypot is False
```

#### Test Fixtures
```python
# conftest.py
import pytest
import asyncio
from bot.config import Config

@pytest.fixture
def config():
    """Test configuration"""
    return Config(env_file="test_safe.config.env")

@pytest.fixture
def event_loop():
    """Event loop for async tests"""
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()

@pytest.fixture
async def mock_blockchain():
    """Mock blockchain interface"""
    with patch('bot.blockchain.Web3') as mock_web3:
        mock_web3.return_value.is_connected.return_value = True
        yield mock_web3
```

### Test Coverage

```bash
# Run tests with coverage
pytest tests/ --cov=bot --cov-report=html --cov-report=term-missing

# View coverage report
open htmlcov/index.html  # macOS
start htmlcov/index.html  # Windows
```

## 🔍 Code Quality

### Code Formatting

#### Black (Automatic)
```bash
# Format all code
black bot/ tests/

# Check formatting
black --check bot/ tests/

# Format specific file
black bot/security.py
```

#### Configuration
```toml
# pyproject.toml
[tool.black]
line-length = 88
target-version = ['py38']
include = '\.pyi?$'
extend-exclude = '''
/(
  # directories
  \.eggs
  | \.git
  | \.mypy_cache
  | \.pytest_cache
  | \.venv
  | build
  | dist
)/
'''
```

### Type Checking

#### MyPy
```bash
# Type check entire project
mypy bot/

# Type check specific module
mypy bot/security.py

# Generate type coverage report
mypy --html-report mypy-report bot/
```

#### Type Annotations
```python
from typing import Optional, List, Dict, Any
from dataclasses import dataclass

@dataclass
class TradeResult:
    success: bool
    transaction_hash: str
    amount_out: float
    error_message: Optional[str] = None

class TradingEngine:
    def __init__(self, config: Config) -> None:
        self.config = config
    
    async def execute_trade(
        self, 
        token_address: str, 
        amount: float
    ) -> TradeResult:
        """Execute a trade with type safety"""
        # Implementation here
        pass
```

### Linting

#### Pylint
```bash
# Lint entire project
pylint bot/

# Lint specific module
pylint bot/security.py

# Generate report
pylint --output-format=html bot/ > pylint-report.html
```

#### Configuration
```ini
# .pylintrc
[MASTER]
extension-pkg-whitelist=pydantic

[MESSAGES CONTROL]
disable=
    too-few-public-methods,
    too-many-arguments,
    line-too-long

[FORMAT]
max-line-length=88
```

### Security Scanning

#### Bandit
```bash
# Security scan
bandit -r bot/

# Generate report
bandit -r bot/ -f html -o bandit-report.html

# Scan with confidence level
bandit -r bot/ -ll  # Low confidence
```

#### Safety (Dependencies)
```bash
# Check for known vulnerabilities
safety check

# Check requirements file
safety check -r requirements.txt
```

## 🔧 Development Workflow

### Feature Development

#### 1. Create Feature Branch
```bash
git checkout -b feature/new-security-feature
```

#### 2. Implement Feature
```python
# bot/security.py
class SecurityManager:
    async def new_security_feature(self, token_address: str) -> bool:
        """
        New security feature implementation.
        
        Args:
            token_address: Token to analyze
            
        Returns:
            bool: Security check result
        """
        # Implementation here
        pass
```

#### 3. Write Tests
```python
# tests/test_security.py
async def test_new_security_feature(self, security_manager):
    """Test new security feature"""
    result = await security_manager.new_security_feature("0x123...")
    assert isinstance(result, bool)
    assert result is True  # or appropriate assertion
```

#### 4. Run Test Suite
```bash
# Run all tests
python test_clean.py

# Run specific tests
pytest tests/test_security.py::test_new_security_feature -v

# Check code quality
black bot/ tests/
mypy bot/
pylint bot/
```

#### 5. Update Documentation
```markdown
## New Security Feature

This feature provides enhanced security analysis by...

### Usage
```python
from bot.security import SecurityManager
security = SecurityManager(config)
result = await security.new_security_feature("0x...")
```

#### 6. Create Pull Request
```bash
git add .
git commit -m "feat: add new security feature with comprehensive tests"
git push origin feature/new-security-feature
```

### Code Review Process

#### Review Checklist
- [ ] Code follows style guidelines (Black, Pylint)
- [ ] Type annotations are present (MyPy clean)
- [ ] Tests are comprehensive and pass
- [ ] Documentation is updated
- [ ] Security considerations addressed
- [ ] Performance impact evaluated
- [ ] Breaking changes documented

#### Review Commands
```bash
# Reviewer checkout and test
git checkout feature/new-security-feature
python test_clean.py
python run_tests.py security
```

## 🏗️ Architecture Guidelines

### Design Patterns

#### Async/Await
```python
class TradingEngine:
    async def execute_trade(self, token_address: str) -> TradeResult:
        """All I/O operations should be async"""
        # Pre-trade security check
        security_result = await self.security.validate_token(token_address)
        
        # Execute trade
        if security_result.is_safe:
            return await self._execute_buy_order(token_address)
        else:
            raise SecurityError("Token failed security validation")
```

#### Dependency Injection
```python
class SniperBot:
    def __init__(self, config: Config):
        # Inject dependencies
        self.blockchain = BlockchainInterface(config)
        self.trading = TradingEngine(config, self.blockchain)
        self.security = SecurityManager(config, self.blockchain)
        self.analytics = TradingAnalytics(config)
```

#### Error Handling
```python
class SecurityManager:
    async def validate_token(self, token_address: str) -> SecurityReport:
        try:
            # Validation logic
            report = await self._perform_validation(token_address)
            return report
        except ValidationError as e:
            self.logger.error(f"Validation failed for {token_address}: {e}")
            raise SecurityValidationError(f"Failed to validate token: {e}")
        except Exception as e:
            self.logger.critical(f"Unexpected error in validation: {e}")
            raise SecurityError(f"Unexpected validation error: {e}")
```

### Performance Guidelines

#### Async Programming
```python
# Good: Concurrent operations
async def validate_multiple_tokens(self, tokens: List[str]) -> List[SecurityReport]:
    tasks = [self.validate_token(token) for token in tokens]
    return await asyncio.gather(*tasks, return_exceptions=True)

# Bad: Sequential operations
async def validate_multiple_tokens_slow(self, tokens: List[str]) -> List[SecurityReport]:
    results = []
    for token in tokens:
        result = await self.validate_token(token)
        results.append(result)
    return results
```

#### Caching
```python
from functools import lru_cache
from cachetools import TTLCache

class BlockchainInterface:
    def __init__(self, config: Config):
        self.contract_cache = TTLCache(maxsize=1000, ttl=3600)
    
    @lru_cache(maxsize=100)
    def get_contract_abi(self, address: str) -> dict:
        """Cache expensive ABI lookups"""
        return self._load_abi(address)
```

### Security Guidelines

#### Input Validation
```python
def validate_token_address(self, address: str) -> str:
    """Validate and normalize token address"""
    if not address:
        raise ValueError("Token address cannot be empty")
    
    if not address.startswith('0x'):
        raise ValueError("Token address must start with 0x")
    
    if len(address) != 42:
        raise ValueError("Token address must be 42 characters long")
    
    # Checksum validation
    try:
        return Web3.toChecksumAddress(address)
    except ValueError:
        raise ValueError("Invalid token address checksum")
```

#### Sensitive Data Handling
```python
class Config:
    def __init__(self):
        # Never log private keys
        self.private_key = os.getenv('PRIVATE_KEY')
        if not self.private_key:
            raise ConfigurationError("Private key not found in environment")
    
    def __repr__(self) -> str:
        # Mask sensitive data in logs
        return f"Config(rpc_url={self.rpc_url}, private_key=***masked***)"
```

## 📚 Documentation Guidelines

### Code Documentation

#### Docstrings
```python
class SecurityManager:
    """
    Comprehensive security manager for token and transaction validation.
    
    This class provides multiple layers of security validation including:
    - Private key validation and protection
    - Token honeypot detection
    - MEV protection mechanisms
    - Contract security analysis
    
    Attributes:
        config: Configuration object with security settings
        blockchain: Blockchain interface for contract interactions
    """
    
    async def validate_token(self, token_address: str) -> SecurityReport:
        """
        Perform comprehensive security validation of a token.
        
        This method runs multiple security checks in parallel including
        honeypot detection, contract verification, and liquidity analysis.
        
        Args:
            token_address: The token contract address to validate
            
        Returns:
            SecurityReport: Comprehensive security analysis report containing
                security score, risk assessment, and detailed findings
                
        Raises:
            SecurityValidationError: If validation process fails
            InvalidTokenError: If token address is invalid
            
        Example:
            >>> security = SecurityManager(config)
            >>> report = await security.validate_token("0x...")
            >>> print(f"Security score: {report.security_score}/100")
        """
```

#### Type Hints
```python
from typing import Optional, List, Dict, Union, Tuple
from decimal import Decimal

async def calculate_trade_metrics(
    self,
    trades: List[TradeRecord],
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
) -> Tuple[Decimal, float, int]:
    """
    Calculate trading performance metrics.
    
    Args:
        trades: List of trade records to analyze
        start_date: Optional start date for filtering
        end_date: Optional end date for filtering
        
    Returns:
        Tuple containing:
            - Total profit/loss as Decimal
            - Win rate as float (0.0 to 1.0)
            - Number of trades as int
    """
```

### API Documentation

Update API documentation when adding new features:
```markdown
### New Method: `validate_token_security`

Comprehensive token security validation with advanced threat detection.

#### Parameters
- `token_address` (str): Token contract address
- `deep_analysis` (bool, optional): Enable deep contract analysis

#### Returns
- `SecurityReport`: Detailed security analysis

#### Example
```python
report = await security.validate_token_security(
    "0x...", 
    deep_analysis=True
)
```
```

## 🚀 Deployment Guidelines

### Environment Configuration

#### Development
```env
ENVIRONMENT=development
DEBUG=true
LOG_LEVEL=DEBUG
USE_TESTNET=true
MOCK_TRADING=true
```

#### Staging
```env
ENVIRONMENT=staging
DEBUG=false
LOG_LEVEL=INFO
USE_TESTNET=true
ENABLE_ALL_SECURITY_FEATURES=true
```

#### Production
```env
ENVIRONMENT=production
DEBUG=false
LOG_LEVEL=WARNING
USE_TESTNET=false
ENABLE_ALL_SECURITY_FEATURES=true
SECURITY_LEVEL=maximum
```

### CI/CD Pipeline

#### GitHub Actions
```yaml
# .github/workflows/ci.yml
name: CI/CD Pipeline

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: '3.8'
      
      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
      
      - name: Run tests
        run: |
          python test_clean.py
          pytest tests/ --cov=bot --cov-report=xml
      
      - name: Code quality
        run: |
          black --check bot/ tests/
          mypy bot/
          pylint bot/
          bandit -r bot/
```

## 🤝 Contributing

### Contribution Workflow

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Ensure code quality standards
5. Update documentation
6. Submit pull request

### Commit Guidelines

```bash
# Format: type(scope): description
feat(security): add MEV protection mechanism
fix(trading): resolve slippage calculation bug
docs(api): update security API documentation  
test(analytics): add performance metrics tests
refactor(utils): improve rate limiter implementation
```

### Pull Request Template

```markdown
## Description
Brief description of changes

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests pass
- [ ] Integration tests pass
- [ ] Security tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added/updated
```

---

**👨‍💻 Happy coding! Follow these guidelines to maintain code quality and ensure the bot remains secure and reliable.**
