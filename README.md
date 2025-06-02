#  Crypto Sniping Bot  Monorepo

This repository contains **two isolated workspaces**:

| Path | What it holds | Toolchain |
|------|---------------|-----------|
| `sniper-contracts/` | Hardhat project with all Solidity code (`Sniper.sol`, `LPLockChecker.sol`, unit tests, deploy scripts) | Node.js & Hardhat |
| `sniper-bot/` | Async Python bot, honeypot detector, LPlock scoring, pytest tests | Python 3.103.12 |

---

## 1. Solidity toolbox (`sniper-contracts/`)

```bash
cd sniper-contracts          # IMPORTANT: run npm inside this folder
npm install                  # installs local Hardhat + toolbox
npm run compile              # Compiles all .sol files
npm test                     # Runs Sniper & LP checker tests
```

*No global Hardhat needed; the CLI is resolved from* `node_modules/.bin`.

### Deploy the LP checker

```bash
npx hardhat run scripts/deploy-lpchecker.js --network <bsc/mainnet | bscTest | localhost>
# copy the printed address into sniper-bot/.env
```

---

## 2. Python bot (`sniper-bot/`)

```powershell
cd sniper-bot
python -m venv .venv
.\.venv\Scripts\Activate.ps1   # Windows PowerShell
pip install -r requirements.txt
cp .env.example .env              # fill RPC_HTTP / RPC_WS / PRIVATE_KEY / LP_CHECKER_ADDRESS
python bot.py
```

**On Bash/macOS**:

```bash
source .venv/bin/activate
```

Run unit tests:

```bash
pytest
```

---

## 3. Folder layout

```
crypto-sniping-bot/
 README.md           you are here
 .gitignore
 sniper-contracts/
   contracts/       Sniper.sol, LPLockChecker.sol
   test/            Sniper + LP checker tests
   scripts/         deploy-lpchecker.js
   package.json
 sniper-bot/
    bot.py
    honeypot_detector.py
    test_honeypot.py
    requirements.txt
    .env.example
```

---

## 4. Typical dev loop

1. Spin a **fork node** for quick iteration:

   ```bash
   npx hardhat node --fork https://bsc-rpc.publicnode.com
   ```

2. Deploy contracts to the fork, paste addresses in `.env`.
3. Run the bot  confirm it snipes the first test liquidity you add via console.
4. Iterate on heuristics & tests; push PRs.

---

 **Educational use only**  Derisk on testnet first; sniping mainnet pools is highly speculative.

## TODO / Roadmap

### Phase 1  Sniping MVP
- [ ] Finish Solidity **sniping contract** (buy, sell, slippage, deadline; flashloan optional)
- [ ] Extend **Python bot**
  - [ ] Listen for `PairCreated` events
  - [ ] Run honeypot + LPlock checks
  - [ ] Trigger sniping contract
  - [ ] Implement simple takeprofit / stoploss sell
- [ ] Local fork & public **testnet** simulations
- [ ] Basic logging & metrics

### Phase 2  Forecasting Engine
- [ ] Build **data pipeline** for historical pool data
- [ ] Graph representation & dimensionality reduction
- [ ] Temporal model (LSTM / GNN) to predict edge weights
- [ ] Integrate scoring into bot

### Phase 3  Scaling & Risk Management
- [ ] Capital allocation & autohalt rules
- [ ] CrossDEX arbitrage module
- [ ] CI/CD, monitoring dashboards
- [ ] Security audit & multisig treasury

### Infrastructure / Ops
- [ ] Select RPC provider / run own node
- [ ] GPU instance for ML training/inference
- [ ] Database layer (Postgres/TimescaleDB or graph DB)
- [ ] Cost tracking & alerts

_Derived from the deepseek project plan (20250602)._
