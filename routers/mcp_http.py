"""HTTP MCP transport endpoint — enables CLI Market to be added as a remote
MCP server in claude.ai, Claude Desktop (HTTP mode), Cursor, VS Code, Kiro,
Codex, Gemini, and any other MCP-compatible client that supports the
Streamable HTTP transport (MCP 2025-03-26).

Endpoint:
  POST /mcp   JSON-RPC 2.0 — handles initialize, tools/list, tools/call

Usage in remote MCP clients:
  URL: https://cli-market-api.fly.dev/mcp
  Header: Authorization: Bearer <your-market-api-token>

API keys must not be placed in the URL. Query parameters are routinely retained
by browser history, proxies and access logs.

Tool tiers — kept in sync with _PRO_TOOLS/_STARTER_TOOLS/_ENTERPRISE_TOOLS
below; those frozensets are the source of truth for upgrade-prompt
behavior, this comment is just a human-readable mirror of it. Everything
not listed under Starter/Pro/Enterprise/Admin is Free.
  Starter — household_get (returns starter_required prompt if tier is free)
  Pro — basket, optimize_purchase, procurement_signal, price_risk,
        favorites, price_alerts, export, ask, add, cart, cart_update,
        checkout, orders, alert_create, alert_delete, household_update,
        ecosystem_radar, promo_detector, retailer_scorecard,
        informal_signal, inflation, scores, macro, intel_brief,
        indicators, trending, affordability, receipts, quality_scores,
        quality_flagged, dispersion, coverage_matrix, prices,
        basket_snapshot, brand_monitor, brand_monitor_promos,
        brand_monitor_config, brand_monitor_alerts
        (returns pro_required prompt if tier is free/starter)
  Enterprise — procurement_bulk (returns enterprise_required prompt if
        tier is below enterprise — a Pro upsell here would undersell it)
  Admin — scan, intel_refresh, enrichment_refresh (require MARKET_API_TOKEN,
        not a paid tier — no upgrade prompt applies; a 401 here means
        wrong audience, not "pay more")
"""

from __future__ import annotations

import asyncio
import os
from datetime import datetime, timezone

import httpx
from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse

from market_funnel import record_funnel_event
from market_billing import PUBLIC_PRO_PRICE_USD, PUBLIC_STARTER_PRICE_USD
from market_stats import (
    COUNTRIES,
    COUNTRY_CODES,
    PACKAGE_VERSION,
    PRICES_VERIFIED_LABEL,
    RETAILERS_VERIFIED,
)
from server_deps import auth_user, require_api_key

router = APIRouter(tags=["mcp-http"])

_API_BASE = "https://cli-market-api.fly.dev"
_MCP_VERSION = "2025-03-26"

_PRO_TOOLS = frozenset({
    "market_basket",
    "market_optimize_purchase",
    "market_procurement_signal",
    "market_price_risk",
    "market_favorites",
    "market_price_alerts",
    "market_export",
    "market_ask",
    "market_add",
    "market_cart",
    "market_cart_update",
    "market_checkout",
    "market_orders",
    "market_alert_create",
    "market_alert_delete",
    "market_household_update",
    "market_ecosystem_radar",
    "market_promo_detector",
    "market_shrinkflation_detector",
    "market_retailer_scorecard",
    "market_informal_signal",
    "market_inflation",
    "market_scores",
    "market_macro",
    "market_intel_brief",
    "market_indicators",
    "market_trending",
    "market_affordability",
    "market_receipts",
    "market_quality_scores",
    "market_quality_flagged",
    "market_dispersion",
    "market_coverage_matrix",
    "market_prices",
    "market_basket_snapshot",
    "market_brand_monitor",
    "market_brand_monitor_promos",
    "market_brand_monitor_config",
    "market_brand_monitor_alerts",
    "market_basket_stress",
    "market_commerce_pulse",
    "market_price_forecast",
    "market_arbitrage",
})

_UPGRADE_MSG = (
    f"This tool requires CLI Market Pro (${PUBLIC_PRO_PRICE_USD:.0f}/mo). "
    f"Start with Starter (${PUBLIC_STARTER_PRICE_USD:.0f}/mo) for search and compare, or upgrade to Pro "
    "to unlock basket, cart, checkout, orders, alerts, export, and AI ask. "
    "Plans at https://cli-market.dev."
)

# Starter-gated tools return a raw HTTP error instead of _UPGRADE_MSG when the
# caller is on the free tier — these get their own message instead.
_STARTER_TOOLS = frozenset({"market_household_get"})

_STARTER_UPGRADE_MSG = (
    f"This tool requires CLI Market Starter (${PUBLIC_STARTER_PRICE_USD:.0f}/mo) or above. "
    "Plans at https://cli-market.dev."
)

# Enterprise-gated tools — distinct from _PRO_TOOLS so the upgrade message
# doesn't undersell a Pro plan that wouldn't actually unlock the tool.
_ENTERPRISE_TOOLS = frozenset({"market_procurement_bulk"})

_ENTERPRISE_UPGRADE_MSG = (
    "This tool requires CLI Market Enterprise. Contact hello@cli-market.dev "
    "or see https://cli-market.dev for B2B procurement plans."
)

# Canonical client slugs — order matters (first match wins).
_CLIENT_MAP: list[tuple[str, list[str]]] = [
    ("claude",    ["claude", "anthropic"]),
    ("cursor",    ["cursor"]),
    ("kiro",      ["kiro", "amazon kiro"]),
    ("codex",     ["codex", "openai-codex", "openai codex"]),
    ("gemini",    ["gemini", "google gemini"]),
    ("windsurf",  ["windsurf"]),
    ("zed",       ["zed"]),
    ("vscode",    ["vscode", "visual studio code", "vs code", "github.copilot"]),
]


def _detect_client(
    client_info: dict | None,
    user_agent: str | None,
) -> tuple[str, str, str]:
    info = client_info or {}
    raw_name = str(info.get("name") or "").strip()
    raw_version = str(info.get("version") or "").strip()
    candidates = [raw_name.lower(), (user_agent or "").lower()]
    for text in candidates:
        if not text:
            continue
        for slug, patterns in _CLIENT_MAP:
            if any(p in text for p in patterns):
                return slug, raw_name or text, raw_version
    return "unknown", raw_name or (user_agent or "")[:80], raw_version


def _log_mcp_event(event: str, username: str | None, meta: dict) -> None:
    """Record MCP telemetry without persisting a bearer credential."""
    try:
        record_funnel_event(event, username=username or None, meta=meta)
    except Exception:
        pass


def _result_outcome(result: dict) -> tuple[str, str | None]:
    """Classify a tool result for the audit trail.

    Most tools surface failure as a top-level {"error": ...}. market_discover
    is the one exception (mcp_http.py _call_tool) — it fans out to three
    upstream calls and reports each failure as a nested {"error": ...} inside
    "lines"/"stores"/"countries" instead, with no top-level "error" key. Without
    this check that tool's audit trail would always read outcome="ok" even when
    an upstream call actually failed — found during the security review that
    added this audit logging, not a hypothetical.
    """
    if "error" in result:
        return "error", result["error"]
    if isinstance(result, dict):
        for value in result.values():
            if isinstance(value, dict) and "error" in value:
                return "partial_error", str(value["error"])[:200]
    return "ok", None


# ── Tool definitions ──────────────────────────────────────────────────────────

