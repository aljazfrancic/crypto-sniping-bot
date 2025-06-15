def pytest_configure(config):
    config.addinivalue_line(
        "markers", "requires_node: mark test as requiring a local Ethereum node"
    )


def is_node_running(url="http://localhost:8545"):
    import requests

    try:
        requests.post(
            url,
            json={
                "jsonrpc": "2.0",
                "method": "web3_clientVersion",
                "params": [],
                "id": 1,
            },
            timeout=2,
        )
        return True
    except Exception:
        return False


def pytest_runtest_setup(item):
    if "requires_node" in item.keywords and not is_node_running():
        pytest.skip("Local Ethereum node is not running on localhost:8545")
