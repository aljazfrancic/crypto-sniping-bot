"""
Configuration Management
Loads and validates environment variables
"""

import os
import logging
from dotenv import load_dotenv
from web3 import Web3
from eth_typing import Address
from eth_utils import to_checksum_address
import json
from pathlib import Path
from typing import Dict, Any, Optional, List, Union
import secrets
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()


class ConfigError(Exception):
    """Configuration validation error."""

    pass


class Config:
    """Secure configuration management with validation."""

    def __init__(self, env_file: str = ".env"):
        """Initialize configuration with validation.

        Args:
            env_file: Path to environment file
        """
        self._load_env(env_file)
        self._validate_config()
        self._setup_security()

    def _load_env(self, env_file: str) -> None:
        """Load environment variables from file."""
        if not os.path.exists(env_file):
            logger.warning(f"Environment file not found: {env_file}")
            return

        load_dotenv(env_file)

    def _setup_security(self) -> None:
        """Setup security configurations."""
        # Generate or load encryption key for sensitive data
        key_file = Path(".secret_key")
        if key_file.exists():
            with open(key_file, "rb") as f:
                self._encryption_key = f.read()
        else:
            self._encryption_key = Fernet.generate_key()
            with open(key_file, "wb") as f:
                f.write(self._encryption_key)
            # Secure the key file
            os.chmod(key_file, 0o600)

        self._cipher = Fernet(self._encryption_key)

    def _validate_config(self) -> None:
        """Validate all required configuration values."""
        required_vars = [
            "RPC_URL",
            "PRIVATE_KEY",
            "ROUTER_ADDRESS",
            "FACTORY_ADDRESS",
            "WETH_ADDRESS",
        ]

        for var in required_vars:
            if not os.getenv(var):
                raise ConfigError(f"Missing required environment variable: {var}")

        # Validate RPC URL
        rpc_url = os.getenv("RPC_URL", "")
        if not rpc_url.startswith(("http://", "https://", "ws://", "wss://")):
            raise ConfigError("RPC_URL must be a valid HTTP/WebSocket URL")

        # Validate chain ID is supported
        chain_id = self.chain_id
        supported_chains = [
            1,
            56,
            137,
            42161,
            10,
            43114,
            250,
            31337,
        ]  # Add mainnet chains
        if chain_id not in supported_chains:
            logger.warning(f"Chain ID {chain_id} may not be fully supported")

        # Validate addresses
        try:
            self.router_address = to_checksum_address(os.getenv("ROUTER_ADDRESS", ""))
            self.factory_address = to_checksum_address(os.getenv("FACTORY_ADDRESS", ""))
            self.weth_address = to_checksum_address(os.getenv("WETH_ADDRESS", ""))
        except ValueError as e:
            raise ConfigError(f"Invalid Ethereum address: {e}")

        # Validate private key with enhanced security
        self._validate_private_key()

        # Validate trading parameters
        self._validate_trading_params()

        # Load ABIs
        self._load_abis()

    def _validate_private_key(self) -> None:
        """Validate private key with enhanced security checks."""
        private_key = os.getenv("PRIVATE_KEY", "")

        # Check for test/demo keys (security risk)
        dangerous_keys = [
            "0xac0974bec39a17e36ba4a6b4d238ff944bacb478cbed5efcae784d7bf4f2ff80",  # Hardhat test key
            "0x59c6995e998f97a5a0044966f0945389dc9e86dae88c7a8412f4603b6b78690d",  # Another common test key
        ]

        # Also check for obvious test patterns
        test_patterns = [
            "1234567890",  # Sequential numbers
            "abcdef1234",  # Simple hex patterns
            "deadbeef",  # Common test hex
            "cafebabe",  # Another common test hex
        ]

        if private_key in dangerous_keys:
            raise ConfigError("DANGER: Using test private key! This will expose funds!")

        # Check for test patterns in the key
        for pattern in test_patterns:
            if pattern in private_key.lower():
                raise ConfigError(
                    "DANGER: Using test private key! This will expose funds!"
                )

        if not private_key.startswith("0x"):
            private_key = "0x" + private_key

        try:
            if len(bytes.fromhex(private_key[2:])) != 32:
                raise ValueError("Invalid private key length")
        except ValueError as e:
            raise ConfigError(f"Invalid private key: {e}")

    def _validate_trading_params(self) -> None:
        """Validate trading parameters for safety."""
        buy_amount = self.buy_amount
        if buy_amount <= 0:
            raise ConfigError("BUY_AMOUNT must be positive")
        if buy_amount > 10:  # More than 10 ETH seems risky
            logger.warning(f"Large buy amount detected: {buy_amount} ETH")

        slippage = self.slippage
        if slippage < 0 or slippage > 50:
            raise ConfigError("SLIPPAGE must be between 0 and 50 percent")

        profit_target = self.profit_target
        if profit_target <= 0:
            raise ConfigError("PROFIT_TARGET must be positive")

        stop_loss = self.stop_loss
        if stop_loss <= 0 or stop_loss >= 100:
            raise ConfigError("STOP_LOSS must be between 0 and 100 percent")

        min_liquidity = self.min_liquidity
        if min_liquidity <= 0:
            raise ConfigError("MIN_LIQUIDITY must be positive")

        gas_multiplier = self.gas_price_multiplier
        if gas_multiplier < 1.0 or gas_multiplier > 5.0:
            raise ConfigError("GAS_PRICE_MULTIPLIER must be between 1.0 and 5.0")

        # Validate rate limiting settings
        max_rpc_calls = self.max_rpc_calls_per_second
        if max_rpc_calls <= 0 or max_rpc_calls > 100:
            raise ConfigError("MAX_RPC_CALLS_PER_SECOND must be between 1 and 100")

    def _load_abis(self) -> None:
        """Load contract ABIs from files."""
        abi_dir = Path(__file__).parent.parent / "abis"
        if not abi_dir.exists():
            raise ConfigError("ABI directory not found")

        self.abis = {}
        for abi_file in abi_dir.glob("*.json"):
            try:
                with open(abi_file) as f:
                    self.abis[abi_file.stem] = json.load(f)
            except json.JSONDecodeError as e:
                raise ConfigError(f"Invalid ABI file {abi_file}: {e}")

    @property
    def rpc_url(self) -> str:
        """Get RPC URL."""
        return os.getenv("RPC_URL", "")

    @property
    def private_key(self) -> str:
        """Get private key."""
        key = os.getenv("PRIVATE_KEY", "")
        return key if key.startswith("0x") else "0x" + key

    @property
    def chain_id(self) -> int:
        """Get chain ID."""
        return int(os.getenv("CHAIN_ID", "1"))

    @property
    def buy_amount(self) -> float:
        """Get buy amount in ETH."""
        return float(os.getenv("BUY_AMOUNT", "0.1"))

    @property
    def slippage(self) -> float:
        """Get maximum slippage percentage."""
        return float(os.getenv("SLIPPAGE", "5.0"))

    @property
    def profit_target(self) -> float:
        """Get take profit percentage."""
        return float(os.getenv("PROFIT_TARGET", "50.0"))

    @property
    def stop_loss(self) -> float:
        """Get stop loss percentage."""
        return float(os.getenv("STOP_LOSS", "10.0"))

    @property
    def min_liquidity(self) -> float:
        """Get minimum pool liquidity in ETH."""
        return float(os.getenv("MIN_LIQUIDITY", "5.0"))

    @property
    def check_honeypot(self) -> bool:
        """Get honeypot detection setting."""
        return os.getenv("CHECK_HONEYPOT", "true").lower() == "true"

    @property
    def auto_sell(self) -> bool:
        """Get auto-sell setting."""
        return os.getenv("AUTO_SELL", "true").lower() == "true"

    @property
    def gas_price_multiplier(self) -> float:
        """Get gas price multiplier."""
        return float(os.getenv("GAS_PRICE_MULTIPLIER", "1.1"))

    @property
    def max_rpc_calls_per_second(self) -> int:
        """Get maximum RPC calls per second for rate limiting."""
        return int(os.getenv("MAX_RPC_CALLS_PER_SECOND", "10"))

    @property
    def max_concurrent_trades(self) -> int:
        """Get maximum concurrent trades."""
        return int(os.getenv("MAX_CONCURRENT_TRADES", "3"))

    @property
    def enable_monitoring(self) -> bool:
        """Get monitoring enablement setting."""
        return os.getenv("ENABLE_MONITORING", "true").lower() == "true"

    @property
    def log_level(self) -> str:
        """Get logging level."""
        return os.getenv("LOG_LEVEL", "INFO").upper()

    @property
    def webhook_url(self) -> Optional[str]:
        """Get webhook URL for notifications."""
        return os.getenv("WEBHOOK_URL")

    @property
    def database_url(self) -> Optional[str]:
        """Get database URL for persistent storage."""
        return os.getenv("DATABASE_URL")

    @property
    def backup_rpc_urls(self) -> List[str]:
        """Get backup RPC URLs."""
        backup_urls = os.getenv("BACKUP_RPC_URLS", "")
        return [url.strip() for url in backup_urls.split(",") if url.strip()]

    def get_abi(self, contract_name: str) -> Dict[str, Any]:
        """Get contract ABI by name."""
        if contract_name not in self.abis:
            raise ConfigError(f"ABI not found for contract: {contract_name}")
        return self.abis[contract_name]

    def get_network_name(self) -> str:
        """Get human-readable network name"""
        networks = {
            1: "Ethereum Mainnet",
            56: "BSC Mainnet",
            137: "Polygon Mainnet",
            42161: "Arbitrum One",
            10: "Optimism",
            43114: "Avalanche C-Chain",
            250: "Fantom Opera",
            31337: "Hardhat Local",
        }
        return networks.get(self.chain_id, f"Unknown Network ({self.chain_id})")

    def get_explorer_url(self) -> str:
        """Get blockchain explorer URL."""
        explorers = {
            1: "https://etherscan.io",
            56: "https://bscscan.com",
            137: "https://polygonscan.com",
            42161: "https://arbiscan.io",
            10: "https://optimistic.etherscan.io",
            43114: "https://snowtrace.io",
            250: "https://ftmscan.com",
        }
        return explorers.get(self.chain_id, "")

    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        return self._cipher.encrypt(data.encode()).decode()

    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        return self._cipher.decrypt(encrypted_data.encode()).decode()

    def validate_environment(self) -> Dict[str, Any]:
        """Validate entire environment and return status."""
        status = {
            "valid": True,
            "errors": [],
            "warnings": [],
            "network": self.get_network_name(),
            "explorer": self.get_explorer_url(),
        }

        try:
            # Test RPC connection
            w3 = Web3(Web3.HTTPProvider(self.rpc_url))
            if not w3.is_connected():
                status["errors"].append("Cannot connect to RPC endpoint")
                status["valid"] = False
            else:
                # Verify chain ID matches
                actual_chain_id = w3.eth.chain_id
                if actual_chain_id != self.chain_id:
                    status["errors"].append(
                        f"Chain ID mismatch: expected {self.chain_id}, got {actual_chain_id}"
                    )
                    status["valid"] = False

        except Exception as e:
            status["errors"].append(f"RPC connection error: {str(e)}")
            status["valid"] = False

        return status

    def to_dict(self, include_sensitive: bool = False) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        config_dict = {
            "chain_id": self.chain_id,
            "network": self.get_network_name(),
            "buy_amount": self.buy_amount,
            "slippage": self.slippage,
            "profit_target": self.profit_target,
            "stop_loss": self.stop_loss,
            "min_liquidity": self.min_liquidity,
            "check_honeypot": self.check_honeypot,
            "auto_sell": self.auto_sell,
            "gas_price_multiplier": self.gas_price_multiplier,
            "max_rpc_calls_per_second": self.max_rpc_calls_per_second,
            "max_concurrent_trades": self.max_concurrent_trades,
            "enable_monitoring": self.enable_monitoring,
            "log_level": self.log_level,
        }

        if include_sensitive:
            config_dict.update(
                {
                    "rpc_url": self.rpc_url,
                    "router_address": self.router_address,
                    "factory_address": self.factory_address,
                    "weth_address": self.weth_address,
                }
            )

        return config_dict
