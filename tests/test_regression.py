"""Regression tests for public SDK functionality.

Backend-specific tests (collector, price_confidence, store_credentials)
live in the private cli-market-backend repo.
"""

import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import pytest


def test_market_core_imports():
    """market_core is the public SDK entry point — must import cleanly."""
    import market_core
    assert hasattr(market_core, "STORES")
    assert hasattr(market_core, "LINES")
    assert hasattr(market_core, "COUNTRIES")


def test_market_cli_imports():
    """CLI is public — must import cleanly."""
    import market_cli


def test_market_mcp_imports():
    """MCP server is public — must import cleanly."""
    import market_mcp
