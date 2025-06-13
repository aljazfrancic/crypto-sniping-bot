"""
Python Bot Tests
Tests for the sniper bot components

Note: For web3.py 6.x, use 'from web3.middleware import geth_poa_middleware' for PoA middleware.
"""

import sys
import pytest
import signal
import aiohttp
from unittest.mock import Mock, AsyncMock, patch
from web3 import Web3
from eth_typing import Address

import bot.config as config_module
import bot.blockchain as blockchain_module
import bot.trading as trading_module
import bot.honeypot as honeypot_module
from bot.sniper import SniperBot
from bot.config import Config
from bot.blockchain import BlockchainInterface
from bot.trading import TradingEngine
from bot.honeypot import HoneypotDetector

# Set up module aliases
sys.modules.setdefault("config", config_module)
sys.modules.setdefault("blockchain", blockchain_module)
sys.modules.setdefault("trading", trading_module)
sys.modules.setdefault("honeypot", honeypot_module)


@pytest.fixture(autouse=True)
def _patch_load_contract(monkeypatch):
    """Avoid loading real contracts during tests."""
    monkeypatch.setattr(BlockchainInterface, "_load_sniper_contract", lambda self: None)


@pytest.fixture
def mock_config():
    config = Mock(spec=Config)
    config.rpc_url = "http://localhost:8545"
    config.chain_id = 1
    config.router_address = "0xrouter"
    config.factory_address = "0xfactory"
    config.weth_address = "0xweth"
    config.pair_address = "0xpair"
    config.private_key = "0x" + "1" * 64
    config.buy_amount = 0.1
    config.slippage = 5
    config.SLIPPAGE = 5
    config.min_liquidity = 1.0
    config.check_honeypot = True
    config.gas_price_multiplier = 1.2
    config.get_abi = Mock(return_value=[])
    config.get_network_name = Mock(return_value="Ethereum Mainnet")
    config.RPC_URL = "http://localhost:8545"
    return config


@pytest.fixture
def mock_w3():
    """Create mock Web3 instance"""
    w3 = Mock(spec=Web3)
    w3.eth = Mock()
    w3.eth.chain_id = 1
    w3.eth.gas_price = 50000000000  # 50 gwei
    w3.eth.get_transaction_count = Mock(return_value=1)
    w3.eth.estimate_gas = Mock(return_value=300000)
    w3.eth.send_raw_transaction = Mock(return_value=b"0x" + b"1" * 64)
    w3.eth.contract = Mock()
    w3.is_connected = Mock(return_value=True)
    w3.eth.get_code.return_value = b'\x60\x60\x60\x40'
    w3.eth.get_block.return_value = {'baseFeePerGas': 1000000000}
    w3.eth.max_priority_fee = 100000000
    return w3


# Patch Web3.is_connected globally for all tests
@pytest.fixture(autouse=True)
def patch_web3_is_connected(monkeypatch):
    monkeypatch.setattr(Web3, "is_connected", lambda self: True)
    yield


