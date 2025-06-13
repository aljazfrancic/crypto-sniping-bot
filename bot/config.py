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
        
    def _load_env(self, env_file: str) -> None:
        """Load environment variables from file."""
        if not os.path.exists(env_file):
            raise ConfigError(f"Environment file not found: {env_file}")
            
        with open(env_file) as f:
            for line in f:
                if line.strip() and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
                    
    def _validate_config(self) -> None:
        """Validate all required configuration values."""
        required_vars = [
            'RPC_URL',
            'PRIVATE_KEY',
            'ROUTER_ADDRESS',
            'FACTORY_ADDRESS',
            'WETH_ADDRESS'
        ]
        
        for var in required_vars:
            if not os.getenv(var):
                raise ConfigError(f"Missing required environment variable: {var}")
                
        # Validate RPC URL
        rpc_url = os.getenv('RPC_URL', '')
        if not rpc_url.startswith(('http://', 'https://', 'ws://', 'wss://')):
            raise ConfigError("RPC_URL must be a valid HTTP/WebSocket URL")
            
        # Validate addresses
        try:
            self.router_address = to_checksum_address(os.getenv('ROUTER_ADDRESS', ''))
            self.factory_address = to_checksum_address(os.getenv('FACTORY_ADDRESS', ''))
            self.weth_address = to_checksum_address(os.getenv('WETH_ADDRESS', ''))
        except ValueError as e:
            raise ConfigError(f"Invalid Ethereum address: {e}")
            
        # Validate private key
        private_key = os.getenv('PRIVATE_KEY', '')
        if not private_key.startswith('0x'):
            private_key = '0x' + private_key
        try:
            if len(bytes.fromhex(private_key[2:])) != 32:
                raise ValueError("Invalid private key length")
        except ValueError as e:
            raise ConfigError(f"Invalid private key: {e}")
            
        # Load ABIs
        self._load_abis()
        
    def _load_abis(self) -> None:
        """Load contract ABIs from files."""
        abi_dir = Path(__file__).parent.parent / 'abis'
        if not abi_dir.exists():
            raise ConfigError("ABI directory not found")
            
        self.abis = {}
        for abi_file in abi_dir.glob('*.json'):
            try:
                with open(abi_file) as f:
                    self.abis[abi_file.stem] = json.load(f)
            except json.JSONDecodeError as e:
                raise ConfigError(f"Invalid ABI file {abi_file}: {e}")
                
    @property
    def rpc_url(self) -> str:
        """Get RPC URL."""
        return os.getenv('RPC_URL', '')
        
    @property
    def private_key(self) -> str:
        """Get private key."""
        key = os.getenv('PRIVATE_KEY', '')
        return key if key.startswith('0x') else '0x' + key
        
    @property
    def chain_id(self) -> int:
        """Get chain ID."""
        return int(os.getenv('CHAIN_ID', '1'))
        
    @property
    def buy_amount(self) -> float:
        """Get buy amount in ETH."""
        return float(os.getenv('BUY_AMOUNT', '0.1'))
        
    @property
    def slippage(self) -> float:
        """Get maximum slippage percentage."""
        return float(os.getenv('SLIPPAGE', '5.0'))
        
    @property
    def profit_target(self) -> float:
        """Get take profit percentage."""
        return float(os.getenv('PROFIT_TARGET', '50.0'))
        
    @property
    def stop_loss(self) -> float:
        """Get stop loss percentage."""
        return float(os.getenv('STOP_LOSS', '10.0'))
        
    @property
    def min_liquidity(self) -> float:
        """Get minimum pool liquidity in ETH."""
        return float(os.getenv('MIN_LIQUIDITY', '5.0'))
        
    @property
    def check_honeypot(self) -> bool:
        """Get honeypot detection setting."""
        return os.getenv('CHECK_HONEYPOT', 'true').lower() == 'true'
        
    @property
    def auto_sell(self) -> bool:
        """Get auto-sell setting."""
        return os.getenv('AUTO_SELL', 'true').lower() == 'true'
        
    @property
    def gas_price_multiplier(self) -> float:
        """Get gas price multiplier."""
        return float(os.getenv('GAS_PRICE_MULTIPLIER', '1.1'))
        
    def get_abi(self, contract_name: str) -> Dict[str, Any]:
        """Get contract ABI by name."""
        if contract_name not in self.abis:
            raise ConfigError(f"ABI not found for contract: {contract_name}")
        return self.abis[contract_name]

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
        return networks.get(self.chain_id, f"Unknown ({self.chain_id})")
