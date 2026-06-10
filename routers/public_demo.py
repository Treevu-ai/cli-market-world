"""Public demo flows for landing and `market demo` (no account).

Endpoints:
  POST /public/demo/session          Issue short-lived demo token (search/compare only)
  GET  /public/demo/compare?q=arroz  Whitelisted queries, 1h cache, IP rate limited.
"""

from __future__ import annotations

import asyncio
import logging
import os
import time
from datetime import datetime, timezone

from fastapi import APIRouter, Header, HTTPException, Request
from pydantic import BaseModel

from routers.search import SearchRequest, _compare_products
from server_deps import check_rate_limit

logger = logging.getLogger("market.server").getChild("public_demo")

router = APIRouter(prefix="/public", tags=["public"])

DEMO_QUERIES = frozenset({"arroz", "leche"})
CACHE_TTL = int(os.getenv("PUBLIC_DEMO_CACHE_TTL", "3600"))

_cache: dict[str, dict] = {}
_refresh_lock = asyncio.Lock()

# Last-known-good fallback if refresh fails (served as stale, not live).
_SEED: dict[str, dict] = {
    "arroz": {
        "query": "arroz",
        "comparison": [
            {
                "name": "Arroz Extra FARAON Bolsa 750g",
                "brand": "FARAON",
                "prices": {"plazavea": 3.9},
                "best_store": "plazavea",
                "best_price": 3.9,
            }
        ],
        "stores_compared": 38,
    },
    "leche": {
        "query": "leche",
        "comparison": [
            {
                "name": "Leche Gloria Entera Bolsa 900ml",
                "brand": "Gloria",
                "prices": {"plazavea": 4.5, "wong_pe": 4.9},
                "best_store": "plazavea",
                "best_price": 4.5,
            }
        ],
        "stores_compared": 38,
    },
}


def _wrap_payload(data: dict, *, cached_at: float | None, stale: bool, seed: bool) -> dict:
    out = dict(data)
    out["demo"] = True
    out["stale"] = stale
    out["seed"] = seed
    if cached_at is not None:
        out["cached_at"] = datetime.fromtimestamp(cached_at, tz=timezone.utc).isoformat()
    return out


async def _refresh_query(query: str) -> dict:
    body = SearchRequest(query=query, limit=5)
    return await _compare_products(body)


class DemoSessionRequest(BaseModel):
    fingerprint: str = ""


@router.post("/demo/session")
def create_demo_session(
    request: Request,
    body: DemoSessionRequest | None = None,
    x_demo_fingerprint: str | None = Header(None, alias="X-Demo-Fingerprint"),
):
    """Mint a temporary demo token — search/compare only, no checkout."""
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(f"demo-session:{client_ip}")
    from market_core.demo_tokens import issue_demo_token

    fp = (x_demo_fingerprint or (body.fingerprint if body else "") or "").strip()
    session = issue_demo_token(client_ip=client_ip, fingerprint=fp)
    try:
        from market_funnel import record_funnel_event

        record_funnel_event(
            "demo_session_created",
            session_id=session.get("session_id"),
            meta={"agent_source": "demo"},
        )
    except Exception:
        pass
    return {"ok": True, **session}


@router.get("/demo/compare")
async def public_demo_compare(request: Request, q: str = "arroz"):
    """Cached compare for landing hero — whitelisted queries only."""
    client_ip = request.client.host if request.client else "unknown"
    check_rate_limit(f"public-demo:{client_ip}")

    query = q.strip().lower()[:50]
    if query not in DEMO_QUERIES:
        raise HTTPException(
            status_code=400,
            detail=f"Demo query must be one of: {sorted(DEMO_QUERIES)}",
        )

    now = time.time()
    entry = _cache.get(query)
    if entry and now - entry["ts"] < CACHE_TTL:
        return _wrap_payload(entry["data"], cached_at=entry["ts"], stale=False, seed=False)

    async with _refresh_lock:
        entry = _cache.get(query)
        if entry and now - entry["ts"] < CACHE_TTL:
            return _wrap_payload(entry["data"], cached_at=entry["ts"], stale=False, seed=False)

        try:
            data = await _refresh_query(query)
            if data.get("comparison"):
                _cache[query] = {"data": data, "ts": time.time()}
                return _wrap_payload(data, cached_at=_cache[query]["ts"], stale=False, seed=False)
        except Exception:
            logger.exception("public_demo refresh failed for %s", query)

        if entry:
            return _wrap_payload(entry["data"], cached_at=entry["ts"], stale=True, seed=False)

        seed = _SEED.get(query)
        if seed:
            return _wrap_payload(seed, cached_at=None, stale=True, seed=True)

        raise HTTPException(status_code=503, detail="Demo compare temporarily unavailable")
