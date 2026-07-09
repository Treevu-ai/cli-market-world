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
import unicodedata

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
from server_deps import require_api_key

from backend_interface import get_store_profile, store_exists
from index_gate import infer_category

logger = logging.getLogger("market.server").getChild("search")

router = APIRouter(tags=["search"])


# ── Relevance filter ────────────────────────────────────────────────────

def _normalize_text(text: str) -> str:
    """Lowercase, strip accents (panó → pano), keep alphanum+spaces."""
    text = text.lower()
    text = unicodedata.normalize("NFD", text)
    text = "".join(c for c in text if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9\s]", " ", text)


def _word_set(text: str) -> frozenset[str]:
    return frozenset(w for w in _normalize_text(text).split() if len(w) >= 2)


def _query_tokens(query: str) -> list[str]:
    """Normalized tokens from the user query (min 2 chars)."""
    return [w for w in _normalize_text(query).split() if len(w) >= 2]


def _is_relevant(product_name: str, q_tokens: list[str], *, require_all: bool = False) -> bool:
    """True if the query tokens appear as complete words in the product name.

    Matching is word-boundary based to prevent prefix false-positives: query
    'pan' should not match 'pantalon' because 'pan' is not a standalone word there.

    require_all=False (default): at least one token must match. Used where the
    caller sees the full result list and picks themselves.
    require_all=True: every token must match. Used by the basket auto-picker, which
    selects a single product per item with no human in the loop; one-token matching
    there silently picks cross-brand / cross-type products (e.g. query
    'leche evaporada gloria entera' matching 'Shake Capuccino UHT Gloria').
    """
    if not q_tokens:
        return True
    name_words = _word_set(product_name)
    if require_all:
        return all(qt in name_words for qt in q_tokens)
    return any(qt in name_words for qt in q_tokens)


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
        stores = [s for s in stores if STORES.get(s, {}).get("country") == cc]
    return stores


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
    from market_core.market_db import name_like_clause

    stores = _resolve_search_stores(body)
    q_tokens = _query_tokens(body.query)
    if not stores or not q_tokens:
        save_search_query(body.query, body.line, body.store, 0)
        return {"query": body.query, "results": [], "total": 0}

    like = name_like_clause()
    like_clause = " OR ".join(like for _ in q_tokens)
    store_placeholders = ",".join("?" for _ in stores)
    candidate_cap = min(500, body.limit * 20)

    db = get_db()
    try:
        rows = db.execute(
            f"""
            SELECT product_id, name, brand, price, list_price, discount, store,
                   store_name, currency, line, line_name, category, stock, url, confidence
            FROM price_snapshots
            WHERE price > 0 AND store IN ({store_placeholders}) AND ({like_clause})
            ORDER BY price ASC
            LIMIT ?
            """,
            (*stores, *[f"%{t}%" for t in q_tokens], candidate_cap),
        ).fetchall()
    finally:
        db.close()

    results: list[dict] = []
    for r in rows:
        row = dict(r)
        if not _is_relevant(row.get("name", ""), q_tokens):
            continue
        row["id"] = row.pop("product_id")
        results.append(row)

    results.sort(key=lambda p: p["price"] if p["price"] > 0 else float("inf"))
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
                prod["line"] = STORES[store]["line"]
                prod["line_name"] = LINES[STORES[store]["line"]]["name"]
                results.append(prod)
            except Exception as pe:
                errors.append({"store": store, "product_id": str(p)[:80], "error": str(pe)})

    results.sort(key=lambda p: p["price"] if p["price"] > 0 else float("inf"))
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
    return f"{p.get('brand', '').lower()}|{name}"


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

    comparison: list[dict] = []
    for _k, sp in key_index.items():
        if len(sp) >= 1:
            prices = {s: p["price"] for s, p in sp.items() if p["price"] > 0}
            if prices:
                best = min(prices, key=prices.get)
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
    comparison.sort(key=lambda x: x["best_price"])
    return comparison


async def _compare_products(body: SearchRequest) -> dict:
    if body.live:
        return await _compare_products_live(body)
    return _compare_products_db(body)


def _compare_products_db(body: SearchRequest) -> dict:
    """DB-backed compare: reads collector-refreshed price_snapshots instead
    of live-scraping every store per request — same rationale and pattern
    as _search_products_db."""
    from market_core.market_db import name_like_clause

    stores = _resolve_search_stores(body)
    q_tokens = _query_tokens(body.query)
    payload: dict = {"query": body.query, "comparison": [], "stores_compared": 0}
    if body.country:
        payload["country"] = body.country.strip().upper()
    if not stores or not q_tokens:
        return payload

    like = name_like_clause()
    like_clause = " OR ".join(like for _ in q_tokens)
    store_placeholders = ",".join("?" for _ in stores)
    candidate_cap = min(500, body.limit * 20)

    db = get_db()
    try:
        rows = db.execute(
            f"""
            SELECT product_id, name, brand, price, store
            FROM price_snapshots
            WHERE price > 0 AND store IN ({store_placeholders}) AND ({like_clause})
            ORDER BY price ASC
            LIMIT ?
            """,
            (*stores, *[f"%{t}%" for t in q_tokens], candidate_cap),
        ).fetchall()
    finally:
        db.close()

    all_products: dict[str, list[dict]] = {}
    for r in rows:
        row = dict(r)
        if not _is_relevant(row.get("name", ""), q_tokens):
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
    stores = body.stores or list(STORES.keys())
    stores = [s for s in stores if s in STORES]
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
            results[store] = {
                "store_name": STORES[store]["name"],
                "currency": STORES[store]["currency"],
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