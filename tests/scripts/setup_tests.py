#!/usr/bin/env python3
"""
Test Setup Script for Crypto Sniping Bot
Sets up everything needed to run tests successfully
"""

import os
import sys
import subprocess
import json
from pathlib import Path
import shutil


def check_python_version():
    """Check if Python version is compatible."""
    print("🐍 Checking Python version...")
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✓ Python {version.major}.{version.minor}.{version.micro} is compatible")
    return True


def install_dependencies():
    """Install all required dependencies."""
    print("\n📦 Installing dependencies...")
    try:
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "--upgrade", "pip"],
            check=True,
            capture_output=True,
        )
        subprocess.run(
            [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
            check=True,
            capture_output=True,
        )
        print("✓ All dependencies installed successfully")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False


def setup_directories():
    """Create necessary directories."""
    print("\n📁 Setting up directories...")

    directories = ["tests", "abis", "logs", "data", ".pytest_cache"]

    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✓ Directory {directory}/ ready")

    return True


def setup_abi_files():
    """Ensure ABI files exist with proper content."""
    print("\n📄 Setting up ABI files...")

    abi_files = {
        "erc20.json": [
            {
                "constant": True,
                "inputs": [],
                "name": "name",
                "outputs": [{"name": "", "type": "string"}],
                "type": "function",
            },
            {
                "constant": True,
                "inputs": [{"name": "_owner", "type": "address"}],
                "name": "balanceOf",
                "outputs": [{"name": "balance", "type": "uint256"}],
                "type": "function",
            },
            {
                "constant": False,
                "inputs": [
                    {"name": "_to", "type": "address"},
                    {"name": "_value", "type": "uint256"},
                ],
                "name": "transfer",
                "outputs": [{"name": "", "type": "bool"}],
                "type": "function",
            },
        ]
    }

    abis_dir = Path("abis")
    for filename, abi_content in abi_files.items():
        abi_path = abis_dir / filename
        if not abi_path.exists() or abi_path.stat().st_size < 50:
            with open(abi_path, "w", encoding="utf-8") as f:
                json.dump(abi_content, f, indent=2)
            print(f"✓ {filename} created/updated")
        else:
            print(f"✓ {filename} already exists")

    return True


def setup_config_files():
    """Setup test configuration files."""
    print("\n⚙️ Setting up configuration files...")

    # Create test environment file for safe testing
    test_config = Path("test_safe.config.env")
    if not test_config.exists():
        with open(test_config, "w", encoding="utf-8") as f:
            f.write(
                """# Safe Test Configuration - No Real Keys!
# This file is safe for testing and won't expose any funds

RPC_URL=https://mainnet.infura.io/v3/test-key-placeholder
BACKUP_RPC_URLS=https://eth.llamarpc.com,https://rpc.ankr.com/eth
WALLET_ADDRESS=0x742d35Cc6634C0532925a3b8D4C3C3bE6DD5A999
PRIVATE_KEY=0x9f8c8c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c5c
ROUTER_ADDRESS=0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D
FACTORY_ADDRESS=0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f
WETH_ADDRESS=0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2
CHAIN_ID=1

# Trading settings
MIN_LIQUIDITY_ETH=1.0
MAX_GAS_PRICE=100
SLIPPAGE_TOLERANCE=5.0
MAX_TRADE_AMOUNT=1.0

# Performance settings
MAX_RPC_CALLS_PER_SECOND=10
MAX_CONCURRENT_TRADES=5
WEBHOOK_URL=https://hooks.slack.com/services/test/webhook
DATABASE_URL=sqlite:///test_sniper_data.db
"""
            )
        print("✓ test_safe.config.env created")
    else:
        print("✓ test_safe.config.env already exists")

    return True


def setup_pytest_config():
    """Ensure pytest configuration is optimal."""
    print("\n🧪 Setting up pytest configuration...")

    pytest_ini_content = """[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto
markers =
    asyncio: marks tests as async
    requires_node: marks tests that require a running blockchain node
    slow: marks tests as slow running
    unit: marks tests as unit tests
    integration: marks tests as integration tests
    security: marks tests as security-related
filterwarnings =
    ignore::DeprecationWarning
    ignore::PendingDeprecationWarning
    ignore::UserWarning:web3.*
    ignore::UserWarning:eth_utils.*
    ignore::RuntimeWarning:asyncio.*
addopts = 
    --tb=short
    --strict-markers
    --disable-warnings
    -v
"""

    with open("pytest.ini", "w", encoding="utf-8") as f:
        f.write(pytest_ini_content)
    print("✓ pytest.ini configured")

    return True


def create_test_runner():
    """Create convenient test runner scripts."""
    print("\n🏃 Creating test runner scripts...")

    # Python test runner
    test_runner_content = '''#!/usr/bin/env python3
"""
Convenient test runner for the crypto sniping bot
"""

import subprocess
import sys
from pathlib import Path

def run_all_tests():
    """Run all tests with coverage."""
    print("Running all tests...")
    cmd = [
        sys.executable, "-m", "pytest", 
        "--cov=bot", 
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "-v"
    ]
    return subprocess.run(cmd)

def run_unit_tests():
    """Run only unit tests."""
    print("Running unit tests...")
    cmd = [sys.executable, "-m", "pytest", "-m", "unit", "-v"]
    return subprocess.run(cmd)

def run_integration_tests():
    """Run only integration tests."""
    print("Running integration tests...")
    cmd = [sys.executable, "-m", "pytest", "-m", "integration", "-v"]
    return subprocess.run(cmd)

def run_clean_test():
    """Run the clean comprehensive test."""
    print("Running clean comprehensive test...")
    cmd = [sys.executable, "test_clean.py"]
    return subprocess.run(cmd)

def run_security_tests():
    """Run security-focused tests."""
    print("Running security tests...")
    cmd = [sys.executable, "-m", "pytest", "-m", "security", "-v"]
    return subprocess.run(cmd)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        if test_type == "unit":
            result = run_unit_tests()
        elif test_type == "integration":
            result = run_integration_tests()
        elif test_type == "clean":
            result = run_clean_test()
        elif test_type == "security":
            result = run_security_tests()
        else:
            print("Usage: python run_tests.py [unit|integration|clean|security|all]")
            sys.exit(1)
    else:
        result = run_all_tests()
    
    sys.exit(result.returncode)
'''

    with open("run_tests.py", "w", encoding="utf-8") as f:
        f.write(test_runner_content)
    print("✓ run_tests.py created")

    # Batch file for Windows
    batch_content = """@echo off
echo Running Crypto Sniping Bot Tests
echo.

if "%1"=="clean" (
    echo Running clean comprehensive test...
    python test_clean.py
) else if "%1"=="unit" (
    echo Running unit tests...
    python -m pytest -m unit -v
) else if "%1"=="integration" (
    echo Running integration tests...
    python -m pytest -m integration -v
) else if "%1"=="security" (
    echo Running security tests...
    python -m pytest -m security -v
) else (
    echo Running all tests with coverage...
    python -m pytest --cov=bot --cov-report=term-missing --cov-report=html:htmlcov -v
)

echo.
echo Test run completed!
pause
"""

    with open("run_tests.bat", "w", encoding="utf-8") as f:
        f.write(batch_content)
    print("✓ run_tests.bat created")

    return True


def verify_setup():
    """Verify that everything is set up correctly."""
    print("\n✅ Verifying setup...")

    checks = [
        ("Python imports work", lambda: __import__("bot.config")),
        ("Pytest available", lambda: __import__("pytest")),
        ("Web3 available", lambda: __import__("web3")),
        ("ABI files exist", lambda: Path("abis/erc20.json").exists()),
        ("Test config exists", lambda: Path("test_safe.config.env").exists()),
    ]

    all_good = True
    for check_name, check_func in checks:
        try:
            check_func()
            print(f"✓ {check_name}")
        except Exception as e:
            print(f"❌ {check_name}: {e}")
            all_good = False

    return all_good


def main():
    """Main setup function."""
    print("🚀 Setting up Crypto Sniping Bot Test Environment\n")

    steps = [
        ("Python version", check_python_version),
        ("Dependencies", install_dependencies),
        ("Directories", setup_directories),
        ("ABI files", setup_abi_files),
        ("Config files", setup_config_files),
        ("Pytest config", setup_pytest_config),
        ("Test runners", create_test_runner),
        ("Verification", verify_setup),
    ]

    for step_name, step_func in steps:
        if not step_func():
            print(f"\n❌ Setup failed at: {step_name}")
            return False

    print("\n🎉 Test environment setup completed successfully!")
    print("\nYou can now run tests using:")
    print("  • python test_clean.py           (comprehensive test)")
    print("  • python run_tests.py            (all tests with coverage)")
    print("  • python run_tests.py clean      (clean comprehensive test)")
    print("  • python run_tests.py unit       (unit tests only)")
    print("  • python run_tests.py security   (security tests only)")
    print("  • pytest                         (standard pytest)")
    print("  • run_tests.bat                  (Windows batch file)")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
