#!/usr/bin/env python3
"""
project_patcher_v2.py
 * switches test script to use `npx truffle` (works on Windows + WSL)
 * fixes unit/test_bot.py import path
 * writes .env.test dummy vars for bot startup
"""

from pathlib import Path
import re, textwrap, subprocess, json, os

ROOT = Path(__file__).resolve().parent
ps1 = ROOT / "crypto-sniping-bot-test.ps1"
test_py = ROOT / "unit" / "test_bot.py"
env_test = ROOT / ".env.test"

# --- 1. ensure truffle local & rewrite PS1 ---
contracts_dir = ROOT / "sniper-contracts"
pkg = contracts_dir / "package.json"
if pkg.exists():
    data = json.loads(pkg.read_text())
    if "@truffle/hdwallet-provider" not in json.dumps(data):
        subprocess.run(["npm", "install", "--prefix", str(contracts_dir),
                        "truffle", "@truffle/hdwallet-provider",
                        "@openzeppelin/contracts"], check=True)
        print("✓ installed local truffle into sniper-contracts/")

if ps1.exists():
    txt = ps1.read_text(encoding="utf-8")
    txt = re.sub(r"truffle test", "npx truffle test", txt)
    ps1.with_suffix(".ps1.bak").write_text(txt, encoding="utf-8")
    ps1.write_text(txt, encoding="utf-8")
    print("✓ Patched PS1 to use npx truffle")

# --- 2. fix unit/test_bot.py import ---
if test_py.exists():
    body = test_py.read_text(encoding="utf-8")
    if "sys.path.append" not in body:
        prefix = textwrap.dedent("""
            import sys, pathlib
            ROOT = pathlib.Path(__file__).resolve().parents[2] / "sniper-bot"
            sys.path.append(str(ROOT))
        """)
        test_py.with_suffix(".py.bak").write_text(body, encoding="utf-8")
        test_py.write_text(prefix + "\n" + body, encoding="utf-8")
        print("✓ Fixed import path in unit/test_bot.py")

# --- 3. create .env.test with placeholders ---
if not env_test.exists():
    env_test.write_text(textwrap.dedent("""\
        RPC_HTTP=https://bsc-testnet.publicnode.com
        RPC_WS=wss://bsc-testnet.publicnode.com
        PRIVATE_KEY=0x"your_dummy_key"
        LP_CHECKER_ADDRESS=0x0000000000000000000000000000000000000000
    """))
    print("✓ Wrote .env.test placeholders")

print("\nAll patches applied. Re-run PowerShell script or pytest now.\n")
