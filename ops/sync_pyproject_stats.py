#!/usr/bin/env python3
"""Sync pyproject.toml description from market_stats."""
from pathlib import Path
import re
import sys

CORE = Path(__file__).resolve().parent.parent.parent / "cli-market-core"
sys.path.insert(0, str(CORE))
from market_core import market_stats as s

pyproject = Path(__file__).resolve().parent.parent / "pyproject.toml"
text = pyproject.read_text(encoding="utf-8")
desc = (
    f"mcp-name: io.github.Treevu-ai/cli-market-world - CLI Market: commerce API for AI agents. "
    f"{s.MCP_TOOLS} MCP tools, {s.INDICATORS_COUNT} indicators, {s.RETAILERS_DEFINED} retailers "
    f"({s.RETAILERS_VERIFIED} verified) in {s.COUNTRIES} countries, {s.PLATFORMS} platforms. MIT."
)
text = re.sub(
    r'description = ".*?"',
    f'description = "{desc}"',
    text,
    count=1,
)
pyproject.write_text(text, encoding="utf-8")
print(f"Updated {pyproject.name} description")