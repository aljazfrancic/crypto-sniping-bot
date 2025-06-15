# 🎯 Crypto Sniping Bot

A high-performance, secure cryptocurrency sniping bot designed for detecting and trading newly listed tokens on decentralized exchanges.

## 🚀 Quick Start

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   cp test.config.env .env
   # Edit .env with your settings
   ```

3. **Run Tests**
   ```bash
   python run_tests.py
   ```

4. **Validate CI Pipeline (Optional)**
   ```bash
   python validate_ci.py
   ```

5. **Start Trading**
   ```bash
   python -m bot.sniper
   ```

## 📚 Documentation

For comprehensive documentation, please visit the [docs](docs/) directory:

- **[Complete README](docs/README.md)** - Full project documentation
- **[Installation Guide](docs/installation.md)** - Detailed setup instructions
- **[Configuration](docs/configuration.md)** - Configuration reference
- **[Testing Guide](docs/TESTING.md)** - Testing documentation
- **[Security Guide](docs/security.md)** - Security best practices
- **[API Reference](docs/api.md)** - Complete API documentation

## ⚡ Key Features

- 🔒 **Advanced Security** - Honeypot detection, MEV protection, private key validation
- 📊 **Analytics Dashboard** - Performance tracking and reporting
- 🏗️ **Modular Architecture** - Clean, maintainable codebase
- ⚡ **High Performance** - Async operations, rate limiting, circuit breakers
- 🧪 **Comprehensive Testing** - 59 tests with 34% code coverage

## ⚠️ Disclaimer

This software is for educational purposes only. Cryptocurrency trading involves substantial risk. Use at your own risk and never invest more than you can afford to lose.

## 📄 License

MIT License - see [LICENSE](LICENSE) file for details. 