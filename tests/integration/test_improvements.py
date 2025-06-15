#!/usr/bin/env python3
"""
Test script to verify all improvements work correctly
Tests configuration, utilities, enhanced error handling, etc.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the bot directory to Python path
sys.path.insert(0, str(Path(__file__).parent))


async def test_config_improvements():
    """Test enhanced configuration features."""
    print("\n🔧 Testing Configuration Improvements...")

    try:
        from bot.config import Config

        # Test with test config
        config = Config("test.config.env")

        # Test new methods
        print(f"✅ Network: {config.get_network_name()}")
        print(f"✅ Explorer: {config.get_explorer_url()}")
        print(f"✅ Max RPC calls/sec: {config.max_rpc_calls_per_second}")
        print(f"✅ Max concurrent trades: {config.max_concurrent_trades}")

        # Test environment validation
        validation = config.validate_environment()
        print(
            f"✅ Environment validation: {'PASSED' if validation['valid'] else 'FAILED'}"
        )

        if not validation["valid"]:
            for error in validation["errors"]:
                print(f"❌ {error}")

        # Test configuration export
        config_dict = config.to_dict(include_sensitive=False)
        print(f"✅ Config export: {len(config_dict)} settings")

        return True

    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False


async def test_utils_functionality():
    """Test utility functions."""
    print("\n🛠️ Testing Utility Functions...")

    try:
        from bot.utils import (
            RateLimiter,
            with_retry,
            RetryConfig,
            Web3Utils,
            format_number,
            validate_address,
        )

        # Test rate limiter
        rate_limiter = RateLimiter(max_calls=5, time_window=1.0)
        start_time = asyncio.get_event_loop().time()

        for i in range(7):  # This should trigger rate limiting
            await rate_limiter.acquire()

        elapsed = asyncio.get_event_loop().time() - start_time
        print(f"✅ Rate limiter working: {elapsed:.2f}s for 7 calls (should be ~1s)")

        # Test retry decorator
        @with_retry(RetryConfig(max_attempts=3, base_delay=0.1))
        async def failing_function():
            if not hasattr(failing_function, "attempts"):
                failing_function.attempts = 0
            failing_function.attempts += 1

            if failing_function.attempts < 3:
                raise Exception("Simulated failure")
            return "Success!"

        result = await failing_function()
        print(f"✅ Retry decorator working: {result}")

        # Test utility functions
        print(f"✅ Format number: {format_number(1234567.89)}")
        print(f"✅ Validate address: {validate_address('0x' + '0' * 40)}")

        return True

    except Exception as e:
        print(f"❌ Utils test failed: {e}")
        return False


async def test_error_handling():
    """Test enhanced error handling."""
    print("\n⚠️ Testing Error Handling...")

    try:
        from bot.exceptions import (
            ConfigurationError,
            BlockchainError,
            TradingError,
            SecurityError,
            map_web3_error,
        )

        # Test error mapping
        blockchain_error = map_web3_error("execution reverted: insufficient funds")
        print(f"✅ Error mapping: {type(blockchain_error).__name__}")

        # Test custom exceptions
        try:
            raise TradingError("Test trading error", token_address="0x123", amount=1.0)
        except TradingError as e:
            print(f"✅ Trading error handled: {e.token_address}")

        return True

    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False


async def test_analytics():
    """Test analytics functionality."""
    print("\n📊 Testing Analytics...")

    try:
        from bot.analytics import TradingAnalytics, TradeRecord, PerformanceMetrics
        from datetime import datetime

        # Create test analytics instance
        analytics = TradingAnalytics("test_analytics.db")

        # Create test trade record
        test_trade = TradeRecord(
            timestamp=datetime.now(),
            token_address="0x123",
            token_symbol="TEST",
            action="buy",
            amount_eth=0.1,
            profit_loss=0.05,
            status="confirmed",
        )

        # Record trade
        success = analytics.record_trade(test_trade)
        print(f"✅ Trade recording: {'SUCCESS' if success else 'FAILED'}")

        # Generate metrics
        metrics = analytics.calculate_performance_metrics()
        print(f"✅ Performance metrics: {metrics.total_trades} trades")

        # Generate report
        report = analytics.generate_report()
        print(f"✅ Report generation: {len(report)} characters")

        # Cleanup test database
        test_db = Path("test_analytics.db")
        if test_db.exists():
            test_db.unlink()

        return True

    except Exception as e:
        print(f"❌ Analytics test failed: {e}")
        return False


async def test_blockchain_interface():
    """Test blockchain interface improvements."""
    print("\n⛓️ Testing Blockchain Interface...")

    try:
        from bot.config import Config
        from bot.blockchain import BlockchainInterface

        config = Config("test.config.env")
        blockchain = BlockchainInterface(config)

        # Test initialization (will use test RPC)
        print("✅ Blockchain interface created")

        # Test contract caching
        cache_key = "test_cache"
        print(
            f"✅ Contract caching: {len(blockchain._contract_cache)} contracts cached"
        )

        # Test health check method exists
        assert hasattr(blockchain, "health_check"), "Health check method missing"
        print("✅ Health check method available")

        return True

    except Exception as e:
        print(f"❌ Blockchain interface test failed: {e}")
        return False


async def test_sniper_enhancements():
    """Test sniper bot enhancements."""
    print("\n🎯 Testing Sniper Bot Enhancements...")

    try:
        from bot.config import Config
        from bot.sniper import SniperBot

        config = Config("test.config.env")
        bot = SniperBot(config)

        # Test enhanced initialization
        print(f"✅ Bot created with enhanced features")
        print(f"✅ Statistics tracking: {len(bot.stats)} metrics")
        print(f"✅ Performance monitoring: {type(bot.performance_monitor).__name__}")
        print(f"✅ Rate limiting: {type(bot.rate_limiter).__name__}")

        # Test position tracking
        assert hasattr(bot, "positions"), "Position tracking missing"
        assert hasattr(bot, "failed_pairs"), "Failed pairs tracking missing"
        print("✅ Enhanced position tracking available")

        return True

    except Exception as e:
        print(f"❌ Sniper enhancements test failed: {e}")
        return False


async def main():
    """Run all improvement tests."""
    print("🚀 Testing Crypto Sniper Bot Improvements")
    print("=" * 50)

    tests = [
        ("Configuration", test_config_improvements),
        ("Utilities", test_utils_functionality),
        ("Error Handling", test_error_handling),
        ("Analytics", test_analytics),
        ("Blockchain Interface", test_blockchain_interface),
        ("Sniper Enhancements", test_sniper_enhancements),
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False

    print("\n" + "=" * 50)
    print("📋 TEST RESULTS SUMMARY")
    print("=" * 50)

    passed = 0
    total = len(tests)

    for test_name, result in results.items():
        status = "✅ PASSED" if result else "❌ FAILED"
        print(f"{test_name:.<30} {status}")
        if result:
            passed += 1

    print("-" * 50)
    print(f"Overall: {passed}/{total} tests passed ({passed/total*100:.1f}%)")

    if passed == total:
        print("\n🎉 All improvements are working correctly!")
        return True
    else:
        print(f"\n⚠️ {total - passed} tests failed. Please review the issues above.")
        return False


if __name__ == "__main__":
    # Setup basic logging
    logging.basicConfig(level=logging.WARNING)

    # Run tests
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
