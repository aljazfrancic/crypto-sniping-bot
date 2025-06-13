"""
Trading Engine
Handles buy/sell execution through the sniper contract
"""

import logging
from typing import Dict, Any, Optional
from web3 import Web3
from web3.exceptions import ContractLogicError, TransactionNotFound
from eth_typing import Address
from eth_utils import to_checksum_address
from .config import Config
from .blockchain import BlockchainInterface
from .honeypot import HoneypotDetector

logger = logging.getLogger(__name__)

class TradingError(Exception):
    """Trading operation error."""
    pass

class TradingEngine:
    """Secure trading engine with safety checks."""
    
    def __init__(self, blockchain: BlockchainInterface, config: Config):
        """Initialize trading engine.
        
        Args:
            blockchain: Blockchain interface
            config: Configuration
        """
        self.blockchain = blockchain
        self.config = config
        self.honeypot = HoneypotDetector(blockchain)
        
        # Initialize contracts
        self._init_contracts()
        
    def _init_contracts(self) -> None:
        """Initialize contract instances."""
        # Router contract
        router_abi = self.config.get_abi('router')
        self.router = self.blockchain.w3.eth.contract(
            address=self.config.router_address,
            abi=router_abi
        )
        
        # Factory contract
        factory_abi = self.config.get_abi('factory')
        self.factory = self.blockchain.w3.eth.contract(
            address=self.config.factory_address,
            abi=factory_abi
        )
        
        # WETH contract
        weth_abi = self.config.get_abi('weth')
        self.weth = self.blockchain.w3.eth.contract(
            address=self.config.weth_address,
            abi=weth_abi
        )
        
    def buy_token(
        self,
        token_address: str,
        amount_eth: float,
        slippage: Optional[float] = None
    ) -> str:
        """Buy tokens with safety checks.
        
        Args:
            token_address: Token contract address
            amount_eth: Amount of ETH to spend
            slippage: Maximum slippage percentage (default from config)
            
        Returns:
            Transaction hash
            
        Raises:
            TradingError: If safety checks fail or transaction fails
        """
        try:
            # Validate token address
            token_address = to_checksum_address(token_address)
            
            # Check honeypot
            if self.config.check_honeypot:
                analysis = self.honeypot.analyze_token(token_address)
                if analysis["is_honeypot"]:
                    raise TradingError("Token is a honeypot")
                    
            # Verify liquidity
            liquidity = self.honeypot.verify_liquidity(token_address)
            if liquidity["amount"] < self.config.min_liquidity:
                raise TradingError(f"Insufficient liquidity: {liquidity['amount']} ETH")
                
            # Calculate amounts
            amount_wei = self.blockchain.w3.to_wei(amount_eth, 'ether')
            amount_out_min = self._calculate_min_output(token_address, amount_wei, slippage)
            
            # Simulate transaction
            self._simulate_buy(token_address, amount_wei, amount_out_min)
            
            # Execute transaction
            tx_hash = self._execute_buy(token_address, amount_wei, amount_out_min)
            
            logger.info(f"Buy transaction sent: {tx_hash}")
            return tx_hash
            
        except ContractLogicError as e:
            raise TradingError(f"Contract error: {str(e)}")
        except TransactionNotFound as e:
            raise TradingError(f"Transaction failed: {str(e)}")
        except Exception as e:
            raise TradingError(f"Unexpected error: {str(e)}")
            
    def _calculate_min_output(
        self,
        token_address: str,
        amount_wei: int,
        slippage: Optional[float] = None
    ) -> int:
        """Calculate minimum output amount with slippage protection.
        
        Args:
            token_address: Token contract address
            amount_wei: Input amount in wei
            slippage: Maximum slippage percentage
            
        Returns:
            Minimum output amount in token units
        """
        # Get expected output
        amounts_out = self.router.functions.getAmountsOut(
            amount_wei,
            [self.config.weth_address, token_address]
        ).call()
        
        expected_output = amounts_out[1]
        
        # Apply slippage
        slippage = slippage or self.config.slippage
        min_output = int(expected_output * (1 - slippage / 100))
        
        return min_output
        
    def _simulate_buy(
        self,
        token_address: str,
        amount_wei: int,
        amount_out_min: int
    ) -> None:
        """Simulate buy transaction before sending.
        
        Args:
            token_address: Token contract address
            amount_wei: Input amount in wei
            amount_out_min: Minimum output amount
            
        Raises:
            TradingError: If simulation fails
        """
        try:
            # Simulate swap
            self.router.functions.swapExactETHForTokens(
                amount_out_min,
                [self.config.weth_address, token_address],
                self.blockchain.account.address,
                self.blockchain.w3.eth.get_block('latest').timestamp + 300
            ).call()
            
        except ContractLogicError as e:
            raise TradingError(f"Buy simulation failed: {str(e)}")
            
    def _execute_buy(
        self,
        token_address: str,
        amount_wei: int,
        amount_out_min: int
    ) -> str:
        """Execute buy transaction.
        
        Args:
            token_address: Token contract address
            amount_wei: Input amount in wei
            amount_out_min: Minimum output amount
            
        Returns:
            Transaction hash
        """
        # Build transaction
        tx = self.router.functions.swapExactETHForTokens(
            amount_out_min,
            [self.config.weth_address, token_address],
            self.blockchain.account.address,
            self.blockchain.w3.eth.get_block('latest').timestamp + 300
        ).build_transaction({
            'from': self.blockchain.account.address,
            'value': amount_wei,
            'gas': self._estimate_gas(token_address, amount_wei, amount_out_min),
            'gasPrice': self._get_gas_price(),
            'nonce': self.blockchain.w3.eth.get_transaction_count(
                self.blockchain.account.address
            )
        })
        
        # Sign and send transaction
        signed_tx = self.blockchain.w3.eth.account.sign_transaction(
            tx,
            self.config.private_key
        )
        return self.blockchain.w3.eth.send_raw_transaction(signed_tx.rawTransaction)
        
    def _estimate_gas(
        self,
        token_address: str,
        amount_wei: int,
        amount_out_min: int
    ) -> int:
        """Estimate gas for buy transaction.
        
        Args:
            token_address: Token contract address
            amount_wei: Input amount in wei
            amount_out_min: Minimum output amount
            
        Returns:
            Estimated gas limit
        """
        try:
            return self.router.functions.swapExactETHForTokens(
                amount_out_min,
                [self.config.weth_address, token_address],
                self.blockchain.account.address,
                self.blockchain.w3.eth.get_block('latest').timestamp + 300
            ).estimate_gas({
                'from': self.blockchain.account.address,
                'value': amount_wei
            })
        except Exception as e:
            logger.warning(f"Gas estimation failed: {e}")
            return 300000  # Fallback gas limit
            
    def _get_gas_price(self) -> int:
        """Get gas price with multiplier.
        
        Returns:
            Gas price in wei
        """
        base_price = self.blockchain.w3.eth.gas_price
        return int(base_price * self.config.gas_price_multiplier)
        
    def get_position(self, token_address: str) -> Dict[str, Any]:
        """Get current position details.
        
        Args:
            token_address: Token contract address
            
        Returns:
            Position information including amount, entry price, and P&L
        """
        try:
            # Get token contract
            token_abi = self.config.get_abi('erc20')
            token = self.blockchain.w3.eth.contract(
                address=token_address,
                abi=token_abi
            )
            
            # Get token balance
            balance = token.functions.balanceOf(
                self.blockchain.account.address
            ).call()
            
            # Get token price
            price = self._get_token_price(token_address)
            
            return {
                'token': token_address,
                'balance': balance,
                'price': price,
                'value': balance * price
            }
            
        except Exception as e:
            raise TradingError(f"Failed to get position: {str(e)}")
            
    def _get_token_price(self, token_address: str) -> float:
        """Get token price in ETH.
        
        Args:
            token_address: Token contract address
            
        Returns:
            Token price in ETH
        """
        try:
            # Get reserves
            pair_address = self.factory.functions.getPair(
                self.config.weth_address,
                token_address
            ).call()
            
            if pair_address == '0x0000000000000000000000000000000000000000':
                return 0
                
            pair_abi = self.config.get_abi('pair')
            pair = self.blockchain.w3.eth.contract(
                address=pair_address,
                abi=pair_abi
            )
            
            reserves = pair.functions.getReserves().call()
            
            # Calculate price
            if reserves[0] == 0 or reserves[1] == 0:
                return 0
                
            return reserves[1] / reserves[0]
            
        except Exception as e:
            raise TradingError(f"Failed to get token price: {str(e)}")

    async def sell_token(
        self, token_address: str, amount: int, min_eth: float
    ) -> Optional[str]:
        """Execute sell transaction through sniper contract"""
        try:
            if not self.blockchain.sniper_contract:
                logger.error("Sniper contract not available")
                return None

            # Convert min ETH to Wei
            min_eth_wei = Web3.to_wei(min_eth, "ether") if min_eth > 0 else 0

            # Build transaction
            func = self.blockchain.sniper_contract.functions.sellToken(
                Web3.to_checksum_address(token_address), amount, min_eth_wei
            )

            tx = self.blockchain.build_transaction(func)

            # Send transaction
            tx_hash = await self.blockchain.send_transaction(tx)

            if tx_hash:
                logger.info(
                    f"Sell order placed - Token: {token_address}, Amount: {amount}"
                )

            return tx_hash

        except Exception as e:
            logger.error(f"Error selling token: {e}")
            return None

    async def emergency_sell_all(self, token_address: str) -> Optional[str]:
        """Emergency sell all tokens with high slippage tolerance"""
        try:
            # Get token balance
            balance = await self.blockchain.get_token_balance(token_address)

            if balance == 0:
                logger.warning("No tokens to sell")
                return None

            logger.warning(f"EMERGENCY SELL - Selling {balance} tokens")

            # Temporarily increase slippage for emergency sell
            original_slippage = self.config.SLIPPAGE
            self.config.SLIPPAGE = 50  # 50% slippage for emergency

            # Execute sell with 0 min ETH (accept any price)
            tx_hash = await self.sell_token(token_address, balance, 0)

            # Restore original slippage
            self.config.SLIPPAGE = original_slippage

            return tx_hash

        except Exception as e:
            logger.error(f"Error in emergency sell: {e}")
            return None

