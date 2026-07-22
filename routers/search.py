"""Product search, comparison, and metadata endpoints.

Endpoints:
  POST /products/search                  Multi-store search (parallel batch)
  POST /products/compare                 Cross-store comparison + fuzzy match
  POST /v1/basket/compare                Multi-item cart comparison across stores
  GET  /products/stock/{product_id}      Latest stock from price_snapshots
  GET  /products/delivery/{product_id}   Placeholder delivery info
  GET  /products/barcode/{code}          OpenFoodFacts barcode lookup
  GET  /products/enrich                  OpenFoodFacts search
  GET  /categories/{store}               VTEX category tree
"""

from __future__ import annotations

import asyncio
import difflib
import logging
import os
import re
import time

import httpx
from fastapi import APIRouter, Header, HTTPException
from pydantic import BaseModel, field_validator

from market_core import (
    get_default_stores,
    LINES,
    PAGE_SIZE,
    STORES,
    fetch_store,
    get_db,
    price_to_usd,
    product_from_json,
    save_price_snapshot,
    save_search_query,
)
from market_core.product_search import (
    build_search_sql,
    is_relevant as _is_relevant,
    normalize_text as _normalize_text,  # noqa: F401 - re-exported for routers/analytics.py
    query_tokens as _query_tokens,
)
from server_deps import require_api_key

from backend_interface import get_store_profile, store_exists
from index_gate import infer_category

logger = logging.getLogger("market.server").getChild("search")

router = APIRouter(tags=["search"])

# _normalize_text/_word_set/_query_tokens/_is_relevant moved to
# market_core.product_search — shared with data_v1_service.query_product_search
# (the intel agent's search tool) so the two no longer drift.


def _attach_source_health(response: dict, store_ids: list[str]) -> dict:
    try:
        from market_core.source_health import health_for_stores

        db = get_db()
        try:
            response["source_health"] = health_for_stores(db, store_ids)
        finally:
            db.close()
    except Exception as exc:
        logger.debug("source_health attach skipped: %s", exc)
    return response


def _resolve_search_stores(body: SearchRequest) -> list[str]:
    stores = [body.store] if body.store else get_default_stores()
    stores = [s for s in stores if store_exists(s)]
    if body.line and body.line in LINES:
        stores = [s for s in stores if (get_store_profile(s) or {}).get("line") == body.line]
    if body.country:
        cc = body.country.strip().upper()
        stores = [s for s in stores if (STORES.get(s) or get_store_profile(s) or {}).get("country") == cc]
    return stores


_GROWTH_CACHE_TTL = 60.0
_growth_cache: tuple[float, frozenset[str]] = (0.0, frozenset())


def _growth_store_set() -> frozenset[str]:
    """store_ids with the paid Growth tier active — short TTL cache since
    growth flips are rare (manual admin action via
    POST /admin/stores/{store_id}/activate-growth), not worth a query per
    search request."""
    global _growth_cache

    now = time.monotonic()
    cached_at, ids = _growth_cache
    if now - cached_at < _GROWTH_CACHE_TTL:
        return ids
    db = get_db()
    try:
        rows = db.execute(
            "SELECT store_id FROM store_credentials WHERE is_growth = 1 AND active = 1"
        ).fetchall()
    except Exception:
        # is_growth column not yet migrated (older cli-market-core) — no
        # growth stores rather than a hard failure on every search.
        db.close()
        return frozenset()
    db.close()
    ids = frozenset(dict(r)["store_id"] for r in rows)
    _growth_cache = (now, ids)
    return ids


class SearchRequest(BaseModel):
    query: str
    store: str | None = None
    line: str | None = None
    country: str | None = None
    page: int = 1
    limit: int = PAGE_SIZE
    # Default reads collector-refreshed price_snapshots (fast, <=4h old).
    # Set true to force a live per-store scrape (slow: 15-30s+, can fail
    # under load) when freshness matters more than latency.
    live: bool = False
    # Default (False) matches ANY query token — fine when a human sees the
    # full result list and filters themselves (the general-search UI this
    # endpoint was originally built for). Set True when nothing but this
    # filter stands between a candidate and being reported as "the" result
    # — e.g. an LLM agent calling this tool directly with no human in the
    # loop. Confirmed live: market_search(query='iphone 11') without this
    # returned toys/cookware/car batteries sharing only a bare '11' token.
    # Mirrors the require_all already used by the basket auto-picker below.
    require_all: bool = False

    @field_validator("query")
    @classmethod
    def sanitize_query(cls, v: str) -> str:
        v = v.strip()[:200]
        if not v:
            raise ValueError("Query no puede estar vacío")
        return re.sub(r"[<>{}()\[\]]", "", v)


