#!/usr/bin/env python3
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
