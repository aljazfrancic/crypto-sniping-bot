"""
Enhanced Blockchain Interface Layer
Handles all Web3 interactions and contract calls with improved reliability
"""

import json
import os
import asyncio
from typing import Optional, Dict, Any, List
from web3 import Web3
from web3.contract import Contract
from eth_account import Account
import logging
from web3.exceptions import ContractLogicError, TransactionNotFound, Web3Exception
from .config import Config
from .utils import RateLimiter, with_retry, RetryConfig, Web3Utils, CircuitBreaker
from .exceptions import BlockchainError, ConnectionError

logger = logging.getLogger(__name__)


class BlockchainInterface:
    """Enhanced blockchain interface with improved reliability and performance."""

    def __init__(self, config: Config):
        """Initialize blockchain interface.

        Args:
            config: Configuration
        """
        self.config = config
        self.w3 = None  # Will be initialized in async method
        self.account = Account.from_key(config.private_key)
        self._abi_cache = {}
        self._contract_cache = {}

        # Enhanced reliability features
        self.rate_limiter = RateLimiter(
            max_calls=config.max_rpc_calls_per_second, time_window=1.0
        )
        self.circuit_breaker = CircuitBreaker(failure_threshold=5, timeout=60.0)

        # Connection health monitoring
        self._last_health_check = 0
        self._health_check_interval = 30  # seconds
        self._connection_failures = 0

    async def initialize(self):
        """Initialize the blockchain interface asynchronously."""
        try:
            # Setup Web3 connection
            await self._setup_connection()

            # Verify connection and chain
            await self._verify_connection()

            logger.info(
                f"✅ Blockchain interface initialized for chain {self.config.chain_id}"
            )

        except Exception as e:
            logger.error(f"Failed to initialize blockchain interface: {e}")
            raise BlockchainError(f"Initialization failed: {e}")

    @with_retry(RetryConfig(max_attempts=3, base_delay=2.0))
    async def _setup_connection(self):
        """Setup Web3 connection with retry logic."""
        # Try primary RPC
        try:
            self.w3 = Web3(Web3.HTTPProvider(self.config.rpc_url))
            if self.w3.is_connected():
                logger.info("Connected to primary RPC")
                return
        except Exception as e:
            logger.warning(f"Primary RPC failed: {e}")

        # Try backup RPCs
        for i, backup_url in enumerate(self.config.backup_rpc_urls):
            try:
                logger.info(f"Trying backup RPC {i+1}...")
                self.w3 = Web3(Web3.HTTPProvider(backup_url))
                if self.w3.is_connected():
                    logger.info(f"Connected to backup RPC {i+1}")
                    return
            except Exception as e:
                logger.warning(f"Backup RPC {i+1} failed: {e}")

        raise ConnectionError("All RPC endpoints failed")

    async def _verify_connection(self):
        """Verify connection and chain ID."""
        if not self.w3 or not self.w3.is_connected():
            raise ConnectionError("Not connected to any RPC endpoint")

        # Verify chain ID
        actual_chain_id = self.w3.eth.chain_id
        if actual_chain_id != self.config.chain_id:
            raise BlockchainError(
                f"Chain ID mismatch: expected {self.config.chain_id}, got {actual_chain_id}"
            )

        # Test a simple call
        await self.rate_limiter.acquire()
        block_number = self.w3.eth.block_number
        logger.info(
            f"Connected to chain {actual_chain_id}, latest block: {block_number}"
        )

    async def health_check(self) -> bool:
        """Perform connection health check."""
        try:
            current_time = asyncio.get_event_loop().time()

            # Only check if enough time has passed
            if current_time - self._last_health_check < self._health_check_interval:
                return True

            self._last_health_check = current_time

            if not self.w3 or not self.w3.is_connected():
                self._connection_failures += 1
                return False

            # Test with a simple call
            await self.rate_limiter.acquire()
            self.w3.eth.block_number

            # Reset failure count on success
            self._connection_failures = 0
            return True

        except Exception as e:
            self._connection_failures += 1
            logger.warning(f"Health check failed: {e}")

            # Auto-reconnect if too many failures
            if self._connection_failures >= 3:
                logger.error("Multiple health check failures, attempting reconnect...")
                await self._setup_connection()

            return False

    def load_abi(self, name: str) -> list:
        """Load ABI from file with caching"""
        if name in self._abi_cache:
            return self._abi_cache[name]

        abi_mapping = {
            "sniper": "Sniper.json",
            "factory": "UniswapV2Factory.json",
            "pair": "UniswapV2Pair.json",
            "router": "UniswapV2Router02.json",
            "erc20": "ERC20.json",
        }

        filename = abi_mapping.get(name)
        if not filename:
            raise ValueError(f"Unknown ABI name: {name}")

        # Try multiple paths
        paths = [
            f"./abi/{filename}",
            f"./artifacts/contracts/{name}.sol/{filename}",
            f"./build/contracts/{filename}",
        ]

        for path in paths:
            if os.path.exists(path):
                with open(path, "r") as f:
                    data = json.load(f)
                    # Handle both Hardhat and Truffle formats
                    abi = data.get("abi", data)
                    self._abi_cache[name] = abi
                    return abi

        # If file not found, return minimal ABI
        logger.warning(f"ABI file not found for {name}, using minimal ABI")
        return self._get_minimal_abi(name)

    def _get_minimal_abi(self, name: str) -> list:
        """Return minimal ABI for basic functionality"""
        if name == "factory":
            return [
                {
                    "anonymous": False,
                    "inputs": [
                        {"indexed": True, "name": "token0", "type": "address"},
                        {"indexed": True, "name": "token1", "type": "address"},
                        {"indexed": False, "name": "pair", "type": "address"},
                        {"indexed": False, "name": "", "type": "uint256"},
                    ],
                    "name": "PairCreated",
                    "type": "event",
                }
            ]
        elif name == "pair":
            return [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "getReserves",
                    "outputs": [
                        {"name": "reserve0", "type": "uint112"},
                        {"name": "reserve1", "type": "uint112"},
                        {"name": "blockTimestampLast", "type": "uint32"},
                    ],
                    "type": "function",
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "token0",
                    "outputs": [{"name": "", "type": "address"}],
                    "type": "function",
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "token1",
                    "outputs": [{"name": "", "type": "address"}],
                    "type": "function",
                },
            ]
        elif name == "erc20":
            return [
                {
                    "constant": True,
                    "inputs": [{"name": "account", "type": "address"}],
                    "name": "balanceOf",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "type": "function",
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function",
                },
            ]
        else:
            return []

    async def get_pair_liquidity(self, pair_address: str) -> float:
        """Get liquidity in ETH for a pair with enhanced error handling."""
        try:
            await self.rate_limiter.acquire()

            # Get or create contract instance
            pair_contract = await self._get_contract(pair_address, "pair")

            # Get reserves with circuit breaker protection
            reserves = await self.circuit_breaker.call(
                pair_contract.functions.getReserves().call
            )

            await self.rate_limiter.acquire()
            token0 = await self.circuit_breaker.call(
                pair_contract.functions.token0().call
            )

            # Determine which reserve is WETH
            weth = self.config.weth_address.lower()
            if token0.lower() == weth:
                weth_reserve = reserves[0]
            else:
                weth_reserve = reserves[1]

            # Convert from Wei to ETH
            liquidity_eth = Web3.from_wei(weth_reserve, "ether")
            return float(liquidity_eth)

        except Exception as e:
            logger.error(f"Error getting pair liquidity for {pair_address}: {e}")
            return 0.0

    async def _get_contract(self, address: str, contract_type: str) -> Contract:
        """Get contract instance with caching."""
        cache_key = f"{address}_{contract_type}"

        if cache_key in self._contract_cache:
            return self._contract_cache[cache_key]

        try:
            abi = self.load_abi(contract_type)
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(address), abi=abi
            )

            # Cache the contract instance
            self._contract_cache[cache_key] = contract
            return contract

        except Exception as e:
            logger.error(f"Failed to create contract {contract_type} at {address}: {e}")
            raise BlockchainError(f"Contract creation failed: {e}")

    @with_retry(RetryConfig(max_attempts=2, base_delay=1.0))
    async def get_token_price(self, pair_address: str, is_token0: bool) -> float:
        """Get token price in ETH with enhanced error handling."""
        try:
            await self.rate_limiter.acquire()

            pair_contract = await self._get_contract(pair_address, "pair")
            reserves = await self.circuit_breaker.call(
                pair_contract.functions.getReserves().call
            )

            if is_token0:
                token_reserve = reserves[0]
                weth_reserve = reserves[1]
            else:
                token_reserve = reserves[1]
                weth_reserve = reserves[0]

            # Calculate price (WETH per token)
            if token_reserve > 0:
                price = weth_reserve / token_reserve
                return float(Web3.from_wei(int(price * 10**18), "ether"))
            else:
                return 0.0

        except Exception as e:
            logger.error(f"Error getting token price for {pair_address}: {e}")
            return 0.0

    async def get_token_balance(self, token_address: str) -> int:
        """Get token balance of sniper contract"""
        try:
            if not self.sniper_contract:
                return 0

            balance = self.sniper_contract.functions.getTokenBalance(
                Web3.to_checksum_address(token_address)
            ).call()

            return balance

        except Exception as e:
            logger.error(f"Error getting token balance: {e}")
            return 0

    async def verify_sniper_contract(self) -> bool:
        """Verify sniper contract is deployed and accessible"""
        try:
            if not self.sniper_contract:
                return False

            # Try to call a view function
            owner = self.sniper_contract.functions.owner().call()
            expected_owner = self.account.address

            if owner.lower() != expected_owner.lower():
                logger.warning(
                    f"Sniper contract owner mismatch: {owner} != {expected_owner}"
                )

            return True

        except Exception as e:
            logger.error(f"Error verifying sniper contract: {e}")
            return False

    def build_transaction(self, func, value=0) -> Dict[str, Any]:
        """Build transaction with proper gas settings"""
        try:
            # Get current gas price
            gas_price = self.w3.eth.gas_price

            # Apply multiplier
            gas_price = int(gas_price * self.config.GAS_PRICE_MULTIPLIER)

            # Build transaction
            tx = func.build_transaction(
                {
                    "from": self.account.address,
                    "value": value,
                    "gas": 500000,  # Will be estimated
                    "gasPrice": gas_price,
                    "nonce": self.w3.eth.get_transaction_count(self.account.address),
                }
            )

            # Estimate gas
            try:
                estimated_gas = self.w3.eth.estimate_gas(tx)
                tx["gas"] = int(estimated_gas * 1.2)  # Add 20% buffer
            except Exception as e:
                logger.warning(f"Gas estimation failed, using default: {e}")

            return tx

        except Exception as e:
            logger.error(f"Error building transaction: {e}")
            raise

    async def send_transaction(self, tx: Dict[str, Any]) -> Optional[str]:
        """Sign and send transaction"""
        try:
            # Sign transaction
            signed_tx = self.account.sign_transaction(tx)

            # Send transaction
            tx_hash = self.w3.eth.send_raw_transaction(signed_tx.rawTransaction)

            logger.info(f"Transaction sent: {tx_hash.hex()}")

            # Wait for confirmation (optional)
            if self.config.WAIT_FOR_CONFIRMATION:
                receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=120)

                if receipt["status"] == 1:
                    logger.info(f"Transaction confirmed: {tx_hash.hex()}")
                else:
                    logger.error(f"Transaction failed: {tx_hash.hex()}")
                    return None

            return tx_hash.hex()

        except Exception as e:
            logger.error(f"Error sending transaction: {e}")
            return None

    def get_balance(self) -> float:
        """Get ETH balance.

        Returns:
            Balance in ETH
        """
        try:
            balance = self.w3.eth.get_balance(self.account.address)
            return self.w3.from_wei(balance, "ether")
        except Exception as e:
            raise BlockchainError(f"Failed to get balance: {str(e)}")

    def get_gas_price(self) -> int:
        """Get current gas price.

        Returns:
            Gas price in wei
        """
        try:
            return self.w3.eth.gas_price
        except Exception as e:
            raise BlockchainError(f"Failed to get gas price: {str(e)}")

    def estimate_gas(self, transaction: Dict[str, Any]) -> int:
        """Estimate gas for transaction.

        Args:
            transaction: Transaction parameters

        Returns:
            Estimated gas limit
        """
        try:
            return self.w3.eth.estimate_gas(transaction)
        except Exception as e:
            logger.warning(f"Gas estimation failed: {e}")
            return 300000  # Fallback gas limit

    def get_transaction_receipt(self, tx_hash: str) -> Dict[str, Any]:
        """Get transaction receipt.

        Args:
            tx_hash: Transaction hash

        Returns:
            Transaction receipt
        """
        try:
            return self.w3.eth.get_transaction_receipt(tx_hash)
        except TransactionNotFound:
            raise BlockchainError("Transaction not found")
        except Exception as e:
            raise BlockchainError(f"Failed to get receipt: {str(e)}")

    def wait_for_transaction(self, tx_hash: str, timeout: int = 300) -> Dict[str, Any]:
        """Wait for transaction confirmation.

        Args:
            tx_hash: Transaction hash
            timeout: Timeout in seconds

        Returns:
            Transaction receipt
        """
        try:
            return self.w3.eth.wait_for_transaction_receipt(tx_hash, timeout=timeout)
        except Exception as e:
            raise BlockchainError(f"Failed to wait for transaction: {str(e)}")

    def get_contract(self, address: str, abi: list) -> Any:
        """Get contract instance.

        Args:
            address: Contract address
            abi: Contract ABI

        Returns:
            Contract instance
        """
        try:
            return self.w3.eth.contract(
                address=self.w3.to_checksum_address(address), abi=abi
            )
        except Exception as e:
            raise BlockchainError(f"Failed to get contract: {str(e)}")

    def get_block_number(self) -> int:
        """Get current block number.

        Returns:
            Block number
        """
        try:
            return self.w3.eth.block_number
        except Exception as e:
            raise BlockchainError(f"Failed to get block number: {str(e)}")

    def get_block_timestamp(self) -> int:
        """Get current block timestamp.

        Returns:
            Block timestamp
        """
        try:
            return self.w3.eth.get_block("latest")["timestamp"]
        except Exception as e:
            raise BlockchainError(f"Failed to get block timestamp: {str(e)}")
