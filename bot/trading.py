"""
Trading Engine
Handles buy/sell execution through the sniper contract
"""

import logging
from typing import Optional
from web3 import Web3

logger = logging.getLogger(__name__)


class TradingEngine:
    """Manages trading operations"""

    def __init__(self, blockchain, config):
        self.blockchain = blockchain
        self.config = config
        self.w3 = blockchain.w3

    async def buy_token(
        self, token_address: str, amount_eth: float, min_tokens: float
    ) -> Optional[str]:
        """Execute buy transaction through sniper contract"""
        try:
            if not self.blockchain.sniper_contract:
                logger.error("Sniper contract not available")
                return None

            # Convert amounts to Wei
            amount_wei = Web3.to_wei(amount_eth, "ether")
            min_tokens_wei = Web3.to_wei(min_tokens, "ether")

            # Build transaction
            func = self.blockchain.sniper_contract.functions.buyToken(
                Web3.to_checksum_address(token_address), min_tokens_wei
            )

            tx = self.blockchain.build_transaction(func, value=amount_wei)

            # Send transaction
            tx_hash = await self.blockchain.send_transaction(tx)

            if tx_hash:
                logger.info(
                    f"Buy order placed - Token: {token_address}, Amount: {amount_eth} ETH"
                )

            return tx_hash

        except Exception as e:
            logger.error(f"Error buying token: {e}")
            return None

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
