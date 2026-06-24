"""HTTP MCP transport endpoint — enables CLI Market to be added as a remote
MCP server in claude.ai, Claude Desktop (HTTP mode), Cursor, VS Code, Kiro,
Codex, Gemini, and any other MCP-compatible client that supports the
Streamable HTTP transport (MCP 2025-03-26).

Endpoint:
  POST /mcp   JSON-RPC 2.0 — handles initialize, tools/list, tools/call

Usage in claude.ai (Add MCP server):
  URL: https://cli-market-production.up.railway.app/mcp?token=<your-market-api-token>
  (claude.ai connectors don't support Bearer auth — use the token query param instead)

Tool tiers:
  Free  — search, compare, stores, trending, inflation, scores, intel_brief,
           whoami, stats, barcode, discover
  Pro   — basket, basket_stress, price_risk, favorites, price_alerts,
           export, ask, add, cart, cart_update, checkout, orders
           (returns upgrade prompt if tier is free)
"""

from __future__ import annotations

import httpx
from fastapi import APIRouter, Header, Request
from fastapi.responses import JSONResponse

from market_funnel import record_funnel_event
from market_stats import PACKAGE_VERSION, RETAILERS_VERIFIED
from server_deps import require_api_key

router = APIRouter(tags=["mcp-http"])

_API_BASE = "https://cli-market-production.up.railway.app"
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
})

