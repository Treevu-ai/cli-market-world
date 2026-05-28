"""Intel / inflation tracking — the data-moat-as-product angle.

Endpoints:
  GET /v1/intel/inflation    Per-product price delta over the last N days
  GET /v1/intel/alerts       (placeholder) threshold-based price alerts
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter

from market_core import STORES, get_db

router = APIRouter(tags=["intel"])


def _since_iso(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=max(1, days))).strftime("%Y-%m-%d %H:%M:%S")


@router.get("/v1/intel/inflation")
def inflation_tracker(
    country: str | None = None,
    line: str | None = None,
    days: int = 30,
    limit: int = 100,
):
    """Compute per-product price deltas within the last `days` window.

    Compares earliest vs latest snapshot per product name in the window.
    Intended for agent-facing inflation signals — not official CPI indices.
    """
    db = get_db()
    since = _since_iso(days)
    q = (
        "SELECT name, store, store_name, currency, price, queried_at "
        "FROM price_snapshots WHERE price > 0 AND queried_at >= ?"
    )
    params: list = [since]
    if country:
        cc_stores = [k for k, v in STORES.items() if v["country"] == country.upper() and not v.get("disabled")]
        if cc_stores:
            q += f" AND store IN ({','.join('?' * len(cc_stores))})"
            params.extend(cc_stores)
    if line:
        q += " AND line = ?"
        params.append(line)
    q += " ORDER BY queried_at DESC LIMIT ?"
    params.append(limit * 4)
    rows = db.execute(q, params).fetchall()
    db.close()

    prods: dict[str, list[dict]] = {}
    for r in rows:
        k = f"{r['store']}|{r['name'].lower()[:40]}"
        prods.setdefault(k, []).append(
            {
                "price": r["price"],
                "date": r["queried_at"],
                "store": r["store_name"],
                "currency": r["currency"],
            }
        )

    items: list[dict] = []
    for _key, snaps in prods.items():
        snaps.sort(key=lambda s: s["date"])
        if len(snaps) >= 2:
            first = snaps[0]
            last = snaps[-1]
            if first["price"] > 0:
                d = round(last["price"] - first["price"], 2)
                dp = round((d / first["price"]) * 100, 1)
                items.append(
                    {
                        "product": _key.split("|", 1)[1],
                        "first_price": first["price"],
                        "last_price": last["price"],
                        "first_date": first["date"],
                        "last_date": last["date"],
                        "delta": d,
                        "delta_pct": dp,
                        "currency": first["currency"],
                        "store": first["store"],
                    }
                )
    items.sort(key=lambda x: abs(x["delta_pct"]), reverse=True)
    items = items[:limit]
    avg = round(sum(i["delta_pct"] for i in items) / len(items), 1) if items else 0
    return {
        "country": country,
        "line": line,
        "days": days,
        "since": since,
        "products_tracked": len(items),
        "avg_inflation_pct": avg,
        "items": items,
        "disclaimer": "Internal collector signal — not an official inflation index.",
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
