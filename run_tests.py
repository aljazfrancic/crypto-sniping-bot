#!/usr/bin/env python3
"""
Wrapper script for running tests - calls the relocated test runner
"""

import subprocess
import sys
import os


def main():
    """Run the test script from its new location."""
    script_path = os.path.join("tests", "scripts", "run_tests.py")

    if not os.path.exists(script_path):
        print(f"Error: Test runner not found at {script_path}")
        sys.exit(1)

    # Pass all arguments to the test runner
    cmd = [sys.executable, script_path] + sys.argv[1:]
    result = subprocess.run(cmd)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