_UPGRADE_MSG = (
    "This tool requires CLI Market Pro ($49/mo). "
    "Start with Starter ($9/mo) for search and compare, or upgrade to Pro "
    "to unlock basket, cart, checkout, orders, alerts, export, and AI ask. "
    "Plans at https://cli-market.dev."
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


def _log_mcp_event(event: str, token: str | None, meta: dict) -> None:
    try:
        record_funnel_event(event, username=token or None, meta=meta)
    except Exception:
        pass


# ── Tool definitions ──────────────────────────────────────────────────────────

_TOOLS = [
    # ── Free ─────────────────────────────────────────────────────────────────
    {
        "name": "market_search",
        "description": (
            f"Search products across {RETAILERS_VERIFIED} LATAM retailers. "
            "Returns prices, brands, stores, and normalized unit prices (price_per_kg/L). "
            "Countries: PE, AR, BR, MX, CO, CL, IT, FR."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string", "description": "Product name, e.g. 'arroz', 'leche entera'"},
                "country": {"type": "string", "description": "ISO country code: PE, AR, BR, MX, CO, CL"},
                "store": {"type": "string", "description": "Store key, e.g. 'wong_pe', 'carrefour_ar'"},
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    {
        "name": "market_compare",
        "description": (
            "Compare prices for a product across all retailers in a country. "
            "Returns price spread %, cheapest and most expensive stores, unit price."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["query"],
            "properties": {
                "query": {"type": "string"},
                "country": {"type": "string"},
                "limit": {"type": "integer", "default": 10},
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
        "description": "Most searched and purchased products in the last 7 days for a country.",
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
        "description": "Discover featured and recommended products for a country.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "country": {"type": "string"},
                "limit": {"type": "integer", "default": 10},
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
            "Per-product price delta over the last N days for a LATAM country. "
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
            "Market intelligence scores for a LATAM country (0-100). "
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
        "name": "market_intel_brief",
        "description": (
            "Aggregated market intelligence brief: composite scores, basket stress, "
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
            "Returns total cost per store, cheapest combination, savings vs most expensive."
        ),
        "inputSchema": {
            "type": "object",
            "required": ["items", "country"],
            "properties": {
                "items": {
                    "type": "array",
                    "description": "List of {name, quantity} objects",
                    "items": {
                        "type": "object",
                        "properties": {
                            "name": {"type": "string"},
                            "quantity": {"type": "number", "default": 1},
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
        "description": "[Pro] Price alerts: products with delta above threshold in the last 30 days.",
        "inputSchema": {
            "type": "object",
            "required": ["product"],
            "properties": {
                "product": {"type": "string"},
                "store": {"type": "string"},
                "threshold_pct": {"type": "number", "default": 5.0},
                "limit": {"type": "integer", "default": 10},
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
        "description": "[Pro] List active price alerts for the user.",
        "inputSchema": {"type": "object", "properties": {}},
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
        "description": "Top brands in the data moat by snapshot count. Filter by product line.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "line": {"type": "string"},
                "country": {"type": "string"},
                "limit": {"type": "integer", "default": 20},
            },
        },
    },
    {
        "name": "market_indicators",
        "description": (
            "Latest enrichment indicator values: Open Food Facts, World Bank, weather, and custom signals. "
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
            "Business-intelligence feed: moat health, collector status, coverage by country and line, "
            "data gate signals (collector_stale). Use before any procurement recommendation."
        ),
        "inputSchema": {"type": "object", "properties": {}},
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
]


# ── Tool execution ────────────────────────────────────────────────────────────

_SLOW_TOOLS = frozenset({"market_basket", "market_optimize_purchase", "market_cart", "market_checkout"})


async def _call_tool(name: str, args: dict, token: str) -> dict:
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
            r = await client.get(f"{_API_BASE}/analytics/trending", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_barcode":
            code = args.get("code", "")
            r = await client.get(f"{_API_BASE}/products/barcode/{code}", headers=headers)
        elif name == "market_inflation":
            r = await client.get(f"{_API_BASE}/v1/intel/inflation", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_scores":
            r = await client.get(f"{_API_BASE}/v1/intel/scores", params={"country": args.get("country")}, headers=headers)
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
            r = await client.post(f"{_API_BASE}/v1/basket/compare", json=args, headers=headers)
        elif name == "market_procurement_signal":
            r = await client.get(f"{_API_BASE}/v1/intel/basket-stress", params={"country": args.get("country")}, headers=headers)
        elif name == "market_price_risk":
            r = await client.get(f"{_API_BASE}/v1/intel/alerts", params={k: v for k, v in args.items() if v is not None}, headers=headers)
        elif name == "market_favorites":
            r = await client.post(f"{_API_BASE}/favorites", json=args, headers=headers)
        elif name == "market_price_alerts":
            r = await client.get(f"{_API_BASE}/v1/alerts", headers=headers)
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
            r = await client.get(f"{_API_BASE}/dashboard/data", headers=headers)
        # ── Pro (alert management) ────────────────────────────────────────────
        elif name == "market_alert_create":
            r = await client.post(f"{_API_BASE}/v1/alerts", json=args, headers=headers)
        elif name == "market_alert_delete":
            alert_id = args.get("alert_id", "")
            r = await client.delete(f"{_API_BASE}/v1/alerts/{alert_id}", headers=headers)
        else:
            return {"error": f"Unknown tool: {name}"}

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
            f"{len(_TOOLS)} MCP tools, 8 countries (PE, AR, BR, MX, CO, CL, IT, FR). "
            "61,000+ real prices refreshed every 4h."
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
    token: str | None = None,
    user_agent: str | None = Header(None, alias="user-agent"),
):
    """HTTP MCP endpoint — JSON-RPC 2.0 over POST (Streamable HTTP, MCP 2025-03-26).

    Add to Claude / Cursor / VS Code / Kiro / Codex / Gemini:
      URL: https://cli-market-production.up.railway.app/mcp?token=<your-api-token>
    """
    effective_auth = authorization or (f"Bearer {token}" if token else None)
    raw_token = effective_auth.replace("Bearer ", "").strip() if effective_auth else None

    try:
        body = await request.json()
    except Exception:
        return JSONResponse(_rpc_err(-32700, "Parse error", None), status_code=400)

    method = body.get("method", "")
    req_id = body.get("id")
    params = body.get("params", {})

    if method == "initialize":
        client_info = params.get("clientInfo") or {}
        client_slug, client_raw, client_version = _detect_client(client_info, user_agent)
        _log_mcp_event("mcp_connect", raw_token, {
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
                    f"{len(_TOOLS)} tools, 8 LATAM countries."
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
            return JSONResponse(_rpc_err(-32001, "Auth required: Authorization header or ?token= query param", req_id), status_code=401)
        try:
            require_api_key(effective_auth)
        except Exception:
            return JSONResponse(_rpc_err(-32001, "Invalid or expired API token", req_id), status_code=401)

        client_info = params.get("clientInfo") or {}
        client_slug, client_raw, _ = _detect_client(client_info, user_agent)
        _log_mcp_event("mcp_tool_call", raw_token, {
            "client": client_slug,
            "client_raw": client_raw,
            "tool": tool_name,
            "country": tool_args.get("country") or None,
        })

        result = await _call_tool(tool_name, tool_args, raw_token)

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
