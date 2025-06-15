#!/usr/bin/env python3
"""
CI Validation Script

This script mirrors the GitHub Actions CI pipeline for local testing.
Run this before pushing to validate your changes will pass CI.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description, allow_failure=False):
    """Run a command and handle the result."""
    print(f"\n🔄 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode == 0:
        print(f"✅ {description} - PASSED")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
    else:
        print(f"❌ {description} - FAILED")
        if result.stderr.strip():
            print(f"   Error: {result.stderr.strip()}")
        if not allow_failure:
            return False
    return True


def validate_test_structure():
    """Validate that the test structure exists."""
    print("\n📁 Validating test structure...")

    required_dirs = [
        "tests",
        "tests/unit",
        "tests/integration",
        "tests/config",
        "tests/scripts",
    ]

    required_files = [
        "tests/unit/test_exceptions.py",
        "tests/unit/test_security.py",
        "tests/integration/test_sniper.py",
        "tests/integration/test_clean.py",
        "tests/integration/test_improvements.py",
        "tests/config/test.config.env",
        "tests/config/test_safe.config.env",
        "run_tests.py",
        "pytest.ini",
    ]

    # Check directories
    for dir_path in required_dirs:
        if not Path(dir_path).exists():
            print(f"❌ Missing directory: {dir_path}")
            return False
        print(f"✅ Directory exists: {dir_path}")

    # Check files
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Missing file: {file_path}")
            return False
        print(f"✅ File exists: {file_path}")

    print("✅ Test structure validation - PASSED")
    return True


def main():
    """Run the complete CI validation pipeline."""
    print("🎯 Starting CI Validation Pipeline")
    print("=" * 50)

    # Change to script directory
    os.chdir(Path(__file__).parent)

    # Validation steps (mirrors .github/workflows/ci.yml)
    steps = [
        # Test structure validation
        (validate_test_structure, "Test structure validation", False),
        # Setup test environment
        ("cp tests/config/test.config.env .env", "Setup test environment", False),
        # Module import tests
        (
            "python -c \"from bot.config import Config; print('✅ Config module')\"",
            "Config module import",
            False,
        ),
        (
            "python -c \"from bot.blockchain import BlockchainInterface; print('✅ BlockchainInterface module')\"",
            "BlockchainInterface module import",
            False,
        ),
        (
            "python -c \"from bot.trading import TradingEngine; print('✅ TradingEngine module')\"",
            "TradingEngine module import",
            False,
        ),
        (
            "python -c \"from bot.honeypot import HoneypotDetector; print('✅ HoneypotDetector module')\"",
            "HoneypotDetector module import",
            False,
        ),
        (
            "python -c \"from bot.security import SecurityManager; print('✅ SecurityManager module')\"",
            "SecurityManager module import",
            False,
        ),
        (
            "python -c \"from bot.exceptions import SniperBotError; print('✅ Exceptions module')\"",
            "Exceptions module import",
            False,
        ),
        # Code quality checks (allow failures)
        ("black --check .", "Black formatting check", True),
        ("mypy bot/", "MyPy type checking", True),
        (
            "pylint bot/ --disable=C0114,C0115,C0116,R0903,R0913,W0613",
            "Pylint static analysis",
            True,
        ),
        # Test execution
        ("python -m pytest tests/unit/ -v --tb=short", "Unit tests (34 tests)", False),
        (
            "python -m pytest tests/integration/ -v --tb=short",
            "Integration tests (35 tests)",
            False,
        ),
        ("python run_tests.py", "Full test suite (72 tests)", False),
    ]

    failed_steps = []

    for step in steps:
        if callable(step[0]):
            # Custom function
            success = step[0]()
        else:
            # Shell command
            success = run_command(step[0], step[1], step[2])

        if not success and not step[2]:  # If not allowed to fail
            failed_steps.append(step[1])

    # Summary
    print("\n" + "=" * 50)
    print("🎯 CI Validation Summary:")

    if not failed_steps:
        print("✅ All critical validations passed!")
        print("🚀 Your changes are ready for CI/CD pipeline!")
        return 0
    else:
        print("❌ Failed validations:")
        for failed in failed_steps:
            print(f"   • {failed}")
        print("\n🔧 Fix these issues before pushing to GitHub")
        return 1


if __name__ == "__main__":
    sys.exit(main())
