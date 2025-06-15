import pytest
from unittest.mock import Mock, patch
from web3 import Web3
from eth_typing import Address
from bot.security import SecurityManager, SecurityError
from bot.blockchain import BlockchainInterface
from bot.config import Config


@pytest.fixture
def mock_web3():
    web3 = Mock(spec=Web3)
    web3.eth = Mock()
    web3.eth.get_block.return_value = {"baseFeePerGas": 1000000000, "transactions": []}
    web3.eth.gas_price = 1000000000
    web3.eth.max_priority_fee = 100000000
    web3.eth.get_code.return_value = b"\x60\x60\x60\x40"
    return web3


@pytest.fixture
def mock_blockchain(mock_web3):
    blockchain = Mock(spec=BlockchainInterface)
    blockchain.w3 = mock_web3
    blockchain.get_gas_price.return_value = 2000000000
    blockchain.get_balance.return_value = Web3.to_wei(1, "ether")
    blockchain.get_contract = Mock()
    blockchain.web3 = mock_web3
    return blockchain


@pytest.fixture
def mock_config():
    config = Mock(spec=Config)
    config.slippage = 5
    config.min_liquidity = 1.0
    config.check_honeypot = True
    config.gas_price_multiplier = 1.2
    config.router_address = "0xrouter"
    config.factory_address = "0xfactory"
    config.weth_address = "0xweth"
    config.pair_address = "0xpair"
    config.get_abi = Mock(return_value=[])
    config.SLIPPAGE = 5
    return config


@pytest.fixture
def security_manager(mock_blockchain, mock_config):
    return SecurityManager(mock_blockchain, mock_config)


def test_price_manipulation_check(security_manager):
    """Test price manipulation detection"""
    token_address = "0x1234567890123456789012345678901234567890"
    expected_price = 1.0
    manipulated_price = 1.1  # 10% higher than expected

    with patch.object(
        security_manager, "_get_token_price", return_value=manipulated_price
    ):
        with pytest.raises(SecurityError) as exc_info:
            security_manager.check_price_manipulation(token_address, expected_price)
        assert "Price manipulation detected" in str(exc_info.value)


def test_mev_risk_check(security_manager, mock_web3):
    """Test MEV risk detection"""
    # Mock pending transactions with MEV bot activity
    mock_web3.eth.get_block.return_value = Mock(
        transactions=[
            {
                "from": "0x0000000000000000000000000000000000000000",
                "gasPrice": 1000000000000,
            }
        ]
    )

    tx = {
        "from": "0x123",
        "to": "0x456",
        "value": Web3.to_wei(0.1, "ether"),
        "data": "0x",
        "nonce": 1,
        "gasPrice": 1000000000,
    }

    with pytest.raises(SecurityError) as exc_info:
        security_manager.check_mev_risk(tx)
    assert "MEV bot activity detected" in str(exc_info.value)


def test_transaction_protection(security_manager):
    """Test transaction protection with EIP-1559"""
    tx = {
        "from": "0x123",
        "to": "0x456",
        "value": Web3.to_wei(0.1, "ether"),
        "data": "0x",
        "nonce": 1,
    }

    protected_tx = security_manager.protect_transaction(tx)

    assert "maxFeePerGas" in protected_tx
    assert "maxPriorityFeePerGas" in protected_tx
    assert protected_tx["type"] == 2  # EIP-1559 transaction type


def test_contract_verification(security_manager):
    """Test contract verification"""
    contract_address = "0x1234567890123456789012345678901234567890"

    # Mock contract code with verification hash
    security_manager.w3.eth.get_code.return_value = b"a2646970667358221234567890"

    result = security_manager.verify_contract(contract_address)
    assert result["is_verified"] is True
    assert isinstance(result["vulnerabilities"], dict)


def test_contract_vulnerabilities(security_manager):
    """Test vulnerability detection in contracts"""
    contract_address = "0x1234567890123456789012345678901234567890"

    # Mock contract code with vulnerabilities
    security_manager.w3.eth.get_code.return_value = b"call.value"

    result = security_manager.verify_contract(contract_address)
    assert result["vulnerabilities"]["reentrancy"] is True


def test_token_price_calculation(security_manager):
    """Test token price calculation"""
    token_address = "0x1234567890123456789012345678901234567890"

    # Mock pair contract
    mock_pair = Mock()
    mock_pair.functions.getReserves.return_value.call.return_value = (
        1000000,
        1000000,
        0,
    )
    security_manager.blockchain.get_contract.return_value = mock_pair

    price = security_manager._get_token_price(token_address)
    assert price == 1.0


def test_invalid_token_address(security_manager):
    """Test handling of invalid token addresses"""
    invalid_address = "0xinvalid"

    with pytest.raises(SecurityError) as exc_info:
        security_manager.check_price_manipulation(invalid_address, 1.0)
    assert "Price check failed" in str(exc_info.value)


def test_mev_protection_with_custom_priority_fee(security_manager):
    """Test MEV protection with custom priority fee"""
    tx = {
        "from": "0x123",
        "to": "0x456",
        "value": Web3.to_wei(0.1, "ether"),
        "data": "0x",
        "nonce": 1,
    }

    # Set custom priority fee
    max_priority_fee = Web3.to_wei(3, "gwei")

    protected_tx = security_manager.protect_transaction(tx, max_priority_fee)

    assert protected_tx["maxPriorityFeePerGas"] == max_priority_fee


