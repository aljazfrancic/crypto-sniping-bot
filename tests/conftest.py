import os
import sys
from pathlib import Path
import pytest
from unittest.mock import Mock
from web3 import Web3
from bot.blockchain import BlockchainInterface
from bot.config import Config

os.environ["PYTEST_DISABLE_PLUGIN_AUTOLOAD"] = "1"

# Ensure the project root is on the import path so tests work without
# requiring PYTHONPATH to be set manually.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

def pytest_configure(config):
    """Configure pytest for better performance"""
    config.option.tbstyle = "short"  # Shorter traceback format

@pytest.fixture(scope="session")
def mock_web3():
    """Session-scoped Web3 mock to avoid recreation"""
    web3 = Mock(spec=Web3)
    web3.eth = Mock()
    web3.eth.get_block.return_value = {'baseFeePerGas': 1000000000, 'transactions': []}
    web3.eth.gas_price = 1000000000
    web3.eth.max_priority_fee = 100000000
    web3.eth.get_code.return_value = b'\x60\x60\x60\x40'
    return web3

@pytest.fixture(scope="session")
def mock_blockchain(mock_web3):
    """Session-scoped blockchain mock"""
    blockchain = Mock(spec=BlockchainInterface)
    blockchain.w3 = mock_web3
    blockchain.get_gas_price.return_value = 2000000000
    blockchain.get_balance.return_value = Web3.to_wei(1, 'ether')
    blockchain.get_contract = Mock()
    blockchain.web3 = mock_web3
    return blockchain

@pytest.fixture(scope="session")
def mock_config():
    """Session-scoped config mock"""
    config = Mock(spec=Config)
    config.slippage = 5
    config.min_liquidity = 1.0
    config.check_honeypot = True
    config.gas_price_multiplier = 1.2
    config.router_address = '0xrouter'
    config.factory_address = '0xfactory'
    config.weth_address = '0xweth'
    config.pair_address = '0xpair'
    config.get_abi = Mock(return_value=[])
    config.SLIPPAGE = 5
    return config
