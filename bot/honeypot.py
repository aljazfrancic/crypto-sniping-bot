"""
Honeypot Detection Module
Checks tokens for common honeypot characteristics
"""

import logging
from web3 import Web3
import aiohttp
import asyncio
from typing import Dict, Any, List
from web3.exceptions import ContractLogicError
from eth_typing import Address
from eth_utils import to_checksum_address
from .config import Config
from .blockchain import BlockchainInterface

logger = logging.getLogger(__name__)

class HoneypotError(Exception):
    """Honeypot detection error."""
    pass

class HoneypotDetector:
    """Detects honeypot tokens and analyzes trading restrictions."""
    
    def __init__(self, blockchain: BlockchainInterface):
        """Initialize honeypot detector.
        
        Args:
            blockchain: Blockchain interface
        """
        self.blockchain = blockchain
        self.w3 = blockchain.w3
        
        # Known honeypot signatures
        self.honeypot_signatures = [
            "0x0000000000000000000000000000000000000000",  # Zero address
            "0x000000000000000000000000000000000000dEaD",  # Dead address
            "0x0000000000000000000000000000000000000001",  # One address
        ]
        
        # Known malicious functions
        self.malicious_functions = [
            "0x00000000",  # Empty function
            "0xffffffff",  # Invalid function
        ]
        
    def analyze_token(self, token_address: str) -> Dict[str, Any]:
        """Analyze token for honeypot characteristics.
        
        Args:
            token_address: Token contract address
            
        Returns:
            Analysis results including honeypot status and restrictions
        """
        try:
            # Validate address
            token_address = to_checksum_address(token_address)
            
            # Get contract code
            code = self.w3.eth.get_code(token_address)
            if not code:
                raise HoneypotError("Invalid token address")
                
            # Check for honeypot characteristics
            is_honeypot = self._check_honeypot(token_address)
            
            # Check trading restrictions
            restrictions = self._check_restrictions(token_address)
            
            # Check liquidity
            liquidity = self.verify_liquidity(token_address)
            
            return {
                "is_honeypot": is_honeypot,
                "restrictions": restrictions,
                "liquidity": liquidity,
                "code_size": len(code),
                "is_verified": self._is_verified(token_address)
            }
            
        except Exception as e:
            raise HoneypotError(f"Token analysis failed: {str(e)}")
            
    def _check_honeypot(self, token_address: str) -> bool:
        """Check if token is a honeypot.
        
        Args:
            token_address: Token contract address
            
        Returns:
            True if token is a honeypot
        """
        try:
            # Get token contract
            token_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "symbol",
                    "outputs": [{"name": "", "type": "string"}],
                    "type": "function"
                }
            ]
            
            token = self.w3.eth.contract(
                address=token_address,
                abi=token_abi
            )
            
            # Check basic token functions
            try:
                token.functions.decimals().call()
                token.functions.symbol().call()
            except ContractLogicError:
                return True
                
            # Check for malicious code patterns
            code = self.w3.eth.get_code(token_address)
            for signature in self.malicious_functions:
                if signature in code.hex():
                    return True
                    
            return False
            
        except Exception as e:
            logger.warning(f"Honeypot check failed: {e}")
            return True  # Fail safe
            
    def _check_restrictions(self, token_address: str) -> Dict[str, Any]:
        """Check token trading restrictions.
        
        Args:
            token_address: Token contract address
            
        Returns:
            Dictionary of restrictions
        """
        restrictions = {
            "max_tx": None,
            "max_wallet": None,
            "trading_enabled": True,
            "blacklist": False
        }
        
        try:
            # Get token contract
            token_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "maxTransactionAmount",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "maxWalletAmount",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "tradingEnabled",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                }
            ]
            
            token = self.w3.eth.contract(
                address=token_address,
                abi=token_abi
            )
            
            # Check max transaction amount
            try:
                restrictions["max_tx"] = token.functions.maxTransactionAmount().call()
            except ContractLogicError:
                pass
                
            # Check max wallet amount
            try:
                restrictions["max_wallet"] = token.functions.maxWalletAmount().call()
            except ContractLogicError:
                pass
                
            # Check if trading is enabled
            try:
                restrictions["trading_enabled"] = token.functions.tradingEnabled().call()
            except ContractLogicError:
                pass
                
            # Check for blacklist function
            code = self.w3.eth.get_code(token_address)
            if b"blacklist" in code or b"Blacklist" in code:
                restrictions["blacklist"] = True
                
            return restrictions
            
        except Exception as e:
            logger.warning(f"Restriction check failed: {e}")
            return restrictions
            
    def verify_liquidity(self, token_address: str) -> Dict[str, Any]:
        """Verify token liquidity.
        
        Args:
            token_address: Token contract address
            
        Returns:
            Liquidity information
        """
        try:
            # Get factory contract
            factory_abi = [
                {
                    "constant": True,
                    "inputs": [
                        {"name": "tokenA", "type": "address"},
                        {"name": "tokenB", "type": "address"}
                    ],
                    "name": "getPair",
                    "outputs": [{"name": "pair", "type": "address"}],
                    "type": "function"
                }
            ]
            
            factory = self.w3.eth.contract(
                address=self.blockchain.config.factory_address,
                abi=factory_abi
            )
            
            # Get pair address
            pair_address = factory.functions.getPair(
                self.blockchain.config.weth_address,
                token_address
            ).call()
            
            if pair_address == '0x0000000000000000000000000000000000000000':
                return {
                    "amount": 0,
                    "locked": False,
                    "pair_address": None
                }
                
            # Get pair contract
            pair_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "getReserves",
                    "outputs": [
                        {"name": "_reserve0", "type": "uint112"},
                        {"name": "_reserve1", "type": "uint112"},
                        {"name": "_blockTimestampLast", "type": "uint32"}
                    ],
                    "type": "function"
                }
            ]
            
            pair = self.w3.eth.contract(
                address=pair_address,
                abi=pair_abi
            )
            
            # Get reserves
            reserves = pair.functions.getReserves().call()
            
            # Calculate liquidity in ETH
            liquidity = reserves[0] / 1e18  # WETH has 18 decimals
            
            return {
                "amount": liquidity,
                "locked": self._is_liquidity_locked(pair_address),
                "pair_address": pair_address
            }
            
        except Exception as e:
            raise HoneypotError(f"Liquidity verification failed: {str(e)}")
            
    def _is_liquidity_locked(self, pair_address: str) -> bool:
        """Check if liquidity is locked.
        
        Args:
            pair_address: Pair contract address
            
        Returns:
            True if liquidity is locked
        """
        try:
            # Check for common locker contracts
            locker_abi = [
                {
                    "constant": True,
                    "inputs": [{"name": "token", "type": "address"}],
                    "name": "getLockedAmount",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "type": "function"
                }
            ]
            
            # Known locker contracts
            lockers = [
                "0x663A5C229c09b049E36dCc11a9B0d4a8Eb9db214",  # Unicrypt
                "0x407993575c91ce7643a4d4cCACc9A98c36eE1BBE",  # PinkLock
            ]
            
            for locker in lockers:
                try:
                    locker_contract = self.w3.eth.contract(
                        address=locker,
                        abi=locker_abi
                    )
                    locked = locker_contract.functions.getLockedAmount(
                        pair_address
                    ).call()
                    if locked > 0:
                        return True
                except:
                    continue
                    
            return False
            
        except Exception as e:
            logger.warning(f"Liquidity lock check failed: {e}")
            return False
            
    def _is_verified(self, token_address: str) -> bool:
        """Check if token contract is verified.
        
        Args:
            token_address: Token contract address
            
        Returns:
            True if contract is verified
        """
        try:
            # Get contract code
            code = self.w3.eth.get_code(token_address)
            
            # Check for metadata hash
            if b"a264697066735822" in code:
                return True
                
            return False
            
        except Exception as e:
            logger.warning(f"Verification check failed: {e}")
            return False