def test_liquidity_verification(security_manager):
    """Test liquidity verification"""
    token_address = "0x1234567890123456789012345678901234567890"

    # Mock pair contract
    mock_pair = Mock()
    mock_pair.functions.getReserves.return_value.call.return_value = (
        Web3.to_wei(0.5, "ether"),
        Web3.to_wei(0.5, "ether"),
        0,
    )
    security_manager.blockchain.get_contract.return_value = mock_pair

    with pytest.raises(SecurityError) as exc_info:
        security_manager.verify_liquidity(token_address)
    assert "Insufficient liquidity" in str(exc_info.value)


def test_sandwich_attack_detection(security_manager):
    """Test sandwich attack detection"""
    token_address = "0x1234567890123456789012345678901234567890"

    # Mock pending transactions showing sandwich attack pattern
    mock_pending_txs = [
        {
            "from": "0xAttacker1",
            "gasPrice": 1000000000000,
            "value": Web3.to_wei(10, "ether"),
        },
        {"from": "0xVictim", "gasPrice": 50000000000, "value": Web3.to_wei(1, "ether")},
        {
            "from": "0xAttacker2",
            "gasPrice": 1000000000000,
            "value": Web3.to_wei(10, "ether"),
        },
    ]

    class PendingBlock:
        def __init__(self, txs):
            self.transactions = txs

    security_manager.w3.eth.get_block.return_value = PendingBlock(mock_pending_txs)

    with pytest.raises(SecurityError) as exc_info:
        security_manager.check_sandwich_attack(token_address)
    assert "Potential sandwich attack detected" in str(exc_info.value)


def test_gas_price_manipulation(security_manager):
    """Test gas price manipulation detection"""
    # Mock extremely high gas price
    security_manager.blockchain.get_gas_price.return_value = Web3.to_wei(1000, "gwei")

    with pytest.raises(SecurityError) as exc_info:
        security_manager.check_gas_price()
    assert "Suspicious gas price detected" in str(exc_info.value)


def test_contract_blacklist(security_manager):
    """Test contract blacklist checking"""
    blacklisted_address = "0x1234567890123456789012345678901234567890"

    # Mock blacklisted contract
    with patch.object(security_manager, "_is_blacklisted", return_value=True):
        with pytest.raises(SecurityError) as exc_info:
            security_manager.verify_contract(blacklisted_address)
        assert "Contract is blacklisted" in str(exc_info.value)


def test_token_restrictions(security_manager):
    """Test token trading restrictions"""
    token_address = "0x1234567890123456789012345678901234567890"

    # Mock contract with trading restrictions
    mock_functions = Mock()
    mock_functions.maxTxAmount.return_value.call.return_value = Web3.to_wei(
        0.1, "ether"
    )
    mock_functions.maxWalletAmount.return_value.call.return_value = Web3.to_wei(
        1, "ether"
    )
    mock_contract = Mock()
    mock_contract.functions = mock_functions
    security_manager.blockchain.get_contract.return_value = mock_contract

    with pytest.raises(SecurityError) as exc_info:
        security_manager.check_token_restrictions(token_address)
    assert "Trading restrictions detected" in str(exc_info.value)


def test_contract_verification_status(security_manager):
    """Test contract verification status checking"""
    unverified_address = "0x1234567890123456789012345678901234567890"

    # Mock unverified contract
    security_manager.w3.eth.get_code.return_value = b"\x60\x60\x60\x40"

    result = security_manager.verify_contract(unverified_address)
    assert result["is_verified"] is False


def test_liquidity_lock_verification(security_manager):
    """Test liquidity lock verification"""
    token_address = "0x1234567890123456789012345678901234567890"

    # Mock unlocked liquidity
    with patch.object(security_manager, "_is_liquidity_locked", return_value=False):
        with pytest.raises(SecurityError) as exc_info:
            security_manager.verify_liquidity_lock(token_address)
        assert "Liquidity is not locked" in str(exc_info.value)


def test_contract_code_size(security_manager):
    """Test contract code size verification"""
    token_address = "0x1234567890123456789012345678901234567890"

    # Mock contract with suspicious code size
    security_manager.w3.eth.get_code.return_value = b"0" * 100000

    with pytest.raises(SecurityError) as exc_info:
        security_manager.verify_contract_size(token_address)
    assert "Suspicious contract size" in str(exc_info.value)


def test_contract_owner_verification(security_manager):
    """Test contract owner verification"""
    token_address = "0x1234567890123456789012345678901234567890"

    # Mock contract with suspicious owner
    mock_functions = Mock()
    mock_functions.owner.return_value.call.return_value = (
        "0x0000000000000000000000000000000000000000"
    )
    mock_contract = Mock()
    mock_contract.functions = mock_functions
    security_manager.blockchain.get_contract.return_value = mock_contract

    with pytest.raises(SecurityError) as exc_info:
        security_manager.verify_contract_owner(token_address)
    assert "Suspicious contract owner" in str(exc_info.value)


def test_contract_permissions(security_manager):
    """Test contract permissions verification"""
    token_address = "0x1234567890123456789012345678901234567890"

    # Mock contract with dangerous permissions
    mock_functions = Mock()
    mock_functions.mint.return_value.call.return_value = True
    mock_functions.pause.return_value.call.return_value = True
    mock_functions.blacklist.return_value.call.return_value = True
    mock_contract = Mock()
    mock_contract.functions = mock_functions
    security_manager.blockchain.get_contract.return_value = mock_contract

    with pytest.raises(SecurityError) as exc_info:
        security_manager.verify_contract_permissions(token_address)
    assert "Dangerous function detected" in str(exc_info.value)