class TestBlockchainInterface:
    def test_initialization(self, mock_w3, mock_config):
        """Test blockchain interface initialization"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            blockchain = BlockchainInterface(mock_config)
            blockchain.w3 = mock_w3
        assert blockchain.w3 == mock_w3
        assert blockchain.config == mock_config

    @pytest.mark.asyncio
    async def test_get_pair_liquidity(self, mock_w3, mock_config):
        """Test getting pair liquidity"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            blockchain = BlockchainInterface(mock_config)
            blockchain.w3 = mock_w3

            # Mock pair contract
            mock_pair = Mock()
            mock_pair.functions.getReserves.return_value.call.return_value = (
                10**20,  # token reserve
                10**19,  # WETH reserve
                1234567890,  # timestamp
            )
            mock_pair.functions.token0.return_value.call.return_value = (
                "0x000000000000000000000000000000000000dEaD"
            )

            mock_w3.eth.contract.return_value = mock_pair

            liquidity = await blockchain.get_pair_liquidity(
                "0x2222222222222222222222222222222222222222"
            )
            assert liquidity == 10.0  # 10^19 wei = 10 ETH

    @pytest.mark.asyncio
    async def test_get_token_price(self, mock_w3, mock_config):
        """Test getting token price"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            blockchain = BlockchainInterface(mock_config)
            blockchain.w3 = mock_w3

            # Mock pair contract
            mock_pair = Mock()
            mock_pair.functions.getReserves.return_value.call.return_value = (
                10**20,  # token reserve (100 tokens)
                10**19,  # WETH reserve (10 ETH)
                1234567890,
            )

            mock_w3.eth.contract.return_value = mock_pair

            price = await blockchain.get_token_price(
                "0x2222222222222222222222222222222222222222", True
            )
            assert price == 0.1  # 10 ETH / 100 tokens = 0.1 ETH per token


class TestTradingEngine:
    @pytest.mark.asyncio
    async def test_buy_token(self, mock_w3, mock_config):
        """Test buying tokens"""
        blockchain = Mock(spec=BlockchainInterface)
        blockchain.w3 = mock_w3
        blockchain.sniper_contract = Mock()
        blockchain.build_transaction = Mock(return_value={"gas": 300000})
        blockchain.send_transaction = AsyncMock(return_value="0xtxhash")
        blockchain.config = mock_config
        if hasattr(blockchain, 'blockchain'):
            blockchain.blockchain = blockchain

        trading = TradingEngine(blockchain, mock_config)

        tx_hash = await trading.buy_token(
            "0x1111111111111111111111111111111111111111", 0.1, 100
        )
        assert tx_hash == "0xtxhash"

    @pytest.mark.asyncio
    async def test_sell_token(self, mock_w3, mock_config):
        """Test selling tokens"""
        blockchain = Mock(spec=BlockchainInterface)
        blockchain.w3 = mock_w3
        blockchain.sniper_contract = Mock()
        blockchain.build_transaction = Mock(return_value={"gas": 300000})
        blockchain.send_transaction = AsyncMock(return_value="0xtxhash")
        blockchain.config = mock_config
        if hasattr(blockchain, 'blockchain'):
            blockchain.blockchain = blockchain

        trading = TradingEngine(blockchain, mock_config)

        tx_hash = await trading.sell_token(
            "0x1111111111111111111111111111111111111111", 1000, 0.1
        )
        assert tx_hash == "0xtxhash"


class TestHoneypotDetector:
    @pytest.mark.asyncio
    async def test_check_contract_code(self, mock_w3, mock_config):
        """Test contract code checking"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            blockchain = BlockchainInterface(mock_config)
            blockchain.w3 = mock_w3
            blockchain.config = mock_config
            detector = HoneypotDetector(blockchain)

            # Mock contract code
            mock_w3.eth.get_code = Mock(return_value=b"0x606060")

            result = await detector._check_contract_code(
                "0x1111111111111111111111111111111111111111"
            )
            assert isinstance(result, bool)

    @pytest.mark.asyncio
    async def test_check_token_functions(self, mock_w3, mock_config):
        """Test token function checking"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            blockchain = BlockchainInterface(mock_config)
            blockchain.w3 = mock_w3
            blockchain.config = mock_config
            detector = HoneypotDetector(blockchain)

            # Mock token contract
            mock_token = Mock()
            mock_token.functions.name.return_value.call.return_value = "Test Token"
            mock_token.functions.symbol.return_value.call.return_value = "TEST"
            mock_token.functions.decimals.return_value.call.return_value = 18
            mock_token.functions.totalSupply.return_value.call.return_value = 10**24

            mock_w3.eth.contract.return_value = mock_token

            result = await detector._check_token_functions(
                "0x1111111111111111111111111111111111111111"
            )
            assert not result  # Should pass all checks

    @pytest.mark.asyncio
    async def test_honeypot_cache(self, mock_w3, mock_config):
        """Test honeypot result caching"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            blockchain = BlockchainInterface(mock_config)
            blockchain.w3 = mock_w3
            blockchain.config = mock_config
            detector = HoneypotDetector(blockchain)

            # Mock successful checks
            detector._check_contract_code = AsyncMock(return_value=False)
            detector._check_honeypot_api = AsyncMock(return_value=False)
            detector._check_token_functions = AsyncMock(return_value=False)

            # First check
            result1 = await detector.check(
                "0x1111111111111111111111111111111111111111"
            )
            assert not result1

            # Second check should use cache
            result2 = await detector.check(
                "0x1111111111111111111111111111111111111111"
            )
            assert not result2

            # Check that methods were only called once
            detector._check_contract_code.assert_called_once()
            detector._check_honeypot_api.assert_called_once()
            detector._check_token_functions.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_honeypot_api(self, mock_w3, mock_config, monkeypatch):
        """Test honeypot API checking"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            blockchain = BlockchainInterface(mock_config)
            blockchain.w3 = mock_w3
            blockchain.config = mock_config
            detector = HoneypotDetector(blockchain)

            class Resp:
                status = 200

                async def json(self):
                    return {"isHoneypot": False}

                async def __aenter__(self):
                    return self

                async def __aexit__(self, exc_type, exc, tb):
                    pass

            class Session:
                async def __aenter__(self):
                    return self

                async def __aexit__(self, exc_type, exc, tb):
                    pass

                def get(self, url, timeout):
                    return Resp()

            monkeypatch.setattr(aiohttp, "ClientSession", Session)

            result = await detector._check_honeypot_api(
                "0x1111111111111111111111111111111111111111"
            )
            assert not result


class TestConfig:
    def test_config_validation(self):
        """Test configuration validation"""
        with patch.dict(
            "os.environ",
            {
                "RPC_URL": "ws://localhost:8545",
                "CHAIN_ID": "1",
                "ROUTER_ADDRESS": (
                    "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
                ),
                "FACTORY_ADDRESS": (
                    "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
                ),
                "WETH_ADDRESS": (
                    "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
                ),
                "PRIVATE_KEY": "0x" + "1" * 64,
                "BUY_AMOUNT": "0.1",
                "SLIPPAGE": "5",
            },
        ):
            with patch.object(Config, '_load_abis', lambda self: None):
                config = Config()
                assert config.rpc_url == "ws://localhost:8545"
                assert config.chain_id == 1
                assert config.router_address == "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"

    def test_invalid_private_key(self):
        """Test invalid private key validation"""
        with patch.dict(
            "os.environ",
            {
                "RPC_URL": "ws://localhost:8545",
                "CHAIN_ID": "1",
                "ROUTER_ADDRESS": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
                "FACTORY_ADDRESS": "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f",
                "WETH_ADDRESS": "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
                "PRIVATE_KEY": "invalid_key",
            },
        ):
            with patch.object(Config, '_load_abis', lambda self: None):
                with pytest.raises(ValueError, match="Invalid private key"):
                    Config()


class TestBlockchainInterfaceAdvanced:
    def test_get_minimal_abi(self, mock_w3, mock_config):
        """Test getting minimal ABI"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            blockchain = BlockchainInterface(mock_config)
            blockchain.w3 = mock_w3
            abi = blockchain._get_minimal_abi()
            assert isinstance(abi, list)

    def test_build_transaction(self, mock_w3, mock_config):
        """Test building transaction"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            blockchain = BlockchainInterface(mock_config)
            blockchain.w3 = mock_w3
            tx = blockchain.build_transaction(
                "0x1111111111111111111111111111111111111111",
                "0x2222222222222222222222222222222222222222",
                1000000,
            )
            assert isinstance(tx, dict)

    @pytest.mark.asyncio
    async def test_send_transaction(self, mock_w3, mock_config):
        """Test sending transaction"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            blockchain = BlockchainInterface(mock_config)
            blockchain.w3 = mock_w3
            tx_hash = await blockchain.send_transaction(
                "0x1111111111111111111111111111111111111111",
                "0x2222222222222222222222222222222222222222",
                1000000,
            )
            assert isinstance(tx_hash, str)