_TOOLS = [
    # ── Free ─────────────────────────────────────────────────────────────────
    {
        "name": "market_search",
        "description": (
            f"Search products across {RETAILERS_VERIFIED} LATAM retailers. "
            "Returns prices, brands, stores, and normalized unit prices (price_per_kg/L). "
            "Countries: PE, AR, BR, MX, CO, CL, IT, FR. "
            "Set require_all=true when you (the agent) will report results directly with "
            "no human filtering them first — default matching is lenient (any query word "
            "matches) and can surface unrelated products that merely share one common word "
            "or number, e.g. 'iphone 11' matching cookware or toys via a bare '11'."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string", "description": "Product name, e.g. 'arroz', 'leche entera'"},
                "country": {"type": "string", "description": "ISO country code: PE, AR, BR, MX, CO, CL"},
                "store": {"type": "string", "description": "Store key, e.g. 'wong_pe', 'carrefour_ar'"},
                "limit": {"type": "integer", "default": 20},
                "require_all": {
                    "type": "boolean",
                    "default": False,
                    "description": (
                        "Require every query word to match (not just one). Use true when "
                        "reporting results with no human review — prevents noise from "
                        "products that only share a single common word/number."
                    ),
                },
            },
        },
    },
    {
        "name": "market_compare",
        "description": (
            "Compare prices for a product across all retailers in a country. "
            "Returns price spread %, cheapest and most expensive stores, unit price. "
            "Set require_all=true when reporting results with no human filtering them first "
            "(see market_search)."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string"},
                "country": {"type": "string"},
                "limit": {"type": "integer", "default": 10},
                "require_all": {
                    "type": "boolean",
                    "default": False,
                    "description": "Require every query word to match (not just one). See market_search.",
                },
            },
        },
    },
    {
        "name": "market_stores",
        "description": f"List {RETAILERS_VERIFIED} indexed LATAM retailers. Filter by country.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "ISO country code (optional)"},
            },
        },
    },
    {
        "name": "market_trending",
        "description": "[Pro] Most searched and purchased products in the last 7 days for a country.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string"},
                "limit": {"type": "integer", "default": 10},
            },
        },
    },
    {
        "name": "market_discover",
        "description": "Retail coverage in one call: business lines, retailers, and countries. Optionally filter stores by country/line.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "Optional country filter for stores"},
                "line": {"type": "string", "description": "Optional business line filter for stores"},
            },
        },
    },
    {
        "name": "market_barcode",
        "description": "Look up a product by barcode / EAN / UPC.",
        "inputSchema": {
            "type": "object",
            "required": ["code"],
            "properties": {
                "code": {"type": "string", "description": "Barcode (EAN-13, UPC-A, etc.)"},
            },
        },
    },
    {
        "name": "market_inflation",
        "description": (
            "[Pro] Per-product price delta over the last N days for a LATAM country. "
            "Returns avg inflation %, top movers, basket stress signals."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["country"],
            "properties": {
                "country": {"type": "string", "description": "ISO country code: PE, AR, BR, MX, CO, CL"},
                "days": {"type": "integer", "default": 30},
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    {
        "name": "market_scores",
        "description": (
            "[Pro] Market intelligence scores for a LATAM country (0-100). "
            "Includes retail aggression, labor stress, logistics risk, macro alignment."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["country"],
            "properties": {
                "country": {"type": "string"},
            },
        },
    },
    {
        "name": "market_macro",
        "description": (
            "[Pro] Official tipo de cambio USD/PEN (compra/venta) and IPC Lima Metropolitana "
            "from BCRP (Peru's central bank). PE only, for now. Distinct from "
            "market_inflation, which is CLI Market's own shelf-price signal (RPV), "
            "not an official CPI index — use market_macro when you need the "
            "government's own inflation/exchange-rate numbers instead."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {},
        },
    },
    {
        "name": "market_intel_brief",
        "description": (
            "[Pro] Aggregated market intelligence brief: composite scores, basket stress, "
            "enrichment indicators (Open Food Facts, Wikimedia, weather, World Bank), "
            "and per-subcategory price/demand signals — all in one call."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "ISO country code: PE, AR, BR, MX, CO, CL"},
                "line": {"type": "string"},
                "days": {"type": "integer", "default": 7},
                "include_catalog": {"type": "boolean", "default": False},
            },
        },
    },
    {
        "name": "market_stats",
        "description": "Platform stats: total products indexed, stores active, data freshness, moat health.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "market_whoami",
        "description": "Return the authenticated user's username and subscription tier.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    # ── Pro ──────────────────────────────────────────────────────────────────
    {
        "name": "market_optimize_purchase",
        "description": (
            "[Pro] Single-call optimized procurement: given a basket of items and a country, "
            "returns the best-value store combination with TCO breakdown (including delivery), "
            "direct action links, and provenance metadata. "
            "Use this instead of the search → compare → basket chain when the goal is "
            'buying a list of products at the lowest total cost. '
            "Constraints: include_tco (bool), include_action_links (bool), require_stock (bool), "
            "max_stores (int), preferred_stores (list)."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["items", "country"],
            "properties": {
                "items": {
                    "type": "array",
                    "description": "List of {name, qty} objects, e.g. [{\"name\":\"leche\",\"qty\":2}]",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "qty": {"type": "number", "default": 1},
                        },
                    },
                },
                "country": {"type": "string", "description": "ISO country code: PE, AR, BR, MX, CO, CL"},
                "constraints": {
                    "type": "object",
                    "description": "Optional procurement constraints",
                    "properties": {
                        "include_tco": {"type": "boolean", "default": True},
                        "include_action_links": {"type": "boolean", "default": False},
                        "require_stock": {"type": "boolean", "default": False},
                        "max_stores": {"type": "integer"},
                        "preferred_stores": {"type": "array", "items": {"type": "string"}},
                    },
                },
            },
        },
    },
    {
        "name": "market_basket",
        "description": (
            "[Pro] Compare a basket of items across stores in a country. "
            "Returns total cost per store, cheapest combination, savings vs most expensive. "
            "Uses the cached price-snapshot DB by default (fast, refreshed every ~4h) — "
            "pass include_tco=false explicitly if you need a live per-item retailer scrape "
            "instead (much slower, 20-90s+, but current-moment prices)."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["items", "country"],
            "properties": {
                "items": {
                    "type": "array",
                    "description": "List of {name, qty} objects",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "qty": {"type": "number", "default": 1},
                        },
                    },
                },
                "country": {"type": "string"},
                "line": {
                    "type": "string",
                    "description": "Filter by store type: supermercados, farmacias, electro, hogar, departamentales, moda, automotriz",
                },
            },
        },
    },
    {
        "name": "market_procurement_signal",
        "description": "[Pro] Basket stress index for a country — affordability signal for procurement decisions.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string"},
            },
        },
    },
    {
        "name": "market_price_risk",
        "description": "[Pro] Price Risk Intelligence — which categories are becoming volatile? Returns risk level (low/moderate/high) with supporting signals.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "PE, AR, MX, BR, CO, CL"},
                "line": {"type": "string", "description": "supermercados, farmacias, electro"},
                "days": {"type": "integer", "default": 7},
            },
        },
    },
    {
        "name": "market_informal_signal",
        "description": (
            "[Pro] Coverage-honesty flag for informal retail channels. Reports how confident our formal-channel "
            "(VTEX/Shopify/Magento/WooCommerce) coverage is for a country/line — does NOT estimate "
            "informal-economy share (ferias, mercados de abastos, venta ambulante are not observed)."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["country"],
            "properties": {
                "country": {"type": "string", "description": "PE, AR, MX, BR, CO, CL"},
                "line": {"type": "string", "default": "supermercados"},
            },
        },
    },
    {
        "name": "market_promo_detector",
        "description": (
            "[Pro] Promo authenticity — flags discounts staged by inflating list_price shortly before "
            "advertising a markdown against it (common LatAm retail pattern)."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["product"],
            "properties": {
                "product": {"type": "string"},
                "store": {"type": "string"},
                "days": {"type": "integer", "default": 30},
            },
        },
    },
    {
        "name": "market_shrinkflation_detector",
        "description": (
            "[Pro] Shrinkflation signal — flags pack-size (weight/volume/unit) reductions at a flat "
            "shelf price, comparing current pack size vs. the product's own stable history."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["product"],
            "properties": {
                "product": {"type": "string"},
                "store": {"type": "string"},
                "days": {"type": "integer", "default": 90},
            },
        },
    },
    {
        "name": "market_retailer_scorecard",
        "description": (
            "[Pro] Retailer scorecard — coverage/freshness, catalog quality, and price volatility for one "
            "store in a single call. Does NOT include cross-store price competitiveness or stock availability."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["store"],
            "properties": {
                "store": {"type": "string", "description": "Store key from market_discover"},
                "days": {"type": "integer", "default": 30},
            },
        },
    },
    {
        "name": "market_basket_stress",
        "description": (
            "[Pro] Minimum canasta básica stress index for a country — cheapest indexed staple per item "
            "vs. a 100-baseline. NOT official CPI; a shelf-price-only proxy."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "PE, AR, MX, BR, CO, CL"},
            },
        },
    },
    {
        "name": "market_commerce_pulse",
        "description": (
            "[Pro] Agentic Commerce Pulse — weekly research report synthesized from moat signals "
            "(inflation, basket stress, promo activity, retailer coverage). JSON or markdown."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "default": "PE"},
                "days": {"type": "integer", "default": 7},
                "lang": {"type": "string", "default": "es", "description": "es or en"},
                "format": {"type": "string", "default": "json", "description": "json or markdown"},
            },
        },
    },
    {
        "name": "market_price_forecast",
        "description": (
            "[Pro] Price forecast from price_history for one product — trend + confidence band over a "
            "horizon. Requires enough historical snapshots; sparse products return low confidence "
            "rather than a fabricated trend."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["product"],
            "properties": {
                "product": {"type": "string", "description": "e.g. leche, arroz"},
                "country": {"type": "string", "default": "PE"},
                "horizon_days": {"type": "integer", "default": 21},
                "lookback_days": {"type": "integer", "default": 90},
            },
        },
    },
    {
        "name": "market_arbitrage",
        "description": (
            "[Pro] Cross-border shelf-price arbitrage — buy-country vs. sell-country spread in USD for a "
            "product across LatAm. Requires product or canonical_id. Shelf prices only; does NOT account "
            "for import duties, freight, or FX volatility between the compared snapshots."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "product": {"type": "string"},
                "canonical_id": {"type": "string"},
                "countries": {"type": "string", "description": "Comma-separated ISO codes, e.g. PE,MX,CL"},
                "min_spread_pct": {"type": "number", "default": 10.0},
            },
        },
    },
    {
        "name": "market_favorites",
        "description": "[Pro] List, add, or remove products from the user's favorites.",
        "inputSchema": {
            "type": "object",
            "required": ["action"],
            "properties": {
                "action": {"type": "string", "enum": ["list", "add", "remove"]},
                "product_id": {"type": "string", "description": "Required for add/remove"},
                "name": {"type": "string"},
                "store": {"type": "string"},
            },
        },
    },
    {
        "name": "market_price_alerts",
        "description": "[Pro] Price alerts: query drops or configure threshold notifications for a product.",
        "inputSchema": {
            "type": "object",
            "required": ["product"],
            "properties": {
                "product": {"type": "string", "description": "Product to monitor"},
                "store": {"type": "string"},
                "threshold_pct": {"type": "number", "default": 5.0},
                "limit": {"type": "integer", "default": 10},
            },
        },
    },
    {
        "name": "market_export",
        "description": "[Pro] Export price snapshot data as JSON or CSV.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string"},
                "line": {"type": "string"},
                "format": {"type": "string", "enum": ["json", "csv"], "default": "json"},
                "limit": {"type": "integer", "default": 500},
            },
        },
    },
    {
        "name": "market_ask",
        "description": "[Pro] Ask a natural-language question about prices, stores, or market conditions.",
        "inputSchema": {
            "type": "object",
            "required": ["prompt"],
            "properties": {
                "prompt": {"type": "string"},
                "country": {"type": "string"},
            },
        },
    },
    {
        "name": "market_add",
        "description": "[Pro] Add a product to the shopping cart.",
        "inputSchema": {
            "type": "object",
            "required": ["product_id", "store"],
            "properties": {
                "product_id": {"type": "string"},
                "name": {"type": "string"},
                "price": {"type": "number"},
                "store": {"type": "string"},
                "quantity": {"type": "integer", "default": 1},
                "url": {"type": "string"},
            },
        },
    },
    {
        "name": "market_cart",
        "description": "[Pro] View current shopping cart contents and totals.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "market_cart_update",
        "description": "[Pro] Update quantity of an item in the cart.",
        "inputSchema": {
            "type": "object",
            "required": ["product_id", "quantity"],
            "properties": {
                "product_id": {"type": "string"},
                "quantity": {"type": "integer"},
            },
        },
    },
    {
        "name": "market_checkout",
        "description": "[Pro] Initiate checkout for the current cart. Returns payment URL.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "payment_method": {"type": "string", "enum": ["yape", "paypal", "plin", "mercadopago"], "default": "yape"},
            },
        },
    },
    {
        "name": "market_orders",
        "description": "[Pro] List past orders for the authenticated user.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 10},
            },
        },
    },
    # ── Free (extended analytics) ─────────────────────────────────────────────
    {
        "name": "market_price_history",
        "description": (
            "Historical price snapshots from the data moat. "
            "Filter by product_id, store, or product line. Useful for trend analysis and auditing."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string", "description": "Product ID to filter by"},
                "store": {"type": "string", "description": "Store key, e.g. 'wong_pe'"},
                "line": {"type": "string", "description": "Product line: supermercados, farmacias, etc."},
                "limit": {"type": "integer", "default": 50},
            },
        },
    },
    {
        "name": "market_brands",
        "description": (
            "Top brands in the data moat by snapshot count. Filter by product line, and "
            "optionally by product/category (query, e.g. 'cafe') to see only the brands "
            "competing in that specific category instead of every brand in the line. "
            "When country is set, each brand also reports is_new: true the first time "
            "it's ever been seen for that country — a signal of a new market entrant."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "line": {"type": "string"},
                "country": {"type": "string"},
                "query": {"type": "string", "description": "Product/category name to scope brands to, e.g. 'cafe'"},
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    {
        "name": "market_indicators",
        "description": (
            "[Pro] Latest enrichment indicator values: Open Food Facts, World Bank, weather, and custom signals. "
            "Filter by country or product line."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string"},
                "line": {"type": "string"},
                "limit": {"type": "integer", "default": 50},
            },
        },
    },
    {
        "name": "market_stock",
        "description": "Latest stock snapshot for a product in a specific store.",
        "inputSchema": {
            "type": "object",
            "required": ["product_id", "store"],
            "properties": {
                "product_id": {"type": "string"},
                "store": {"type": "string", "description": "Store key, e.g. 'wong_pe'"},
            },
        },
    },
    {
        "name": "market_delivery",
        "description": "Delivery availability and estimated days for a product at a given store.",
        "inputSchema": {
            "type": "object",
            "required": ["product_id", "store"],
            "properties": {
                "product_id": {"type": "string"},
                "store": {"type": "string"},
                "zipcode": {"type": "string", "description": "Optional postal code"},
            },
        },
    },
    {
        "name": "market_dashboard",
        "description": (
            "Data-gate check: collector_stale, coverage_pct, publishable. Use before any procurement "
            "recommendation. Returns the compact gate payload by default (~1KB) — pass full=true only "
            "if you need the complete BI dashboard (moat health, coverage by country/line); that "
            "payload can exceed MCP client token limits."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "full": {"type": "boolean", "default": False, "description": "Return the full dashboard payload instead of the compact gate view"},
            },
        },
    },
    # ── Pro (alert management) ────────────────────────────────────────────────
    {
        "name": "market_alert_create",
        "description": (
            "[Pro] Create a price alert. Triggers when price moves above/below a threshold. "
            "Conditions: price_increase, price_decrease, price_change, price_below, price_above."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["condition", "product_query"],
            "properties": {
                "condition": {
                    "type": "string",
                    "enum": ["price_increase", "price_decrease", "price_change", "price_below", "price_above"],
                },
                "product_query": {"type": "string", "description": "Product name or search query"},
                "name": {"type": "string", "description": "Optional label for the alert"},
                "store": {"type": "string", "description": "Limit alert to a specific store"},
                "threshold_pct": {"type": "number", "default": 5.0, "description": "Trigger threshold in %"},
                "notify_email": {"type": "string", "description": "Email to notify on trigger"},
                "notify_webhook": {"type": "string", "description": "Webhook URL to POST on trigger"},
                "cooldown_hours": {"type": "integer", "default": 24, "description": "Min hours between notifications"},
            },
        },
    },
    {
        "name": "market_alert_delete",
        "description": "[Pro] Delete a price alert by its ID.",
        "inputSchema": {
            "type": "object",
            "required": ["alert_id"],
            "properties": {
                "alert_id": {"type": "string"},
            },
        },
    },
    # ── Free (intel + shop) ───────────────────────────────────────────────────
    {
        "name": "market_affordability",
        "description": (
            "[Pro] Affordability OS — canasta pressure, wage ratio, macro gap vs official CPI, regulatory headlines. "
            "One-call cost-of-living composite for LATAM. Countries: PE, AR, MX, BR, CO, CL."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "PE, AR, MX, BR, CO, CL"},
                "line": {"type": "string", "default": "supermercados"},
                "days": {"type": "integer", "default": 30},
            },
        },
    },
    {
        "name": "market_substitutes",
        "description": (
            "Product substitutes with unit-normalized savings and Nutri-Score tradeoffs. "
            "Use when the exact SKU is unavailable or to optimize basket cost."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["query", "country"],
            "properties": {
                "query": {"type": "string", "description": "Product name to match"},
                "country": {"type": "string", "description": "PE, AR, MX, BR, CO, CL"},
                "store": {"type": "string"},
                "limit": {"type": "integer", "default": 3},
            },
        },
    },
    {
        "name": "market_inflation_report",
        "description": (
            "Inflation Intelligence — where is price pressure increasing? "
            "Returns pressure level (stable/rising/rising_fast/falling/above_official) "
            "from internal shelf inflation and macro CPI gap."
        ),
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string", "description": "PE, AR, MX, BR, CO, CL"},
                "line": {"type": "string"},
                "days": {"type": "integer", "default": 30},
            },
        },
    },
    {
        "name": "market_exchange",
        "description": "Convert amounts between operating currencies (PEN, ARS, BRL, MXN, COP, CLP, EUR, USD).",
        "inputSchema": {
            "type": "object",
            "required": ["amount", "from_currency", "to_currency"],
            "properties": {
                "amount": {"type": "number"},
                "from_currency": {"type": "string", "description": "e.g. PEN, ARS, USD"},
                "to_currency": {"type": "string", "description": "e.g. USD, EUR, MXN"},
            },
        },
    },
    {
        "name": "market_enrich",
        "description": "Search Open Food Facts for nutritional enrichment data (Nutri-Score, ingredients, allergens).",
        "inputSchema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string"},
                "limit": {"type": "integer", "default": 5},
            },
        },
    },
    {
        "name": "market_categories",
        "description": "Explore VTEX category tree for a retailer. Deep catalog discovery.",
        "inputSchema": {
            "type": "object",
            "required": ["store"],
            "properties": {
                "store": {"type": "string", "description": "Store key, e.g. 'wong_pe'"},
            },
        },
    },
    {
        "name": "market_voice",
        "description": "Transcribe voice audio to text. Pass a public audio file URL (.ogg, .mp3, .wav).",
        "inputSchema": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "Public audio file URL"},
            },
        },
    },
    {
        "name": "market_ticket",
        "description": (
            "Scan a purchase receipt via OCR and compare prices against the data moat. "
            "Pass a public image URL. Set submit_to_crowd=true to contribute to moat validation."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["url"],
            "properties": {
                "url": {"type": "string", "description": "Receipt image URL (.jpg, .png)"},
                "country": {"type": "string", "description": "PE, AR, BR, MX, CO, CL"},
                "submit_to_crowd": {"type": "boolean", "default": False},
                "line_items": {"type": "array", "description": "Optional parsed line items for crowd submit"},
            },
        },
    },
    {
        "name": "market_moat_confidence",
        "description": "Crowd-sourced moat confidence score from receipt confirmations (7-day window).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "product_id": {"type": "string"},
                "store": {"type": "string"},
                "name": {"type": "string"},
            },
        },
    },
    {
        "name": "market_subscription",
        "description": "Current subscription plan: tier, rate limits, and available API keys.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "market_preferences",
        "description": "User preferences from purchase history: favorite stores and total spent.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    {
        "name": "market_household_get",
        "description": "[Starter] Household profile: monthly budget, dietary restrictions, staple list, default stores.",
        "inputSchema": {"type": "object", "properties": {}},
    },
    # ── Pro (enterprise intel + account) ──────────────────────────────────────
    {
        "name": "market_ecosystem_radar",
        "description": "[Pro] Ecosystem launches radar — curated Product Hunt cache. Retail and food-tech signal only.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {"type": "string", "default": "food"},
                "days": {"type": "integer", "default": 7},
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    {
        "name": "market_household_update",
        "description": "[Pro] Create or update household profile (budget, restrictions, staples). Pass patch=true to merge.",
        "inputSchema": {
            "type": "object",
            "required": ["payload"],
            "properties": {
                "payload": {
                    "type": "object",
                    "description": "Household schema: size, country, budget_monthly, restrictions, staple_list",
                },
                "patch": {"type": "boolean", "default": False},
            },
        },
    },
    {
        "name": "market_procurement_bulk",
        "description": "[Enterprise] B2B bulk procurement signals for SKU lists. Returns signals, substitutes, and export.",
        "inputSchema": {
            "type": "object",
            "required": ["lines"],
            "properties": {
                "country": {"type": "string", "default": "PE"},
                "organization_id": {"type": "string"},
                "lines": {
                    "type": "array",
                    "description": '[{"sku_query":"arroz 50kg","qty":10,"unit":"kg"}]',
                },
                "include_substitutes": {"type": "boolean", "default": True},
                "output": {"type": "string", "default": "json"},
            },
        },
    },
    # ── Quality / crowd data ─────────────────────────────────────────────────
    {
        "name": "market_receipts",
        "description": "[Pro] List your submitted receipt scans (newest first) — status and moat diff for each.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "limit": {"type": "integer", "default": 20},
                "offset": {"type": "integer", "default": 0},
            },
        },
    },
    {
        "name": "market_quality_scores",
        "description": "[Pro] Composite data-quality scores for the moat: freshness, unit normalization, and match confidence over a lookback window.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "days": {"type": "integer", "default": 7},
            },
        },
    },
    {
        "name": "market_quality_flagged",
        "description": "[Pro] Paginated data-quality anomalies (discount, outlier, or spread flags) surfaced by the moat's quality pipeline.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "reason": {"type": "string", "description": "discount | outlier | spread"},
                "limit": {"type": "integer", "default": 50},
                "offset": {"type": "integer", "default": 0},
            },
        },
    },
    {
        "name": "market_dispersion",
        "description": "[Pro] Price spread groups by subcategory from the data moat — the raw dispersion signal behind market_price_risk.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "line": {"type": "string"},
                "currency": {"type": "string"},
                "limit": {"type": "integer", "default": 50},
                "offset": {"type": "integer", "default": 0},
            },
        },
    },
    {
        "name": "market_coverage_matrix",
        "description": "[Pro] Country x business-line coverage map — check before market_search or market_basket whether the moat has data for a given country/line combination.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "line": {"type": "string"},
            },
        },
    },
    {
        "name": "market_prices",
        "description": "[Pro] Paginated raw price snapshots from the data moat. Filter by country, line, currency, or store; clean=true (default) excludes flagged/suspect rows.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "clean": {"type": "boolean", "default": True},
                "country": {"type": "string"},
                "line": {"type": "string"},
                "currency": {"type": "string"},
                "store": {"type": "string"},
                "limit": {"type": "integer", "default": 100},
                "offset": {"type": "integer", "default": 0},
            },
        },
    },
    {
        "name": "market_basket_snapshot",
        "description": "[Pro] Canasta básica snapshot computed directly from the DB — distinct from market_basket, which live-compares a specific item list you pass in.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "stores": {"type": "string", "description": "Comma-separated store keys"},
                "min_items": {"type": "integer", "default": 3},
            },
        },
    },
    # ── Brand Intelligence ────────────────────────────────────────────────────
    {
        "name": "market_brand_monitor",
        "description": "[Pro] Cross-store SKU snapshot for a brand and its declared competitors — prices, dispersion, and PVP deviations if configured.",
        "inputSchema": {
            "type": "object",
            "required": ["brand"],
            "properties": {
                "brand": {"type": "string", "description": "Brand name to monitor, e.g. 'Gloria'"},
                "country": {"type": "string", "default": "PE"},
                "competitors": {"type": "string", "description": "Comma-separated competitor brand names"},
                "line": {"type": "string"},
                "days": {"type": "integer", "default": 30},
            },
        },
    },
    {
        "name": "market_brand_monitor_promos",
        "description": "[Pro] Promo activation history for a brand and its competitors — when and where discounts ran, and their depth.",
        "inputSchema": {
            "type": "object",
            "required": ["brand"],
            "properties": {
                "brand": {"type": "string"},
                "country": {"type": "string", "default": "PE"},
                "competitors": {"type": "string", "description": "Comma-separated competitor brand names"},
                "line": {"type": "string"},
                "days": {"type": "integer", "default": 30},
            },
        },
    },
    {
        "name": "market_brand_monitor_config",
        "description": "[Pro] Register or update brand config: suggested retail prices (PVP) per SKU and declared competitor brands.",
        "inputSchema": {
            "type": "object",
            "required": ["brand_slug"],
            "properties": {
                "brand_slug": {"type": "string"},
                "competitors": {"type": "array", "description": "Competitor brand names, auto-included in market_brand_monitor calls"},
                "sku_pvps": {"type": "object", "description": "Mapping of product_id -> suggested retail price"},
            },
        },
    },
    {
        "name": "market_brand_monitor_alerts",
        "description": "[Pro] Active PVP deviations for registered brand SKUs. Requires a prior market_brand_monitor_config call with sku_pvps.",
        "inputSchema": {
            "type": "object",
            "required": ["brand"],
            "properties": {
                "brand": {"type": "string", "description": "Brand slug, must match registered config"},
                "country": {"type": "string", "default": "PE"},
            },
        },
    },
    # ── Admin ─────────────────────────────────────────────────────────────────
    {
        "name": "market_scan",
        "description": "[Admin] Scan for new VTEX stores. Admin-only.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "line": {"type": "string", "description": "Optional business line filter"},
            },
        },
    },
    {
        "name": "market_intel_refresh",
        "description": "[Admin] Recalculate internal indicators and fetch public APIs (FX, World Bank CPI, OFF, weather).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string"},
                "line": {"type": "string"},
            },
        },
    },
    {
        "name": "market_enrichment_refresh",
        "description": "[Admin] Refresh enrichment indicators only (OFF, Wiki, weather, food CPI).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string"},
            },
        },
    },
]


