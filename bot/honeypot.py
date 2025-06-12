"""
Honeypot Detection Module
Checks tokens for common honeypot characteristics
"""

import logging
from web3 import Web3
import aiohttp
import asyncio
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class HoneypotChecker:
    """Detects potential honeypot tokens"""
    
    def __init__(self, w3: Web3, config):
        self.w3 = w3
        self.config = config
        self.honeypot_cache = {}
        
    async def check(self, token_address: str) -> bool:
        """
        Check if token is a potential honeypot
        Returns True if honeypot detected, False if safe
        """
        # Check cache first
        if token_address in self.honeypot_cache:
            return self.honeypot_cache[token_address]
            
        try:
            # Run multiple checks in parallel
            checks = await asyncio.gather(
                self._check_contract_code(token_address),
                self._check_honeypot_api(token_address),
                self._check_token_functions(token_address),
                return_exceptions=True
            )
            
            # Analyze results
            code_check, api_check, function_check = checks
            
            # If any check indicates honeypot, mark as unsafe
            is_honeypot = False
            
            if isinstance(code_check, bool) and code_check:
                logger.warning(f"Contract code check failed for {token_address}")
                is_honeypot = True
                
            if isinstance(api_check, bool) and api_check:
                logger.warning(f"Honeypot API detected issues for {token_address}")
                is_honeypot = True
                
            if isinstance(function_check, bool) and function_check:
                logger.warning(f"Token function check failed for {token_address}")
                is_honeypot = True
                
            # Cache result
            self.honeypot_cache[token_address] = is_honeypot
            
            return is_honeypot
            
        except Exception as e:
            logger.error(f"Error checking honeypot: {e}")
            # Be cautious - if check fails, assume unsafe
            return True
            
    async def _check_contract_code(self, token_address: str) -> bool:
        """Check contract bytecode for suspicious patterns"""
        try:
            code = self.w3.eth.get_code(token_address)
            code_hex = code.hex()
            
            # Check for common honeypot patterns in bytecode
            honeypot_signatures = [
                "18160ddd",  # totalSupply() that might be manipulated
                "a9059cbb",  # transfer() that might have hidden conditions
                "23b872dd",  # transferFrom() with potential restrictions
            ]
            
            # Look for suspicious patterns
            suspicious_patterns = 0
            for signature in honeypot_signatures:
                if signature in code_hex:
                    # Check if the function appears multiple times (potential override)
                    occurrences = code_hex.count(signature)
                    if occurrences > 2:  # Normal would be 1-2 times
                        suspicious_patterns += 1
                        
            return suspicious_patterns >= 2
            
        except Exception as e:
            logger.error(f"Error checking contract code: {e}")
            return True
            
    async def _check_honeypot_api(self, token_address: str) -> bool:
        """Check external honeypot detection APIs"""
        # Skip API check if disabled
        if not getattr(self.config, 'USE_HONEYPOT_API', True):
            return False
            
        try:
            # Example using honeypot.is API (if available)
            # This is a placeholder - replace with actual API
            async with aiohttp.ClientSession() as session:
                # Various APIs available:
                # - honeypot.is
                # - gopluslabs.io
                # - tokensniffer.com
                
                # Example for BSC using GoPlusLabs
                if self.config.CHAIN_ID == 56:  # BSC
                    url = f"https://api.gopluslabs.io/api/v1/token/security/{token_address}?chain_id=56"
                    
                    async with session.get(url, timeout=5) as response:
                        if response.status == 200:
                            data = await response.json()
                            
                            # Check various honeypot indicators
                            if 'result' in data and token_address.lower() in data['result']:
                                token_data = data['result'][token_address.lower()]
                                
                                # Check for honeypot indicators
                                if token_data.get('is_honeypot') == '1':
                                    return True
                                    
                                # Check other risk factors
                                if token_data.get('cannot_sell_all') == '1':
                                    return True
                                    
                                if token_data.get('transfer_pausable') == '1':
                                    return True
                                    
                                if token_data.get('is_blacklisted') == '1':
                                    return True
                                    
                                # Check buy/sell tax
                                buy_tax = float(token_data.get('buy_tax', '0'))
                                sell_tax = float(token_data.get('sell_tax', '0'))
                                
                                if buy_tax > 10 or sell_tax > 10:  # More than 10% tax
                                    logger.warning(f"High tax detected - Buy: {buy_tax}%, Sell: {sell_tax}%")
                                    return True
                                    
            return False
            
        except Exception as e:
            logger.error(f"Error checking honeypot API: {e}")
            return False  # Don't block on API failure
            
    async def _check_token_functions(self, token_address: str) -> bool:
        """Check if token implements standard ERC20 functions properly"""
        try:
            # Minimal ERC20 ABI for checking
            erc20_abi = [
                {
                    "constant": True,
                    "inputs": [],
                    "name": "name",
                    "outputs": [{"name": "", "type": "string"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "symbol",
                    "outputs": [{"name": "", "type": "string"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "decimals",
                    "outputs": [{"name": "", "type": "uint8"}],
                    "type": "function"
                },
                {
                    "constant": True,
                    "inputs": [],
                    "name": "totalSupply",
                    "outputs": [{"name": "", "type": "uint256"}],
                    "type": "function"
                }
            ]
            
            token = self.w3.eth.contract(
                address=Web3.to_checksum_address(token_address),
                abi=erc20_abi
            )
            
            # Try to call basic functions
            checks_passed = 0
            total_checks = 0
            
            # Check name
            try:
                total_checks += 1
                name = token.functions.name().call()
                if name and len(name) > 0:
                    checks_passed += 1
            except:
                pass
                
            # Check symbol
            try:
                total_checks += 1
                symbol = token.functions.symbol().call()
                if symbol and len(symbol) > 0 and len(symbol) <= 10:
                    checks_passed += 1
            except:
                pass
                
            # Check decimals
            try:
                total_checks += 1
                decimals = token.functions.decimals().call()
                if 0 <= decimals <= 18:
                    checks_passed += 1
            except:
                pass
                
            # Check total supply
            try:
                total_checks += 1
                total_supply = token.functions.totalSupply().call()
                if total_supply > 0:
                    checks_passed += 1
            except:
                pass
                
            # If less than half of checks pass, consider suspicious
            if checks_passed < total_checks / 2:
                return True
                
            return False
            
        except Exception as e:
            logger.error(f"Error checking token functions: {e}")
            return True
            
    def clear_cache(self):
        """Clear the honeypot cache"""
        self.honeypot_cache.clear()
        logger.info("Honeypot cache cleared")
                