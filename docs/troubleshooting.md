# 🔧 Troubleshooting Guide

This guide provides solutions for common issues you might encounter while using the Crypto Sniping Bot.

## 🔌 Connection Issues

### 1. RPC Connection Failed

**Symptoms:**
- Bot fails to start
- "Connection refused" error
- High latency in responses

**Solutions:**
1. Check RPC URL in `.env`:
```env
RPC_URL=https://eth-mainnet.alchemyapi.io/v2/your-api-key
```

2. Verify network connectivity:
```bash
ping eth-mainnet.alchemyapi.io
```

3. Try alternative RPC providers:
- Infura
- QuickNode
- Ankr

4. Check rate limits:
```python
# Increase timeout
web3 = Web3(Web3.HTTPProvider(RPC_URL, request_kwargs={'timeout': 30}))
```

### 2. WebSocket Connection Issues

**Symptoms:**
- Real-time updates not working
- Connection drops frequently
- High latency in events

**Solutions:**
1. Check WebSocket URL:
```python
ws_url = RPC_URL.replace('https://', 'wss://')
```

2. Implement reconnection logic:
```python
async def connect_websocket():
    while True:
        try:
            ws = await websockets.connect(ws_url)
            return ws
        except Exception as e:
            print(f"Connection failed: {e}")
            await asyncio.sleep(5)
```

3. Monitor connection health:
```python
async def monitor_connection(ws):
    while True:
        try:
            pong = await ws.ping()
            await asyncio.wait_for(pong, timeout=10)
        except Exception:
            await reconnect()
```

## 💰 Transaction Issues

### 1. Transaction Failed

**Symptoms:**
- Transaction reverts
- "Out of gas" error
- Transaction pending for too long

**Solutions:**
1. Check gas settings:
```python
# Increase gas limit
tx_params = {
    'gas': 500000,  # Increase from default
    'maxFeePerGas': web3.eth.gas_price * 2,
    'maxPriorityFeePerGas': web3.eth.max_priority_fee
}
```

2. Verify slippage:
```python
# Increase slippage tolerance
slippage = 3.0  # 3% instead of default 2.5%
```

3. Check token approval:
```python
# Verify token approval
allowance = await token.functions.allowance(
    wallet_address,
    router_address
).call()

if allowance < amount:
    await approve_token(amount)
```

### 2. High Gas Prices

**Symptoms:**
- Transactions too expensive
- Failed transactions due to gas
- High priority fees

**Solutions:**
1. Implement gas optimization:
```python
async def get_optimal_gas():
    base_fee = web3.eth.get_block('latest')['baseFeePerGas']
    priority_fee = web3.eth.max_priority_fee
    
    return {
        'maxFeePerGas': base_fee * 1.5 + priority_fee,
        'maxPriorityFeePerGas': priority_fee
    }
```

2. Use gas price monitoring:
```python
async def monitor_gas_prices():
    while True:
        gas_price = web3.eth.gas_price
        if gas_price < threshold:
            execute_transaction()
        await asyncio.sleep(1)
```

3. Implement gas price prediction:
```python
async def predict_gas_price():
    # Get historical gas prices
    blocks = await get_recent_blocks(10)
    gas_prices = [block['baseFeePerGas'] for block in blocks]
    
    # Calculate average
    return sum(gas_prices) / len(gas_prices)
```

## 🔒 Security Issues

### 1. Honeypot Detection

**Symptoms:**
- Can't sell tokens
- High sell tax
- Blacklisted addresses

**Solutions:**
1. Implement pre-trade checks:
```python
async def check_honeypot(token_address):
    # Check sell tax
    sell_tax = await get_sell_tax(token_address)
    if sell_tax > MAX_SELL_TAX:
        raise SecurityError("High sell tax detected")
    
    # Check blacklist
    if await is_blacklisted(token_address):
        raise SecurityError("Token is blacklisted")
    
    # Check liquidity
    if not await has_sufficient_liquidity(token_address):
        raise SecurityError("Insufficient liquidity")
```

2. Monitor contract changes:
```python
async def monitor_contract(token_address):
    # Get initial code
    initial_code = web3.eth.get_code(token_address)
    
    while True:
        current_code = web3.eth.get_code(token_address)
        if current_code != initial_code:
            raise SecurityError("Contract code changed")
        await asyncio.sleep(1)
```

### 2. MEV Protection