# ── Tool execution ────────────────────────────────────────────────────────────

_SLOW_TOOLS = frozenset({
    "market_basket", "market_optimize_purchase", "market_cart", "market_checkout",
    # market_search/market_compare default to the fast DB-backed path (see
    # routers/search.py) but callers can pass live=true for a per-store
    # scrape, and /products/compare always scrapes live — give both the same
    # 60s headroom as the other DB-fallback tools instead of a 20s timeout
    # that was shorter than typical live-scrape latency (18-34s observed).
    "market_search", "market_compare",
})

# Tools backed by cli-market-core's shared api_routes.py (Depends(_require_v1_auth)
# only -- that package has no billing/tier concept, so it can't self-enforce) or
# by routers unrelated to this fix. Real backend tier checks (require_pro,
# require_starter, require_export) exist for tools NOT listed here -- those
# already get 402/403 from the API itself, correctly translated to the right
# upgrade message below by name membership in _PRO_TOOLS/_STARTER_TOOLS/
# _ENTERPRISE_TOOLS. The tools below never receive a 402/403 from the backend
# regardless of caller tier, so gate them here instead -- otherwise their [Pro]/
# [Enterprise] labels above are purely aspirational.
_PRE_CHECK_TIER: dict[str, str] = {
    "market_receipts": "pro",
    "market_quality_scores": "pro",
    "market_quality_flagged": "pro",
    "market_dispersion": "pro",
    "market_coverage_matrix": "pro",
    "market_prices": "pro",
    "market_basket_snapshot": "pro",
    "market_procurement_bulk": "enterprise",
    # Found via a full tier-gating audit of all 65 tools (2026-07-27): these
    # were labeled [Pro]/[Starter] but their market_core-backed endpoint only
    # checks Depends(_require_v1_auth) -- same structural gap as the wave-6
    # tools above, just not caught until the audit actually read every
    # handler instead of trusting the aspirational [Pro] label.
    "market_optimize_purchase": "pro",
    "market_procurement_signal": "pro",
    "market_price_risk": "pro",
    "market_informal_signal": "pro",
    "market_promo_detector": "pro",
    "market_shrinkflation_detector": "pro",
    "market_retailer_scorecard": "pro",
    "market_ecosystem_radar": "pro",
    "market_household_get": "starter",
    "market_household_update": "pro",
    # Added with their real endpoints (cli-market-core 1.11.92) — same [Pro]
    # bundle="intel" tier as their siblings above (market_procurement_signal,
    # market_price_risk, market_retailer_scorecard); their market_core-backed
    # endpoint has the same structural gap (Depends(_require_v1_auth) only).
    "market_basket_stress": "pro",
    "market_commerce_pulse": "pro",
    "market_price_forecast": "pro",
    "market_arbitrage": "pro",
}

