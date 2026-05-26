"""Dashboard — read-only operational views over the data moat.

Endpoints:
  GET /dashboard         HTML single-page dashboard (Chart.js)
  GET /dashboard/data    JSON feed consumed by the dashboard
  GET /dashboard/usage   Per-user tier + usage (requires auth)

Note: /dashboard returns an embedded HTML string today. When the Next.js
landing in /landing absorbs this view, swap dashboard_html.DASHBOARD_HTML
for a 302 redirect to https://cli-market.dev/dashboard.
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Header
from fastapi.responses import HTMLResponse

from market_core import STORES, TIERS, db_get_subscription, get_db
from server_deps import require_user

from .dashboard_html import DASHBOARD_HTML
from .health import _age_hours

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def dashboard():
    return HTMLResponse(DASHBOARD_HTML)


@router.get("/dashboard/data")
def dashboard_data():
    """Aggregates feeding the dashboard charts and alerts."""
    db = get_db()
    by_line = db.execute(
        """
        SELECT line, line_name, COUNT(*) as count,
               ROUND(AVG(price), 2) as avg_price,
               ROUND(MIN(price), 2) as min_price,
               ROUND(MAX(price), 2) as max_price
        FROM price_snapshots WHERE price > 0 AND price < 999999
        GROUP BY line ORDER BY count DESC
        """
    ).fetchall()

    by_country = db.execute(
        """
        SELECT store, COUNT(*) as count
        FROM price_snapshots WHERE price > 0
        GROUP BY store ORDER BY count DESC
        """
    ).fetchall()

    # Derive country from STORES dict (we don't denormalize it into the table).
    country_agg: dict[str, dict] = {}
    for r in by_country:
        country = STORES.get(r["store"], {}).get("country", "??")
        c = country_agg.setdefault(
            country, {"country": country, "count": 0, "stores": set()}
        )
        c["count"] += r["count"]
        c["stores"].add(r["store"])
    by_country_list = sorted(
        [
            {"country": c["country"], "count": c["count"], "stores": len(c["stores"])}
            for c in country_agg.values()
        ],
        key=lambda x: x["count"],
        reverse=True,
    )

    top_products = db.execute(
        """
        SELECT name, store_name, price, currency, line_name, queried_at
        FROM price_snapshots WHERE price > 0 AND price < 999999
        ORDER BY queried_at DESC LIMIT 20
        """
    ).fetchall()

    total_runs = db.execute("SELECT COUNT(*) as n FROM collector_runs").fetchone()["n"]

    # Collector status
    last_run = db.execute(
        "SELECT started_at, finished_at, stores_succeeded, stores_attempted, prices_collected "
        "FROM collector_runs ORDER BY id DESC LIMIT 1"
    ).fetchone()
    collector_status = "unknown"
    if last_run:
        finished = last_run["finished_at"]
        if finished:
            age_h = _age_hours(finished)
            if age_h is not None:
                collector_status = (
                    "healthy" if age_h < 12 else ("stale" if age_h < 24 else "dead")
                )
        else:
            collector_status = "running"

    failing_stores = db.execute(
        "SELECT store, consecutive_failures FROM store_health "
        "WHERE consecutive_failures >= 3 ORDER BY consecutive_failures DESC"
    ).fetchall()

    now7 = (datetime.now(timezone.utc) - timedelta(days=7)).isoformat()
    prev14 = (datetime.now(timezone.utc) - timedelta(days=14)).isoformat()
    recent = db.execute(
        "SELECT COUNT(*) as n FROM price_snapshots WHERE queried_at >= ?", (now7,)
    ).fetchone()["n"]
    older = db.execute(
        "SELECT COUNT(*) as n FROM price_snapshots WHERE queried_at >= ? AND queried_at < ?",
        (prev14, now7),
    ).fetchone()["n"]

    db.close()
    return {
        "by_line": [dict(r) for r in by_line],
        "by_country": by_country_list,
        "top_products": [dict(r) for r in top_products],
        "total_runs": total_runs,
        "collector": {
            "status": collector_status,
            "last_run": last_run["started_at"] if last_run else None,
            "last_finished": last_run["finished_at"] if last_run else None,
            "stores_succeeded": last_run["stores_succeeded"] if last_run else 0,
            "prices_collected": last_run["prices_collected"] if last_run else 0,
        },
        "failing_stores": [dict(r) for r in failing_stores],
        "price_trend": {"recent_7d": recent, "previous_7d": older},
    }


@router.get("/dashboard/usage")
def dashboard_usage(authorization: str | None = Header(None)):
    """Per-user usage view — for the user's account page in the dashboard."""
    username = require_user(authorization)
    sub = db_get_subscription(username)
    tier = sub.get("tier", "free")
    limits = TIERS.get(tier, TIERS["free"])
    db = get_db()
    today_reqs = (
        db.execute(
            "SELECT SUM(counter) as n FROM rate_limits "
            "WHERE key LIKE ? AND window_start >= ?",
            ("%:daily", datetime.now(timezone.utc).strftime("%Y-%m-%d")),
        ).fetchone()["n"]
        or 0
    )
    keys = db.execute(
        "SELECT COUNT(*) as n FROM api_keys WHERE username=?", (username,)
    ).fetchone()["n"]
    db.close()
    return {
        "username": username,
        "tier": tier,
        "limits": {
            "req_min": limits["req_min"] or "unlimited",
            "req_day": limits["req_day"] or "unlimited",
            "checkout": limits["checkout"],
        },
        "usage": {"requests_today": today_reqs, "api_keys_used": keys},
    }