class TestTradingEngineExtra:
    @pytest.mark.asyncio
    async def test_emergency_sell_all(self, mock_w3, mock_config):
        """Test emergency sell all functionality"""
        blockchain = Mock(spec=BlockchainInterface)
        blockchain.w3 = mock_w3
        blockchain.sniper_contract = Mock()
        blockchain.build_transaction = Mock(return_value={"gas": 300000})
        blockchain.send_transaction = AsyncMock(return_value="0xtxhash")
        blockchain.get_token_balance = AsyncMock(return_value=1000)
        blockchain.config = mock_config
        if hasattr(blockchain, 'blockchain'):
            blockchain.blockchain = blockchain
        mock_config.SLIPPAGE = 5

        trading = TradingEngine(blockchain, mock_config)

        tx_hash = await trading.emergency_sell_all(
            "0x1111111111111111111111111111111111111111"
        )
        assert tx_hash == "0xtxhash"

    @pytest.mark.asyncio
    async def test_emergency_sell_all_no_balance(self, mock_w3, mock_config):
        """Test emergency sell all with no balance"""
        blockchain = Mock(spec=BlockchainInterface)
        blockchain.w3 = mock_w3
        blockchain.sniper_contract = Mock()
        blockchain.build_transaction = Mock(return_value={"gas": 300000})
        blockchain.send_transaction = AsyncMock(return_value="0xtxhash")
        blockchain.get_token_balance = AsyncMock(return_value=0)
        blockchain.config = mock_config
        if hasattr(blockchain, 'blockchain'):
            blockchain.blockchain = blockchain
        mock_config.SLIPPAGE = 5

        trading = TradingEngine(blockchain, mock_config)

        tx_hash = await trading.emergency_sell_all(
            "0x1111111111111111111111111111111111111111"
        )
        assert tx_hash is None


class TestConfigExtra:
    def test_get_network_name(self, mock_config):
        """Test getting network name"""
        assert mock_config.get_network_name() == "Ethereum Mainnet"


