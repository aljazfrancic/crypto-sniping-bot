"""
Custom exceptions for crypto sniping bot
Provides specific error types for better error handling and debugging
"""

from typing import Optional, Dict, Any


class SniperBotError(Exception):
    """Base exception for all bot errors"""

    pass


class ConfigurationError(SniperBotError):
    """Configuration validation errors"""

    pass


class BlockchainError(SniperBotError):
    """Blockchain interaction errors"""

    def __init__(
        self,
        message: str,
        tx_hash: Optional[str] = None,
        gas_used: Optional[int] = None,
    ):
        super().__init__(message)
        self.tx_hash = tx_hash
        self.gas_used = gas_used


class TradingError(SniperBotError):
    """Trading execution errors"""

    def __init__(
        self,
        message: str,
        token_address: Optional[str] = None,
        amount: Optional[float] = None,
        tx_data: Optional[Dict[str, Any]] = None,
    ):
        super().__init__(message)
        self.token_address = token_address
        self.amount = amount
        self.tx_data = tx_data


class SecurityError(SniperBotError):
    """Security validation errors"""

    pass


class HoneypotError(SecurityError):
    """Honeypot detection errors"""

    def __init__(
        self, message: str, token_address: str, confidence_score: Optional[float] = None
    ):
        super().__init__(message)
        self.token_address = token_address
        self.confidence_score = confidence_score


class InsufficientLiquidityError(TradingError):
    """Insufficient liquidity errors"""

    def __init__(
        self, message: str, required_liquidity: float, actual_liquidity: float
    ):
        super().__init__(message)
        self.required_liquidity = required_liquidity
        self.actual_liquidity = actual_liquidity


class SlippageExceededError(TradingError):
    """Slippage tolerance exceeded"""

    def __init__(
        self,
        message: str,
        expected_price: float,
        actual_price: float,
        slippage_tolerance: float,
    ):
        super().__init__(message)
        self.expected_price = expected_price
        self.actual_price = actual_price
        self.slippage_tolerance = slippage_tolerance


class GasEstimationError(BlockchainError):
    """Gas estimation failures"""

    def __init__(self, message: str, fallback_gas: int):
        super().__init__(message)
        self.fallback_gas = fallback_gas


class ConnectionError(BlockchainError):
    """Blockchain connection errors"""

    pass


class TransactionFailedError(BlockchainError):
    """Transaction execution failures"""

    def __init__(
        self,
        message: str,
        tx_hash: Optional[str] = None,
        revert_reason: Optional[str] = None,
    ):
        super().__init__(message, tx_hash)
        self.revert_reason = revert_reason


# Web3 specific error mappings
WEB3_ERROR_MAPPING = {
    "execution reverted": TransactionFailedError,
    "insufficient funds": TradingError,
    "gas limit exceeded": GasEstimationError,
    "nonce too low": BlockchainError,
    "replacement transaction underpriced": BlockchainError,
    "transaction underpriced": BlockchainError,
}


def map_web3_error(error_message: str, **kwargs) -> SniperBotError:
    """Map Web3 error messages to specific exception types"""
    error_message_lower = error_message.lower()

    for key, exception_class in WEB3_ERROR_MAPPING.items():
        if key in error_message_lower:
            return exception_class(error_message, **kwargs)

    return BlockchainError(error_message, **kwargs)
