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
from typing import Dict, Set, Optional
from web3 import Web3
from web3.middleware import ExtraDataToPOAMiddleware

from bot.config import Config
from bot.blockchain import BlockchainInterface
from bot.trading import TradingEngine
from bot.honeypot import HoneypotDetector
from bot.utils import (
    RateLimiter,
    with_retry,
    RetryConfig,
    NotificationManager,
    PerformanceMonitor,
    format_number,
)
from bot.exceptions import (
    ConfigurationError,
    BlockchainError,
    TradingError,
    SecurityError,
)


# Configure logging with better formatting
def setup_logging(log_level: str = "INFO"):
    """Setup enhanced logging configuration."""
    log_format = (
        "%(asctime)s - %(name)s - %(levelname)s - "
        "[%(filename)s:%(lineno)d] - %(message)s"
    )

    logging.basicConfig(
        level=getattr(logging, log_level),
        format=log_format,
        handlers=[
            logging.FileHandler("sniper_bot.log"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    # Reduce noise from third-party libraries
    logging.getLogger("web3").setLevel(logging.WARNING)
    logging.getLogger("urllib3").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)


logger = logging.getLogger(__name__)


class SniperBot:
    """Enhanced main bot class with improved reliability and performance."""

    def __init__(self, config: Config):
        """Initialize the sniper bot with enhanced features.

        Args:
            config: Bot configuration
        """
        self.config = config
        self.running = True
        self.w3 = None
        self.blockchain = None
        self.trading = None
        self.honeypot_detector = None

        # Enhanced tracking
        self.positions: Dict[str, Dict] = {}
        self.monitored_pairs: Set[str] = set()
        self.failed_pairs: Set[str] = set()

        # Performance and reliability components
        self.rate_limiter = RateLimiter(
            max_calls=self.config.max_rpc_calls_per_second, time_window=1.0
        )
        self.performance_monitor = PerformanceMonitor()
        self.notification_manager = NotificationManager(self.config.webhook_url)

        # Statistics
        self.stats = {
            "pairs_detected": 0,
            "pairs_analyzed": 0,
            "trades_attempted": 0,
            "trades_successful": 0,
            "trades_failed": 0,
            "honeypots_detected": 0,
            "total_profit_loss": 0.0,
        }

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Shutdown signal {signum} received, stopping bot...")
        self.running = False

    async def initialize(self):
        """Initialize all bot components asynchronously."""
        try:
            logger.info("🚀 Initializing Crypto Sniper Bot...")

            # Setup Web3 connection with retry logic
            await self._setup_web3_connection()

            # Initialize blockchain interface
            self.blockchain = BlockchainInterface(self.config)
            await self.blockchain.initialize()

            # Initialize trading engine
            self.trading = TradingEngine(self.blockchain, self.config)

            # Initialize honeypot detector
            self.honeypot_detector = HoneypotDetector(self.blockchain)

            # Validate environment
            validation_result = self.config.validate_environment()
            if not validation_result["valid"]:
                for error in validation_result["errors"]:
                    logger.error(f"❌ {error}")
                raise ConfigurationError("Environment validation failed")

            logger.info(f"✅ Connected to {validation_result['network']}")
            logger.info("✅ Bot initialization completed successfully")

            # Send startup notification
            await self.notification_manager.send_notification(
                f"🤖 Sniper Bot started on {validation_result['network']}",
                level="info",
                data={"network": validation_result["network"]},
            )

        except Exception as e:
            logger.error(f"❌ Failed to initialize bot: {e}")
            raise

    @with_retry(RetryConfig(max_attempts=3, base_delay=2.0))
    async def _setup_web3_connection(self):
        """Setup Web3 connection with enhanced error handling and backup RPCs."""
        # Try primary RPC first
        try:
            self.w3 = await self._create_web3_connection(self.config.rpc_url)
            logger.info(f"✅ Connected to primary RPC")
            return
        except Exception as e:
            logger.warning(f"Primary RPC failed: {e}")

        # Try backup RPCs
        for i, backup_url in enumerate(self.config.backup_rpc_urls):
            try:
                logger.info(f"Trying backup RPC {i+1}...")
                self.w3 = await self._create_web3_connection(backup_url)
                logger.info(f"✅ Connected to backup RPC {i+1}")
                return
            except Exception as e:
                logger.warning(f"Backup RPC {i+1} failed: {e}")

        raise BlockchainError("All RPC endpoints failed")

    async def _create_web3_connection(self, rpc_url: str) -> Web3:
        """Create and validate a Web3 connection."""
        if rpc_url.startswith("ws"):
            provider = Web3.WebsocketProvider(
                rpc_url,
                websocket_timeout=60,
                websocket_kwargs={"max_size": 1024 * 1024 * 10},  # 10MB
            )
        else:
            provider = Web3.HTTPProvider(rpc_url)

        w3 = Web3(provider)

        # Add middleware for PoA chains
        w3.middleware_onion.inject(ExtraDataToPOAMiddleware, layer=0)

        # Test connection
        if not w3.is_connected():
            raise BlockchainError("Failed to connect to RPC endpoint")

        # Verify chain ID
        actual_chain_id = w3.eth.chain_id
        if actual_chain_id != self.config.chain_id:
            raise BlockchainError(
                f"Chain ID mismatch: expected {self.config.chain_id}, "
                f"got {actual_chain_id}"
            )

        return w3

    async def listen_for_pairs(self):
        """Enhanced pair listening with better error handling and performance monitoring."""
        factory_abi = self.blockchain.load_abi("factory")
        factory = self.w3.eth.contract(
            address=Web3.to_checksum_address(self.config.factory_address),
            abi=factory_abi,
        )

        current_block = self.w3.eth.block_number
        logger.info(f"📡 Listening for new pairs from block {current_block}...")

        # Create event filter with retry logic
        event_filter = None
        reconnect_attempts = 0
        max_reconnect_attempts = 5

        while self.running:
            try:
                # Create or recreate event filter if needed
                if event_filter is None:
                    await self.rate_limiter.acquire()
                    event_filter = factory.events.PairCreated.create_filter(
                        fromBlock=current_block
                    )
                    reconnect_attempts = 0

                # Get new events with rate limiting
                await self.rate_limiter.acquire()

                self.performance_monitor.start_timer("event_processing")
                new_events = event_filter.get_new_entries()

                for event in new_events:
                    self.stats["pairs_detected"] += 1
                    asyncio.create_task(self._handle_new_pair_async(event))

                self.performance_monitor.end_timer("event_processing")

                # Small delay to prevent overwhelming the node
                await asyncio.sleep(0.5)

            except ConnectionError as e:
                reconnect_attempts += 1
                logger.error(
                    f"Connection error ({reconnect_attempts}/{max_reconnect_attempts}): {e}"
                )

                if reconnect_attempts >= max_reconnect_attempts:
                    logger.error(
                        "Max reconnection attempts reached, switching to backup RPC"
                    )
                    await self._setup_web3_connection()
                    reconnect_attempts = 0

                event_filter = None
                await asyncio.sleep(min(10 * reconnect_attempts, 60))

            except Exception as e:
                logger.error(f"Unexpected error in event loop: {e}")
                event_filter = None
                await asyncio.sleep(5)

    async def _handle_new_pair_async(self, event):
        """Handle new pair creation event asynchronously with comprehensive safety checks."""
        try:
            self.performance_monitor.start_timer("pair_analysis")

            # Extract pair information
            token0 = event["args"]["token0"]
            token1 = event["args"]["token1"]
            pair = event["args"]["pair"]

            # Skip if already processed or failed
            if pair in self.monitored_pairs or pair in self.failed_pairs:
                return

            self.monitored_pairs.add(pair)
            self.stats["pairs_analyzed"] += 1

            # Determine target token (non-WETH token)
            weth = self.config.weth_address.lower()
            if token0.lower() == weth:
                target_token = token1
                is_token0 = False
            elif token1.lower() == weth:
                target_token = token0
                is_token0 = True
            else:
                logger.debug(f"Skipping pair {pair} - no WETH pairing")
                return

            logger.info(f"🔍 Analyzing new pair: {pair}")
            logger.info(f"Target token: {target_token}")

            # Comprehensive safety analysis
            safety_result = await self._comprehensive_safety_check(target_token, pair)

            if safety_result["is_safe"]:
                logger.info(f"✅ Token {target_token} passed all safety checks")
                await self._execute_buy_strategy(
                    target_token, pair, is_token0, safety_result
                )
            else:
                logger.warning(
                    f"❌ Token {target_token} failed safety checks: {safety_result['reason']}"
                )
                self.failed_pairs.add(pair)

                if safety_result.get("is_honeypot", False):
                    self.stats["honeypots_detected"] += 1

            self.performance_monitor.end_timer("pair_analysis")

        except Exception as e:
            logger.error(
                f"Error handling new pair {event.get('args', {}).get('pair', 'unknown')}: {e}"
            )
            self.failed_pairs.add(event.get("args", {}).get("pair", ""))

    async def _comprehensive_safety_check(
        self, token_address: str, pair_address: str
    ) -> Dict:
        """Perform comprehensive safety checks on a token."""
        result = {
            "is_safe": False,
            "reason": "",
            "confidence": 0.0,
            "checks": {},
        }

        try:
            # Check 1: Contract code validation
            await self.rate_limiter.acquire()
            code = self.w3.eth.get_code(token_address)
            if len(code) <= 2:
                result["reason"] = "No contract code"
                return result
            result["checks"]["has_code"] = True

            # Check 2: Honeypot detection
            if self.config.check_honeypot:
                is_honeypot = await self.honeypot_detector.check(token_address)
                result["checks"]["honeypot"] = not is_honeypot
                result["is_honeypot"] = is_honeypot
                if is_honeypot:
                    result["reason"] = "Honeypot detected"
                    return result

            # Check 3: Liquidity verification
            await self.rate_limiter.acquire()
            liquidity_eth = await self.blockchain.get_pair_liquidity(pair_address)
            min_liquidity = self.config.min_liquidity
            result["checks"]["liquidity"] = liquidity_eth >= min_liquidity

            if liquidity_eth < min_liquidity:
                result["reason"] = (
                    f"Insufficient liquidity: {format_number(liquidity_eth)} < {format_number(min_liquidity)} ETH"
                )
                return result

            # Check 4: Token information validation
            token_info = await self._get_token_info(token_address)
            result["checks"]["token_info"] = token_info is not None

            if not token_info:
                result["reason"] = "Failed to get token information"
                return result

            # All checks passed
            result["is_safe"] = True
            result["confidence"] = 0.8  # Base confidence
            result["token_info"] = token_info
            result["liquidity_eth"] = liquidity_eth

            return result

        except Exception as e:
            result["reason"] = f"Safety check error: {str(e)}"
            return result

    async def _get_token_info(self, token_address: str) -> Optional[Dict]:
        """Get token information with error handling."""
        try:
            erc20_abi = self.config.get_abi("erc20")
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address), abi=erc20_abi
            )

            # Get basic token info with timeout
            name = symbol = "UNKNOWN"
            decimals = 18
            total_supply = 0

            try:
                name = contract.functions.name().call()
            except:
                pass

            try:
                symbol = contract.functions.symbol().call()
            except:
                pass

            try:
                decimals = contract.functions.decimals().call()
            except:
                pass

            try:
                total_supply = contract.functions.totalSupply().call()
            except:
                pass

            return {
                "name": name,
                "symbol": symbol,
                "decimals": decimals,
                "total_supply": total_supply,
                "address": token_address,
            }

        except Exception as e:
            logger.error(f"Failed to get token info for {token_address}: {e}")
            return None

    async def _execute_buy_strategy(
        self, token_address: str, pair_address: str, is_token0: bool, safety_data: Dict
    ):
        """Execute buy strategy with enhanced error handling and position tracking."""
        try:
            self.stats["trades_attempted"] += 1
            self.performance_monitor.start_timer("trade_execution")

            logger.info(
                f"💰 Executing buy for {safety_data['token_info']['symbol']} ({token_address})"
            )

            # Calculate buy amount based on available balance and risk management
            buy_amount = min(
                self.config.buy_amount, await self._get_available_balance() * 0.1
            )  # Max 10% of balance

            if buy_amount <= 0:
                logger.warning("Insufficient balance for trade")
                return

            # Execute buy transaction
            tx_hash = await self.trading.buy_token(
                token_address, buy_amount, self.config.slippage
            )

            if tx_hash:
                logger.info(f"✅ Buy transaction sent: {tx_hash}")

                # Track position
                self.positions[token_address] = {
                    "symbol": safety_data["token_info"]["symbol"],
                    "pair_address": pair_address,
                    "buy_tx": tx_hash,
                    "buy_amount": buy_amount,
                    "buy_time": datetime.now(),
                    "status": "pending",
                }

                self.stats["trades_successful"] += 1

                # Send success notification
                await self.notification_manager.send_notification(
                    f"🎯 Successfully bought {safety_data['token_info']['symbol']} for {format_number(buy_amount)} ETH",
                    level="success",
                    data={
                        "token": safety_data["token_info"]["symbol"],
                        "amount": buy_amount,
                        "tx_hash": tx_hash,
                    },
                )

                # Start position monitoring
                if self.config.auto_sell:
                    asyncio.create_task(self._monitor_position(token_address))

            else:
                logger.error("Buy transaction failed")
                self.stats["trades_failed"] += 1

            self.performance_monitor.end_timer("trade_execution")

        except Exception as e:
            logger.error(f"Failed to execute buy for {token_address}: {e}")
            self.stats["trades_failed"] += 1

            # Send error notification
            await self.notification_manager.send_notification(
                f"❌ Buy failed for {safety_data.get('token_info', {}).get('symbol', 'UNKNOWN')}: {str(e)}",
                level="error",
                data={"token_address": token_address, "error": str(e)},
            )

    async def _get_available_balance(self) -> float:
        """Get available ETH balance."""
        try:
            await self.rate_limiter.acquire()
            balance_wei = self.w3.eth.get_balance(
                self.w3.eth.default_account or self.blockchain.account.address
            )
            return self.w3.from_wei(balance_wei, "ether")
        except Exception as e:
            logger.error(f"Failed to get balance: {e}")
            return 0.0

    async def _monitor_position(self, token_address: str):
        """Monitor position for profit/loss and auto-sell conditions."""
        if token_address not in self.positions:
            return

        position = self.positions[token_address]
        logger.info(f"📊 Monitoring position: {position['symbol']}")

        try:
            while self.running and position["status"] != "sold":
                await asyncio.sleep(30)  # Check every 30 seconds

                # Get current price and calculate P&L
                current_price = await self._get_token_price(token_address)
                if current_price <= 0:
                    continue

                # Calculate profit/loss percentage
                # This is simplified - in reality you'd need to track exact amounts
                profit_loss = (
                    (current_price - position.get("entry_price", current_price))
                    / position.get("entry_price", current_price)
                ) * 100

                # Check sell conditions
                should_sell = False
                sell_reason = ""

                if profit_loss >= self.config.profit_target:
                    should_sell = True
                    sell_reason = f"Profit target reached: {profit_loss:.2f}%"
                elif profit_loss <= -self.config.stop_loss:
                    should_sell = True
                    sell_reason = f"Stop loss triggered: {profit_loss:.2f}%"

                if should_sell:
                    logger.info(f"🔔 {sell_reason} for {position['symbol']}")
                    await self._execute_sell(token_address, sell_reason)
                    break

        except Exception as e:
            logger.error(f"Error monitoring position {token_address}: {e}")

    async def _get_token_price(self, token_address: str) -> float:
        """Get current token price."""
        try:
            return await self.trading.get_position(token_address).get(
                "current_price", 0.0
            )
        except Exception as e:
            logger.error(f"Failed to get price for {token_address}: {e}")
            return 0.0

    async def _execute_sell(self, token_address: str, reason: str):
        """Execute sell order with error handling."""
        try:
            if token_address not in self.positions:
                return

            position = self.positions[token_address]
            logger.info(f"💸 Selling {position['symbol']}: {reason}")

            # Get token balance
            balance = await self._get_token_balance(token_address)
            if balance <= 0:
                logger.warning(f"No balance to sell for {token_address}")
                return

            # Execute sell
            tx_hash = await self.trading.sell_token(
                token_address, balance, 0
            )  # Market sell

            if tx_hash:
                position["status"] = "sold"
                position["sell_tx"] = tx_hash
                position["sell_reason"] = reason
                position["sell_time"] = datetime.now()

                logger.info(f"✅ Sell transaction sent: {tx_hash}")

                # Send notification
                await self.notification_manager.send_notification(
                    f"💰 Sold {position['symbol']}: {reason}",
                    level="info",
                    data={
                        "token": position["symbol"],
                        "reason": reason,
                        "tx_hash": tx_hash,
                    },
                )

        except Exception as e:
            logger.error(f"Failed to sell {token_address}: {e}")

    async def _get_token_balance(self, token_address: str) -> int:
        """Get token balance for the bot's address."""
        try:
            erc20_abi = self.config.get_abi("erc20")
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address), abi=erc20_abi
            )

            balance = contract.functions.balanceOf(
                self.blockchain.account.address
            ).call()
            return balance

        except Exception as e:
            logger.error(f"Failed to get token balance for {token_address}: {e}")
            return 0

    async def display_stats(self):
        """Display enhanced bot statistics."""
        while self.running:
            try:
                logger.info("📊 === Bot Statistics ===")
                logger.info(f"Pairs detected: {self.stats['pairs_detected']}")
                logger.info(f"Pairs analyzed: {self.stats['pairs_analyzed']}")
                logger.info(f"Trades attempted: {self.stats['trades_attempted']}")
                logger.info(f"Trades successful: {self.stats['trades_successful']}")
                logger.info(f"Trades failed: {self.stats['trades_failed']}")
                logger.info(f"Honeypots detected: {self.stats['honeypots_detected']}")
                logger.info(
                    f"Active positions: {len([p for p in self.positions.values() if p['status'] != 'sold'])}"
                )

                # Performance stats
                perf_stats = self.performance_monitor.get_stats()
                if perf_stats:
                    logger.info("⚡ Performance Stats:")
                    for operation, stats in perf_stats.items():
                        logger.info(
                            f"  {operation}: avg {stats['average']:.3f}s, count {stats['count']}"
                        )

                await asyncio.sleep(300)  # Every 5 minutes

            except Exception as e:
                logger.error(f"Error displaying stats: {e}")
                await asyncio.sleep(60)

    async def run(self):
        """Enhanced main run loop with better error handling and graceful shutdown."""
        try:
            logger.info("🚀 Starting Crypto Sniper Bot...")

            # Initialize all components
            await self.initialize()

            # Start concurrent tasks
            tasks = [
                asyncio.create_task(self.listen_for_pairs()),
                asyncio.create_task(self.display_stats()),
            ]

            logger.info("✅ Bot is running! Press Ctrl+C to stop.")

            # Wait for tasks or shutdown signal
            await asyncio.gather(*tasks, return_exceptions=True)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received")
        except Exception as e:
            logger.error(f"Fatal error in main loop: {e}")
        finally:
            await self._cleanup()

    async def _cleanup(self):
        """Cleanup resources and save state."""
        logger.info("🧹 Cleaning up...")

        self.running = False

        # Close notification manager
        await self.notification_manager.close()

        # Save final stats
        logger.info("📊 Final Statistics:")
        for key, value in self.stats.items():
            logger.info(f"  {key}: {value}")

        # Send shutdown notification
        await self.notification_manager.send_notification(
            "🛑 Sniper Bot shutting down", level="info", data=self.stats
        )

        logger.info("✅ Cleanup completed")


async def main():
    """Enhanced main function with better error handling."""
    try:
        # Load configuration
        config = Config()

        # Setup logging
        setup_logging(config.log_level)

        # Create and run bot
        bot = SniperBot(config)
        await bot.run()

    except ConfigurationError as e:
        logger.error(f"❌ Configuration error: {e}")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