class TestBlockchainInterfaceMore:
    @pytest.mark.asyncio
    async def test_get_token_balance(self, mock_w3, mock_config):
        """Test getting token balance"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            blockchain = BlockchainInterface(mock_config)
            blockchain.w3 = mock_w3
            balance = await blockchain.get_token_balance(
                "0x1111111111111111111111111111111111111111",
                "0x2222222222222222222222222222222222222222",
            )
            assert isinstance(balance, int)

    @pytest.mark.asyncio
    async def test_verify_sniper_contract(self, mock_w3, mock_config):
        """Test verifying sniper contract"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            blockchain = BlockchainInterface(mock_config)
            blockchain.w3 = mock_w3
            result = await blockchain.verify_sniper_contract()
            assert isinstance(result, bool)


class TestSniperBot:
    @pytest.fixture
    def mock_sniper_bot(self, mock_w3, mock_config):
        """Create a mock SniperBot instance with mocked dependencies"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            blockchain = BlockchainInterface(mock_config)
            blockchain.w3 = mock_w3
            trading = TradingEngine(blockchain, mock_config)
            detector = HoneypotDetector(blockchain)
            bot = SniperBot(mock_config)
            bot.blockchain = blockchain
            bot.trading = trading
            bot.honeypot_detector = detector
            return bot

    @pytest.mark.asyncio
    async def test_initialize(self, mock_w3, mock_config):
        """Test bot initialization"""
        with patch.object(BlockchainInterface, "_load_sniper_contract", return_value=None):
            bot = SniperBot(mock_config)
            await bot.initialize()
            assert bot.blockchain is not None
            assert bot.trading is not None
            assert bot.honeypot_detector is not None

    @pytest.mark.asyncio
    async def test_is_token_safe_false(self, mock_sniper_bot):
        """Test token safety check when token is unsafe"""
        mock_sniper_bot.honeypot_detector.check = AsyncMock(return_value=True)
        result = await mock_sniper_bot.is_token_safe("0xunsafe")
        assert not result

    @pytest.mark.asyncio
    async def test_handle_new_token(self, mock_sniper_bot):
        """Test handling of new token detection"""
        # Mock successful checks
        mock_sniper_bot.is_token_safe = AsyncMock(return_value=True)
        mock_sniper_bot.blockchain.get_pair_liquidity = AsyncMock(return_value=2.0)
        mock_sniper_bot.trading.buy_token = AsyncMock(return_value="0xtxhash")

        await mock_sniper_bot.handle_new_token("0xnewtoken")
        mock_sniper_bot.trading.buy_token.assert_called_once()

    @pytest.mark.asyncio
    async def test_handle_new_token_unsafe(self, mock_sniper_bot):
        """Test handling of unsafe token"""
        mock_sniper_bot.is_token_safe = AsyncMock(return_value=False)
        await mock_sniper_bot.handle_new_token("0xunsafe")
        mock_sniper_bot.trading.buy_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_new_token_insufficient_liquidity(self, mock_sniper_bot):
        """Test handling of token with insufficient liquidity"""
        mock_sniper_bot.is_token_safe = AsyncMock(return_value=True)
        mock_sniper_bot.blockchain.get_pair_liquidity = AsyncMock(return_value=0.5)
        await mock_sniper_bot.handle_new_token("0xlowliquidity")
        mock_sniper_bot.trading.buy_token.assert_not_called()

    @pytest.mark.asyncio
    async def test_handle_new_token_buy_failure(self, mock_sniper_bot):
        """Test handling of buy transaction failure"""
        mock_sniper_bot.is_token_safe = AsyncMock(return_value=True)
        mock_sniper_bot.blockchain.get_pair_liquidity = AsyncMock(return_value=2.0)
        mock_sniper_bot.trading.buy_token = AsyncMock(side_effect=Exception("Buy failed"))
        
        with pytest.raises(Exception) as exc_info:
            await mock_sniper_bot.handle_new_token("0xnewtoken")
        assert str(exc_info.value) == "Buy failed"

    @pytest.mark.asyncio
    async def test_emergency_sell(self, mock_sniper_bot):
        """Test emergency sell functionality"""
        mock_sniper_bot.trading.emergency_sell_all = AsyncMock(return_value="0xtxhash")
        await mock_sniper_bot.emergency_sell("0xtoken")
        mock_sniper_bot.trading.emergency_sell_all.assert_called_once_with("0xtoken")

    @pytest.mark.asyncio
    async def test_emergency_sell_failure(self, mock_sniper_bot):
        """Test emergency sell failure handling"""
        mock_sniper_bot.trading.emergency_sell_all = AsyncMock(side_effect=Exception("Sell failed"))
        with pytest.raises(Exception) as exc_info:
            await mock_sniper_bot.emergency_sell("0xtoken")
        assert str(exc_info.value) == "Sell failed"

    def test_cleanup(self, mock_sniper_bot):
        """Test bot cleanup"""
        mock_sniper_bot.cleanup()
        # Add assertions based on cleanup implementation
        assert mock_sniper_bot.running is False
