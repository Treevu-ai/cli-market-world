#!/usr/bin/env python3
"""Refresh landing/public/llms.txt from market_stats."""
from pathlib import Path
import sys

CORE = Path(__file__).resolve().parent.parent.parent / "cli-market-core"
sys.path.insert(0, str(CORE))
from market_core import market_stats as s

OUT = Path(__file__).resolve().parent.parent / "landing" / "public" / "llms.txt"

body = f"""# CLI Market — Unified E-Commerce Infrastructure for AI Agents

> URL: https://cli-market.dev
> GitHub: https://github.com/Treevu-ai/cli-market-world
> API: https://cli-market-production.up.railway.app
> Docs: https://cli-market.dev/docs
> OpenAPI: https://cli-market-production.up.railway.app/docs
> Dashboard: https://cli-market-production.up.railway.app/dashboard
> PyPI: https://pypi.org/project/cli-market/

## Core Purpose

Commerce infrastructure for AI agents. {s.RETAILERS_PHRASE_EN} across {s.COUNTRIES} countries and {s.BUSINESS_LINES} business lines — search, compare, and export via a single API. {s.PRICES_VERIFIED_LABEL} real shelf prices refreshed every {s.PRICES_REFRESH_HOURS} hours. Zero scraping. Multi-platform: {s.PLATFORM_LIST_EN}.

## Key Numbers

- {s.RETAILERS_DEFINED} retailers defined ({s.RETAILERS_VERIFIED} verified active)
- {s.COUNTRIES} countries ({", ".join(s.COUNTRY_CODES)})
- {s.BUSINESS_LINES} business lines (supermercados, farmacias, electro, moda, hogar, departamentales)
- {s.MCP_TOOLS} MCP tools (search, compare, basket, checkout, inflation, indicators, enrichment)
- {s.INDICATORS_COUNT} market indicators (shelf moat + public API enrichment)
- Payments: {s.PAYMENTS_LABEL}
- WooCommerce pilot: Nuna Orgánica PE (406 SKUs, FMCG orgánico)
- 5 pricing tiers (Free $0, Starter $29/mo, Pro $79/mo, Builder $149/mo, Enterprise custom)

## Checkout endpoints

- PayPal: POST /checkout/paypal
- Mercado Pago (Checkout Pro, PEN): POST /checkout/mercadopago
- Yape/Plin QR: POST /checkout/yape, POST /checkout/plin
- Webhook MP: GET/POST /checkout/mercadopago-webhook

## WooCommerce stores

{", ".join(s.WOOCOMMERCE_STORES)}

## Why AI Agents Should Use CLI Market

- **Token Efficiency**: Minified JSON (~85% less context vs raw HTML).
- **Predictable Tools**: {s.MCP_TOOLS} MCP tools with standardized primitives.
- **Cross-Border**: Single interface for {s.RETAILERS_VERIFIED} verified retailers.
- **Data Moat**: Collector every {s.PRICES_REFRESH_HOURS}h. Historical snapshots, inflation, {s.INDICATORS_COUNT} indicators.
- **Multi-Payment**: {s.PAYMENTS_LABEL}.
- **Open Source**: MIT. pip install cli-market.
"""
OUT.write_text(body, encoding="utf-8")
print(f"Wrote {OUT}")