class BasketRequest(BaseModel):
    items: list[dict]
    stores: list[str] | None = None
    # Wave 4 params — when any of these are set the handler delegates to
    # market_core.market_basket.build_basket_compare (DB-based, fully enveloped).
    include_tco: bool = False
    payment_method: str = "yape"
    include_delivery: bool = True
    zipcode: str | None = None
    include_action_links: bool = False
    country: str = "PE"
    enveloped: bool = True
    # Default reads price_snapshots via the DB-backed matcher (fast, <=4h
    # old) regardless of include_tco/include_action_links. Set true to force
    # the old live per-store-per-item scrape (source: "live" in the
    # response) — O(stores*items) fan-out, can take 15-30s+ under load.
    live: bool = False


@router.post(
    "/products/search",
    summary="Search products across 41+ verified retailers",
)
async def search_products(body: SearchRequest, authorization: str | None = Header(None)):
    """Search for products by name across all active retailers. Use for product discovery —
    e.g. "leche evaporada Gloria" or "arroz 5kg". Returns ranked matches with price,
    store name, stock status, and product URL. Covers 41 verified retailers across
    PE, AR, BR, MX, CO, CL, IT, FR. Prices are shelf data refreshed every 4h — never
    scraped on demand (pass live=true to force a per-store scrape instead; slower
    and best-effort). Prefer POST /v1/basket/compare when procuring multiple items;
    use this endpoint for single-item discovery or spot price checks."""
    username = require_api_key(authorization)
    try:
        result = await _search_products(body)
        if username.startswith("demo:"):
            try:
                from market_funnel import record_funnel_event

                record_funnel_event(
                    "demo_first_tool_call",
                    session_id=username.split(":", 1)[-1],
                    meta={"tool": "search", "query": body.query, "agent_source": "demo"},
                    dedupe=True,
                )
            except Exception:
                pass
        try:
            from market_funnel import maybe_first_search
            maybe_first_search(username, query=body.query)
        except Exception:
            pass
        return result
    except Exception as e:
        logger.exception("search_products crashed")
        raise HTTPException(status_code=500, detail=str(e))


async def _parallel_fetch_stores(
    stores: list[str],
    query: str,
    page: int,
    limit: int,
) -> tuple[dict[str, list], list[dict]]:
    """Fetch retailer product lists in parallel batches (shared by search + compare)."""
    parallel_batch = 20
    timeout_s = float(os.getenv("SEARCH_TIMEOUT", "15.0"))
    all_raw: dict[str, list] = {}
    errors: list[dict] = []

    async def fetch_one(store: str):
        try:
            raw = await fetch_store(store, query, page, limit)
            return store, raw, None
        except Exception as e:
            return store, [], str(e)

    for i in range(0, len(stores), parallel_batch):
        batch = stores[i : i + parallel_batch]
        batch_tasks = [fetch_one(s) for s in batch]
        try:
            batch_results = await asyncio.wait_for(asyncio.gather(*batch_tasks), timeout=timeout_s)
        except asyncio.TimeoutError:
            errors.extend({"store": s, "error": "timeout"} for s in batch)
            break
        except Exception as e:
            logger.error("Fetch batch error: %s", e)
            errors.append({"store": "batch", "error": str(e)})
            break
        for store, raw, err in batch_results:
            if err:
                errors.append({"store": store, "error": err})
            else:
                all_raw[store] = raw
    return all_raw, errors


async def _search_products(body: SearchRequest):
    if body.live:
        return await _search_products_live(body)
    return _search_products_db(body)


