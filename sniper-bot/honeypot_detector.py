"""Honeypot and scam detection utilities."""
import re
from typing import List, Tuple
from web3 import Web3

HONEYPOT_SELECTORS = [
    "0x3b124fe3",  # _isBlacklisted(address)
    "0x6b7f4e0a",  # botBlacklist(address)
    "0x8da5cb5b",  # owner()
    "0x715018a6",  # renounceOwnership()
    "0xc9567bf9",  # openTrading()
    "0xa9059cbb",  # transfer(address,uint256)
    "0x23b872dd",  # transferFrom(address,address,uint256)
]

HONEYPOT_PATTERNS = [
    rb"(?i)(blacklist|bot|sniper)",
    rb"(tax|fee).{0,50}(9[0-9]|100)",
    rb"(trading|swap).*?(enabled|started|open)",
    rb"onlyOwner.*?transfer",
]

class HoneypotDetector:
    def __init__(self, w3: Web3):
        self.w3 = w3

    def analyze_bytecode(self, address: str) -> Tuple[bool, List[str]]:
        try:
            bytecode = self.w3.eth.get_code(address).hex()
            if not bytecode or bytecode == "0x":
                return False, ["No bytecode found"]

            issues = []
            for selector in HONEYPOT_SELECTORS:
                if selector in bytecode:
                    issues.append(f"Suspicious selector: {selector}")

            bytecode_bytes = bytes.fromhex(bytecode[2:])
            for pattern in HONEYPOT_PATTERNS:
                if re.search(pattern, bytecode_bytes):
                    issues.append(f"Pattern match: {pattern.pattern}")

            if len(bytecode) > 50000:
                issues.append("Unusually large contract")

            return len(issues) > 0, issues
        except Exception as e:
            return True, [f"Analysis failed: {str(e)}"]