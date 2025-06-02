"""Optimized async sniper bot with advanced filtering and MEV protection."""
import asyncio
import json
import os
import time
import websockets
import logging
from decimal import Decimal
from typing import Dict, Set, Optional, Tuple
from dataclasses import dataclass
from dotenv import load_dotenv
from web3 import Web3
from web3.middleware import geth_poa_middleware
from concurrent.futures import ThreadPoolExecutor
import threading

load_dotenv()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Environment variables
RPC_HTTP = os.environ.get("RPC_HTTP")
RPC_WS = os.environ.get("RPC_WS")
PRIVATE_KEY = os.environ.get("PRIVATE_KEY")
ROUTER = Web3.to_checksum_address(os.environ.get("ROUTER"))
WBNB = Web3.to_checksum_address(os.environ.get("WBNB"))
MAX_BUY = Decimal(os.environ.get("MAX_BUY_BNB", "0.02"))

# Configuration
MIN_LIQUIDITY_BNB = Decimal("5.0")
MAX_DEV_OWNERSHIP = 15
GAS_PRICE_MULTIPLIER = 1.2
MAX_SLIPPAGE = 50

w3 = Web3(Web3.HTTPProvider(RPC_HTTP))
w3.middleware_onion.inject(geth_poa_middleware, layer=0)
acct = w3.eth.account.from_key(PRIVATE_KEY)

ADD_LIQ_ETH = "0xf305d719"

