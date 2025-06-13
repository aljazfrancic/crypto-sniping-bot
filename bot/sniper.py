#!/usr/bin/env python3
"""
Crypto Sniper Bot - Main Entry Point
Monitors DEX for new pairs and executes automated trading
"""

import asyncio
import logging
import signal
import sys
from datetime import datetime
from web3 import Web3
from web3.middleware import geth_poa_middleware  # web3.py 6.x compatible import

from config import Config
from blockchain import BlockchainInterface
from trading import TradingEngine
from honeypot import HoneypotChecker

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.FileHandler("sniper_bot.log"), logging.StreamHandler()],
)
logger = logging.getLogger(__name__)


class SniperBot:
    """Main bot class that orchestrates all components"""

    def __init__(self, config: Config):
        self.config = config
        self.running = True
        self.w3 = self._setup_web3()
        self.blockchain = BlockchainInterface(self.w3, config)
        self.trading = TradingEngine(self.blockchain, config)
        self.honeypot_checker = HoneypotChecker(self.w3, config)
        self.positions = {}
        self.monitored_pairs = set()
        self.router_address = None  # Initialize with None or appropriate default

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info("Shutdown signal received, stopping bot...")
        self.running = False

    def _setup_web3(self):
        """Initialize Web3 connection"""
        if self.config.RPC_URL.startswith("ws"):
            provider = Web3.WebsocketProvider(
                self.config.RPC_URL,
                websocket_timeout=60,
                websocket_kwargs={
                    "max_size": 1024 * 1024 * 10
                },  # 10MB max message size
            )
        else:
            provider = Web3.HTTPProvider(self.config.RPC_URL)

        w3 = Web3(provider)

        # Add middleware for PoA chains (BSC, Polygon, etc.)
        w3.middleware_onion.inject(geth_poa_middleware, layer=0)

        # Verify connection
        if not w3.is_connected():
            raise Exception("Failed to connect to blockchain node")

        logger.info(f"Connected to blockchain - Chain ID: {w3.eth.chain_id}")
        return w3

    async def listen_for_pairs(self):
        """Listen for PairCreated events from Uniswap/PancakeSwap factory"""
        factory_abi = self.blockchain.load_abi("factory")
        factory = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.config.FACTORY_ADDRESS),
            abi=factory_abi,
        )

        # Get current block
        current_block = self.w3.eth.block_number

        # Create event filter
        event_filter = factory.events.PairCreated.create_filter(fromBlock=current_block)

        logger.info(f"Listening for new pairs from block {current_block}...")

        while self.running:
            try:
                # Get new events
                for event in event_filter.get_new_entries():
                    await self._handle_new_pair(event)

                # Small delay to prevent overwhelming the node
                await asyncio.sleep(1)

            except Exception as e:
                logger.error(f"Error in event loop: {e}")
                await asyncio.sleep(5)

                # Recreate filter if connection lost
                if not self.w3.is_connected():
                    logger.warning("Connection lost, attempting to reconnect...")
                    self.w3 = self._setup_web3()
                    event_filter = factory.events.PairCreated.create_filter(
                        fromBlock="latest"
                    )

    async def _handle_new_pair(self, event):
        """Handle new pair creation event"""
        try:
            token0 = event["args"]["token0"]
            token1 = event["args"]["token1"]
            pair = event["args"]["pair"]

            # Skip if we've already seen this pair
            if pair in self.monitored_pairs:
                return

            self.monitored_pairs.add(pair)

            # Determine which token is the target (not WETH/WBNB)
            weth = self.config.WETH_ADDRESS.lower()
            if token0.lower() == weth:
                target_token = token1
                is_token0 = False
            elif token1.lower() == weth:
                target_token = token0
                is_token0 = True
            else:
                # Neither token is WETH, skip this pair
                logger.debug(f"Skipping pair {pair} - no WETH")
                return

            logger.info(f"New pair detected: {pair}")
            logger.info(f"Target token: {target_token}")

            # Perform safety checks
            if await self._is_token_safe(target_token, pair):
                await self._execute_buy(target_token, pair, is_token0)
            else:
                logger.warning(f"Token {target_token} failed safety checks")

        except Exception as e:
            logger.error(f"Error handling new pair: {e}")

    async def _is_token_safe(self, token_address, pair_address):
        """Perform safety checks on token"""
        try:
            # Check if honeypot detection is enabled
            if self.config.CHECK_HONEYPOT:
                is_honeypot = await self.honeypot_checker.check(token_address)
                if is_honeypot:
                    logger.warning(f"Token {token_address} detected as honeypot")
                    return False

            # Check liquidity
            liquidity_eth = await self.blockchain.get_pair_liquidity(pair_address)
            if liquidity_eth < self.config.MIN_LIQUIDITY:
                logger.warning(
                    f"Insufficient liquidity: {liquidity_eth:.4f} ETH < {self.config.MIN_LIQUIDITY} ETH"
                )
                return False

            # Check if contract is verified (basic check)
            code = self.w3.eth.get_code(token_address)
            if len(code) <= 2:  # '0x' means no code
                logger.warning(f"Token {token_address} has no contract code")
                return False

            logger.info(f"Token {token_address} passed safety checks")
            return True

        except Exception as e:
            logger.error(f"Error checking token safety: {e}")
            return False

    async def _execute_buy(self, token_address, pair_address, is_token0):
        """Execute buy transaction"""
        try:
            # Get current token price
            price = await self.blockchain.get_token_price(pair_address, is_token0)
            logger.info(f"Current price: {price:.8f} ETH per token")

            # Calculate tokens expected
            expected_tokens = self.config.BUY_AMOUNT / price
            min_tokens = expected_tokens * (1 - self.config.SLIPPAGE / 100)

            logger.info(
                f"Attempting to buy ~{expected_tokens:.2f} tokens with {self.config.BUY_AMOUNT} ETH"
            )

            # Execute buy through sniper contract
            tx_hash = await self.trading.buy_token(
                token_address, self.config.BUY_AMOUNT, min_tokens
            )

            if tx_hash:
                logger.info(f"Buy transaction sent: {tx_hash}")

                # Store position info
                self.positions[token_address] = {
                    "pair": pair_address,
                    "is_token0": is_token0,
                    "buy_tx": tx_hash,
                    "buy_amount": self.config.BUY_AMOUNT,
                    "buy_price": price,
                    "expected_tokens": expected_tokens,
                    "buy_time": datetime.now(),
                    "status": "bought",
                }

                # Start monitoring for sell conditions
                if self.config.AUTO_SELL:
                    asyncio.create_task(self._monitor_position(token_address))

        except Exception as e:
            logger.error(f"Error executing buy: {e}")

    async def _monitor_position(self, token_address):
        """Monitor position for sell conditions"""
        position = self.positions.get(token_address)
        if not position:
            return

        logger.info(f"Monitoring position for token {token_address}")

        while self.running and position["status"] == "bought":
            try:
                # Get current price
                current_price = await self.blockchain.get_token_price(
                    position["pair"], position["is_token0"]
                )

                # Calculate profit/loss percentage
                price_change = (
                    (current_price - position["buy_price"]) / position["buy_price"]
                ) * 100

                logger.debug(f"Token {token_address} price change: {price_change:.2f}%")

                # Check profit target
                if price_change >= self.config.PROFIT_TARGET:
                    logger.info(
                        f"Profit target reached for {token_address}: {price_change:.2f}%"
                    )
                    await self._execute_sell(token_address, "profit_target")
                    break

                # Check stop loss
                elif price_change <= -self.config.STOP_LOSS:
                    logger.warning(
                        f"Stop loss triggered for {token_address}: {price_change:.2f}%"
                    )
                    await self._execute_sell(token_address, "stop_loss")
                    break

                # Wait before next check
                await asyncio.sleep(5)

            except Exception as e:
                logger.error(f"Error monitoring position: {e}")
                await asyncio.sleep(10)

    async def _execute_sell(self, token_address, reason):
        """Execute sell transaction"""
        try:
            position = self.positions.get(token_address)
            if not position or position["status"] != "bought":
                return

            # Get token balance
            balance = await self.blockchain.get_token_balance(token_address)
            if balance == 0:
                logger.warning(f"No tokens to sell for {token_address}")
                position["status"] = "sold"
                return

            logger.info(f"Selling {balance} tokens - Reason: {reason}")

            # Execute sell
            tx_hash = await self.trading.sell_token(
                token_address, balance, 0  # Will use slippage calculation in contract
            )

            if tx_hash:
                logger.info(f"Sell transaction sent: {tx_hash}")
                position["sell_tx"] = tx_hash
                position["sell_time"] = datetime.now()
                position["sell_reason"] = reason
                position["status"] = "sold"

        except Exception as e:
            logger.error(f"Error executing sell: {e}")

    async def display_stats(self):
        """Periodically display bot statistics"""
        while self.running:
            try:
                await asyncio.sleep(60)  # Every minute

                total_positions = len(self.positions)
                bought = sum(
                    1 for p in self.positions.values() if p["status"] == "bought"
                )
                sold = sum(1 for p in self.positions.values() if p["status"] == "sold")

                logger.info(
                    f"Bot Statistics - Total: {total_positions}, Active: {bought}, Sold: {sold}"
                )

                # Display current positions
                for token, position in self.positions.items():
                    if position["status"] == "bought":
                        current_price = await self.blockchain.get_token_price(
                            position["pair"], position["is_token0"]
                        )
                        pnl = (
                            (current_price - position["buy_price"])
                            / position["buy_price"]
                        ) * 100
                        logger.info(f"Active position {token[:8]}... - P&L: {pnl:.2f}%")

            except Exception as e:
                logger.error(f"Error displaying stats: {e}")

    async def run(self):
        """Main bot loop"""
        logger.info("=" * 50)
        logger.info("Starting Crypto Sniper Bot")
        logger.info(f"Chain ID: {self.config.CHAIN_ID}")
        logger.info(f"Buy Amount: {self.config.BUY_AMOUNT} ETH")
        logger.info(f"Slippage: {self.config.SLIPPAGE}%")
        logger.info(f"Profit Target: {self.config.PROFIT_TARGET}%")
        logger.info(f"Stop Loss: {self.config.STOP_LOSS}%")
        logger.info("=" * 50)

        # Verify contract deployment
        if not await self.blockchain.verify_sniper_contract():
            logger.error("Sniper contract not deployed or invalid")
            return

        # Start background tasks
        tasks = [
            asyncio.create_task(self.listen_for_pairs()),
            asyncio.create_task(self.display_stats()),
        ]

        try:
            await asyncio.gather(*tasks)
        except Exception as e:
            logger.error(f"Bot error: {e}")
        finally:
            logger.info("Bot stopped")


async def main():
    """Entry point"""
    try:
        config = Config()
        bot = SniperBot(config)
        await bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
