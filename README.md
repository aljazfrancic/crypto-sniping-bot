# 💸 Stonks Crypto Sniping Bot

**Short description:** Blazing‑fast bot that snipes newly‑created liquidity pools on EVM DEXes and scales with ML‑powered forecasting for long‑term edge.

## Overview
The Stonks Crypto Sniping Bot is an end‑to‑end framework that *detects*, *buys* and *exits* profitable tokens seconds after a liquidity pool appears.  
Phase ➊ delivers an on‑chain sniping contract and a Python daemon that listens for `PairCreated` events. Phase ➋ layers a graph‑based time‑series forecaster on top of live DEX data to identify higher‑conviction trades and cross‑DEX arbitrage.

| Layer | Tech | Purpose |
|-------|------|---------|
| **Solidity Sniper** | Hardhat + OpenZeppelin | Executes token swaps with slippage + deadline guards |
| **Python Bot** | web3.py + asyncio | Watches mempool / `PairCreated`, calls sniper, monitors positions |
| **Forecasting** | PyTorch Geometric | Predicts edge‑weighted token graph to rank opportunities |
| **Ops** | Docker + GitHub Actions | CI, unit‑tests, automatic deployment |

## Architecture
```
                  ┌──────────────────────────┐
                  │  Polygon / Ethereum RPC  │
                  └────────────┬─────────────┘
                               │  PairCreated
                     async WebSocket listener
                               ▼
    ┌──────────────┐   call   ┌─────────────────┐
    │  Python Bot  ├────────► │  Sniper Contract│
    └─────┬────────┘          └────────┬────────┘
          │ price stream                  │ bought tokens
          ▼                               ▼
    Forecasting Engine             Sell / Exit Logic
```

## Getting Started
### Prerequisites
```bash
# Node & Python toolchain
nvm use 18
npm i -g hardhat
python -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt
```

### Local Test
```bash
# 1. Run a forked chain
npx hardhat node --fork https://rpc.ankr.com/eth
# 2. Deploy contracts & run tests
npx hardhat test
# 3. Fire up the bot
python bot/sniper.py --rpc ws://localhost:8545
```

## Usage
* Environment variables live in `.env.example`.
* The bot logs every step and exposes a REST / Prometheus port for health checks.
* See `scripts/demo.sh` for a one‑command demo on Polygon Mumbai.

## Roadmap & TODO
- [ ] **Solidity** – finalize `LPLockChecker` and integrate honeypot detection  
- [ ] **Python** – mempool monitoring & multi‑tx nonce compatibility  
- [ ] **Forecasting** – prototype GNN on top‑500‑token graph  
- [ ] **CI/CD** – GitHub Actions: lint ➜ test ➜ slither ➜ deploy  
- [ ] **Docs** – architecture diagram & contributor guide  
- [ ] **Security Audit** – run Slither + MythX before main‑net  
- [ ] **ROI Tracking** – SQLite → Grafana dashboard  

## Contributing
PRs are welcome! Please open an issue first to discuss changes.  
Run `pre-commit run --all-files` before pushing.

## License
MIT © 2025 Stonks DAO