_STARTER_QUALIFYING_TIERS = frozenset({"starter", "pro", "pro_founding", "pro_annual", "enterprise", "builder"})
_PRO_QUALIFYING_TIERS = frozenset({"pro", "pro_founding", "pro_annual", "enterprise", "builder"})
_ENTERPRISE_QUALIFYING_TIERS = frozenset({"enterprise"})


def _pre_check_tier(name: str, token: str) -> dict | None:
    """Enforce tier for tools whose backend endpoint can't check it itself.

    Returns an error dict (same shape _call_tool's 402/403 handling produces)
    when the caller doesn't qualify, or None to proceed with the real call.
    """
    required = _PRE_CHECK_TIER.get(name)
    if not required:
        return None
    from market_billing import db_get_subscription
    from market_core.platform_admin import is_platform_admin

    try:
        username = auth_user(token)
    except Exception:
        return None  # let the normal auth path in _call_tool produce the 401
    if is_platform_admin(username):
        return None
    tier = db_get_subscription(username).get("tier", "free")
    if required == "enterprise":
        if tier not in _ENTERPRISE_QUALIFYING_TIERS:
            return {"error": "enterprise_required", "message": _ENTERPRISE_UPGRADE_MSG}
    elif required == "pro":
        if tier not in _PRO_QUALIFYING_TIERS:
            return {"error": "pro_required", "message": _UPGRADE_MSG}
    elif required == "starter":
        if tier not in _STARTER_QUALIFYING_TIERS:
            return {"error": "starter_required", "message": _STARTER_UPGRADE_MSG}
    return None


