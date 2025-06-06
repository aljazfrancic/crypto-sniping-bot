"""
Python Bot Tests
Tests for the sniper bot components
"""

import pytest
import asyncio
from unittest.mock import Mock, AsyncMock, patch
from web3 import Web3
from config import Config
from blockchain import BlockchainInterface
from trading import TradingEngine
from honeypot import HoneypotChecker


@pytest.fixture
def mock_config():
    """Create mock configuration"""
    config = Mock(spec=Config)
    config.RPC_URL = "ws://localhost:8545"
    config.CHAIN_ID = 1
    config.ROUTER_ADDRESS = "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D"
    config.FACTORY_ADDRESS = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
    config.WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2"
    config.SNIPER_CONTRACT = "0x1234567890123456789012345678901234567890"
    config.PRIVATE_KEY = "0x" + "1" * 64
    config.BUY_AMOUNT = 0.1
    config.SLIPPAGE = 5
    config.GAS_PRICE_MULTIPLIER = 1.5
    config.PROFIT_TARGET = 50
    config.STOP_LOSS = 10
    config.AUTO_SELL = True
    config.MIN_LIQUIDITY = 5
    config.CHECK_HONEYPOT = True
    config.USE_HONEYPOT_API = True
    config.WAIT_FOR_CONFIRMATION = False
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
    w3.eth.send_raw_transaction = Mock(return_value=b'0x' + b'1' * 64)
    w3.eth.contract = Mock()
    w3.is_connected = Mock(return_value=True)
    return w3


class TestBlockchainInterface:
    def test_initialization(self, mock_w3, mock_config):
        """Test blockchain interface initialization"""
        blockchain = BlockchainInterface(mock_w3, mock_config)
        assert blockchain.w3 == mock_w3
        assert blockchain.config == mock_config
        
    @pytest.mark.asyncio
    async def test_get_pair_liquidity(self, mock_w3, mock_config):
        """Test getting pair liquidity"""
        blockchain = BlockchainInterface(mock_w3, mock_config)
        
        # Mock pair contract
        mock_pair = Mock()
        mock_pair.functions.getReserves.return_value.call.return_value = (
            10**20,  # token reserve
            10**19,  # WETH reserve
            1234567890  # timestamp
        )
        mock_pair.functions.token0.return_value.call.return_value = mock_config.WETH_ADDRESS
        
        mock_w3.eth.contract.return_value = mock_pair
        
        liquidity = await blockchain.get_pair_liquidity("0xpairaddress")
        assert liquidity == 10.0  # 10^19 wei = 10 ETH
        
    @pytest.mark.asyncio
    async def test_get_token_price(self, mock_w3, mock_config):
        """Test getting token price"""
        blockchain = BlockchainInterface(mock_w3, mock_config)
        
        # Mock pair contract
        mock_pair = Mock()
        mock_pair.functions.getReserves.return_value.call.return_value = (
            10**20,  # token reserve (100 tokens)
            10**19,  # WETH reserve (10 ETH)
            1234567890
        )
        
        mock_w3.eth.contract.return_value = mock_pair
        
        price = await blockchain.get_token_price("0xpairaddress", True)
        assert price == 0.1  # 10 ETH / 100 tokens = 0.1 ETH per token


class TestTradingEngine:
    @pytest.mark.asyncio
    async def test_buy_token(self, mock_w3, mock_config):
        """Test buying tokens"""
        blockchain = Mock(spec=BlockchainInterface)
        blockchain.w3 = mock_w3
        blockchain.sniper_contract = Mock()
        blockchain.build_transaction = Mock(return_value={'gas': 300000})
        blockchain.send_transaction = AsyncMock(return_value="0xtxhash")
        
        trading = TradingEngine(blockchain, mock_config)
        
        tx_hash = await trading.buy_token("0xtokenaddress", 0.1, 100)
        assert tx_hash == "0xtxhash"
        
    @pytest.mark.asyncio
    async def test_sell_token(self, mock_w3, mock_config):
        """Test selling tokens"""
        blockchain = Mock(spec=BlockchainInterface)
        blockchain.w3 = mock_w3
        blockchain.sniper_contract = Mock()
        blockchain.build_transaction = Mock(return_value={'gas': 300000})
        blockchain.send_transaction = AsyncMock(return_value="0xtxhash")
        
        trading = TradingEngine(blockchain, mock_config)
        
        tx_hash = await trading.sell_token("0xtokenaddress", 1000, 0.1)
        assert tx_hash == "0xtxhash"


class TestHoneypotChecker:
    @pytest.mark.asyncio
    async def test_check_contract_code(self, mock_w3, mock_config):
        """Test contract code checking"""
        checker = HoneypotChecker(mock_w3, mock_config)
        
        # Mock contract code
        mock_w3.eth.get_code = AsyncMock(return_value=b'0x606060')
        
        result = await checker._check_contract_code("0xtokenaddress")
        assert isinstance(result, bool)
        
    @pytest.mark.asyncio
    async def test_check_token_functions(self, mock_w3, mock_config):
        """Test token function checking"""
        checker = HoneypotChecker(mock_w3, mock_config)
        
        # Mock token contract
        mock_token = Mock()
        mock_token.functions.name.return_value.call.return_value = "Test Token"
        mock_token.functions.symbol.return_value.call.return_value = "TEST"
        mock_token.functions.decimals.return_value.call.return_value = 18
        mock_token.functions.totalSupply.return_value.call.return_value = 10**24
        
        mock_w3.eth.contract.return_value = mock_token
        
        result = await checker._check_token_functions("0xtokenaddress")
        assert result == False  # Should pass all checks
        
    @pytest.mark.asyncio
    async def test_honeypot_cache(self, mock_w3, mock_config):
        """Test honeypot result caching"""
        checker = HoneypotChecker(mock_w3, mock_config)
        
        # Mock successful checks
        checker._check_contract_code = AsyncMock(return_value=False)
        checker._check_honeypot_api = AsyncMock(return_value=False)
        checker._check_token_functions = AsyncMock(return_value=False)
        
        # First check
        result1 = await checker.check("0xtokenaddress")
        assert result1 == False
        
        # Second check should use cache
        result2 = await checker.check("0xtokenaddress")
        assert result2 == False
        
        # Check that methods were only called once
        checker._check_contract_code.assert_called_once()


class TestConfig:
    def test_config_validation(self):
        """Test configuration validation"""
        with patch.dict('os.environ', {
            'RPC_URL': 'ws://localhost:8545',
            'CHAIN_ID': '1',
            'ROUTER_ADDRESS': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
            'FACTORY_ADDRESS': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
            'WETH_ADDRESS': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
            'PRIVATE_KEY': '0x' + '1' * 64,
            'BUY_AMOUNT': '0.1',
            'SLIPPAGE': '5'
        }):
            config = Config()
            assert config.CHAIN_ID == 1
            assert config.BUY_AMOUNT == 0.1
            assert config.SLIPPAGE == 5
            
    def test_invalid_private_key(self):
        """Test invalid private key validation"""
        with patch.dict('os.environ', {
            'RPC_URL': 'ws://localhost:8545',
            'CHAIN_ID': '1',
            'ROUTER_ADDRESS': '0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D',
            'FACTORY_ADDRESS': '0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f',
            'WETH_ADDRESS': '0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2',
            'PRIVATE_KEY': 'invalid_key'
        }):
            with pytest.raises(ValueError, match="Invalid private key"):
                Config()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])