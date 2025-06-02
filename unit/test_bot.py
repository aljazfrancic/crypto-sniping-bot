import pytest
from unittest.mock import patch, MagicMock
from ..sniping_bot import listen_for_pools, execute_snipe

@pytest.fixture
def mock_web3():
    with patch('web3.Web3') as mock:
        w3 = mock.return_value
        w3.is_connected.return_value = True
        w3.eth.contract.return_value.events.PairCreated.create_filter.return_value = MagicMock()
        yield w3

def test_listen_for_pools(mock_web3):
    listen_for_pools()
    mock_web3.eth.contract.assert_called()

@patch('sniping_bot.w3')
def test_execute_snipe(mock_w3):
    mock_w3.toWei.return_value = 10**17  # 0.1 ETH
    execute_snipe({'token0': '0xTestToken'})
    mock_w3.eth.contract.return_value.functions.snipe.assert_called()