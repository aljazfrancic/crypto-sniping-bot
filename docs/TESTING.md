# Testing Guide for Crypto Sniping Bot

This guide covers the comprehensive testing suite with 72 tests organized in a clean structure.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- All dependencies installed (`pip install -r requirements.txt`)

### Setup Test Environment
```bash
# Copy test configuration
cp tests/config/test.config.env .env

# Or use safe test configuration
cp tests/config/test_safe.config.env .env
```

### Run All Tests
```bash
# Run all 72 tests
python run_tests.py

# With coverage report (48% coverage)
python run_tests.py --coverage

# Or using pytest directly
pytest tests/ -v
```

## 📋 Test Structure

### Organized Test Categories

The bot includes 72 tests organized in a clean directory structure:

```
tests/
├── unit/              # Unit tests (33 tests)
│   ├── test_exceptions.py    # Exception handling tests
│   └── test_security.py      # Security unit tests
├── integration/       # Integration tests (39 tests)
│   ├── test_sniper.py        # Core bot functionality
│   ├── test_clean.py         # Comprehensive integration tests
│   └── test_improvements.py  # Feature improvements
├── config/           # Test configurations
│   ├── test.config.env       # Standard test config
│   └── test_safe.config.env  # Safe test config (no real funds)
└── scripts/          # Test utilities
    ├── run_tests.py          # Test runner script
    └── setup_tests.py        # Test environment setup
```

### 1. Unit Tests (33 tests)
**Location**: `tests/unit/`

#### Exception Handling (`test_exceptions.py`)
- Base exception functionality
- Error mapping from Web3
- Contextual error information
- Exception inheritance

```bash
python -m pytest tests/unit/test_exceptions.py -v
```

#### Security Unit Tests (`test_security.py`)
- Private key validation
- Security configuration
- Risk management parameters
- Input validation

```bash
python -m pytest tests/unit/test_security.py -v
```

### 2. Integration Tests (39 tests)
**Location**: `tests/integration/`

#### Core Bot Tests (`test_sniper.py`)
- End-to-end trading workflows
- Blockchain integration
- Error handling scenarios
- Performance validation

```bash
python -m pytest tests/integration/test_sniper.py -v
```

#### Clean Integration Tests (`test_clean.py`)
- Complete system validation
- Security enhancements verification
- Analytics and performance tracking
- Production-ready utilities testing

```bash
python -m pytest tests/integration/test_clean.py -v
```

#### Feature Improvements (`test_improvements.py`)
- New feature validation
- Enhancement testing
- Regression prevention
- Performance improvements

```bash
python -m pytest tests/integration/test_improvements.py -v
```

## 🛠️ Test Runners

### Python Test Runner
**File**: `tests/scripts/run_tests.py` (also available as `run_tests.py` in root)

Run all 72 tests with various options:

```bash
# Run all 72 tests
python run_tests.py

# Run with coverage report (48% coverage)
python run_tests.py --coverage

# Run using pytest directly
python -m pytest tests/ -v

# Run specific categories
python -m pytest tests/unit/ -v        # Unit tests only
python -m pytest tests/integration/ -v # Integration tests only
```

### Individual Test Files
```bash
# Run specific test files
python -m pytest tests/unit/test_security.py -v
python -m pytest tests/integration/test_sniper.py -v
python -m pytest tests/integration/test_clean.py -v

# Run with specific markers
python -m pytest -m unit tests/ -v
python -m pytest -m integration tests/ -v
```

## ⚙️ Configuration

### pytest Configuration
**File**: `pytest.ini`

Configured with:
- Async test support
- Custom markers (unit, integration, security, slow)
- Warning filters
- Short traceback format

### Test Markers
```python
@pytest.mark.unit           # Unit tests
@pytest.mark.integration    # Integration tests
@pytest.mark.security       # Security-focused tests
@pytest.mark.slow           # Slow-running tests
@pytest.mark.requires_node  # Requires blockchain node
```

### Test Configurations
**Files**: `tests/config/`

