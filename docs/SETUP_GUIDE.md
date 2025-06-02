# Quick Setup Guide

## Installation Steps

1. Extract files and navigate to directory
2. Run: npm install
3. Run: cd sniper-bot
4. Run: python -m venv .venv
5. Activate: source .venv/bin/activate (Linux/Mac) or .venv\Scripts\activate (Windows)
6. Run: pip install -r requirements.txt
7. Copy config: cp .env.example .env
8. Edit .env with your settings
9. Test: python optimized_bot.py

## Safety First

- Test on BSC testnet before mainnet
- Start with small amounts (0.001-0.01 BNB)
- Never commit private keys to Git
- Use dedicated trading wallet

## Configuration

Conservative: MAX_BUY_BNB=0.005, STOP_LOSS_PERCENTAGE=30
Aggressive: MAX_BUY_BNB=0.02, STOP_LOSS_PERCENTAGE=60