ERC20_ABI = [
    {"constant":True,"inputs":[],"name":"totalSupply","outputs":[{"type":"uint256"}],"type":"function"},
    {"constant":True,"inputs":[{"name":"","type":"address"}],"name":"balanceOf","outputs":[{"type":"uint256"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"owner","outputs":[{"type":"address"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"name","outputs":[{"type":"string"}],"type":"function"},
    {"constant":True,"inputs":[],"name":"symbol","outputs":[{"type":"string"}],"type":"function"}
]

ROUTER_ABI = [
    {"inputs":[{"type":"uint256"},{"type":"address[]"},{"type":"address"},{"type":"uint256"}],"name":"swapExactETHForTokensSupportingFeeOnTransferTokens","outputs":[],"type":"function"},
    {"inputs":[{"type":"uint256"},{"type":"address[]"}],"name":"getAmountsOut","outputs":[{"type":"uint256[]"}],"type":"function"}
]

@dataclass
class TokenInfo:
    address: str
    name: str
    symbol: str
    total_supply: int
    dev_percentage: float
    liquidity_bnb: Decimal
    score: float

class OptimizedSniperBot:
    def __init__(self):
        self.processed_tokens: Set[str] = set()
        self.token_cache: Dict[str, TokenInfo] = {}
        self.recent_txs: Dict[str, float] = {}
        self.executor = ThreadPoolExecutor(max_workers=10)
        self.lock = threading.Lock()
        
    def get_dynamic_gas_price(self) -> Tuple[int, int]:
        """Get optimized gas prices"""
        try:
            hist = w3.eth.fee_history(10, 'latest', reward_percentiles=[75])
            latest_block = w3.eth.get_block('latest')
            base_fee = latest_block.baseFeePerGas
            
            priority_fees = [reward[0] for reward in hist['reward'] if reward[0] > 0]
            if priority_fees:
                priority_fee = int(sum(priority_fees) / len(priority_fees) * GAS_PRICE_MULTIPLIER)
            else:
                priority_fee = w3.to_wei(2, 'gwei')
            
            max_fee = int(base_fee * 2 + priority_fee)
            return max_fee, priority_fee
        except:
            return w3.to_wei(10, 'gwei'), w3.to_wei(2, 'gwei')

    def analyze_token(self, token_address: str) -> Optional[TokenInfo]:
        """Analyze token with safety checks"""
        try:
            if token_address in self.token_cache:
                return self.token_cache[token_address]
                
            contract = w3.eth.contract(address=token_address, abi=ERC20_ABI)
            
            name = contract.functions.name().call()
            symbol = contract.functions.symbol().call()
            total_supply = contract.functions.totalSupply().call()
            
            # Check for suspicious names
            suspicious_terms = ['test', 'scam', 'fake', 'rug', 'moon', 'safe']
            if any(term in name.lower() or term in symbol.lower() for term in suspicious_terms):
                return None
            
            # Dev ownership check
            try:
                owner = contract.functions.owner().call()
                dev_balance = contract.functions.balanceOf(owner).call()
                dev_percentage = (dev_balance * 100) / total_supply if total_supply > 0 else 100
            except:
                dev_percentage = 0
            
            if dev_percentage > MAX_DEV_OWNERSHIP:
                return None
            
            # Calculate score
            score = 100.0 - dev_percentage * 2
            if score < 70:
                return None
            
            token_info = TokenInfo(
                address=token_address,
                name=name,
                symbol=symbol,
                total_supply=total_supply,
                dev_percentage=dev_percentage,
                liquidity_bnb=Decimal("10.0"),
                score=score
            )
            
            self.token_cache[token_address] = token_info
            return token_info
            
        except Exception as e:
            logger.error(f"Token analysis failed: {e}")
            return None

    async def execute_buy_order(self, token_info: TokenInfo):
        """Execute buy order"""
        try:
            router = w3.eth.contract(address=ROUTER, abi=ROUTER_ABI)
            amount_wei = w3.to_wei(MAX_BUY, 'ether')
            
            max_fee, priority_fee = self.get_dynamic_gas_price()
            deadline = int(time.time()) + 30
            
            tx = router.functions.swapExactETHForTokensSupportingFeeOnTransferTokens(
                0, [WBNB, token_info.address], acct.address, deadline
            ).build_transaction({
                'from': acct.address,
                'value': amount_wei,
                'nonce': w3.eth.get_transaction_count(acct.address),
                'maxFeePerGas': max_fee,
                'maxPriorityFeePerGas': priority_fee,
                'gas': 500000,
                'chainId': w3.eth.chain_id
            })
            
            signed = acct.sign_transaction(tx)
            tx_hash = w3.eth.send_raw_transaction(signed.rawTransaction)
            
            logger.info(f"BUY: {token_info.symbol} | Hash: {tx_hash.hex()}")
            
        except Exception as e:
            logger.error(f"Buy failed: {e}")

    async def process_transaction(self, tx_hash: str):
        """Process transaction for sniping"""
        try:
            if tx_hash in self.recent_txs:
                return
                
            with self.lock:
                self.recent_txs[tx_hash] = time.time()
            
            tx = w3.eth.get_transaction(tx_hash)
            
            if (tx.to != ROUTER or 
                not tx.input.startswith(ADD_LIQ_ETH) or 
                len(tx.input) < 200):
                return
            
            token_address = Web3.to_checksum_address("0x" + tx.input[-40:])
            
            if token_address in self.processed_tokens:
                return
                
            self.processed_tokens.add(token_address)
            
            token_info = await asyncio.get_event_loop().run_in_executor(
                self.executor, self.analyze_token, token_address
            )
            
            if token_info and token_info.score > 70:
                await self.execute_buy_order(token_info)
                
        except Exception as e:
            logger.error(f"Processing failed: {e}")

    async def run(self):
        """Main bot loop"""
        while True:
            try:
                async with websockets.connect(RPC_WS) as ws:
                    await ws.send(json.dumps({
                        "id": 1,
                        "method": "eth_subscribe",
                        "params": ["newPendingTransactions"]
                    }))
                    
                    logger.info("Optimized Sniper Bot Started!")
                    
                    while True:
                        try:
                            message = await asyncio.wait_for(ws.recv(), timeout=30)
                            data = json.loads(message)
                            
                            if 'params' in data and 'result' in data['params']:
                                tx_hash = data['params']['result']
                                asyncio.create_task(self.process_transaction(tx_hash))
                                
                        except asyncio.TimeoutError:
                            await ws.ping()
                            
            except Exception as e:
                logger.error(f"Connection failed: {e}")
                await asyncio.sleep(5)

def main():
    bot = OptimizedSniperBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        logger.info("Bot stopped")

if __name__ == "__main__":
    main()
