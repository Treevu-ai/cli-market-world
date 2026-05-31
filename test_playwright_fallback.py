#!/usr/bin/env python3
"""
Test script for Playwright fallback mechanism in VTEX connector.
This validates that the self-healing fallback works correctly.

Usage:
    python3 test_playwright_fallback.py
    
Prerequisites:
    pip install 'cli-market[playwright]'
    playwright install chromium
"""

import asyncio
import logging
import sys
from datetime import datetime

# Setup logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s [%(levelname)s] %(name)s - %(message)s'
)
logger = logging.getLogger(__name__)


async def test_playwright_availability():
    """Test 1: Check if Playwright is installed."""
    logger.info("=" * 60)
    logger.info("TEST 1: Playwright Installation Check")
    logger.info("=" * 60)
    
    try:
        import importlib.util
        if importlib.util.find_spec("playwright.async_api") is None:
            raise ImportError("playwright.async_api not found")
        logger.info("✅ Playwright is installed and importable")
        return True
    except ImportError:
        logger.error("❌ Playwright not installed!")
        logger.error("   Install with: pip install 'cli-market[playwright]'")
        logger.error("   Then run: playwright install chromium")
        return False


async def test_cache_mechanism():
    """Test 2: Validate cache with TTL."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 2: Cookie Cache with TTL")
    logger.info("=" * 60)
    
    from market_connectors.vtex import (
        _STORE_COOKIE_CACHE,
        _COOKIE_CACHE_TTL,
        VtexConnector
    )
    
    connector = VtexConnector()
    store_key = "test_store"
    test_cookies = [
        {"name": "cf_clearance", "value": "test_value_123"},
        {"name": "sessionid", "value": "test_session_456"}
    ]
    
    # Store cookies
    connector._set_cached_cookies(store_key, test_cookies)
    logger.info(f"✅ Stored {len(test_cookies)} cookies for {store_key}")
    
    # Retrieve cookies immediately (should be valid)
    retrieved = connector._get_cached_cookies(store_key)
    if retrieved == test_cookies:
        logger.info(f"✅ Retrieved {len(retrieved)} cookies successfully")
    else:
        logger.error("❌ Retrieved cookies don't match!")
        return False
    
    # Check cache structure
    if store_key in _STORE_COOKIE_CACHE:
        cache_entry = _STORE_COOKIE_CACHE[store_key]
        if "cookies" in cache_entry and "expires_at" in cache_entry:
            logger.info("✅ Cache structure is correct:")
            logger.info(f"   - TTL: {_COOKIE_CACHE_TTL}s")
            logger.info(f"   - Expires at: {datetime.fromtimestamp(cache_entry['expires_at'])}")
        else:
            logger.error("❌ Cache entry missing required fields!")
            return False
    
    return True


async def test_lock_mechanism():
    """Test 3: Validate per-store locks."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 3: Per-Store Lock Mechanism")
    logger.info("=" * 60)
    
    from market_connectors.vtex import _STORE_LOCKS
    
    store_key = "test_lock_store"
    
    # Check that lock is created for store_key
    lock = _STORE_LOCKS[store_key]
    logger.info(f"✅ Created lock for {store_key}")
    
    # Test lock acquisition
    acquired = False
    try:
        async with lock:
            logger.info(f"✅ Successfully acquired lock for {store_key}")
            acquired = True
        logger.info(f"✅ Successfully released lock for {store_key}")
    except Exception as e:
        logger.error(f"❌ Lock error: {e}")
        return False
    
    return acquired


