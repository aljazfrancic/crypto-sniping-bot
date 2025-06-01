"""Minimal async sniper bot – listens for addLiquidityETH and buys via Router.
 Educational use only."""
import asyncio, json, os, time, websockets
from decimal import Decimal
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware

load_dotenv()

RPC_HTTP = os.environ.get("RPC_HTTP")
RPC_WS   = os.environ.get("RPC_WS")
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
ROUTER  = Web3.to_checksum_address(os.environ.get("ROUTER"))
WBNB    = Web3.to_checksum_address(os.environ.get("WBNB"))
MAX_BUY = Decimal(os.environ.get("MAX_BUY_BNB", "0.02"))

w3 = Web3(Web3.HTTPProvider(RPC_HTTP))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
acct = w3.eth.account.from_key(PRIVATE_KEY)

ADD_LIQ_ETH = "0xf305d719"  # addLiquidityETH(bytes,...)

ERC20_ABI = json.loads('[{"constant":true,"inputs":[],"name":"totalSupply","outputs":[{"type":"uint256"}],"type":"function"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"type":"uint256"}],"type":"function"},{"constant":true,"inputs":[],"name":"owner","outputs":[{"type":"address"}],"type":"function"}]')

def dev_holds_too_much(token):
    c = w3.eth.contract(address=token, abi=ERC20_ABI)
    try:
        total = c.functions.totalSupply().call()
        owner = c.functions.owner().call()
        bal   = c.functions.balanceOf(owner).call()
        return bal * 100 // total > 10
    except Exception:
        return True

def tip():
    hist = w3.eth.fee_history(20, 'latest', reward_percentiles=[95])
    return int(hist['reward'][0][0])

async def process(tx_hash):
    try: tx = w3.eth.get_transaction(tx_hash)
    except: return
    if tx.to != ROUTER or not tx.input.startswith(ADD_LIQ_ETH): return
    token = Web3.to_checksum_address("0x"+tx.input[-40:])
    if dev_holds_too_much(token): return
    await buy(token)

async def buy(token):
    router = w3.eth.contract(address=ROUTER, abi=[])
    amt = w3.to_wei(MAX_BUY, 'ether')
    deadline = int(time.time())+20
    bribe = tip()
    tx = router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
        0, [WBNB, token], acct.address, deadline
    ).build_transaction({
        'from': acct.address,
        'value': amt,
        'nonce': w3.eth.get_transaction_count(acct.address),
        'maxFeePerGas': w3.eth.get_block('latest').baseFeePerGas + bribe,
        'maxPriorityFeePerGas': bribe,
        'gas': 450000,
        'chainId': w3.eth.chain_id
    })
    signed = acct.sign_transaction(tx)
    try:
        h = w3.eth.send_raw_transaction(signed.rawTransaction)
        print("BUY", token, h.hex())
    except Exception as e:
        print("tx fail", e)

async def main():
    async with websockets.connect(RPC_WS) as ws:
        await ws.send(json.dumps({"id":1,"method":"eth_subscribe","params":["newPendingTransactions"]}))
        print("Listening mempool …")
        while True:
            msg = json.loads(await ws.recv())
            if 'params' in msg:
                await process(msg['params']['result'])

if __name__ == "__main__":
    asyncio.run(main())