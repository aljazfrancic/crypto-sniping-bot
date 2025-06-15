# Testing Guide for Crypto Sniping Bot

This guide covers all testing options available for the crypto sniping bot project.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ installed
- All dependencies installed (run `python setup_tests.py` to set up everything)

### Run All Tests
```bash
# Comprehensive test (recommended for verification)
python test_clean.py

# Standard pytest with coverage
python run_tests.py

# Or using pytest directly
pytest
```

## 📋 Test Categories

### 1. Comprehensive Integration Test
**File**: `test_clean.py`

This is our main test suite that validates all major improvements:
- ✅ Security enhancements (private key protection)
- ✅ Analytics and performance tracking
- ✅ Production-ready utilities (rate limiting, circuit breaker)
- ✅ Blockchain interface improvements
- ✅ Notification system
- ✅ Performance monitoring
- ✅ Error handling

```bash
python test_clean.py
```

### 2. Security Tests
**Directory**: `tests/test_security.py`

Focused on security features:
- Price manipulation detection
- MEV protection
- Contract verification
- Sandwich attack detection
- Gas price manipulation
- Contract blacklisting
- Token restrictions

```bash
pytest tests/test_security.py -v
```

### 3. Exception Handling Tests
**Directory**: `tests/test_exceptions.py`

Tests custom exception classes:
- Base exception functionality
- Error mapping from Web3
- Contextual error information
- Exception inheritance

```bash
pytest tests/test_exceptions.py -v
```

## 🛠️ Test Runners

### Python Test Runner
**File**: `run_tests.py`

Convenient test runner with multiple options:

```bash
# All tests with coverage
python run_tests.py

# Unit tests only
python run_tests.py unit

# Integration tests only
python run_tests.py integration

# Clean comprehensive test
python run_tests.py clean

# Security tests only
python run_tests.py security
```

### Windows Batch File
**File**: `run_tests.bat`

Double-click to run or use from command line:

```cmd
run_tests.bat              # All tests
run_tests.bat clean        # Comprehensive test
run_tests.bat unit         # Unit tests
run_tests.bat security     # Security tests
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

### Safe Test Configuration
**File**: `test_safe.config.env`

Safe configuration file for testing that won't expose real funds:
- Placeholder RPC URLs
- Test private keys (detected and rejected by security)
- Safe wallet addresses
- Test webhook URLs

## 📊 Coverage Reports

Generate HTML coverage reports:
```bash
pytest --cov=bot --cov-report=html:htmlcov
```

View the report:
```bash
# Open htmlcov/index.html in your browser
```

## 🔧 Setup and Maintenance

### Initial Setup
```bash
# Run the setup script to configure everything
python setup_tests.py
```

This script:
- ✅ Verifies Python version compatibility
- ✅ Installs all dependencies
- ✅ Creates necessary directories
- ✅ Sets up ABI files
- ✅ Creates safe test configurations
- ✅ Configures pytest
- ✅ Creates test runner scripts
- ✅ Verifies the setup

### Clean Up
```bash
# Clean temporary files and caches
python cleanup.py
```

### Update Dependencies
```bash
pip install -r requirements.txt --upgrade
```

## 📁 Test Structure

```
crypto-sniping-bot/
├── test_clean.py              # Main comprehensive test
├── run_tests.py               # Test runner script
├── run_tests.bat             # Windows batch runner
├── setup_tests.py            # Test environment setup
├── pytest.ini               # Pytest configuration
├── test_safe.config.env     # Safe test configuration
├── tests/                   # Traditional pytest tests
│   ├── test_security.py     # Security tests
│   ├── test_exceptions.py   # Exception tests
│   └── conftest.py          # Pytest fixtures
├── abis/                    # Contract ABI files
│   ├── erc20.json
│   ├── router.json
│   ├── pair.json
│   └── factory.json
└── requirements.txt         # Dependencies
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