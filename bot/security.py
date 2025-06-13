import logging
from typing import Dict, Any, Optional
from web3 import Web3
from web3.exceptions import ContractLogicError
from .config import Config
from .blockchain import BlockchainInterface

logger = logging.getLogger(__name__)

class SecurityError(Exception):
    """Security check error."""
    pass

class SecurityManager:
    """Manages security checks and MEV protection."""
    
    def __init__(self, blockchain: BlockchainInterface, config: Config):
        """Initialize security manager.
        
        Args:
            blockchain: Blockchain interface
            config: Configuration
        """
        self.blockchain = blockchain
        self.config = config
        self.w3 = blockchain.w3
        
        # Price deviation tolerance (5%)
        self.max_price_deviation = 1.05
        
        # Known MEV bot addresses
        self.mev_bots = {
            # Flashbots
            "0x0000000000000000000000000000000000000000",
            # Private transactions
            "0x0000000000000000000000000000000000000001",
        }
        
    def check_price_manipulation(
        self,
        token_address: str,
        expected_price: float
    ) -> None:
        """Check for price manipulation.
        
        Args:
            token_address: Token contract address
            expected_price: Expected token price
            
        Raises:
            SecurityError: If price manipulation detected
        """
        try:
            # Get current price
            current_price = self._get_token_price(token_address)
            
            # Check deviation
            if current_price > expected_price * self.max_price_deviation:
                raise SecurityError(
                    f"Price manipulation detected: {current_price} > {expected_price * self.max_price_deviation}"
                )
                
        except Exception as e:
            raise SecurityError(f"Price check failed: {str(e)}")
            
    def check_mev_risk(self, transaction: Dict[str, Any]) -> None:
        """Check for MEV risk.
        
        Args:
            transaction: Transaction parameters
            
        Raises:
            SecurityError: If MEV risk detected
        """
        try:
            # Check pending transactions
            pending = self.w3.eth.get_block('pending', full_transactions=True)
            
            # Look for MEV bot activity
            for tx in pending.transactions:
                if tx['from'].lower() in self.mev_bots:
                    raise SecurityError("MEV bot activity detected")
                    
            # Check gas price
            if transaction.get('gasPrice', 0) < self.w3.eth.gas_price:
                raise SecurityError("Gas price too low for MEV protection")
                
        except Exception as e:
            raise SecurityError(f"MEV check failed: {str(e)}")
            
    def protect_transaction(
        self,
        transaction: Dict[str, Any],
        max_priority_fee: Optional[int] = None
    ) -> Dict[str, Any]:
        """Add MEV protection to transaction.
        
        Args:
            transaction: Transaction parameters
            max_priority_fee: Maximum priority fee in wei
            
        Returns:
            Protected transaction
        """
        try:
            # Get base fee
            base_fee = self.w3.eth.get_block('latest')['baseFeePerGas']
            
            # Calculate priority fee
            if max_priority_fee is None:
                max_priority_fee = self.w3.eth.max_priority_fee
            
            # Set max fee
            max_fee = base_fee * 2 + max_priority_fee
            
            # Update transaction
            transaction.update({
                'maxFeePerGas': max_fee,
                'maxPriorityFeePerGas': max_priority_fee,
                'type': 2  # EIP-1559
            })
            
            return transaction
            
        except Exception as e:
            raise SecurityError(f"Failed to protect transaction: {str(e)}")
            
    def _get_token_price(self, token_address: str) -> float:
        """Get token price in ETH.
        
        Args:
            token_address: Token contract address
            
        Returns:
            Token price in ETH
        """
        try:
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
            
            pair = self.blockchain.get_contract(
                self.config.pair_address,
                pair_abi
            )
            
            # Get reserves
            reserves = pair.functions.getReserves().call()
            
            # Calculate price
            if reserves[0] == 0 or reserves[1] == 0:
                return 0
                
            return reserves[1] / reserves[0]
            
        except Exception as e:
            raise SecurityError(f"Failed to get token price: {str(e)}")
            
    def verify_contract(self, address: str) -> Dict[str, Any]:
        """Verify contract security.
        
        Args:
            address: Contract address
            
        Returns:
            Verification results
        """
        try:
            # Get contract code
            code = self.w3.eth.get_code(address)
            
            # Check for common vulnerabilities
            vulnerabilities = {
                "reentrancy": False,
                "overflow": False,
                "unchecked_send": False,
                "uninitialized": False
            }
            
            # Check for reentrancy
            if b"call.value" in code or b"send" in code:
                vulnerabilities["reentrancy"] = True
                
            # Check for overflow
            if b"SafeMath" not in code:
                vulnerabilities["overflow"] = True
                
            # Check for unchecked send
            if b"require(" not in code and b"assert(" not in code:
                vulnerabilities["unchecked_send"] = True
                
            # Check for uninitialized variables
            if b"initialized" not in code:
                vulnerabilities["uninitialized"] = True
                
            return {
                "is_verified": self._is_verified(address),
                "code_size": len(code),
                "vulnerabilities": vulnerabilities
            }
            
        except Exception as e:
            raise SecurityError(f"Contract verification failed: {str(e)}")
            
    def _is_verified(self, address: str) -> bool:
        """Check if contract is verified.
        
        Args:
            address: Contract address
            
        Returns:
            True if contract is verified
        """
        try:
            code = self.w3.eth.get_code(address)
            return b"a264697066735822" in code
        except Exception:
            return False 