**Symptoms:**
- Front-running
- Sandwich attacks
- High slippage

**Solutions:**
1. Use private transactions:
```python
async def send_private_tx(tx):
    # Use Flashbots
    flashbots = await FlashbotsProvider.create(web3)
    bundle = await flashbots.send_bundle([tx])
    return bundle
```

2. Implement slippage protection:
```python
async def protect_slippage(amount_in, amount_out_min):
    # Calculate expected output
    expected_output = await get_expected_output(amount_in)
    
    # Verify minimum output
    if amount_out_min < expected_output * (1 - MAX_SLIPPAGE):
        raise SecurityError("Slippage too high")
```

## 📊 Performance Issues

### 1. Slow Response Time

**Symptoms:**
- Delayed trades
- Missed opportunities
- High latency

**Solutions:**
1. Optimize RPC connection:
```python
# Use multiple RPC providers
rpc_providers = [
    Web3.HTTPProvider(url1),
    Web3.HTTPProvider(url2),
    Web3.HTTPProvider(url3)
]

# Implement load balancing
async def get_best_provider():
    latencies = await measure_latencies(rpc_providers)
    return rpc_providers[min(latencies)]
```

2. Implement caching:
```python
# Cache token data
token_cache = {}

async def get_token_data(address):
    if address in token_cache:
        return token_cache[address]
    
    data = await fetch_token_data(address)
    token_cache[address] = data
    return data
```

### 2. High Resource Usage

**Symptoms:**
- High CPU usage
- High memory usage
- Slow system response

**Solutions:**
1. Optimize memory usage:
```python
# Use generators
async def stream_events():
    async for event in event_stream:
        yield event

# Clear unused data
def clear_cache():
    token_cache.clear()
    price_cache.clear()
```

2. Implement rate limiting:
```python
# Rate limit API calls
async def rate_limited_call(func, *args):
    await asyncio.sleep(1)  # 1 second delay
    return await func(*args)
```

## 🔄 Common Errors

### 1. Configuration Errors

**Error:** "Invalid configuration"
**Solution:**
1. Check `.env` file:
```bash
# Verify all required variables
cat .env | grep -v "^#"
```

2. Validate configuration:
```python
def validate_config():
    required_vars = [
        'RPC_URL',
        'PRIVATE_KEY',
        'CHAIN_ID'
    ]
    
    for var in required_vars:
        if not os.getenv(var):
            raise ConfigError(f"Missing {var}")
```

### 2. Network Errors

**Error:** "Network error"
**Solution:**
1. Check network connection:
```python
async def check_network():
    try:
        await web3.eth.get_block_number()
        return True
    except Exception:
        return False
```

2. Implement retry logic:
```python
async def retry_operation(func, max_retries=3):
    for i in range(max_retries):
        try:
            return await func()
        except Exception as e:
            if i == max_retries - 1:
                raise
            await asyncio.sleep(2 ** i)
```

## 📝 Logging

### 1. Enable Debug Logging

```python
import logging

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('debug.log'),
        logging.StreamHandler()
    ]
)
```

### 2. Monitor Logs

```bash
# Monitor logs in real-time
tail -f debug.log

# Search for errors
grep ERROR debug.log

# Monitor specific component
grep "trading" debug.log
```

## 🔍 Debugging Tools

### 1. Web3 Debugging

```python
# Enable Web3 debug logging
import logging
logging.getLogger('web3').setLevel(logging.DEBUG)

# Monitor gas prices
async def monitor_gas():
    while True:
        gas = web3.eth.gas_price
        print(f"Current gas: {gas}")
        await asyncio.sleep(1)
```

### 2. Transaction Debugging

```python
# Debug transaction
async def debug_tx(tx_hash):
    # Get transaction
    tx = await web3.eth.get_transaction(tx_hash)
    
    # Get receipt
    receipt = await web3.eth.get_transaction_receipt(tx_hash)
    
    # Get trace
    trace = await web3.eth.trace_transaction(tx_hash)
    
    return {
        'transaction': tx,
        'receipt': receipt,
        'trace': trace
    }
```

## 📚 Additional Resources

- [Ethereum Stack Exchange](https://ethereum.stackexchange.com)
- [Web3.py Documentation](https://web3py.readthedocs.io)
- [OpenZeppelin Forum](https://forum.openzeppelin.com)
- [Discord Community](https://discord.gg/your-server) 