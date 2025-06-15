"""
Tests for custom exceptions
"""

import pytest
from bot.exceptions import (
    SniperBotError,
    ConfigurationError,
    BlockchainError,
    TradingError,
    SecurityError,
    HoneypotError,
    InsufficientLiquidityError,
    SlippageExceededError,
    GasEstimationError,
    ConnectionError,
    TransactionFailedError,
    map_web3_error,
)


class TestCustomExceptions:
    """Test custom exception hierarchy"""

    def test_base_exception(self):
        """Test base exception"""
        error = SniperBotError("Test error")
        assert str(error) == "Test error"
        assert isinstance(error, Exception)

    def test_configuration_error(self):
        """Test configuration error"""
        error = ConfigurationError("Invalid config")
        assert str(error) == "Invalid config"
        assert isinstance(error, SniperBotError)

    def test_blockchain_error_with_details(self):
        """Test blockchain error with transaction details"""
        error = BlockchainError("Transaction failed", tx_hash="0x123", gas_used=21000)
        assert str(error) == "Transaction failed"
        assert error.tx_hash == "0x123"
        assert error.gas_used == 21000

    def test_trading_error_with_details(self):
        """Test trading error with trading details"""
        error = TradingError(
            "Buy failed", token_address="0xtoken", amount=1.0, tx_data={"gas": 200000}
        )
        assert str(error) == "Buy failed"
        assert error.token_address == "0xtoken"
        assert error.amount == 1.0
        assert error.tx_data["gas"] == 200000

    def test_honeypot_error(self):
        """Test honeypot detection error"""
        error = HoneypotError(
            "Token is honeypot", token_address="0xbadtoken", confidence_score=0.95
        )
        assert str(error) == "Token is honeypot"
        assert error.token_address == "0xbadtoken"
        assert error.confidence_score == 0.95
        assert isinstance(error, SecurityError)

    def test_insufficient_liquidity_error(self):
        """Test insufficient liquidity error"""
        error = InsufficientLiquidityError(
            "Not enough liquidity", required_liquidity=5.0, actual_liquidity=2.0
        )
        assert str(error) == "Not enough liquidity"
        assert error.required_liquidity == 5.0
        assert error.actual_liquidity == 2.0
        assert isinstance(error, TradingError)

    def test_slippage_exceeded_error(self):
        """Test slippage exceeded error"""
        error = SlippageExceededError(
            "Slippage too high",
            expected_price=100.0,
            actual_price=95.0,
            slippage_tolerance=3.0,
        )
        assert str(error) == "Slippage too high"
        assert error.expected_price == 100.0
        assert error.actual_price == 95.0
        assert error.slippage_tolerance == 3.0

    def test_gas_estimation_error(self):
        """Test gas estimation error"""
        error = GasEstimationError("Gas estimation failed", fallback_gas=300000)
        assert str(error) == "Gas estimation failed"
        assert error.fallback_gas == 300000

    def test_transaction_failed_error(self):
        """Test transaction failed error"""
        error = TransactionFailedError(
            "Transaction reverted",
            tx_hash="0xfailed",
            revert_reason="Insufficient balance",
        )
        assert str(error) == "Transaction reverted"
        assert error.tx_hash == "0xfailed"
        assert error.revert_reason == "Insufficient balance"


class TestWeb3ErrorMapping:
    """Test Web3 error message mapping"""

    def test_map_execution_reverted(self):
        """Test mapping execution reverted error"""
        error = map_web3_error("execution reverted", tx_hash="0x123")
        assert isinstance(error, TransactionFailedError)
        assert error.tx_hash == "0x123"

    def test_map_insufficient_funds(self):
        """Test mapping insufficient funds error"""
        error = map_web3_error("insufficient funds for transfer")
        assert isinstance(error, TradingError)

    def test_map_gas_limit_exceeded(self):
        """Test mapping gas limit exceeded error"""
        error = map_web3_error("gas limit exceeded", fallback_gas=500000)
        assert isinstance(error, GasEstimationError)
        assert error.fallback_gas == 500000

    def test_map_nonce_error(self):
        """Test mapping nonce error"""
        error = map_web3_error("nonce too low")
        assert isinstance(error, BlockchainError)

    def test_map_unknown_error(self):
        """Test mapping unknown error"""
        error = map_web3_error("unknown blockchain error")
        assert isinstance(error, BlockchainError)
        assert str(error) == "unknown blockchain error"

    def test_case_insensitive_mapping(self):
        """Test that error mapping is case insensitive"""
        error = map_web3_error("EXECUTION REVERTED")
        assert isinstance(error, TransactionFailedError)