def _search_products_db(body: SearchRequest) -> dict:
    """DB-backed search: reads collector-refreshed price_snapshots (<=4h old)
    instead of live-scraping every store per request. A live per-store fan-out
    (still available via live=true) routinely took 15-30s+ against 38 stores
    and could OOM the shared-cpu-1x API machine — the same class of problem
    already fixed for market_basket by defaulting it to the DB path.
    """
    stores = _resolve_search_stores(body)
    q_tokens = _query_tokens(body.query)
    if not stores or not q_tokens:
        save_search_query(body.query, body.line, body.store, 0)
        return {"query": body.query, "results": [], "total": 0}

    sql, params = build_search_sql(
        stores=stores,
        q_tokens=q_tokens,
        require_all=body.require_all,
        limit=body.limit,
        columns=(
            "product_id, name, brand, price, list_price, discount, store, "
            "store_name, currency, line, line_name, category, stock, url, confidence"
        ),
    )
    db = get_db()
    try:
        rows = db.execute(sql, params).fetchall()
    finally:
        db.close()

    results: list[dict] = []
    for r in rows:
        row = dict(r)
        if not _is_relevant(row.get("name", ""), q_tokens, require_all=body.require_all):
            continue
        row["id"] = row.pop("product_id")
        results.append(row)

    growth_stores = _growth_store_set()
    results.sort(key=lambda p: (
        p["price"] if p["price"] > 0 else float("inf"),
        0 if p.get("store") in growth_stores else 1,
    ))
    save_search_query(body.query, body.line, body.store, len(results))

    response: dict = {"query": body.query, "results": results, "total": len(results)}
    return _attach_source_health(response, stores)


async def _search_products_live(body: SearchRequest):
    stores = _resolve_search_stores(body)
    all_raw, errors = await _parallel_fetch_stores(stores, body.query, body.page, body.limit)

    results: list[dict] = []
    for store, raw in all_raw.items():
        for p in raw:
            try:
                prod = product_from_json(p, store)
                store_line = (STORES.get(store) or get_store_profile(store) or {}).get("line", "")
                if store_line:
                    prod["line"] = store_line
                    prod["line_name"] = LINES.get(store_line, {}).get("name", store_line)
                results.append(prod)
            except Exception as pe:
                errors.append({"store": store, "product_id": str(p)[:80], "error": str(pe)})

    growth_stores = _growth_store_set()
    results.sort(key=lambda p: (
        p["price"] if p["price"] > 0 else float("inf"),
        0 if p.get("store") in growth_stores else 1,
    ))
    for p in results:
        save_price_snapshot(p)
    save_search_query(body.query, body.line, body.store, len(results))

    response: dict = {"query": body.query, "results": results, "total": len(results)}
    if errors:
        response["partial"] = True
        response["errors"] = errors
    return _attach_source_health(response, stores)


def _match_key(p: dict) -> str:
    name = re.sub(r"[^a-záéíóúñ0-9]", "", p["name"].lower())
    # `p.get('brand', '')` only falls back to '' when the key is *absent* —
    # rows with an explicit brand=NULL (a real, valid price_snapshots state,
    # not just a test fixture gap) still pass None through and crash .lower().
    brand = p.get("brand") or ""
    return f"{brand.lower()}|{name}"


def _fuzzy_compare(all_products: dict[str, list[dict]], stores: list[str]) -> list[dict]:
    """Cross-store brand+name fuzzy matching, shared by the DB and live compare paths."""
    key_index: dict[str, dict] = {}
    for store, prods in all_products.items():
        for p in prods:
            k = _match_key(p)
            key_index.setdefault(k, {})[store] = p

    FUZZY_THRESHOLD = 0.70
    store_list = list(stores)
    for i in range(len(store_list)):
        for j in range(i + 1, len(store_list)):
            sa, sb = store_list[i], store_list[j]
            only_a = [k for k, sp in key_index.items() if sa in sp and sb not in sp]
            only_b = [k for k, sp in key_index.items() if sb in sp and sa not in sp]
            matched_b: set[str] = set()
            for ka in only_a:
                prod_a = key_index[ka][sa]
                best_score = 0.0
                best_kb = None
                for kb in only_b:
                    if kb in matched_b:
                        continue
                    score = difflib.SequenceMatcher(
                        None, _match_key(prod_a), _match_key(key_index[kb][sb])
                    ).ratio()
                    if score > best_score:
                        best_score = score
                        best_kb = kb
                if best_score >= FUZZY_THRESHOLD and best_kb:
                    key_index[ka][sb] = key_index[best_kb][sb]
                    matched_b.add(best_kb)

    growth_stores = _growth_store_set()
    comparison: list[dict] = []
    for _k, sp in key_index.items():
        if len(sp) >= 1:
            prices = {s: p["price"] for s, p in sp.items() if p["price"] > 0}
            if prices:
                # Growth stores (paid placement) win exact price ties only —
                # never outrank a genuinely cheaper competitor, so "cheapest
                # first" stays true regardless of who's paying.
                best = min(prices, key=lambda s: (prices[s], 0 if s in growth_stores else 1))
                rep = sp[list(sp.keys())[0]]
                comparison.append(
                    {
                        "name": rep["name"],
                        "brand": rep.get("brand", ""),
                        "prices": prices,
                        "best_store": best,
                        "best_price": prices[best],
                    }
                )
    comparison.sort(key=lambda x: (
        x["best_price"],
        0 if x.get("best_store") in growth_stores else 1,
    ))
    return comparison


