# 💸 Crypto Sniping Bot – Monorepo

This repository contains **two isolated workspaces**:

| Path | What it holds | Tool‑chain |
|------|---------------|-----------|
| `sniper-contracts/` | Hardhat project with all Solidity code (`Sniper.sol`, `LPLockChecker.sol`, unit tests, deploy scripts) | Node.js & Hardhat |
| `sniper-bot/` | Async Python bot, honeypot detector, LP‑lock scoring, pytest tests | Python 3.10‑3.12 |

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
├─ README.md          ← you are here
├─ .gitignore
├─ sniper-contracts/
│  ├─ contracts/      ← Sniper.sol, LPLockChecker.sol
│  ├─ test/           ← Sniper + LP checker tests
│  ├─ scripts/        ← deploy-lpchecker.js
│  └─ package.json
└─ sniper-bot/
   ├─ bot.py
   ├─ honeypot_detector.py
   ├─ test_honeypot.py
   ├─ requirements.txt
   └─ .env.example
```

---

## 4. Typical dev loop

1. Spin a **fork node** for quick iteration:

   ```bash
   npx hardhat node --fork https://bsc-rpc.publicnode.com
   ```

2. Deploy contracts to the fork, paste addresses in `.env`.
3. Run the bot – confirm it snipes the first test liquidity you add via console.
4. Iterate on heuristics & tests; push PRs.

---

⚠️ **Educational use only** – De‑risk on test‑net first; sniping mainnet pools is highly speculative.