async def _call_tool(name: str, args: dict, token: str) -> dict:
    pre_check_error = _pre_check_tier(name, token)
    if pre_check_error:
        return pre_check_error
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    _timeout = 60.0 if name in _SLOW_TOOLS else 20.0
    async with httpx.AsyncClient(timeout=_timeout) as client:
        # ── Free tools ────────────────────────────────────────────────────────
        if name == "market_search":
            r = await client.post(f"{_API_BASE}/products/search", json=args, headers=headers)
        elif name == "market_compare":
            r = await client.post(f"{_API_BASE}/products/compare", json=args, headers=headers)
        elif name == "market_stores":
            r = await client.get(f"{_API_BASE}/stores", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_trending":
            r = await client.get(f"{_API_BASE}/analytics/trending", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_discover":
            # Was wired to /analytics/trending (same URL as market_trending) —
            # copy-paste bug, never composed lines+stores+countries like the
            # stdio implementation does. Compose it the same way here.
            store_params = {}
            if args.get("country"):
                store_params["country"] = args["country"]
            if args.get("line"):
                store_params["line"] = args["line"]
            lines_r, stores_r, countries_r = await asyncio.gather(
                client.get(f"{_API_BASE}/lines", headers=headers),
                client.get(f"{_API_BASE}/stores", params=store_params, headers=headers),
                client.get(f"{_API_BASE}/countries", headers=headers),
            )
            return {
                "lines": lines_r.json() if lines_r.status_code < 400 else {"error": lines_r.text[:200]},
                "stores": stores_r.json() if stores_r.status_code < 400 else {"error": stores_r.text[:200]},
                "countries": countries_r.json() if countries_r.status_code < 400 else {"error": countries_r.text[:200]},
            }
        elif name == "market_barcode":
            code = args.get("code", "")
            r = await client.get(f"{_API_BASE}/products/barcode/{code}", headers=headers)
        elif name == "market_inflation":
            r = await client.get(f"{_API_BASE}/v1/intel/inflation", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_scores":
            r = await client.get(f"{_API_BASE}/v1/intel/scores", params={"country": args.get("country")}, headers=headers)
        elif name == "market_macro":
            r = await client.get(f"{_API_BASE}/v1/intel/macro", headers=headers)
        elif name == "market_intel_brief":
            r = await client.get(f"{_API_BASE}/v1/intel/brief", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_stats":
            r = await client.get(f"{_API_BASE}/analytics/stats", headers=headers)
        elif name == "market_whoami":
            r = await client.get(f"{_API_BASE}/auth/whoami", headers=headers)
        # ── Pro tools ─────────────────────────────────────────────────────────
        elif name == "market_optimize_purchase":
            r = await client.post(f"{_API_BASE}/v1/missions/optimize-purchase", json=args, headers=headers)
        elif name == "market_basket":
            # Default to the DB-backed path (fast, ~ms) instead of the live
            # per-item retailer scrape (with Playwright fallback) that
            # /v1/basket/compare does when include_tco/include_action_links
            # are both absent — that path routinely took 20-90s+ and could
            # OOM the shared-cpu-1x machine. Callers that explicitly want
            # live-scraped freshness can still pass include_tco=false.
            basket_args = {"include_tco": True, **args}
            r = await client.post(f"{_API_BASE}/v1/basket/compare", json=basket_args, headers=headers)
        elif name == "market_procurement_signal":
            # /v1/intel/basket-stress was never a real route (verified 404 in
            # prod) — the actual endpoint is procurement-signal. This tool
            # has had no test coverage, so the mismatch shipped silently.
            r = await client.get(f"{_API_BASE}/v1/intel/procurement-signal", params={"country": args.get("country")}, headers=headers)
        elif name == "market_price_risk":
            # Was wired to /v1/intel/alerts (the discount-finder endpoint,
            # actually used by market_price_alerts) instead of the dedicated
            # price-risk endpoint — likely copy-pasted from a neighboring line.
            r = await client.get(f"{_API_BASE}/v1/intel/price-risk", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_informal_signal":
            r = await client.get(f"{_API_BASE}/v1/intel/informal-signal", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_promo_detector":
            r = await client.get(f"{_API_BASE}/v1/intel/promo-detector", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_shrinkflation_detector":
            r = await client.get(f"{_API_BASE}/v1/intel/shrinkflation-detector", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_retailer_scorecard":
            r = await client.get(f"{_API_BASE}/v1/intel/retailer-scorecard", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_basket_stress":
            # /v1/intel/basket-stress never existed as a route (verified 404 in
            # prod, cli-market-world#p0-missing-intel-endpoints) — cli-market-core
            # 1.11.92 adds the real handler. This tool had no dispatch case here
            # at all (fell through to "Unknown tool"), separate from the
            # unrelated basket-stress/procurement-signal mixup noted above on
            # market_procurement_signal.
            r = await client.get(f"{_API_BASE}/v1/intel/basket-stress", params={"country": args.get("country")}, headers=headers)
        elif name == "market_commerce_pulse":
            r = await client.get(f"{_API_BASE}/v1/intel/pulse", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_price_forecast":
            r = await client.get(f"{_API_BASE}/v1/intel/forecast", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_arbitrage":
            r = await client.get(f"{_API_BASE}/v1/intel/arbitrage", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_favorites":
            r = await client.post(f"{_API_BASE}/favorites", json=args, headers=headers)
        elif name == "market_price_alerts":
            # Was hitting /v1/alerts (the user's saved-alert subscriptions,
            # no query params forwarded) instead of /v1/intel/alerts (the
            # actual product/threshold discount query) — always returned an
            # empty list regardless of what was asked.
            r = await client.get(
                f"{_API_BASE}/v1/intel/alerts",
                params={k: v for k, v in args.items() if v is not None},
                headers=headers,
            )
        elif name == "market_export":
            r = await client.post(f"{_API_BASE}/v1/data/export", json=args, headers=headers)
        elif name == "market_ask":
            r = await client.post(f"{_API_BASE}/agent/ask", json=args, headers=headers)
        elif name == "market_add":
            r = await client.post(f"{_API_BASE}/cart/add", json=args, headers=headers)
        elif name == "market_cart":
            r = await client.get(f"{_API_BASE}/cart", headers=headers)
        elif name == "market_cart_update":
            r = await client.put(f"{_API_BASE}/cart/update", json=args, headers=headers)
        elif name == "market_checkout":
            r = await client.post(f"{_API_BASE}/checkout", json=args, headers=headers)
        elif name == "market_orders":
            r = await client.get(f"{_API_BASE}/orders", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        # ── Free (extended analytics) ─────────────────────────────────────────
        elif name == "market_price_history":
            r = await client.get(f"{_API_BASE}/analytics/price-history", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_brands":
            r = await client.get(f"{_API_BASE}/analytics/brands", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_indicators":
            r = await client.get(f"{_API_BASE}/analytics/indicators", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_stock":
            pid = args.get("product_id", "")
            r = await client.get(f"{_API_BASE}/products/stock/{pid}", params={"store": args.get("store")}, headers=headers)
        elif name == "market_delivery":
            pid = args.get("product_id", "")
            params = {k: v for k, v in args.items() if k != "product_id" and v is not None}
            r = await client.get(f"{_API_BASE}/products/delivery/{pid}", params=params, headers=headers)
        elif name == "market_dashboard":
            slim_params = {} if args.get("full") else {"slim": "true"}
            r = await client.get(f"{_API_BASE}/dashboard/data", params=slim_params, headers=headers)
        # ── Pro (alert management) ────────────────────────────────────────────
        elif name == "market_alert_create":
            r = await client.post(f"{_API_BASE}/v1/alerts", json=args, headers=headers)
        elif name == "market_alert_delete":
            alert_id = args.get("alert_id", "")
            r = await client.delete(f"{_API_BASE}/v1/alerts/{alert_id}", headers=headers)
        # ── Free (intel + shop) ───────────────────────────────────────────────
        elif name == "market_affordability":
            r = await client.get(f"{_API_BASE}/v1/intel/affordability", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_substitutes":
            r = await client.get(f"{_API_BASE}/v1/products/substitutes", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_inflation_report":
            r = await client.get(f"{_API_BASE}/v1/intel/inflation-report", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_exchange":
            r = await client.post(f"{_API_BASE}/v1/utils/exchange", json={"amount": args["amount"], "from": args["from_currency"], "to": args["to_currency"]}, headers=headers)
        elif name == "market_enrich":
            r = await client.get(f"{_API_BASE}/products/enrich", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_categories":
            store = args.get("store", "")
            r = await client.get(f"{_API_BASE}/categories/{store}", headers=headers)
        elif name == "market_voice":
            r = await client.post(f"{_API_BASE}/v1/voice/transcribe-url", json={"url": args["url"]}, headers=headers)
        elif name == "market_ticket":
            payload: dict = {"url": args["url"], "country": args.get("country")}
            r = await client.post(f"{_API_BASE}/v1/ticket/scan-url", json=payload, headers=headers)
            if r.status_code < 400 and args.get("submit_to_crowd"):
                crowd = await client.post(
                    f"{_API_BASE}/v1/receipts/submit",
                    json={"url": args["url"], "country": args.get("country", "PE"), "line_items": args.get("line_items")},
                    headers=headers,
                )
                base = r.json() if r.status_code < 400 else {"error": r.text[:200]}
                return {**base, "crowd_submission": crowd.json() if crowd.status_code < 400 else {"error": crowd.text[:200]}}
        elif name == "market_moat_confidence":
            r = await client.get(f"{_API_BASE}/v1/moat/confidence", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_subscription":
            r = await client.get(f"{_API_BASE}/auth/subscription", headers=headers)
        elif name == "market_preferences":
            r = await client.get(f"{_API_BASE}/agent/preferences", headers=headers)
        elif name == "market_household_get":
            r = await client.get(f"{_API_BASE}/v1/household", headers=headers)
        # ── Pro (enterprise intel + account) ──────────────────────────────────
        elif name == "market_ecosystem_radar":
            r = await client.get(f"{_API_BASE}/v1/ecosystem/launches", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_household_update":
            method = client.patch if args.get("patch") else client.put
            r = await method(f"{_API_BASE}/v1/household", json=args["payload"], headers=headers)
        elif name == "market_procurement_bulk":
            r = await client.post(f"{_API_BASE}/v1/intel/procurement-bulk", json=args, headers=headers)
        # ── Quality / crowd data ─────────────────────────────────────────────────
        elif name == "market_receipts":
            r = await client.get(f"{_API_BASE}/v1/receipts", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_quality_scores":
            r = await client.get(f"{_API_BASE}/v1/quality/scores", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_quality_flagged":
            r = await client.get(f"{_API_BASE}/v1/quality/flagged", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_dispersion":
            r = await client.get(f"{_API_BASE}/v1/dispersion", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_coverage_matrix":
            r = await client.get(f"{_API_BASE}/v1/coverage/matrix", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_prices":
            r = await client.get(f"{_API_BASE}/v1/prices", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_basket_snapshot":
            r = await client.get(f"{_API_BASE}/v1/basket", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        # ── Brand Intelligence ───────────────────────────────────────────────────
        elif name == "market_brand_monitor":
            r = await client.get(f"{_API_BASE}/v1/brand-monitor", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_brand_monitor_promos":
            r = await client.get(f"{_API_BASE}/v1/brand-monitor/promos", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_brand_monitor_config":
            r = await client.post(f"{_API_BASE}/v1/brand-monitor/config", json=args, headers=headers)
        elif name == "market_brand_monitor_alerts":
            r = await client.get(f"{_API_BASE}/v1/brand-monitor/alerts", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        # ── Admin ─────────────────────────────────────────────────────────────
        elif name == "market_scan":
            r = await client.post(f"{_API_BASE}/v1/admin/scan-stores", json={"line": args.get("line")}, headers=headers)
        elif name == "market_intel_refresh":
            r = await client.post(f"{_API_BASE}/v1/intel/refresh", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_enrichment_refresh":
            r = await client.post(f"{_API_BASE}/v1/intel/enrichment/refresh", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        else:
            return {"error": f"Unknown tool: {name}"}

        if r.status_code in (402, 403) and name in _ENTERPRISE_TOOLS:
            return {"error": "enterprise_required", "message": _ENTERPRISE_UPGRADE_MSG}
        if r.status_code in (402, 403) and name in _STARTER_TOOLS:
            return {"error": "starter_required", "message": _STARTER_UPGRADE_MSG}
        if r.status_code in (402, 403) and name in _PRO_TOOLS:
            return {"error": "pro_required", "message": _UPGRADE_MSG}
        if r.status_code >= 400:
            return {"error": f"HTTP {r.status_code}", "detail": r.text[:200]}
        return r.json()


# ── JSON-RPC helpers ──────────────────────────────────────────────────────────

def _rpc_ok(result: dict, req_id) -> dict:
    return {"jsonrpc": "2.0", "result": result, "id": req_id}


def _rpc_err(code: int, message: str, req_id) -> dict:
    return {"jsonrpc": "2.0", "error": {"code": code, "message": message}, "id": req_id}


# ── Routes ────────────────────────────────────────────────────────────────────

@router.get("/.well-known/mcp/server-card.json")
async def mcp_server_card():
    """Static server card for Smithery and MCP directory scanners."""
    return JSONResponse({
        "name": "CLI Market",
        "version": PACKAGE_VERSION,
        "description": (
            f"Commerce infrastructure for AI agents — {RETAILERS_VERIFIED} verified LATAM retailers, "
            f"{len(_TOOLS)} MCP tools, {COUNTRIES} countries ({', '.join(COUNTRY_CODES)}). "
            f"{PRICES_VERIFIED_LABEL} real prices refreshed every 4h."
        ),
        "homepage": "https://cli-market.dev",
        "repository": "https://pypi.org/project/cli-market-world/",
        "license": "MIT",
        "categories": ["commerce", "data", "retail"],
        "keywords": ["latam", "retail", "prices", "ecommerce", "vtex", "agents", "mcp", "procurement"],
        "capabilities": {"tools": {}},
        "authentication": {
            "type": "bearer",
            "required": True,
            "description": "Free API key via POST /auth/register or https://cli-market.dev",
        },
        "tools": [t["name"] for t in _TOOLS],
        "configSchema": {
            "type": "object",
            "required": ["apiKey"],
            "properties": {
                "apiKey": {
                    "type": "string",
                    "title": "API Key",
                    "description": "CLI Market API key (sk-...). Get one free at https://cli-market.dev",
                    "format": "password",
                },
            },
        },
    })


@router.get("/mcp")
async def mcp_http_get():
    """Inform SSE-transport clients that this server uses Streamable HTTP (POST only)."""
    return JSONResponse(
        {"error": "This MCP server uses Streamable HTTP transport (MCP 2025-03-26). Send POST requests to this endpoint."},
        status_code=405,
        headers={"Allow": "POST"},
    )


@router.post("/mcp")
async def mcp_http(
    request: Request,
    authorization: str | None = Header(None),
    user_agent: str | None = Header(None, alias="user-agent"),
):
    """HTTP MCP endpoint — JSON-RPC 2.0 over POST (Streamable HTTP, MCP 2025-03-26).

    Add to Claude / Cursor / VS Code / Kiro / Codex / Gemini:
      URL: https://cli-market-api.fly.dev/mcp
      Header: Authorization: Bearer <your-api-token>
    """
    has_query_token = "token" in request.query_params
    query_token = request.query_params.get("token")
    legacy_query_token_enabled = os.getenv("MCP_ALLOW_QUERY_TOKEN", "").strip() == "1"
    if has_query_token and not legacy_query_token_enabled:
        return JSONResponse(
            _rpc_err(
                -32001,
                "API tokens in the URL are disabled. Send Authorization: Bearer <token>.",
                None,
            ),
            status_code=400,
        )

    # This escape hatch is deliberately disabled by default. It gives operators
    # a short, explicit migration path for a legacy client while keeping the
    # safe default (no credentials in URLs) in every environment.
    effective_auth = authorization or (f"Bearer {query_token}" if query_token else None)
    raw_token = effective_auth.replace("Bearer ", "").strip() if effective_auth else None

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(_rpc_err(-32700, "Parse error", None), status_code=400)

    method = body.get("method", "")
    req_id = body.get("id")
    params = body.get("params", {})

    if method == "initialize":
        username = None
        if raw_token:
            try:
                username = auth_user(raw_token)
            except Exception:
                # Initialization remains public; an invalid token is rejected on tools/call.
                username = None
        client_info = params.get("clientInfo") or {}
        client_slug, client_raw, client_version = _detect_client(client_info, user_agent)
        _log_mcp_event("mcp_connect", username, {
            "client": client_slug,
            "client_raw": client_raw,
            "client_version": client_version,
            "protocol_version": params.get("protocolVersion", ""),
        })
        return JSONResponse(_rpc_ok({
            "protocolVersion": _MCP_VERSION,
            "capabilities": {"tools": {"listChanged": False}},
            "serverInfo": {
                "name": "cli-market",
                "version": PACKAGE_VERSION,
                "description": (
                    f"Commerce infrastructure for AI agents — {RETAILERS_VERIFIED} retailers, "
                    f"{len(_TOOLS)} tools, {COUNTRIES} LATAM countries."
                ),
            },
        }, req_id))

    if method == "notifications/initialized":
        return JSONResponse({})

    if method == "tools/list":
        return JSONResponse(_rpc_ok({"tools": _TOOLS}, req_id))

    if method == "tools/call":
        tool_name = params.get("name", "")
        tool_args = params.get("arguments", {})

        if not effective_auth:
            return JSONResponse(_rpc_err(-32001, "Auth required: Authorization header with a Bearer token", req_id), status_code=401)
        try:
            username = require_api_key(effective_auth)
        except Exception:
            return JSONResponse(_rpc_err(-32001, "Invalid or expired API token", req_id), status_code=401)

        client_info = params.get("clientInfo") or {}
        client_slug, client_raw, _ = _detect_client(client_info, user_agent)
        source_ip = request.client.host if request.client else None
        call_started = datetime.now(timezone.utc)
        _log_mcp_event("mcp_tool_call", username, {
            "client": client_slug,
            "client_raw": client_raw,
            "tool": tool_name,
            "country": tool_args.get("country") or None,
            "request_id": req_id,
            "source_ip": source_ip,
        })

        result = await _call_tool(tool_name, tool_args, raw_token)

        # Outcome logged as a distinct event (not merged into mcp_tool_call above)
        # so an auditor can trace a specific request_id from "called" to "resolved"
        # even when the call errors before this point is reached — e.g. a crash
        # inside _call_tool still leaves the call-attempt record intact.
        latency_ms = round((datetime.now(timezone.utc) - call_started).total_seconds() * 1000, 1)
        outcome, error_code = _result_outcome(result)
        _log_mcp_event("mcp_tool_result", username, {
            "tool": tool_name,
            "request_id": req_id,
            "source_ip": source_ip,
            "outcome": outcome,
            "error_code": error_code,
            "latency_ms": latency_ms,
        })

        if "error" in result:
            return JSONResponse(_rpc_ok({
                "content": [{"type": "text", "text": result.get("message") or f"Error: {result['error']}"}],
                "isError": True,
            }, req_id))

        import json
        return JSONResponse(_rpc_ok({
            "content": [{"type": "text", "text": json.dumps(result, ensure_ascii=False, indent=2)}],
        }, req_id))

    return JSONResponse(_rpc_err(-32601, f"Method not found: {method}", req_id), status_code=404)
