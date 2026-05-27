"""Dashboard — read-only operational views over the data moat.

Endpoints:
  GET /dashboard         HTML single-page dashboard (Chart.js)
  GET /dashboard/data    JSON feed consumed by the dashboard
  GET /dashboard/usage   Per-user tier + usage (requires auth)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Header

from market_core import STORES, TIERS, db_get_subscription, get_db
from server_deps import require_user

from .dashboard_html import DASHBOARD_HTML
from .health import _age_hours

router = APIRouter(tags=["dashboard"])


@router.get("/dashboard")
def dashboard(static: bool = False):
    from fastapi.responses import HTMLResponse
    if static:
        return HTMLResponse(_static_dashboard())
    return HTMLResponse(DASHBOARD_HTML)


@router.get("/dashboard/data")
def dashboard_data():
    """Business-intelligence feed for the Data Moat dashboard."""
    try:
        return _dashboard_data()
    except Exception as e:
        import traceback
        return {"error": str(e), "trace": traceback.format_exc()[-400:]}


def _dashboard_data():
    db = get_db()
    now = datetime.now(timezone.utc)

    # ── KPIs ──────────────────────────────────────────────────────────────────
    total_snapshots = db.execute(
        "SELECT COUNT(*) as n FROM price_snapshots WHERE price > 0"
    ).fetchone()["n"]

    active_stores = db.execute(
        "SELECT COUNT(DISTINCT store) as n FROM price_snapshots WHERE price > 0"
    ).fetchone()["n"]

    total_runs = db.execute("SELECT COUNT(*) as n FROM collector_runs").fetchone()["n"]

    # ── By line ──────────────────────────────────────────────────────────────
    by_line = db.execute(
        """
        SELECT line, line_name,
               COUNT(*) as count,
               ROUND(AVG(price)::numeric, 2) as avg_price,
               ROUND(MIN(price)::numeric, 2) as min_price,
               ROUND(MAX(price)::numeric, 2) as max_price
        FROM price_snapshots WHERE price > 0 AND price < 999999
        GROUP BY line, line_name ORDER BY count DESC
        """
    ).fetchall()

    # ── By country ───────────────────────────────────────────────────────────
    by_country_raw = db.execute(
        "SELECT store, COUNT(*) as count FROM price_snapshots WHERE price > 0 GROUP BY store"
    ).fetchall()

    country_agg: dict[str, dict] = {}
    for r in by_country_raw:
        country = STORES.get(r["store"], {}).get("country", "??")
        c = country_agg.setdefault(country, {"country": country, "count": 0, "stores": set()})
        c["count"] += r["count"]
        c["stores"].add(r["store"])
    by_country = sorted(
        [{"country": c["country"], "count": c["count"], "stores": len(c["stores"])}
         for c in country_agg.values()],
        key=lambda x: x["count"], reverse=True,
    )

    # ── Dispersión por línea ─────────────────────────────────────────────────
    dispersion = []
    for row in by_line:
        if row["avg_price"] and row["avg_price"] > 0:
            spread = round((row["max_price"] - row["min_price"]) / row["avg_price"], 2)
        else:
            spread = 0
        dispersion.append({"line": row["line_name"] or row["line"],
                           "avg_price": row["avg_price"],
                           "spread_ratio": spread})

    # ── Top discounts ────────────────────────────────────────────────────────
    top_discounts = db.execute(
        """
        SELECT name, store_name, price, list_price,
               ROUND(((1 - price / NULLIF(list_price,0)) * 100)::numeric) as discount_pct,
               currency, line_name
        FROM price_snapshots
        WHERE list_price > price AND price > 0 AND list_price < 999999
        ORDER BY discount_pct DESC LIMIT 10
        """
    ).fetchall()

    # ── Cheapest store by line ───────────────────────────────────────────────
    cheapest_by_line = db.execute(
        """
        SELECT line_name, store_name, ROUND(AVG(price)::numeric,2) as avg_price, currency, COUNT(*) as n
        FROM price_snapshots WHERE price > 0 AND price < 999999
        GROUP BY line, line_name, store, store_name, currency ORDER BY line, avg_price ASC
        """
    ).fetchall()

    seen_lines: set[str] = set()
    cheapest_dedup: list[dict] = []
    for r in cheapest_by_line:
        ln = r["line_name"] or "?"
        if ln not in seen_lines:
            seen_lines.add(ln)
            cheapest_dedup.append(dict(r))

    # ── Coverage ─────────────────────────────────────────────────────────────
    cutoff_24h = (now - timedelta(hours=24)).isoformat()
    stores_24h = db.execute(
        "SELECT COUNT(DISTINCT store) as n FROM price_snapshots WHERE queried_at >= ?",
        (cutoff_24h,),
    ).fetchone()["n"]

    # ── Price trend 7d ───────────────────────────────────────────────────────
    now7 = (now - timedelta(days=7)).isoformat()
    now14 = (now - timedelta(days=14)).isoformat()

    recent_prices = db.execute(
        """SELECT product_id, store, price, queried_at
           FROM price_snapshots WHERE price > 0 AND queried_at >= ?""",
        (now7,)
    ).fetchall()

    older_prices = db.execute(
        """SELECT product_id, store, price, queried_at
           FROM price_snapshots WHERE price > 0 AND queried_at >= ? AND queried_at < ?""",
        (now14, now7)
    ).fetchall()

    recent_map: dict[tuple, dict] = {}
    for r in recent_prices:
        key = (r["product_id"], r["store"])
        if key not in recent_map or r["queried_at"] > recent_map[key]["queried_at"]:
            recent_map[key] = dict(r)

    older_map: dict[tuple, dict] = {}
    for r in older_prices:
        key = (r["product_id"], r["store"])
        if key not in older_map or r["queried_at"] > older_map[key]["queried_at"]:
            older_map[key] = dict(r)

    movers: list[dict] = []
    for key, recent in recent_map.items():
        older = older_map.get(key)
        if older and older["price"] > 0:
            delta_pct = round((recent["price"] - older["price"]) / older["price"] * 100, 1)
            movers.append({
                "product_id": recent["product_id"],
                "store": recent["store"],
                "price_before": older["price"],
                "price_now": recent["price"],
                "delta_pct": delta_pct,
            })

    top_risers = sorted([m for m in movers if m["delta_pct"] > 0],
                        key=lambda x: x["delta_pct"], reverse=True)[:5]
    top_fallers = sorted([m for m in movers if m["delta_pct"] < 0],
                         key=lambda x: x["delta_pct"])[:5]

    # ── Collector status ─────────────────────────────────────────────────────
    last_run = db.execute(
        "SELECT started_at, finished_at, stores_succeeded, stores_attempted, prices_collected "
        "FROM collector_runs ORDER BY id DESC LIMIT 1"
    ).fetchone()

    collector_status = "unknown"
    collector_age_h = None
    if last_run:
        finished = last_run["finished_at"]
        if finished:
            collector_age_h = _age_hours(finished)
            if collector_age_h is not None:
                collector_status = ("healthy" if collector_age_h < 12
                                    else ("stale" if collector_age_h < 24 else "dead"))
        else:
            collector_status = "running"

    failing_stores = db.execute(
        "SELECT store, consecutive_failures FROM store_health "
        "WHERE consecutive_failures >= 3 ORDER BY consecutive_failures DESC"
    ).fetchall()

    # ── Freshness ────────────────────────────────────────────────────────────
    freshness = db.execute(
        """SELECT store, store_name, MAX(queried_at) as last_seen
           FROM price_snapshots WHERE price > 0
           GROUP BY store, store_name ORDER BY last_seen DESC LIMIT 20"""
    ).fetchall()

    # ── Operacional: store health scores ─────────────────────────────────────
    store_health = db.execute(
        """SELECT store, total_requests, total_successes,
                  CASE WHEN total_requests>0 THEN ROUND((total_successes*100.0/total_requests)::numeric,1) ELSE 0 END as success_pct,
                  consecutive_failures, last_success, last_error
           FROM store_health ORDER BY success_pct ASC, consecutive_failures DESC"""
    ).fetchall()

    # ── Operacional: collector run history ───────────────────────────────────
    collector_history = db.execute(
        """SELECT started_at, finished_at, stores_attempted, stores_succeeded,
                  prices_collected, errors
           FROM collector_runs ORDER BY id DESC LIMIT 10"""
    ).fetchall()

    # ── Exploratoria: price distribution ─────────────────────────────────────
    price_dist = db.execute(
        """SELECT
             CASE WHEN price<=10 THEN '0-10'
                  WHEN price<=50 THEN '10-50'
                  WHEN price<=100 THEN '50-100'
                  WHEN price<=500 THEN '100-500'
                  ELSE '500+'
             END as bucket,
             COUNT(*) as count
           FROM price_snapshots WHERE price>0 AND price<999999
           GROUP BY bucket ORDER BY MIN(price)"""
    ).fetchall()

    # ── Exploratoria: line-country matrix ────────────────────────────────────
    line_country_raw = db.execute(
        """SELECT ps.line, ps.store, COUNT(*) as n
           FROM price_snapshots ps WHERE ps.price>0
           GROUP BY ps.line, ps.store"""
    ).fetchall()
    line_country_map: dict[str, set] = {}
    for r in line_country_raw:
        country = STORES.get(r["store"], {}).get("country", "??")
        key = f"{r['line']}|{country}"
        line_country_map.setdefault(key, set()).add(r["store"])
    line_country_matrix = [{"line": k.split("|")[0], "country": k.split("|")[1], "stores": len(v)}
                           for k, v in line_country_map.items()]

    # ── Exploratoria: products per store ─────────────────────────────────────
    products_per_store = db.execute(
        """SELECT store_name, store, COUNT(DISTINCT product_id) as unique_products,
                  COUNT(*) as total_snapshots
           FROM price_snapshots WHERE price>0
           GROUP BY store, store_name ORDER BY unique_products DESC LIMIT 15"""
    ).fetchall()

    # ── Weak signal: outliers (price > 3× line average) ──────────────────────
    outliers = []
    for row in by_line:
        if row["count"] < 5:
            continue
        threshold = row["avg_price"] * 3
        try:
            anoms = db.execute(
                """SELECT name, store_name, price, currency, line_name
                   FROM price_snapshots WHERE line=? AND price>0 AND price>?
                   ORDER BY price DESC LIMIT 5""",
                (row["line"], threshold)
            ).fetchall()
            for a in anoms:
                outliers.append(dict(a))
        except Exception:
            pass
    outliers = outliers[:10]

    db.close()

    return {
        "generated_at": now.isoformat(),
        "kpis": {
            "total_snapshots": total_snapshots,
            "active_stores": active_stores,
            "total_stores": len(STORES),
            "total_runs": total_runs,
            "stores_24h": stores_24h,
        },
        "by_line": [dict(r) for r in by_line],
        "by_country": by_country,
        "dispersion": dispersion,
        "top_discounts": [dict(r) for r in top_discounts],
        "cheapest_by_line": cheapest_dedup,
        "top_risers": top_risers,
        "top_fallers": top_fallers,
        "collector": {
            "status": collector_status,
            "age_hours": round(collector_age_h, 1) if collector_age_h else None,
            "last_run": last_run["started_at"] if last_run else None,
            "last_finished": last_run["finished_at"] if last_run else None,
            "stores_succeeded": last_run["stores_succeeded"] if last_run else 0,
            "prices_collected": last_run["prices_collected"] if last_run else 0,
        },
        "failing_stores": [dict(r) for r in failing_stores],
        "freshness": [dict(r) for r in freshness],
        # ── Operacional ──────────────────────────────────────────────────────
        "store_health": [dict(r) for r in store_health],
        "collector_history": [dict(r) for r in collector_history],
        # ── Exploratoria ─────────────────────────────────────────────────────
        "price_distribution": [dict(r) for r in price_dist],
        "line_country_matrix": line_country_matrix,
        "products_per_store": [dict(r) for r in products_per_store],
        # ── Weak signal ──────────────────────────────────────────────────────
        "outliers": outliers,
    }


def _static_dashboard() -> str:
    """Server-rendered fallback dashboard — no JavaScript required."""
    data = _dashboard_data()
    if "error" in data:
        return f"<html><body style='background:#0a0a0a;color:#ff4444;font:12px monospace;padding:20px'><pre>{data['error']}\n{data.get('trace','')}</pre></body></html>"
    
    k = data["kpis"]
    rows = []
    rows.append(f"<tr><td>Precios</td><td style='color:#3cffd0'>{k['total_snapshots']:,}</td></tr>")
    rows.append(f"<tr><td>Tiendas</td><td style='color:#3cffd0'>{k['active_stores']}/{k['total_stores']}</td></tr>")
    rows.append(f"<tr><td>Países</td><td style='color:#3cffd0'>{len(data['by_country'])}</td></tr>")
    rows.append(f"<tr><td>Ciclos</td><td style='color:#3cffd0'>{k['total_runs']}</td></tr>")
    rows.append(f"<tr><td>24h activas</td><td style='color:#3cffd0'>{k['stores_24h']}</td></tr>")
    
    lines_html = "".join(f"<tr><td>{r['line_name']}</td><td style='color:#3cffd0'>{r['count']:,}</td><td>{r['avg_price']:.2f}</td><td>{r['min_price']:.2f}</td><td>{r['max_price']:.2f}</td></tr>" for r in data["by_line"])
    disc_html = "".join(f"<tr><td>{r['name'][:40]}</td><td>{r['store_name']}</td><td style='color:#3cffd0'>-{r['discount_pct']}%</td></tr>" for r in data["top_discounts"])
    cheap_html = "".join(f"<tr><td>{r['line_name']}</td><td>{r['store_name']}</td><td style='color:#3cffd0'>{r['avg_price']:.2f}</td></tr>" for r in data["cheapest_by_line"])
    out_html = "".join(f"<tr><td>{r['name'][:35]}</td><td>{r['store_name']}</td><td style='color:#ff4444'>{r['price']:.2f}</td></tr>" for r in data["outliers"])
    fresh_html = "".join(f"<tr><td>{r['store_name']}</td><td>{r['last_seen'][:19]}</td></tr>" for r in data["freshness"][:10])
    coll = data["collector"]
    
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>CLI Market // Data Moat</title>
<style>
body{{background:#0a0a0a;color:#b0b0b0;font:12px 'JetBrains Mono',monospace;padding:12px 16px}}
h1{{color:#3cffd0;font-size:14px;margin:0 0 4px}}
.sub{{color:#444;font-size:10px;margin:0 0 16px}}
table{{border-collapse:collapse;width:100%;max-width:800px;margin-bottom:16px}}
th{{text-align:left;color:#444;font-size:10px;text-transform:uppercase;padding:4px 8px;border-bottom:1px solid #1a1a1a}}
td{{padding:3px 8px;border-bottom:1px solid #111;font-size:11px}}
td.num{{text-align:right}}
.section{{color:#3cffd0;font-size:11px;margin:16px 0 6px;text-transform:uppercase;letter-spacing:2px}}
.footer{{color:#333;font-size:9px;margin-top:20px;border-top:1px solid #1a1a1a;padding-top:8px}}
</style></head><body>
<h1>CLI Market Data Moat</h1>
<p class="sub">Server-rendered · PostgreSQL · {coll['status']} · {coll['prices_collected']:,} prices · {coll['stores_succeeded']} stores · {data['generated_at'][:19]}</p>

<div class="section">[ KPIs ]</div>
<table><tr><th>Metric</th><th>Value</th></tr>{''.join(rows)}</table>

<div class="section">[ PRECIOS POR LÍNEA ]</div>
<table><tr><th>Línea</th><th>Precios</th><th>Avg</th><th>Min</th><th>Max</th></tr>{lines_html}</table>

<div class="section">[ TIENDA MÁS BARATA POR LÍNEA ]</div>
<table><tr><th>Línea</th><th>Tienda</th><th>Avg</th></tr>{cheap_html}</table>

<div class="section">[ TOP DESCUENTOS ]</div>
<table><tr><th>Producto</th><th>Tienda</th><th>Desc</th></tr>{disc_html}</table>

<div class="section">[ OUTLIERS ]</div>
<table><tr><th>Producto</th><th>Tienda</th><th>Precio</th></tr>{out_html}</table>

<div class="section">[ FRESCURA ]</div>
<table><tr><th>Tienda</th><th>Último snapshot</th></tr>{fresh_html}</table>

<p class="footer">actualizado {data['generated_at'][:19]} · CLI Market Data Moat · auto-refresh 5min</p>
</body></html>"""
    return html


@router.get("/dashboard/usage")
def dashboard_usage(authorization: str | None = Header(None)):
    """Per-user usage view."""
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
        ).fetchone()["n"] or 0
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
