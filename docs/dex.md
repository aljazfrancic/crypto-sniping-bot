# 🔄 DEX Integration - Enterprise Edition

This comprehensive guide explains how the Crypto Sniping Bot enterprise edition integrates with various decentralized exchanges, featuring advanced routing, multi-DEX arbitrage, and sophisticated trading strategies.

## 📊 Supported DEXes

### 1. Uniswap V2

- **Network**: Ethereum
- **Router**: `0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D`
- **Factory**: `0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f`
- **Features**:
  - Standard V2 AMM
  - ETH pairs
  - ERC20 support
  - Flash swaps

### 2. PancakeSwap

- **Network**: BSC
- **Router**: `0x10ED43C718714eb63d5aA57B78B54704E256024E`
- **Factory**: `0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73`
- **Features**:
  - BSC optimization
  - BNB pairs
  - BEP20 support
  - Syrup pools

### 3. SushiSwap

- **Network**: Ethereum
- **Router**: `0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F`
- **Factory**: `0xC0AEe478e3658e2610c5F7A4A2E1777cE9e4f2Ac`
- **Features**:
  - SUSHI rewards
  - Onsen pools
  - Cross-chain support
  - Kashi lending

## 🔧 Integration Details

### 1. Router Integration

```python
# Example router configuration
{
    "uniswap_v2": {
        "router": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
        "factory": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
        "weth": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    },
    "pancakeswap": {
        "router": "0x10ED43C718714eb63d5aA57B78B54704E256024E",
        "factory": "0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73",
        "wbnb": "0xbb4CdB9CBd36B01bD1cBaEBF2De08d9173bc095c"
    }
}
```

### 2. Contract ABIs

```python
# Router ABI
ROUTER_ABI = [
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "uint256", "name": "amountOutMin", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"},
            {"internalType": "address", "name": "to", "type": "address"},
            {"internalType": "uint256", "name": "deadline", "type": "uint256"}
        ],
        "name": "swapExactTokensForTokens",
        "outputs": [
            {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
        ],
        "stateMutability": "nonpayable",
        "type": "function"
    }
]
```

### 3. Pair Detection

```python
# Example pair detection
async def detect_new_pair(event):
    pair_address = event['args']['pair']
    token0 = event['args']['token0']
    token1 = event['args']['token1']

    # Verify pair
    pair_contract = web3.eth.contract(
        address=pair_address,
        abi=PAIR_ABI
    )

    # Get reserves
    reserves = await pair_contract.functions.getReserves().call()

    return {
        'pair': pair_address,
        'token0': token0,
        'token1': token1,
        'reserves': reserves
    }
```

## 🔍 DEX Monitoring

### 1. Factory Events

```python
# Monitor factory events
async def monitor_factory():
    factory = web3.eth.contract(
        address=FACTORY_ADDRESS,
        abi=FACTORY_ABI
    )

    # Subscribe to PairCreated event
    pair_filter = factory.events.PairCreated.create_filter(fromBlock='latest')

    while True:
        for event in pair_filter.get_new_entries():
            await handle_new_pair(event)
```

### 2. Price Monitoring

```python
# Monitor pair prices
async def monitor_prices(pair_address):
    pair = web3.eth.contract(
        address=pair_address,
        abi=PAIR_ABI
    )

    # Get initial reserves
    reserves = await pair.functions.getReserves().call()

    # Monitor reserve changes
    reserve_filter = pair.events.Sync.create_filter(fromBlock='latest')

    while True:
        for event in reserve_filter.get_new_entries():
            await handle_price_change(event, reserves)
```

## 💱 Trading Functions

### 1. Buy Function

```python
async def buy_token(router, token_address, amount_in, amount_out_min):
    # Prepare transaction
    tx = {
        'from': account.address,
        'value': amount_in,
        'gas': 300000,
        'gasPrice': web3.eth.gas_price
    }

    # Execute swap
    tx_hash = await router.functions.swapExactETHForTokens(
        amount_out_min,
        [WETH_ADDRESS, token_address],
        account.address,
        int(time.time()) + 300
    ).transact(tx)

    return tx_hash
```

### 2. Sell Function

```python
async def sell_token(router, token_address, amount_in, amount_out_min):
    # Approve router
    await token.functions.approve(
        router.address,
        amount_in
    ).transact()

    # Prepare transaction
    tx = {
        'from': account.address,
        'gas': 300000,
        'gasPrice': web3.eth.gas_price
    }

    # Execute swap
    tx_hash = await router.functions.swapExactTokensForETH(
        amount_in,
        amount_out_min,
        [token_address, WETH_ADDRESS],
        account.address,
        int(time.time()) + 300
    ).transact(tx)

    return tx_hash
```

## 🔒 Security Features

### 1. Contract Verification

```python
async def verify_contract(address):
    # Check contract code
    code = web3.eth.get_code(address)
    if len(code) == 0:
        raise SecurityError("Invalid contract address")

    # Verify contract on Etherscan
    if not await is_verified(address):
        raise SecurityError("Contract not verified")

    return True
```

### 2. Liquidity Verification

```python
async def verify_liquidity(pair_address):
    pair = web3.eth.contract(
        address=pair_address,
        abi=PAIR_ABI
    )

    # Get reserves
    reserves = await pair.functions.getReserves().call()

    # Check minimum liquidity
    if reserves[0] < MIN_LIQUIDITY:
        raise SecurityError("Insufficient liquidity")

    return True
```

## 📈 Performance Optimization

### 1. Gas Optimization

```python
# Optimize gas price
async def get_optimal_gas_price():
    base_fee = web3.eth.get_block('latest')['baseFeePerGas']
    priority_fee = web3.eth.max_priority_fee

    return {
        'maxFeePerGas': base_fee * 2 + priority_fee,
        'maxPriorityFeePerGas': priority_fee
    }
```

### 2. Transaction Optimization

```python
# Optimize transaction
async def optimize_transaction(tx):
    # Estimate gas
    gas_limit = await web3.eth.estimate_gas(tx)

    # Get optimal gas price
    gas_price = await get_optimal_gas_price()

    return {
        **tx,
        'gas': gas_limit,
        **gas_price
    }
```

## 🚨 Common Issues

### 1. Transaction Failures

- **Insufficient Gas**: Increase gas limit
- **Slippage**: Adjust slippage tolerance
- **Price Impact**: Check liquidity depth
- **Contract Issues**: Verify contract code

### 2. Integration Issues

- **ABI Mismatch**: Update contract ABIs
- **Network Issues**: Check RPC connection
- **Contract Changes**: Monitor DEX updates
- **Gas Price**: Monitor network conditions

## 📚 Additional Resources

- [Uniswap V2 Documentation](https://docs.uniswap.org)
- [PancakeSwap Documentation](https://docs.pancakeswap.finance)
- [SushiSwap Documentation](https://dev.sushi.com)
- [Web3.py Documentation](https://web3py.readthedocs.io)
