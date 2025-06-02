import unittest
from unittest.mock import MagicMock
from honeypot_detector import HoneypotDetector

class TestHoneypotDetector(unittest.TestCase):
    def setUp(self):
        self.w3 = MagicMock()
        self.detector = HoneypotDetector(self.w3)

    def _mock_code(self, code_hex: str):
        self.w3.eth.get_code.return_value.hex.return_value = code_hex

    def test_selector_detection(self):
        self._mock_code("0x60806040" + "3b124fe3")
        hp, issues = self.detector.analyze_bytecode("0x123")
        self.assertTrue(hp)
        self.assertTrue(any("3b124fe3" in i for i in issues))

    def test_pattern_detection(self):
        blacklist_hex = "0x" + "blacklist".encode().hex()
        self._mock_code(blacklist_hex)
        hp, issues = self.detector.analyze_bytecode("0xabc")
        self.assertTrue(hp)

    def test_large_contract(self):
        self._mock_code("0x" + "a"*100000)
        hp, issues = self.detector.analyze_bytecode("0xdef")
        self.assertTrue(hp)
        self.assertTrue(any("Unusually large" in i for i in issues))

if __name__ == "__main__":
    unittest.main()