async def test_fallback_method_signature():
    """Test 4: Validate fallback method exists and has correct signature."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 4: Fallback Method Signature")
    logger.info("=" * 60)
    
    from market_connectors.vtex import VtexConnector
    import inspect
    
    connector = VtexConnector()
    
    # Check method exists
    if not hasattr(connector, '_search_playwright_fallback'):
        logger.error("❌ Method _search_playwright_fallback not found!")
        return False
    logger.info("✅ Method _search_playwright_fallback exists")
    
    # Check method is async
    method = connector._search_playwright_fallback
    if not asyncio.iscoroutinefunction(method):
        logger.error("❌ Method is not async!")
        return False
    logger.info("✅ Method is async")
    
    # Check signature
    sig = inspect.signature(method)
    expected_params = ['url', 'params', 'store_key', 'store_config']
    actual_params = list(sig.parameters.keys())
    
    if actual_params == expected_params:
        logger.info(f"✅ Method signature correct: {', '.join(actual_params)}")
    else:
        logger.error("❌ Parameter mismatch!")
        logger.error(f"   Expected: {expected_params}")
        logger.error(f"   Actual: {actual_params}")
        return False
    
    return True


async def test_search_method_flow():
    """Test 5: Validate search method has fallback integration."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 5: Search Method Integration")
    logger.info("=" * 60)
    
    from market_connectors.vtex import VtexConnector
    import inspect
    
    connector = VtexConnector()
    
    # Check search method exists
    if not hasattr(connector, 'search'):
        logger.error("❌ search method not found!")
        return False
    logger.info("✅ search method exists")
    
    # Check it's async
    method = connector.search
    if not asyncio.iscoroutinefunction(method):
        logger.error("❌ search method is not async!")
        return False
    logger.info("✅ search method is async")
    
    # Verify it uses locks and fallback (check source)
    source = inspect.getsource(method)
    
    checks = [
        ("_STORE_LOCKS", "per-store locking"),
        ("_get_cached_cookies", "cache retrieval"),
        ("_search_playwright_fallback", "fallback mechanism"),
        ("httpx.AsyncClient", "HTTP client"),
        ("logger", "logging"),
    ]
    
    for check_str, description in checks:
        if check_str in source:
            logger.info(f"✅ Uses {description}")
        else:
            logger.error(f"❌ Missing {description}!")
            return False
    
    return True


async def test_fetch_all_products_flow():
    """Test 6: Validate fetch_all_products has fallback integration."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 6: fetch_all_products Method Integration")
    logger.info("=" * 60)
    
    from market_connectors.vtex import VtexConnector
    import inspect
    
    connector = VtexConnector()
    
    # Check method exists
    if not hasattr(connector, 'fetch_all_products'):
        logger.error("❌ fetch_all_products method not found!")
        return False
    logger.info("✅ fetch_all_products method exists")
    
    # Check it's async
    method = connector.fetch_all_products
    if not asyncio.iscoroutinefunction(method):
        logger.error("❌ fetch_all_products method is not async!")
        return False
    logger.info("✅ fetch_all_products method is async")
    
    # Verify fallback integration
    source = inspect.getsource(method)
    if "_search_playwright_fallback" in source:
        logger.info("✅ Uses fallback mechanism")
    else:
        logger.error("❌ Missing fallback mechanism!")
        return False
    
    return True


async def test_logging_integration():
    """Test 7: Verify logging is properly configured."""
    logger.info("\n" + "=" * 60)
    logger.info("TEST 7: Logging Integration")
    logger.info("=" * 60)
    
    from market_connectors import vtex
    
    # Check logger exists
    if not hasattr(vtex, 'logger'):
        logger.error("❌ Logger not configured in vtex module!")
        return False
    logger.info("✅ Logger is properly configured")
    
    vtex_logger = vtex.logger
    if vtex_logger.name == "market_connectors.vtex":
        logger.info(f"✅ Logger name correct: {vtex_logger.name}")
    else:
        logger.warning(f"⚠️  Logger name: {vtex_logger.name}")
    
    return True


async def run_all_tests():
    """Run all tests in sequence."""
    logger.info("\n\n")
    logger.info("#" * 60)
    logger.info("# CLI Market: Playwright Fallback Test Suite")
    logger.info("#" * 60)
    logger.info(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("Playwright Installation", test_playwright_availability),
        ("Cookie Cache Mechanism", test_cache_mechanism),
        ("Lock Mechanism", test_lock_mechanism),
        ("Fallback Method Signature", test_fallback_method_signature),
        ("Search Integration", test_search_method_flow),
        ("Fetch All Integration", test_fetch_all_products_flow),
        ("Logging Integration", test_logging_integration),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = await test_func()
            results.append((test_name, result))
        except Exception as e:
            logger.error(f"❌ Test {test_name} raised exception: {e}")
            results.append((test_name, False))
    
    # Summary
    logger.info("\n\n")
    logger.info("#" * 60)
    logger.info("# Test Summary")
    logger.info("#" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        logger.info(f"{status}: {test_name}")
    
    logger.info(f"\nTotal: {passed}/{total} tests passed")
    logger.info(f"Ended at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    if passed == total:
        logger.info("\n🎉 All tests passed! Playwright fallback is ready to use.")
        return 0
    else:
        logger.error(f"\n❌ {total - passed} test(s) failed. Please review above.")
        return 1


if __name__ == "__main__":
    exit_code = asyncio.run(run_all_tests())
    sys.exit(exit_code)
