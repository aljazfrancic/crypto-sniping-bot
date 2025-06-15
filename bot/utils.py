"""
Utility functions for the crypto sniping bot
Includes rate limiting, retry logic, and helper functions
"""

import asyncio
import logging
import time
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from functools import wraps
from collections import deque
import aiohttp
from web3 import Web3
from web3.exceptions import Web3Exception
import json

logger = logging.getLogger(__name__)

T = TypeVar("T")


class RateLimiter:
    """Rate limiter to prevent overwhelming RPC endpoints."""

    def __init__(self, max_calls: int, time_window: float = 1.0):
        """Initialize rate limiter.

        Args:
            max_calls: Maximum calls allowed in time window
            time_window: Time window in seconds
        """
        self.max_calls = max_calls
        self.time_window = time_window
        self.calls = deque()
        self._lock = asyncio.Lock()

    async def acquire(self) -> None:
        """Acquire permission to make a call."""
        while True:
            async with self._lock:
                now = time.time()

                # Remove old calls outside the time window
                while self.calls and self.calls[0] <= now - self.time_window:
                    self.calls.popleft()

                # Check if we can make the call now
                if len(self.calls) < self.max_calls:
                    self.calls.append(now)
                    return

                # Calculate wait time if we've exceeded the rate limit
                wait_time = self.time_window - (now - self.calls[0])

            # Wait outside the lock to avoid blocking other operations
            if wait_time > 0:
                logger.debug(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
            else:
                # Small delay to prevent tight loop
                await asyncio.sleep(0.01)


class RetryConfig:
    """Configuration for retry logic."""

    def __init__(
        self,
        max_attempts: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True,
    ):
        self.max_attempts = max_attempts
        self.base_delay = base_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


def with_retry(config: RetryConfig = None):
    """Decorator to add retry logic to functions."""
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == config.max_attempts - 1:
                        break

                    # Calculate delay with exponential backoff
                    delay = min(
                        config.base_delay * (config.exponential_base**attempt),
                        config.max_delay,
                    )

                    # Add jitter to prevent thundering herd
                    if config.jitter:
                        import random

                        delay *= 0.5 + random.random() * 0.5

                    logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    await asyncio.sleep(delay)

            raise last_exception

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if attempt == config.max_attempts - 1:
                        break

                    # Calculate delay with exponential backoff
                    delay = min(
                        config.base_delay * (config.exponential_base**attempt),
                        config.max_delay,
                    )

                    # Add jitter to prevent thundering herd
                    if config.jitter:
                        import random

                        delay *= 0.5 + random.random() * 0.5

                    logger.warning(
                        f"Attempt {attempt + 1} failed: {str(e)}. "
                        f"Retrying in {delay:.2f} seconds..."
                    )
                    time.sleep(delay)

            raise last_exception

        return async_wrapper if asyncio.iscoroutinefunction(func) else sync_wrapper

    return decorator


class CircuitBreaker:
    """Circuit breaker to handle failing services."""

    def __init__(
        self,
        failure_threshold: int = 5,
        timeout: float = 60.0,
        recovery_timeout: float = 30.0,
    ):
        self.failure_threshold = failure_threshold
        self.timeout = timeout
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = None
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
        self._lock = asyncio.Lock()

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection."""
        async with self._lock:
            if self.state == "OPEN":
                if time.time() - self.last_failure_time < self.timeout:
                    raise Exception("Circuit breaker is OPEN")
                else:
                    self.state = "HALF_OPEN"

            try:
                if asyncio.iscoroutinefunction(func):
                    result = await func(*args, **kwargs)
                else:
                    result = func(*args, **kwargs)

                # Success - reset circuit breaker
                if self.state == "HALF_OPEN":
                    self.state = "CLOSED"
                    self.failure_count = 0

                return result

            except Exception as e:
                self.failure_count += 1
                self.last_failure_time = time.time()

                if self.failure_count >= self.failure_threshold:
                    self.state = "OPEN"
                    logger.error(
                        f"Circuit breaker opened due to {self.failure_count} failures"
                    )

                raise e


class Web3Utils:
    """Utility functions for Web3 interactions."""

    @staticmethod
    def is_contract(w3: Web3, address: str) -> bool:
        """Check if address is a contract."""
        try:
            code = w3.eth.get_code(address)
            return len(code) > 2  # More than just '0x'
        except Exception:
            return False

    @staticmethod
    def get_token_info(w3: Web3, token_address: str, abi: List[Dict]) -> Dict[str, Any]:
        """Get basic token information."""
        try:
            contract = w3.eth.contract(address=token_address, abi=abi)

            name = "Unknown"
            symbol = "UNKNOWN"
            decimals = 18
            total_supply = 0

            try:
                name = contract.functions.name().call()
            except Exception:
                pass

            try:
                symbol = contract.functions.symbol().call()
            except Exception:
                pass

            try:
                decimals = contract.functions.decimals().call()
            except Exception:
                pass

            try:
                total_supply = contract.functions.totalSupply().call()
            except Exception:
                pass

            return {
                "name": name,
                "symbol": symbol,
                "decimals": decimals,
                "total_supply": total_supply,
                "address": token_address,
            }

        except Exception as e:
            logger.error(f"Failed to get token info for {token_address}: {e}")
            return {
                "name": "Unknown",
                "symbol": "UNKNOWN",
                "decimals": 18,
                "total_supply": 0,
                "address": token_address,
            }

    @staticmethod
    def calculate_gas_price(w3: Web3, multiplier: float = 1.1) -> int:
        """Calculate optimal gas price."""
        try:
            base_fee = w3.eth.gas_price
            return int(base_fee * multiplier)
        except Exception:
            # Fallback gas price (in wei)
            return w3.to_wei(20, "gwei")

    @staticmethod
    def estimate_gas_with_buffer(
        w3: Web3, transaction: Dict[str, Any], buffer_percent: float = 20.0
    ) -> int:
        """Estimate gas with a safety buffer."""
        try:
            estimated = w3.eth.estimate_gas(transaction)
            buffer = int(estimated * buffer_percent / 100)
            return estimated + buffer
        except Exception as e:
            logger.warning(f"Gas estimation failed: {e}")
            # Return a reasonable default
            return 300000


class NotificationManager:
    """Manage notifications via webhooks."""

    def __init__(self, webhook_url: Optional[str] = None):
        self.webhook_url = webhook_url
        self.session = None

    async def send_notification(
        self, message: str, level: str = "info", data: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Send notification via webhook."""
        if not self.webhook_url:
            return False

        try:
            if not self.session:
                self.session = aiohttp.ClientSession()

            payload = {
                "message": message,
                "level": level,
                "timestamp": time.time(),
                "data": data or {},
            }

            async with self.session.post(
                self.webhook_url, json=payload, timeout=aiohttp.ClientTimeout(total=10)
            ) as response:
                return response.status == 200

        except Exception as e:
            logger.error(f"Failed to send notification: {e}")
            return False

    async def close(self):
        """Close the session."""
        if self.session:
            await self.session.close()


class PriceCalculator:
    """Utility for price calculations and conversions."""

    @staticmethod
    def calculate_price_impact(
        amount_in: int, reserve_in: int, reserve_out: int
    ) -> float:
        """Calculate price impact of a trade."""
        if reserve_in == 0 or reserve_out == 0:
            return 100.0  # Maximum impact if no liquidity

        # Using constant product formula: x * y = k
        # Price impact = (amount_out_with_fee / amount_out_without_fee - 1) * 100

        # Without fee (theoretical)
        amount_out_without_fee = (amount_in * reserve_out) / reserve_in

        # With fee (0.3% for most DEXs)
        amount_in_with_fee = amount_in * 997  # 0.3% fee
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in * 1000 + amount_in_with_fee
        amount_out_with_fee = numerator / denominator

        if amount_out_without_fee == 0:
            return 100.0

        price_impact = (1 - amount_out_with_fee / amount_out_without_fee) * 100
        return max(0, price_impact)

    @staticmethod
    def calculate_slippage(expected_amount: int, actual_amount: int) -> float:
        """Calculate slippage percentage."""
        if expected_amount == 0:
            return 100.0

        slippage = ((expected_amount - actual_amount) / expected_amount) * 100
        return max(0, slippage)

    @staticmethod
    def get_amount_out(
        amount_in: int,
        reserve_in: int,
        reserve_out: int,
        fee: int = 997,  # 0.3% fee (997/1000)
    ) -> int:
        """Calculate output amount using constant product formula."""
        if reserve_in == 0 or reserve_out == 0:
            return 0

        amount_in_with_fee = amount_in * fee
        numerator = amount_in_with_fee * reserve_out
        denominator = reserve_in * 1000 + amount_in_with_fee

        return numerator // denominator


def format_number(value: Union[int, float], decimals: int = 4) -> str:
    """Format number for display."""
    if isinstance(value, int) and value > 10**18:
        # Likely a token amount, convert from wei
        value = value / 10**18

    if value < 0.0001:
        return f"{value:.8f}"
    elif value < 1:
        return f"{value:.6f}"
    elif value < 1000:
        return f"{value:.{decimals}f}"
    elif value < 1000000:
        return f"{value/1000:.2f}K"
    elif value < 1000000000:
        return f"{value/1000000:.2f}M"
    else:
        return f"{value/1000000000:.2f}B"


def validate_address(address: str) -> bool:
    """Validate Ethereum address format."""
    try:
        Web3.to_checksum_address(address)
        return True
    except Exception:
        return False


def get_current_timestamp() -> int:
    """Get current Unix timestamp."""
    return int(time.time())


def calculate_deadline(minutes: int = 20) -> int:
    """Calculate transaction deadline."""
    return get_current_timestamp() + (minutes * 60)


class PerformanceMonitor:
    """Monitor performance metrics."""

    def __init__(self):
        self.metrics = {}
        self.start_times = {}

    def start_timer(self, operation: str) -> None:
        """Start timing an operation."""
        self.start_times[operation] = time.time()

    def end_timer(self, operation: str) -> float:
        """End timing and record duration."""
        if operation not in self.start_times:
            return 0.0

        duration = time.time() - self.start_times[operation]

        if operation not in self.metrics:
            self.metrics[operation] = []

        self.metrics[operation].append(duration)
        del self.start_times[operation]

        return duration

    def get_average_time(self, operation: str) -> float:
        """Get average time for an operation."""
        if operation not in self.metrics or not self.metrics[operation]:
            return 0.0

        return sum(self.metrics[operation]) / len(self.metrics[operation])

    def get_stats(self) -> Dict[str, Dict[str, float]]:
        """Get performance statistics."""
        stats = {}

        for operation, times in self.metrics.items():
            if times:
                stats[operation] = {
                    "count": len(times),
                    "average": sum(times) / len(times),
                    "min": min(times),
                    "max": max(times),
                    "total": sum(times),
                }

        return stats
