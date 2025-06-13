"""
Blockchain Interface Layer
Handles all Web3 interactions and contract calls
"""

import json
import os
from typing import Optional, Dict, Any
from web3 import Web3
from web3.contract import Contract
from eth_account import Account
import logging

logger = logging.getLogger(__name__)


class BlockchainInterface:
    """Handles all blockchain interactions"""

    def __init__(self, w3: Web3, config):
        self.w3 = w3
        self.config = config
        self.account = Account.from_key(config.PRIVATE_KEY)
        self.sniper_contract = self._load_sniper_contract()
        self._abi_cache = {}
        self.router_address = None  # Initialize with None or appropriate default

    def _load_sniper_contract(self) -> Optional[Contract]:
        """Load the deployed sniper contract"""
        try:
            if not self.config.SNIPER_CONTRACT:
                logger.warning("No sniper contract address configured")
                return None

            abi = self.load_abi("sniper")
            contract = self.w3.eth.contract(
                address=Web3.to_checksum_address(self.config.SNIPER_CONTRACT), abi=abi
            )
            return contract
        except Exception as e:
            logger.error(f"Failed to load sniper contract: {e}")
            return None

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
        """Get liquidity in ETH for a pair"""
        try:
            pair_abi = self.load_abi("pair")
            pair = self.w3.eth.contract(
                address=Web3.to_checksum_address(pair_address), abi=pair_abi
            )

            # Get reserves
            reserves = pair.functions.getReserves().call()
            token0 = pair.functions.token0().call()

            # Determine which reserve is WETH
            weth = self.config.WETH_ADDRESS.lower()
            if token0.lower() == weth:
                weth_reserve = reserves[0]
            else:
                weth_reserve = reserves[1]

            # Convert from Wei to ETH
            liquidity_eth = Web3.from_wei(weth_reserve, "ether")
            return float(liquidity_eth)

        except Exception as e:
            logger.error(f"Error getting pair liquidity: {e}")
            return 0.0

    async def get_token_price(self, pair_address: str, is_token0: bool) -> float:
        """Get token price in ETH"""
        try:
            pair_abi = self.load_abi("pair")
            pair = self.w3.eth.contract(
                address=Web3.to_checksum_address(pair_address), abi=pair_abi
            )

            # Get reserves
            reserves = pair.functions.getReserves().call()

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
            logger.error(f"Error getting token price: {e}")
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
