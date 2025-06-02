import os
import asyncio
import json
from web3 import Web3
from websockets import connect
from utils.secrets_loader import get_key

# Factory ABI snippet
FACTORY_ABI = [...]  # Add your actual PancakeFactory ABI here

async def listen_for_pools():
    w3 = Web3(Web3.WebsocketProvider(os.getenv("BSC_NODE")))
    factory = w3.eth.contract(address='0xcA143Ce32Fe78f1f7019d7d551a6402fC5350c73', abi=FACTORY_ABI)
    event_filter = factory.events.PairCreated.create_filter(fromBlock='latest')
    
    while True:
        for event in event_filter.get_new_entries():
            asyncio.create_task(execute_snipe(event['args']))

async def execute_snipe(pool_data):
    # FlashSniper contract interaction
    contract = w3.eth.contract(address=os.getenv("FLASH_SNIPER_ADDR"), abi=SNIPER_ABI)
    tx = contract.functions.snipe(
        pool_data['token0'],
        w3.toWei(0.1, 'ether')
    ).build_transaction({
        'from': w3.eth.account.from_key(get_key()).address,
        'nonce': w3.eth.get_transaction_count(w3.eth.account.from_key(get_key()).address)
    })
    # Send transaction with MEV protection
    signed_tx = w3.eth.account.sign_transaction(tx, private_key=get_key())
    tx_hash = w3.eth.send_raw_transaction(signed_tx.rawTransaction)

if __name__ == "__main__":
    asyncio.run(listen_for_pools())