async def _compare_products(body: SearchRequest) -> dict:
    if body.live:
        return await _compare_products_live(body)
    return _compare_products_db(body)


def _compare_products_db(body: SearchRequest) -> dict:
    """DB-backed compare: reads collector-refreshed price_snapshots instead
    of live-scraping every store per request — same rationale and pattern
    as _search_products_db."""
    stores = _resolve_search_stores(body)
    q_tokens = _query_tokens(body.query)
    payload: dict = {"query": body.query, "comparison": [], "stores_compared": 0}
    if body.country:
        payload["country"] = body.country.strip().upper()
    if not stores or not q_tokens:
        return payload

    sql, params = build_search_sql(
        stores=stores,
        q_tokens=q_tokens,
        require_all=body.require_all,
        limit=body.limit,
        columns="product_id, name, brand, price, store",
    )
    db = get_db()
    try:
        rows = db.execute(sql, params).fetchall()
    finally:
        db.close()

    all_products: dict[str, list[dict]] = {}
    for r in rows:
        row = dict(r)
        if not _is_relevant(row.get("name", ""), q_tokens, require_all=body.require_all):
            continue
        all_products.setdefault(row["store"], []).append(row)

    payload["comparison"] = _fuzzy_compare(all_products, stores)
    payload["stores_compared"] = len(all_products)
    return _attach_source_health(payload, list(all_products.keys()) or stores)


async def _compare_products_live(body: SearchRequest) -> dict:
    """Live per-store scrape (unchanged behavior). Opt in via live=true."""
    stores = _resolve_search_stores(body)
    all_raw, errors = await _parallel_fetch_stores(stores, body.query, body.page, body.limit)

    all_products = {}
    for s, raw in all_raw.items():
        all_products[s] = []
        for p in raw:
            try:
                all_products[s].append(product_from_json(p, s))
            except Exception:
                pass

    comparison = _fuzzy_compare(all_products, stores)
    payload: dict = {"query": body.query, "comparison": comparison, "stores_compared": len(all_raw)}
    if body.country:
        payload["country"] = body.country.strip().upper()
    if errors:
        payload["partial"] = True
        payload["errors"] = errors
    return _attach_source_health(payload, list(all_raw.keys()) or stores)


@router.post(
    "/products/compare",
    summary="Compare prices for one product across all stores",
)
async def compare_products(body: SearchRequest, authorization: str | None = Header(None)):
    """Compare prices for a single product across multiple stores using
    brand+name fuzzy matching. Returns one ranked match per store with price and URL.
    Prices are shelf data refreshed every 4h — never scraped on demand (pass
    live=true to force a per-store scrape instead; slower and best-effort).
    Use when you need the cheapest store for a specific product. For a full
    multi-item basket use POST /v1/basket/compare instead."""
    username = require_api_key(authorization)
    if username.startswith("demo:"):
        try:
            from market_funnel import record_funnel_event

            record_funnel_event(
                "demo_first_tool_call",
                session_id=username.split(":", 1)[-1],
                meta={"tool": "compare", "query": body.query, "agent_source": "demo"},
                dedupe=True,
            )
        except Exception:
            pass
    return await _compare_products(body)


