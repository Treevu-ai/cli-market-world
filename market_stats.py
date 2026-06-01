"""Canonical marketing stats — single source of truth for README, PyPI, landing.

Always phrase retailers as: "60 retailers, 30 verified active" (defined vs live).
Run: python3 ops/sync_market_stats.py
"""

from __future__ import annotations

# ── Canonical figures (aligned to market_stores.py catalog) ─────────────────
RETAILERS_DEFINED = 66
RETAILERS_VERIFIED = 36
PLATFORMS = 3
PLATFORM_VTEX = 44
PLATFORM_SHOPIFY = 15
PLATFORM_MAGENTO = 7
COUNTRIES = 11
COUNTRY_CODES = ("PE", "AR", "BR", "MX", "CO", "CL", "IT", "FR", "ES", "CH", "US")
MCP_TOOLS = 43
INDICATORS_COUNT = 34
ENRICHMENT_SOURCES_LABEL = "OFF · Wikimedia · Open-Meteo · World Bank · IMF · Eurostat · BCB"
PRICES_VERIFIED_LABEL = "45,000+"  # live: dashboard kpis.total_indexed
PRICES_REFRESH_HOURS = 4   # collector daemon interval
PACKAGE_VERSION = "1.7.0"
LICENSE = "MIT"
PAYMENTS_LABEL = "PayPal + QR (Yape/Plin)"
BUSINESS_LINES = 6

RETAILERS_PHRASE_EN = f"{RETAILERS_DEFINED} retailers, {RETAILERS_VERIFIED} verified active"
RETAILERS_PHRASE_ES = f"{RETAILERS_DEFINED} retailers, {RETAILERS_VERIFIED} verificados activos"
PLATFORMS_PHRASE_EN = f"{PLATFORMS} platforms (VTEX · Shopify · Magento)"
PLATFORMS_PHRASE_ES = f"{PLATFORMS} plataformas (VTEX · Shopify · Magento)"


def header_en() -> str:
    return (
        "CLI Market — Commerce infrastructure for AI agents.\n"
        f"{RETAILERS_DEFINED} retailers across {PLATFORMS} platforms "
        f"(VTEX · Shopify · Magento), {RETAILERS_VERIFIED} verified live.\n"
        f"{COUNTRIES} countries. {MCP_TOOLS} MCP tools. {PRICES_VERIFIED_LABEL} verified shelf prices, "
        f"normalized per kg/L, refreshed every {PRICES_REFRESH_HOURS}h.\n"
        "One pip install. One API. Zero scraping. MIT."
    )


def header_es() -> str:
    return (
        "CLI Market — Infraestructura de comercio para agentes de IA.\n"
        f"{RETAILERS_DEFINED} retailers en {PLATFORMS} plataformas "
        f"(VTEX · Shopify · Magento), {RETAILERS_VERIFIED} verificados y activos.\n"
        f"{COUNTRIES} países. {MCP_TOOLS} herramientas MCP. {PRICES_VERIFIED_LABEL} precios reales de góndola, "
        f"normalizados por kg/L, actualizados cada {PRICES_REFRESH_HOURS}h.\n"
        "Un pip install. Una API. Cero scraping. MIT."
    )


def pypi_summary() -> str:
    return (
        "mcp-name: io.github.Treevu-ai/cli-market-world - "
        "CLI Market: commerce API for AI agents. "
        f"{MCP_TOOLS} MCP tools, {INDICATORS_COUNT} indicators, "
        f"{RETAILERS_VERIFIED} verified retailers in {COUNTRIES} countries. MIT."
    )


def readme_tagline_html() -> str:
    return (
        f"<b>Commerce infrastructure for AI agents.</b><br>"
        f"{RETAILERS_DEFINED} retailers ({RETAILERS_VERIFIED} verified). {COUNTRIES} countries. "
        f"{PLATFORMS} platforms. {MCP_TOOLS} MCP tools. {PAYMENTS_LABEL}.<br>"
        f"{PRICES_VERIFIED_LABEL} verified shelf prices, normalized per kg/L, refreshed every {PRICES_REFRESH_HOURS} hours.<br>"
        f"One <code>pip install</code>. One API. Zero scraping."
    )


def server_json_description() -> str:
    return (
        f"Commerce for AI agents. {MCP_TOOLS} MCP tools. "
        f"{RETAILERS_DEFINED} retailers ({RETAILERS_VERIFIED} verified), {COUNTRIES} countries, {PLATFORMS} platforms."
    )


def seo_description() -> str:
    return (
        f"Commerce API for AI agents. {MCP_TOOLS} MCP tools, {RETAILERS_PHRASE_EN}. "
        f"{COUNTRIES} countries. {PRICES_VERIFIED_LABEL} verified shelf prices refreshed every {PRICES_REFRESH_HOURS} hours. "
        "Normalized per kg/L, quality-filtered. pip install cli-market."
    )


SHOPIFY_BRANDS = (
    "Adidas",
    "Gymshark",
    "Allbirds",
    "Alo Yoga",
    "Glossier",
    "Fenty Beauty",
    "Kylie Cosmetics",
    "ColourPop",
    "Brooklinen",
    "Casper",
    "On Running",
    "Parachute",
    "Nomad",
    "Magic Mind",
    "Privalia BR",
)
