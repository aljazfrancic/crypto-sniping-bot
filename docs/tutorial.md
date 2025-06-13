# Tutorial

## Setup

1. Install dependencies:
```bash
pip install -r requirements.txt
npm install
```

2. Deploy contract:
```bash
# Testnet
npx hardhat run scripts/deploy.js --network goerli

# Mainnet
npx hardhat run scripts/deploy.js --network mainnet
```

3. Configure:
```bash
cp .env.example .env
# Edit .env with your settings
```

## Usage

1. Start bot:
```bash
python bot/sniper.py
```

2. Monitor logs:
```bash
tail -f sniper_bot.log
```

## Configuration

Key settings in `.env`:
- `RPC_URL`: Your RPC endpoint
- `PRIVATE_KEY`: Wallet private key
- `ROUTER_ADDRESS`: DEX router address
- `FACTORY_ADDRESS`: DEX factory address
- `PROFIT_TARGET`: Take-profit percentage
- `STOP_LOSS`: Stop-loss percentage
- `MIN_LIQUIDITY`: Minimum liquidity
- `CHECK_HONEYPOT`: Enable honeypot detection
- `AUTO_SELL`: Enable auto-sell

## Troubleshooting

Common issues:
1. RPC Connection Errors
   - Check RPC endpoint
   - Verify network connectivity
   - Try alternative providers

2. Transaction Failures
   - Check wallet balance
   - Verify gas settings
   - Adjust slippage

3. Contract Errors
   - Verify deployment
   - Check addresses
   - Validate network

## Support

- [Discord](https://discord.gg/bZXer5ZttK) - Community support
- GitHub Issues - Bug reports
- [API Reference](docs/api.md) - Detailed docs

## Best Practices

1. Start with small amounts
2. Monitor transactions
3. Update dependencies
4. Use dedicated wallets
5. Regular backups 