@router.post(
    "/v1/basket/compare",
    summary="Find the cheapest single store for a multi-item basket",
)
async def basket_compare(body: BasketRequest, authorization: str | None = Header(None)):
    """Find the cheapest single store for a multi-item procurement basket.
    Searches each item across all (or a filtered list of) stores and returns
    the store with the lowest combined total. Ideal for procurement flows where
    a single supplier per order is preferred. Missing items are skipped gracefully.
    Always call this before adding items to cart for multi-item orders — it
    returns best_store and best_total so you can target the right retailer.
    Pass include_tco=true or include_action_links=true for Wave 4 cost analysis."""
    require_api_key(authorization)
    # DB-backed path is the default (fast, reads collector-refreshed
    # price_snapshots) — matches the fix already forced for the market_basket
    # MCP tool (mcp_http.py always passed include_tco=True to reach this
    # branch). live=true opts into the old per-item live scrape below.
    if not body.live:
        from market_core.market_basket import build_basket_compare as _core_basket

        store_filter = {s for s in body.stores if s} if body.stores else None
        db = get_db()
        try:
            return _core_basket(
                db,
                items=body.items,
                store_filter=store_filter,
                enveloped=body.enveloped,
                include_tco=body.include_tco,
                payment_method=body.payment_method,
                include_delivery=body.include_delivery,
                zipcode=body.zipcode,
                include_action_links=body.include_action_links,
                country=body.country,
            )
        finally:
            db.close()
    stores = body.stores or get_default_stores()
    stores = [s for s in stores if s in STORES or store_exists(s)]
    # Fetch every item across every store in parallel instead of the old
    # sequential `for store: for item: await fetch_store(...)` — that was
    # O(stores * items) fully-serialized awaits (world#363: a 3-item PE
    # basket across ~15 stores timed out at 60s). One _parallel_fetch_stores
    # call per item already batches+parallelizes across stores internally;
    # gathering across items too means total latency is bounded by the
    # slowest single item-fetch round, not the sum of all of them.
    item_fetches = await asyncio.gather(
        *(_parallel_fetch_stores(stores, item["name"], 1, PAGE_SIZE) for item in body.items)
    )
    item_raw_by_store: list[dict[str, list]] = [raw for raw, _errors in item_fetches]

    results: dict[str, dict] = {}
    for store in stores:
        t = 0.0
        found: list[dict] = []
        for item, raw_by_store in zip(body.items, item_raw_by_store, strict=True):
            try:
                raw = raw_by_store.get(store)
                if not raw:
                    continue
                # Convert and filter: only keep products where every query word
                # appears as a complete word in the product name. The basket
                # auto-picks a single product per item, so one-token matching
                # silently selects cross-brand / cross-type products
                # (e.g. "leche evaporada gloria entera" → "Shake Capuccino UHT Gloria").
                q_tokens = _query_tokens(item["name"])
                # Category guard: when the query maps to a canasta staple, require
                # the candidate to map to the SAME staple. This rejects cross-category
                # false matches that token overlap can't (e.g. "aceite vegetal"
                # matching canned fish "en aceite vegetal"). None = no constraint.
                q_category = infer_category(item["name"])
                candidates: list[dict] = []
                for p in raw:
                    try:
                        prod = product_from_json(p, store)
                        name = prod.get("name", "")
                        if q_tokens and not _is_relevant(name, q_tokens, require_all=True):
                            continue
                        if q_category and infer_category(name) != q_category:
                            continue
                        candidates.append(prod)
                    except Exception:
                        continue
                if not candidates:
                    continue
                best_prod = min(
                    candidates,
                    key=lambda p: p["price"] if p["price"] > 0 else float("inf"),
                )
                q = item.get("qty", 1)
                t += best_prod["price"] * q
                found.append(
                    {
                        "name": best_prod["name"][:40],
                        "price": best_prod["price"],
                        "qty": q,
                        "subtotal": round(best_prod["price"] * q, 2),
                    }
                )
            except Exception:
                continue
        if found:
            store_profile = STORES.get(store) or get_store_profile(store) or {}
            results[store] = {
                "store_name": store_profile.get("name", store),
                "currency": store_profile.get("currency", "USD"),
                "items": found,
                "total": round(t, 2),
                "items_found": len(found),
                "items_requested": len(body.items),
            }
    def _total_usd(store_key: str) -> float:
        r = results[store_key]
        usd = price_to_usd(r["total"], r["currency"])
        return usd if usd is not None else r["total"]

    best = min(results, key=_total_usd) if results else None
    return {
        "source": "live",
        "basket": body.items,
        "comparison": results,
        "best_store": best,
        "best_total": results[best]["total"] if best else None,
        "best_total_usd": _total_usd(best) if best else None,
        "stores_compared": len(results),
    }


