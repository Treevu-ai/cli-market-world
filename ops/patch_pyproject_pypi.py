#!/usr/bin/env python3
from pathlib import Path

p = Path(__file__).resolve().parent.parent / "pyproject.toml"
t = p.read_text(encoding="utf-8")

deps = '''dependencies = [
    "httpx>=0.27",
    "rich>=13.0",
    "fastapi>=0.115",
    "uvicorn>=0.30",
    "pydantic>=2.0",
    "python-multipart>=0.0.9",
    "psycopg2-binary>=2.9",
    "asyncpg>=0.29",
    "playwright>=1.45.0",
]'''

import re
t = re.sub(r"dependencies = \[\s*\"cli-market-core[^]]+\]", deps, t, count=1)

setuptools = '''[tool.setuptools]
py-modules = [
    "market_cli", "market_server", "market_security", "server_deps", "collect_prices", "backend_interface",
    "store_credentials", "market_stats", "retailer_onboarding", "market_alerts", "market_basket",
    "market_spread", "market_units", "market_db", "market_indicators", "market_enrich_subcategory",
    "market_billing", "market_mcp", "market_intel_agent", "market_health_alert", "market_enrich_sources",
    "data_v1_service", "dashboard_glossary", "dashboard_quality", "dashboard_renderer",
    "dashboard_view_model", "source_health", "price_confidence",
]

[tool.setuptools.packages.find]
include = ["market_core*", "market_connectors*"]'''

t = re.sub(r"\[tool\.setuptools\][^\[]+", setuptools + "\n\n", t, count=1)
t = t.replace('version = "1.9.0"', 'version = "1.9.1"')
p.write_text(t, encoding="utf-8")
print("patched pyproject.toml")