#### Standard Test Config (`test.config.env`)
Configuration for local development and testing:
- Local Hardhat RPC URL (http://localhost:8545)
- Local chain ID (31337)
- Test environment settings

#### Safe Test Config (`test_safe.config.env`)
Safe configuration file for testing that won't expose real funds:
- Placeholder RPC URLs
- Test private keys (detected and rejected by security)
- Safe wallet addresses
- Test webhook URLs

```bash
# Use standard test config
cp tests/config/test.config.env .env

# Use safe test config (recommended)
cp tests/config/test_safe.config.env .env
```

## 📊 Coverage Reports

The test suite currently achieves **48% code coverage** across all modules.

Generate HTML coverage reports:
```bash
# Run tests with coverage
python run_tests.py --coverage

# Or using pytest directly
pytest --cov=bot --cov-report=html:htmlcov tests/

# Generate terminal coverage report
pytest --cov=bot --cov-report=term-missing tests/
```

View the HTML report:
```bash
# Open htmlcov/index.html in your browser
start htmlcov/index.html  # Windows
open htmlcov/index.html   # macOS
xdg-open htmlcov/index.html  # Linux
```

## 🔧 Setup and Maintenance

### Initial Setup
```bash
# Install dependencies
pip install -r requirements.txt

# Set up test environment
cp tests/config/test.config.env .env

# Verify setup by running tests
python run_tests.py
```

The organized test structure provides:
- ✅ 72 comprehensive tests (34 unit + 35 integration + 3 config)
- ✅ Clean directory organization
- ✅ Multiple test configurations
- ✅ 48% code coverage
- ✅ Secure test environment
- ✅ Easy-to-use test runners

### Clean Up
```bash
# Clean temporary files and caches
python cleanup.py
```

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## 📁 Current Test Structure

```
crypto-sniping-bot/
├── run_tests.py              # Main test runner (wrapper)
├── pytest.ini               # Pytest configuration
├── tests/                   # Organized test directory
│   ├── unit/                # Unit tests (34 tests)
│   │   ├── test_exceptions.py
│   │   └── test_security.py
│   ├── integration/         # Integration tests (39 tests)
│   │   ├── test_sniper.py
│   │   ├── test_clean.py
│   │   └── test_improvements.py
│   ├── config/             # Test configurations
│   │   ├── test.config.env
│   │   └── test_safe.config.env
│   └── scripts/            # Test utilities
│       ├── run_tests.py
│       └── setup_tests.py
├── conftest.py             # Pytest fixtures
├── abis/                   # Contract ABI files
│   ├── erc20.json
│   ├── router.json
│   ├── pair.json
│   └── factory.json
└── requirements.txt        # Dependencies
```

## 🎯 Testing Best Practices

### Before Committing
1. Run the comprehensive test: `python test_clean.py`
2. Run security tests: `pytest tests/test_security.py -v`
3. Check that all critical functionality works

### For Development
1. Use test markers to run specific test types
2. Run `python run_tests.py unit` for quick feedback
3. Use `pytest -x` to stop on first failure

### For CI/CD
```bash
# In your CI pipeline
python setup_tests.py          # Setup environment
pytest --cov=bot --junitxml=results.xml --cov-report=xml
```

## 🚨 Security Testing

The test suite includes multiple security layers:

1. **Private Key Protection**: Detects and rejects dangerous test keys
2. **MEV Protection**: Tests against frontrunning and sandwich attacks
3. **Contract Verification**: Validates contract authenticity
4. **Price Manipulation**: Detects artificial price movements
5. **Gas Price Protection**: Guards against gas price manipulation

All security tests use safe, non-functional test data.

## 📝 Adding New Tests

### For New Features
1. Add unit tests to appropriate files in `tests/`
2. Add integration test to `test_clean.py`
3. Use appropriate markers
4. Include security considerations

### Test Template
```python
import pytest
from bot.your_module import YourClass

class TestYourFeature:
    @pytest.mark.unit
    def test_basic_functionality(self):
        # Test implementation
        pass
    
    @pytest.mark.integration
    async def test_integration(self):
        # Async test implementation
        pass
    
    @pytest.mark.security
    def test_security_aspect(self):
        # Security test implementation
        pass
```

## 🆘 Troubleshooting

### Common Issues

1. **Import Errors**: Run `python setup_tests.py` to ensure proper setup
2. **Permission Errors**: On Windows, run as administrator if needed
3. **Missing Dependencies**: Check `requirements.txt` and reinstall
4. **Database Lock Errors**: Normal on Windows, tests handle this gracefully

### Debug Mode
```bash
# Run tests with verbose output
pytest -v -s

# Run with debug info
pytest --tb=long -v
```

### Environment Issues
```bash
# Verify setup
python -c "import bot.config; print('✓ Bot imports work')"
python -c "import pytest; print('✓ Pytest available')"
python -c "import web3; print('✓ Web3 available')"
```

## 📈 Test Results

Expected results for a successful run:

### Comprehensive Test (test_clean.py)
```
✅ All tests passed! The crypto sniping bot improvements are working correctly.

Key improvements validated:
• Enhanced configuration management with validation
• Comprehensive analytics and reporting system  
• Production-ready utilities (rate limiting, circuit breaker, retry logic)
• Improved blockchain interface with health monitoring
• Notification system for alerts and monitoring
• Performance monitoring and metrics collection
• Robust error handling with custom exceptions
```

### Security Tests
```
================================= 18 passed in 0.24s =================================
```

### Exception Tests  
```
================================= 15 passed in 0.12s =================================
```

The test environment is now fully configured and ready for development and CI/CD integration! 🎉 