# Crypto Sniping Bot – Cleaned & Unified

This repo now has **one** Node project for the Solidity contracts and tests,
plus a lightweight Python sniping bot.

## Layout
```
contracts/           Sniper.sol
test/                Hardhat test
hardhat.config.js    Hardhat + dotenv
package.json         Hardhat + OZ + dotenv deps
sniper-bot/          Python async bot
```
## Setup

```bash
# 1 — install Node deps
npm install          # installs hardhat locally
npm run compile      # compiles Sniper.sol

# 2 — run tests
npm test

# 3 — Python bot
cd sniper-bot
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# fill PRIVATE_KEY etc.
python bot.py
```
**Tip:** If you ever see `HH12`, make sure you’re inside the repo folder and
run scripts via `npm run` or `npx --no-install` so Hardhat uses the local install.