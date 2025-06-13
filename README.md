# 🪙️🔫🤖 Crypto Sniping Bot MVP

[![CI](https://github.com/aljazfrancic/crypto-sniping-bot/actions/workflows/ci.yml/badge.svg)](https://github.com/aljazfrancic/crypto-sniping-bot/actions/workflows/ci.yml)
[![Coverage: Python](https://img.shields.io/badge/coverage-pytest--cov-informational)](https://pytest-cov.readthedocs.io/)
[![Coverage: Solidity](https://img.shields.io/badge/coverage-hardhat--coverage-informational)](https://github.com/sc-forks/solidity-coverage)
[![Lint: Python](https://img.shields.io/badge/lint-flake8-informational)](https://flake8.pycqa.org/)
[![Lint: JS](https://img.shields.io/badge/lint-eslint-informational)](https://eslint.org/)
[![Lint: Solidity](https://img.shields.io/badge/lint-solhint-informational)](https://protofire.github.io/solhint/)

A high-performance bot for sniping newly created liquidity pools on DEXes. This MVP provides core functionality for automated token trading with safety features.

---

## 🚀 Quickstart

1. **Clone the repository**
   ```bash
   git clone https://github.com/aljazfrancic/crypto-sniping-bot.git
   cd crypto-sniping-bot
   ```
2. **Install dependencies**
   ```bash
   npm install
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure environment**
   - Copy `.env.example` to `.env` and fill in your values.
   ```bash
   cp .env.example .env
   # Edit .env with your preferred editor
   ```
4. **Compile and test contracts**
   ```bash
   npx hardhat compile
   npx hardhat test
   npx hardhat coverage
   ```
5. **Run Python tests and coverage**
   ```bash
   pytest --cov=bot tests/
   ```
6. **Run the bot**
   ```bash
   python bot/sniper.py
   ```

---

## 🤔 FAQ

**Q: Is my private key safe?**
- Never share your `.env` file. Use a dedicated wallet for the bot.

**Q: How do I update dependencies?**
- Dependabot is enabled for both Python and Node.js. You'll get PRs for updates.

**Q: What networks are supported?**
- Ethereum, BSC, and Polygon (one at a time, set via `CHAIN_ID`).

**Q: How do I troubleshoot errors?**
- See the Troubleshooting section below and check your logs in `sniper_bot.log`.

**Q: How do I contribute?**
- See the Contributing section below.

---

## 🛠️ How it Works

1. **Monitors blockchain** for new liquidity pool creation events.
2. **Checks safety** (honeypot, slippage, liquidity, etc.).
3. **Executes buy/sell** transactions via the deployed Sniper contract.
4. **Manages positions** with take-profit and stop-loss logic.

See the [Architecture Diagram](#🏗️🖼️-architecture) for a visual overview.

---

## 📋🔧 Prerequisites

* Node.js v18+ and npm
* Python 3.13+
* Git
* A funded wallet with ETH/BNB for gas and trading
* RPC endpoint (Alchemy, Infura, QuickNode, etc.)

---

## ⚙️🚀 Usage

### Basic Commands

```bash
# Run on testnet first
npx hardhat run scripts/deploy.js --network bscTestnet
python bot/sniper.py

# Check logs
tail -f sniper_bot.log

# Run Python tests
pytest tests/test_sniper.py -v
```

### Configuration Options

| Setting          | Description                         | Default |
| ---------------- | ----------------------------------- | ------- |
| `BUY_AMOUNT`     | Amount to spend per snipe (ETH/BNB) | 0.1     |
| `SLIPPAGE`       | Maximum slippage tolerance (%)      | 5       |
| `PROFIT_TARGET`  | Take profit at this gain (%)        | 50      |
| `STOP_LOSS`      | Stop loss at this loss (%)          | 10      |
| `MIN_LIQUIDITY`  | Minimum pool liquidity (ETH/BNB)    | 5       |
| `CHECK_HONEYPOT` | Enable honeypot detection           | true    |

---

## 🧪✔️ Testing & Coverage

- **Python:** `pytest --cov=bot tests/` for coverage report.
- **Solidity:** `npx hardhat coverage` for contract coverage.
- **CI:** All tests and linters run on every push and PR.

---

## 📈🧪 Code Coverage

- **Python:** Run `pytest --cov=bot tests/` to see coverage report.
- **Solidity:** Run `npx hardhat coverage` to see contract coverage.

---

## 🧹 Linting

- **Python:** `flake8 bot tests`
- **JS:** `npx eslint .`
- **Solidity:** `npx solhint contracts/**/*.sol`

---

## 🏗️🖼️ Architecture

![Scheme](media/scheme.png "Scheme")

---

## 🛡️⚠️ Safety Features

1. **Honeypot Detection**
   * Contract bytecode analysis
   * Token function verification
   * External API checks (optional)
2. **Slippage Protection**
   * Configurable maximum slippage
   * Automatic calculation based on liquidity
3. **Position Management**
   * Maximum position limits
   * Automatic profit taking
   * Stop loss protection

---

## 📊👀 Monitoring

The bot logs all activities to `sniper_bot.log` and displays statistics every minute:

* Total positions opened
* Active positions with P&L
* Successful trades

---

## 🔧❓ Troubleshooting

**"No contract code at address"**
- Ensure the sniper contract is deployed
- Verify the address in your .env file

**"Insufficient funds"**
- Check wallet balance for both native token and gas
- Ensure BUY_AMOUNT is less than your balance

**"Connection lost"**
- Check your RPC endpoint
- Use a reliable WebSocket provider

**High gas fees**
- Adjust GAS_PRICE_MULTIPLIER
- Consider using a different network

---

## 🛠️💡 Development

### Project Structure

```
crypto-sniping-bot/
├── contracts/         # Solidity smart contracts
│   ├── Sniper.sol    # Main sniper contract
│   └── mocks/        # Mock contracts for testing
├── bot/              # Python bot implementation
├── test/             # Hardhat test files
├── tests/            # Python test files
├── scripts/          # Deployment and utility scripts
├── .github/          # GitHub Actions workflows
└── .env.example      # Example environment config
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Run all tests and linters (`npm test`, `pytest`, `flake8`, `eslint`, `solhint`)
5. Ensure all tests pass and code is linted
6. Submit a pull request

---

## 📜⚖️ License

This project is for educational purposes. Use at your own risk.

---

## 🚨📢 Disclaimer

**IMPORTANT**: Cryptocurrency trading carries significant risk. This bot is provided as‑is with no guarantees. You may lose your entire investment. Always:

* Test thoroughly on testnet first
* Start with small amounts
* Never invest more than you can afford to lose
* Understand the code before using it
* Be aware of local regulations

---

## 📞💬 Support

* Open an issue for bugs
* Check existing issues before creating new ones
* [Discord](https://discord.gg/bZXer5ZttK)

---

**Remember**: This is a powerful tool. Use it responsibly and always DYOR (Do Your Own Research)! 🌟