@router.get(
    "/products/stock/{product_id}",
    summary="Check latest stock snapshot for a product in a specific store",
)
def product_stock(product_id: str, store: str, authorization: str | None = Header(None)):
    """Returns the most recent stock status for a product in a specific store,
    drawn from the last collector run (every 4h). Pass product_id from a search
    result and the store key (e.g. 'wong', 'metro_pe'). Returns null stock if
    no snapshot exists yet."""
    require_api_key(authorization)
    db = get_db()
    row = db.execute(
        "SELECT stock, name, store_name FROM price_snapshots "
        "WHERE product_id=? AND store=? ORDER BY queried_at DESC LIMIT 1",
        (product_id, store),
    ).fetchone()
    db.close()
    if not row:
        return {"product_id": product_id, "store": store, "stock": None, "message": "No data"}
    return {
        "product_id": product_id,
        "store": store,
        "stock": row["stock"],
        "name": row["name"],
        "store_name": row["store_name"],
    }


@router.get(
    "/products/delivery/{product_id}",
    summary="Get delivery estimate for a product from a specific store",
)
def product_delivery(product_id: str, store: str, zipcode: str = ""):
    """Referential delivery estimate — VTEX defaults/simulation when available."""
    store_info = STORES.get(store, {})
    message = "Estimación referencial. Confirmar plazo, costo y cobertura con el retailer."
    fee = None
    source = None
    delivery_available = False
    estimated_days = "—"

    try:
        from market_core.market_tco import simulate_delivery_quote

        quote = simulate_delivery_quote(
            store,
            subtotal=0.0,
            product_id=product_id,
            zipcode=zipcode or None,
        )
        if quote.get("available"):
            delivery_available = True
            fee = quote.get("fee")
            source = quote.get("source") or "referential"
            estimated_days = "2-5"
    except Exception:
        pass

    return {
        "product_id": product_id,
        "store": store,
        "store_name": store_info.get("name", store),
        "delivery_available": delivery_available,
        "estimated_days": estimated_days,
        "fee": fee,
        "source": source,
        "referential": True,
        "message": message,
        "store_url": f"{store_info.get('base','')}/{product_id}/p",
    }


@router.get(
    "/products/barcode/{code}",
    summary="Look up product metadata by EAN/UPC barcode",
)
def barcode_lookup(code: str):
    """Look up product name, brand, and Nutri-Score from OpenFoodFacts by
    EAN or UPC barcode. Use when you have a physical barcode and want to
    identify the product before searching for prices."""
    r = httpx.get(f"https://world.openfoodfacts.org/api/v2/product/{code}.json", timeout=10)
    if r.status_code == 200:
        product = r.json().get("product", {})
        return {
            "code": code,
            "name": product.get("product_name", ""),
            "brand": product.get("brands", ""),
            "nutriscore": product.get("nutriscore_grade", "").upper(),
            "categories": product.get("categories", ""),
        }
    return {"code": code, "error": "not found"}


@router.get("/products/enrich")
def enrich_products(query: str, limit: int = 5):
    """OpenFoodFacts text search."""
    r = httpx.get(
        f"https://world.openfoodfacts.org/cgi/search.pl?search_terms={query}&json=1&page_size={limit}",
        timeout=10,
    )
    if r.status_code == 200:
        products = r.json().get("products", [])
        results = []
        for p in products:
            results.append(
                {
                    "name": p.get("product_name", ""),
                    "brand": p.get("brands", ""),
                    "nutriscore": p.get("nutriscore_grade", "").upper(),
                    "barcode": p.get("code", ""),
                }
            )
        return {"results": results, "total": r.json().get("count", 0)}
    return {"results": [], "total": 0}


@router.get("/categories/{store}")
async def categories(store: str):
    """VTEX category tree (depth 10) for a store."""
    base = STORES.get(store, {}).get("base", "")
    if not base:
        raise HTTPException(status_code=404, detail="Tienda no encontrada")
    url = f"{base}/api/catalog_system/pub/category/tree/10"
    async with httpx.AsyncClient(timeout=10.0) as client:
        resp = await client.get(url)
    try:
        return resp.json()
    except Exception:
        raise HTTPException(status_code=502, detail="Upstream returned non-JSON response")