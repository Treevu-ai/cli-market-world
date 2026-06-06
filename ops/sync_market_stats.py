#!/usr/bin/env python3
"""Emit landing/lib/marketStats.ts and sync README, PyPI, server.json from market_stats.py."""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE_ROOT = ROOT.parent / "cli-market-core"
for p in (ROOT, CORE_ROOT):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from market_core import market_stats as s

OUT_TS = ROOT / "landing" / "lib" / "marketStats.ts"


def write_market_stats_ts() -> None:
    ts = f"""// AUTO-GENERATED — do not edit. Run: python3 ops/sync_market_stats.py

export const MARKET_STATS = {{
  retailersDefined: {s.RETAILERS_DEFINED},
  retailersVerified: {s.RETAILERS_VERIFIED},
  platforms: {s.PLATFORMS},
  platformVtex: {s.PLATFORM_VTEX},
  platformShopify: {s.PLATFORM_SHOPIFY},
  platformMagento: {s.PLATFORM_MAGENTO},
  platformWooCommerce: {s.PLATFORM_WOOCOMMERCE},
  woocommerceStores: {json.dumps(list(s.WOOCOMMERCE_STORES))},
  countries: {s.COUNTRIES},
  countryCodes: {list(s.COUNTRY_CODES)!r},
  mcpTools: {s.MCP_TOOLS},
  indicatorsCount: {s.INDICATORS_COUNT},
  enrichmentSourcesLabel: "{s.ENRICHMENT_SOURCES_LABEL}",
  pricesVerifiedLabel: "{s.PRICES_VERIFIED_LABEL}",
  pricesRefreshHours: {s.PRICES_REFRESH_HOURS},
  packageVersion: "{s.PACKAGE_VERSION}",
  license: "{s.LICENSE}",
  paymentsLabel: "{s.PAYMENTS_LABEL}",
  businessLines: {s.BUSINESS_LINES},
  retailersPhraseEn: "{s.RETAILERS_PHRASE_EN}",
  retailersPhraseEs: "{s.RETAILERS_PHRASE_ES}",
  platformsPhraseEn: "{s.PLATFORMS_PHRASE_EN}",
  platformsPhraseEs: "{s.PLATFORMS_PHRASE_ES}",
  headerEn: {json.dumps(s.header_en())},
  headerEs: {json.dumps(s.header_es())},
  shopifyBrands: {json.dumps(list(s.SHOPIFY_BRANDS))},
  seoDescription: {json.dumps(s.seo_description())},
  serverDescription: {json.dumps(s.server_json_description())},
}} as const;
"""
    OUT_TS.write_text(ts, encoding="utf-8")
    print(f"Wrote {OUT_TS}")


