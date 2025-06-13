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
            # Blacklist check
            if self._is_blacklisted(address):
                raise SecurityError("Contract is blacklisted")
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

    def verify_liquidity(self, token_address: str) -> Dict[str, Any]:
        """Verify token liquidity.
        
        Args:
            token_address: Token contract address
            
        Returns:
            Liquidity information
            
        Raises:
            SecurityError: If liquidity check fails
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
            
            # Calculate liquidity in ETH
            liquidity = reserves[0] / 1e18  # WETH has 18 decimals
            
            if liquidity < self.config.min_liquidity:
                raise SecurityError(f"Insufficient liquidity: {liquidity} ETH")
                
            return {
                "amount": liquidity,
                "locked": self._is_liquidity_locked(token_address),
                "pair_address": self.config.pair_address
            }
            
        except Exception as e:
            raise SecurityError(f"Liquidity verification failed: {str(e)}")
            
    def check_sandwich_attack(self, token_address: str) -> None:
        """Check for sandwich attack.
        
        Args:
            token_address: Token contract address
            
        Raises:
            SecurityError: If sandwich attack detected
        """
        try:
            # Get pending transactions
            pending = self.w3.eth.get_block('pending', full_transactions=True)
            
            # Look for sandwich attack pattern
            for i in range(len(pending.transactions) - 2):
                tx1 = pending.transactions[i]
                tx2 = pending.transactions[i + 1]
                tx3 = pending.transactions[i + 2]
                
                if (tx1['value'] > tx2['value'] * 5 and
                    tx3['value'] > tx2['value'] * 5 and
                    tx1['gasPrice'] > tx2['gasPrice'] * 2 and
                    tx3['gasPrice'] > tx2['gasPrice'] * 2):
                    raise SecurityError("Potential sandwich attack detected")
                    
        except Exception as e:
            raise SecurityError(f"Sandwich attack check failed: {str(e)}")
            
    def check_gas_price(self) -> None:
        """Check for gas price manipulation.
        
        Raises:
            SecurityError: If gas price manipulation detected
        """
        try:
            current_gas = self.blockchain.get_gas_price()
            if current_gas > self.w3.eth.gas_price * self.config.gas_price_multiplier:
                raise SecurityError("Suspicious gas price detected")
                
        except Exception as e:
            raise SecurityError(f"Gas price check failed: {str(e)}")
            
    def _is_blacklisted(self, address: str) -> bool:
        """Check if address is blacklisted.
        
        Args:
            address: Contract address
            
        Returns:
            True if address is blacklisted
        """
        # TODO: Implement blacklist checking
        return False
        
    def check_token_restrictions(self, token_address: str) -> None:
        """Check token trading restrictions.
        
        Args:
            token_address: Token contract address
            
        Raises:
            SecurityError: If trading restrictions detected
        """
        try:
            # Get token contract
            token_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "maxTxAmount",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "maxWalletAmount",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "type": "function"
                }
            ]
            
            token = self.blockchain.get_contract(token_address, token_abi)
            
            # Check restrictions
            max_tx = token.functions.maxTxAmount().call()
            max_wallet = token.functions.maxWalletAmount().call()
            
            if max_tx < Web3.to_wei(1, 'ether') or max_wallet < Web3.to_wei(10, 'ether'):
                raise SecurityError("Trading restrictions detected")
                
        except Exception as e:
            raise SecurityError(f"Token restriction check failed: {str(e)}")
            
    def _is_liquidity_locked(self, token_address: str) -> bool:
        """Check if liquidity is locked.
        
        Args:
            token_address: Token contract address
            
        Returns:
            True if liquidity is locked
        """
        # TODO: Implement liquidity lock checking
        return False
        
    def verify_liquidity_lock(self, token_address: str) -> None:
        """Verify liquidity lock.
        
        Args:
            token_address: Token contract address
            
        Raises:
            SecurityError: If liquidity is not locked
        """
        if not self._is_liquidity_locked(token_address):
            raise SecurityError("Liquidity is not locked")
            
    def verify_contract_size(self, token_address: str) -> None:
        """Verify contract code size.
        
        Args:
            token_address: Token contract address
            
        Raises:
            SecurityError: If contract size is suspicious
        """
        try:
            code = self.w3.eth.get_code(token_address)
            if len(code) > 50000:  # Arbitrary size limit
                raise SecurityError("Suspicious contract size")
                
        except Exception as e:
            raise SecurityError(f"Contract size check failed: {str(e)}")
            
    def verify_contract_owner(self, token_address: str) -> None:
        """Verify contract owner.
        
        Args:
            token_address: Token contract address
            
        Raises:
            SecurityError: If owner is suspicious
        """
        try:
            # Get owner function
            owner_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "owner",
                    "outputs": [{"name": "", "type": "address"}],
                    "type": "function"
                }
            ]
            
            contract = self.blockchain.get_contract(token_address, owner_abi)
            owner = contract.functions.owner().call()
            
            # Check if owner is suspicious
            if owner.lower() in self.mev_bots:
                raise SecurityError("Suspicious contract owner")
                
        except Exception as e:
            raise SecurityError(f"Owner verification failed: {str(e)}")
            
    def verify_contract_permissions(self, token_address: str) -> None:
        """Verify contract permissions.
        
        Args:
            token_address: Token contract address
            
        Raises:
            SecurityError: If dangerous permissions detected
        """
        try:
            # Get contract functions
            contract_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "mint",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "pause",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "blacklist",
                    "outputs": [{"name": "", "type": "bool"}],
                    "type": "function"
                }
            ]
            
            contract = self.blockchain.get_contract(token_address, contract_abi)
            
            # Check for dangerous functions
            dangerous_functions = ['mint', 'pause', 'blacklist']
            for func in dangerous_functions:
                if hasattr(contract.functions, func):
                    raise SecurityError(f"Dangerous function detected: {func}")
                    
        except Exception as e:
            raise SecurityError(f"Permission verification failed: {str(e)}") 