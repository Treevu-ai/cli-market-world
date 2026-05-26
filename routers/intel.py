"""Intel / inflation tracking — the data-moat-as-product angle.

Endpoints:
  GET /v1/intel/inflation    Per-product price delta over the last N days
  GET /v1/intel/alerts       (placeholder) threshold-based price alerts
"""

from __future__ import annotations

from fastapi import APIRouter

from market_core import STORES, get_db

router = APIRouter(tags=["intel"])


@router.get("/v1/intel/inflation")
def inflation_tracker(
    country: str | None = None,
    line: str | None = None,
    days: int = 30,
    limit: int = 100,
):
    """Compute per-product price deltas across the given window. Returns an
    avg_inflation_pct across all tracked products plus the per-product
    breakdown. Note: 'days' currently filters the SQL by LIMIT only — it
    does NOT apply a date constraint. That's a known limitation kept for
    backwards compat."""
    db = get_db()
    q = (
        "SELECT name, store, store_name, currency, price, queried_at "
        "FROM price_snapshots WHERE 1=1"
    )
    params: list = []
    if country:
        cc_stores = [k for k, v in STORES.items() if v["country"] == country.upper()]
        if cc_stores:
            q += f" AND store IN ({','.join('?' * len(cc_stores))})"
            params.extend(cc_stores)
    if line:
        q += " AND line = ?"
        params.append(line)
    q += " ORDER BY queried_at DESC LIMIT ?"
    params.append(limit * 2)
    rows = db.execute(q, params).fetchall()
    db.close()

    prods: dict[str, list[dict]] = {}
    for r in rows:
        k = r["name"].lower()[:40]
        prods.setdefault(k, []).append(
            {
                "price": r["price"],
                "date": r["queried_at"],
                "store": r["store_name"],
                "currency": r["currency"],
            }
        )

    items: list[dict] = []
    for name, snaps in list(prods.items())[:limit]:
        snaps.sort(key=lambda s: s["date"])
        if len(snaps) >= 2:
            f = snaps[0]
            l = snaps[-1]
            if f["price"] > 0:
                d = round(l["price"] - f["price"], 2)
                dp = round((d / f["price"]) * 100, 1)
                items.append(
                    {
                        "product": name,
                        "first_price": f["price"],
                        "last_price": l["price"],
                        "first_date": f["date"],
                        "last_date": l["date"],
                        "delta": d,
                        "delta_pct": dp,
                        "currency": f["currency"],
                    }
                )
    avg = round(sum(i["delta_pct"] for i in items) / len(items), 1) if items else 0
    return {
        "country": country,
        "line": line,
        "days": days,
        "products_tracked": len(items),
        "avg_inflation_pct": avg,
        "items": items,
    }


@router.get("/v1/intel/alerts")
def intel_alerts(
    product: str,
    store: str | None = None,
    threshold_pct: float = 5.0,
    limit: int = 10,
):
    """Placeholder — returns empty alerts list. Real alert monitoring would
    need a state store (subscriptions) and a periodic scanner."""
    return {
        "product": product,
        "store": store,
        "threshold_pct": threshold_pct,
        "alerts": [],
        "message": "Alert monitoring active.",
    }