def sync_readme() -> None:
    path = ROOT / "README.md"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'<img src="https://img\.shields\.io/badge/retailers-\d+-brightgreen" alt="[^"]*">',
        f'<img src="https://img.shields.io/badge/retailers-{s.RETAILERS_DEFINED}-brightgreen" alt="{s.RETAILERS_DEFINED} retailers">',
        text,
    )
    text = re.sub(
        r'<img src="https://img\.shields\.io/badge/platforms-\d+-blue" alt="[^"]*">',
        f'<img src="https://img.shields.io/badge/platforms-{s.PLATFORMS}-blue" alt="{s.PLATFORMS} platforms">',
        text,
    )
    text = re.sub(
        r'<img src="https://img\.shields\.io/badge/MCP%20tools-\d+-00d75f" alt="[^"]*">',
        f'<img src="https://img.shields.io/badge/MCP%20tools-{s.MCP_TOOLS}-00d75f" alt="{s.MCP_TOOLS} MCP tools">',
        text,
    )
    text = re.sub(
        r"## \d+ MCP tools",
        f"## {s.MCP_TOOLS} MCP tools",
        text,
        count=1,
    )
    text = re.sub(
        r"<p align=\"center\"><b>Commerce infrastructure for AI agents\.</b><br>.*?</p>",
        f'<p align="center">{s.readme_tagline_html()}</p>',
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = re.sub(
        r"├── market_mcp\.py            → MCP server \(\d+ tools\)",
        f"├── market_mcp.py            → MCP server ({s.MCP_TOOLS} tools)",
        text,
        count=1,
    )
    text = text.replace(
        "One API call across 30 verified retailers.",
        f"One API call across {s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verified).",
    )
    text = text.replace(
        "any product across 30 verified retailers in 8 countries",
        f"any product across {s.RETAILERS_VERIFIED} verified retailers in {s.COUNTRIES} countries",
    )
    # Spanish: verified prices label (catches both "39 000+" and "39,000+")
    text = re.sub(
        r"\*\*Más de [\d,. ]+\+? precios de góndola verificados\*\*",
        f"**Más de {s.PRICES_VERIFIED_LABEL} precios de góndola verificados**",
        text,
    )
    text = re.sub(
        r"\*\*[\d,]+\+ verified shelf prices\*\*",
        f"**{s.PRICES_VERIFIED_LABEL} verified shelf prices**",
        text,
    )
    # Spanish: retailers + countries in body text (bold and plain)
    text = re.sub(
        r"\d+ retailers \(\d+ verificados\)",
        f"{s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verificados)",
        text,
    )
    text = re.sub(
        r"\d+ retailers, \d+ verified active(?! en)",
        f"{s.RETAILERS_DEFINED} retailers, {s.RETAILERS_VERIFIED} verified active",
        text,
    )
    text = re.sub(
        r"\d+ retailers \(\d+ verified\)",
        f"{s.RETAILERS_DEFINED} retailers ({s.RETAILERS_VERIFIED} verified)",
        text,
    )
    text = re.sub(
        r"\d+ verified active\b",
        f"{s.RETAILERS_VERIFIED} verified active",
        text,
    )
    # Countries count (both bold and plain)
    text = re.sub(
        r"\b\d+ países\b",
        f"{s.COUNTRIES} países",
        text,
    )
    text = re.sub(
        r"\b\d+ countries\b",
        f"{s.COUNTRIES} countries",
        text,
    )
    # Indicators count
    text = re.sub(
        r"· \d+ indicadores\b",
        f"· {s.INDICATORS_COUNT} indicadores",
        text,
    )
    text = re.sub(
        r"· \d+ indicators\b",
        f"· {s.INDICATORS_COUNT} indicators",
        text,
    )
    path.write_text(text, encoding="utf-8")
    print(f"Synced {path}")


def sync_pyproject() -> None:
    path = ROOT / "pyproject.toml"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r'^version = ".*"$',
        f'version = "{s.PACKAGE_VERSION}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    desc = s.pypi_summary().replace('"', '\\"')
    text = re.sub(
        r'^description = ".*"$',
        f'description = "{desc}"',
        text,
        count=1,
        flags=re.MULTILINE,
    )
    path.write_text(text, encoding="utf-8")
    print(f"Synced {path}")


def sync_server_json() -> None:
    desc = s.server_json_description()
    for rel in ("server.json", "landing/public/server.json"):
        path = ROOT / rel
        data = json.loads(path.read_text(encoding="utf-8"))
        data["description"] = desc
        data["version"] = s.PACKAGE_VERSION
        if data.get("packages"):
            data["packages"][0]["version"] = s.PACKAGE_VERSION
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        print(f"Synced {path}")


def sync_mcp_json() -> None:
    path = ROOT / "landing" / "public" / "mcp.json"
    data = json.loads(path.read_text(encoding="utf-8"))
    data["description"] = (
        f"Commerce infrastructure for AI agents — {s.MCP_TOOLS} MCP tools to search, compare, "
        f"and purchase across {s.RETAILERS_VERIFIED} retailers in {s.COUNTRIES} countries. "
        f"{s.PRICES_VERIFIED_LABEL} real prices, {s.INDICATORS_COUNT} market indicators, refreshed every {s.PRICES_REFRESH_HOURS} hours. MIT."
    )
    data["tools"] = [
        "market_login", "market_lines", "market_search", "market_compare", "market_add",
        "market_cart", "market_cart_update", "market_cart_remove", "market_checkout",
        "market_orders", "market_reorder", "market_ask", "market_basket", "market_inflation",
        "market_indicators", "market_scores", "market_intel_refresh", "market_enrichment",
        "market_enrichment_subcategories", "market_enrichment_refresh", "market_analytics_indicators",
        "market_categories", "market_barcode", "market_enrich", "market_stores", "market_countries",
        "market_ticket", "market_voice", "market_price_history", "market_stats", "market_alerts",
        "market_whoami", "market_preferences", "market_subscription", "market_export",
        "market_trending", "market_scan", "market_stock", "market_brands", "market_favorites",
        "market_notify", "market_exchange", "market_delivery",
    ]
    path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    print(f"Synced {path}")
    root = ROOT / "mcp.json"
    root.write_text(path.read_text(encoding="utf-8"), encoding="utf-8")
    print(f"Synced {root}")


def sync_og_svg() -> None:
    path = ROOT / "landing" / "public" / "og.svg"
    text = path.read_text(encoding="utf-8")
    text = re.sub(
        r"\d+ MCP tools \| pip install",
        f"{s.MCP_TOOLS} MCP tools | pip install",
        text,
        count=1,
    )
    path.write_text(text, encoding="utf-8")
    print(f"Synced {path}")


def sync_og_preview_svg() -> None:
    path = ROOT / "landing" / "public" / "og-preview.svg"
    text = path.read_text(encoding="utf-8")
    text = re.sub(r"\d+ MCP", f"{s.MCP_TOOLS} MCP", text, count=1)
    path.write_text(text, encoding="utf-8")
    print(f"Synced {path}")


def main() -> None:
    write_market_stats_ts()
    sync_readme()
    sync_pyproject()
    sync_server_json()
    sync_mcp_json()
    sync_og_svg()
    sync_og_preview_svg()


if __name__ == "__main__":
    main()
