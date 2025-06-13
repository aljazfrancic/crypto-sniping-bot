"""
Configuration Management
Loads and validates environment variables
"""

import os
import logging
from dotenv import load_dotenv
from web3 import Web3

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class Config:
    """Configuration class with validation"""

    def __init__(self):
        # Network settings
        self.RPC_URL = self._get_required("RPC_URL")
        self.CHAIN_ID = int(self._get_required("CHAIN_ID"))

        # Contract addresses
        self.ROUTER_ADDRESS = self._get_required("ROUTER_ADDRESS")
        self.FACTORY_ADDRESS = self._get_required("FACTORY_ADDRESS")
        self.WETH_ADDRESS = self._get_required("WETH_ADDRESS")
        self.SNIPER_CONTRACT = os.getenv("SNIPER_CONTRACT", "")

        # Wallet settings
        self.PRIVATE_KEY = self._get_required("PRIVATE_KEY")

        # Validate private key
        if not self._is_valid_private_key(self.PRIVATE_KEY):
            raise ValueError("Invalid private key format")

        # Trading settings
        self.BUY_AMOUNT = float(os.getenv("BUY_AMOUNT", "0.1"))
        self.SLIPPAGE = float(os.getenv("SLIPPAGE", "5"))
        self.GAS_PRICE_MULTIPLIER = float(os.getenv("GAS_PRICE_MULTIPLIER", "1.5"))

        # Sell settings
        self.PROFIT_TARGET = float(os.getenv("PROFIT_TARGET", "50"))
        self.STOP_LOSS = float(os.getenv("STOP_LOSS", "10"))
        self.AUTO_SELL = os.getenv("AUTO_SELL", "true").lower() == "true"

        # Safety settings
        self.MIN_LIQUIDITY = float(os.getenv("MIN_LIQUIDITY", "5"))
        self.CHECK_HONEYPOT = os.getenv("CHECK_HONEYPOT", "true").lower() == "true"
        self.USE_HONEYPOT_API = os.getenv("USE_HONEYPOT_API", "true").lower() == "true"

        # Advanced settings
        self.WAIT_FOR_CONFIRMATION = (
            os.getenv("WAIT_FOR_CONFIRMATION", "false").lower() == "true"
        )
        self.MAX_POSITIONS = int(os.getenv("MAX_POSITIONS", "10"))
        self.POSITION_SIZE_PERCENTAGE = float(
            os.getenv("POSITION_SIZE_PERCENTAGE", "100")
        )

        # Validate configuration
        self._validate_config()

        # Log configuration (without sensitive data)
        self._log_config()

    def _get_required(self, key: str) -> str:
        """Get required environment variable"""
        value = os.getenv(key)
        if not value:
            raise ValueError(f"Required environment variable {key} not set")
        return value

    def _is_valid_private_key(self, key: str) -> bool:
        """Validate private key format"""
        try:
            # Remove 0x prefix if present
            if key.startswith("0x"):
                key = key[2:]

            # Check if it's 64 hex characters
            if len(key) != 64:
                return False

            # Try to convert to int to verify it's hex
            int(key, 16)
            return True

        except Exception:
            return False

    def _validate_config(self):
        """Validate configuration values"""
        # Validate addresses
        required_addresses = [
            ("ROUTER_ADDRESS", self.ROUTER_ADDRESS),
            ("FACTORY_ADDRESS", self.FACTORY_ADDRESS),
            ("WETH_ADDRESS", self.WETH_ADDRESS),
        ]

        for name, address in required_addresses:
            if not Web3.is_address(address):
                raise ValueError(f"Invalid {name}: {address}")

        # Validate numeric ranges
        if self.BUY_AMOUNT <= 0:
            raise ValueError("BUY_AMOUNT must be greater than 0")

        if not 0 < self.SLIPPAGE <= 100:
            raise ValueError("SLIPPAGE must be between 0 and 100")

        if self.GAS_PRICE_MULTIPLIER < 1:
            raise ValueError("GAS_PRICE_MULTIPLIER must be at least 1")

        if self.PROFIT_TARGET <= 0:
            raise ValueError("PROFIT_TARGET must be greater than 0")

        if self.STOP_LOSS < 0 or self.STOP_LOSS >= 100:
            raise ValueError("STOP_LOSS must be between 0 and 100")

        if self.MIN_LIQUIDITY < 0:
            raise ValueError("MIN_LIQUIDITY must be non-negative")

    def _log_config(self):
        """Log configuration (excluding sensitive data)"""
        logger.info("Configuration loaded:")
        logger.info(f"  Chain ID: {self.CHAIN_ID}")
        logger.info(f"  RPC URL: {self.RPC_URL[:30]}...")
        logger.info(f"  Router: {self.ROUTER_ADDRESS}")
        logger.info(f"  Factory: {self.FACTORY_ADDRESS}")
        logger.info(f"  WETH: {self.WETH_ADDRESS}")
        logger.info(f"  Sniper Contract: {self.SNIPER_CONTRACT or 'Not deployed'}")
        logger.info(f"  Buy Amount: {self.BUY_AMOUNT} ETH")
        logger.info(f"  Slippage: {self.SLIPPAGE}%")
        logger.info(f"  Profit Target: {self.PROFIT_TARGET}%")
        logger.info(f"  Stop Loss: {self.STOP_LOSS}%")
        logger.info(f"  Min Liquidity: {self.MIN_LIQUIDITY} ETH")
        logger.info(f"  Honeypot Check: {self.CHECK_HONEYPOT}")

    def get_network_name(self) -> str:
        """Get human-readable network name"""
        networks = {
            1: "Ethereum Mainnet",
            5: "Goerli Testnet",
            56: "BSC Mainnet",
            97: "BSC Testnet",
            137: "Polygon Mainnet",
            80001: "Mumbai Testnet",
            43114: "Avalanche Mainnet",
            43113: "Avalanche Testnet",
            31337: "Local Network",
        }
        return networks.get(self.CHAIN_ID, f"Unknown ({self.CHAIN_ID})")
