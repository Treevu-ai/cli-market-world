"""Dashboard — read-only operational views over the data moat.

Endpoints:
  GET /dashboard         HTML single-page dashboard (Chart.js)
  GET /dashboard/data    JSON feed consumed by the dashboard
  GET /dashboard/usage   Per-user tier + usage (requires auth)
"""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Header

from market_core import STORES, TIERS, DEFAULT_STORES, db_get_subscription, get_db, price_to_usd
from market_spread import build_spread_analytics
from dashboard_glossary import (
    LAYER_METRICS,
    build_metric_glossary,
    metric_description,
    metric_label,
    section_summary,
    section_title,
)
from server_deps import require_user

from .health import _age_hours

router = APIRouter(tags=["dashboard"])


def _build_moat_guide(
    *,
    total_indexed: int,
    unique_products: int,
    stores_indexed: int,
    snapshots_24h: int,
    stores_fresh_24h: int,
    coverage_7d_pct: float,
    fresh_24h_pct: float,
    moat_age_h: float | None,
    collector_status: str,
    collector_age_h: float | None,
    last_collected_at,
    last_run,
    catalog_stores: int,
    marketing_gate_pass: bool,
    stale_stores: list[str],
) -> dict:
    """Human-readable layers so agents and humans share one mental model."""
    last_ts = str(last_collected_at)[:19] if last_collected_at else None
    freshness_label = "fresh"
    if moat_age_h is None:
        freshness_label = "unknown"
    elif moat_age_h >= 24:
        freshness_label = "stale"
    elif moat_age_h >= 8:
        freshness_label = "aging"

    return {
        "headline": "Data Moat = inventario verificado + señales de mercado",
        "mental_model": [
            "Inventario: cuántos precios tenemos guardados en total (como un archivo histórico).",
            "Frescura: cuántos de esos precios se actualizaron en las últimas 24 h (¿sirven para decidir hoy?).",
            "Cobertura 7 días: de las tiendas que monitoreamos, ¿cuántas respondieron al menos una vez esta semana?",
            "Collector: robot que visita las tiendas cada pocas horas; si falla, el archivo sigue existiendo pero envejece.",
        ],
        "layers": [
            {
                "id": "inventory",
                "title": "1 · Inventario",
                "question": "¿Cuánto tenemos acumulado?",
                "metrics": {
                    "total_indexed": total_indexed,
                    "unique_products": unique_products,
                    "stores_indexed": stores_indexed,
                },
                "metric_help": LAYER_METRICS["inventory"],
                "note": "Stock de precios reales ya leídos de las webs de las tiendas. Sigue disponible aunque el collector esté en pausa.",
            },
            {
                "id": "freshness",
                "title": "2 · Frescura",
                "question": "¿Puedo confiar en el precio de hoy?",
                "metrics": {
                    "snapshots_24h": snapshots_24h,
                    "stores_fresh_24h": stores_fresh_24h,
                    "fresh_24h_pct": fresh_24h_pct,
                    "moat_age_hours": round(moat_age_h, 1) if moat_age_h is not None else None,
                    "last_collected_at": last_ts,
                    "status": freshness_label,
                },
                "metric_help": LAYER_METRICS["freshness"],
                "note": "Si «actualizaciones 24 h» es 0 pero hay inventario, los números son viejos — conviene esperar un refresh.",
            },
            {
                "id": "coverage",
                "title": "3 · Cobertura",
                "question": "¿Qué tan completo está el catálogo activo?",
                "metrics": {
                    "stores_active_catalog": catalog_stores,
                    "coverage_7d_pct": coverage_7d_pct,
                    "marketing_gate_pct": 80,
                    "marketing_gate_pass": marketing_gate_pass,
                    "stale_stores_sample": stale_stores,
                },
                "metric_help": LAYER_METRICS["coverage"],
                "note": "Meta interna: al menos 80 % de tiendas con datos en 7 días antes de campañas públicas.",
            },
            {
                "id": "agents",
                "title": "4 · Para agentes",
                "question": "¿Qué puedo hacer con esto?",
                "surfaces": [
                    {"cmd": "market compare <producto>", "use": "Buscar el precio más bajo del mismo producto en varias tiendas"},
                    {"cmd": "market basket", "use": "Calcular cuánto cuesta la canasta básica en cada tienda"},
                    {"cmd": "GET /v1/intel/inflation?days=7", "use": "Ver si los precios subieron o bajaron en la última semana"},
                    {"cmd": "GET /dashboard/data", "use": "Descargar todos los KPIs y explicaciones en JSON"},
                ],
            },
            {
                "id": "ops",
                "title": "5 · Collector (ops)",
                "question": "¿El pipeline de ingestión está sano?",
                "metrics": {
                    "collector_status": collector_status,
                    "collector_age_hours": round(collector_age_h, 1) if collector_age_h is not None else None,
                    "last_prices_collected": last_run["prices_collected"] if last_run else 0,
                    "last_stores_succeeded": last_run["stores_succeeded"] if last_run else 0,
                },
                "metric_help": LAYER_METRICS["ops"],
                "note": "Distinto de frescura: una corrida puede terminar con 0 precios si una tienda bloqueó el acceso.",
            },
        ],
    }


@router.get("/dashboard")
def dashboard():
    from fastapi.responses import HTMLResponse
    try:
        html = _static_dashboard()
    except Exception as e:
        import traceback
        html = f"<pre>STATIC DASHBOARD CRASH:\n{e}\n\n{traceback.format_exc()}</pre>"
    return HTMLResponse(html)


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
    cutoff_24h_sql = "datetime('now', '-24 hours')"

    # ── KPIs: moat size vs 24h refresh (distinct metrics) ─────────────────────
    total_indexed = db.execute(
        "SELECT COUNT(*) as n FROM price_snapshots WHERE price > 0 AND price < 999999"
    ).fetchone()["n"]

    unique_products = db.execute(
        "SELECT COUNT(DISTINCT product_id || store) as n FROM price_snapshots WHERE price > 0"
    ).fetchone()["n"]

    stores_indexed = db.execute(
        "SELECT COUNT(DISTINCT store) as n FROM price_snapshots WHERE price > 0"
    ).fetchone()["n"]

    last_collected_row = db.execute(
        "SELECT MAX(queried_at) as ts FROM price_snapshots WHERE price > 0"
    ).fetchone()
    last_collected_at = last_collected_row["ts"] if last_collected_row else None
    moat_age_h = _age_hours(last_collected_at) if last_collected_at else None

    snapshots_24h = db.execute(
        "SELECT COUNT(*) as n FROM price_snapshots WHERE price > 0 AND queried_at >= "
        + cutoff_24h_sql
    ).fetchone()["n"]

    active_stores_24h = db.execute(
        "SELECT COUNT(DISTINCT store) as n FROM price_snapshots WHERE price > 0 AND queried_at >= "
        + cutoff_24h_sql
    ).fetchone()["n"]

    total_runs = db.execute("SELECT COUNT(*) as n FROM collector_runs").fetchone()["n"]

    # ── By line ──────────────────────────────────────────────────────────────
    by_line = db.execute(
        """
        SELECT line, line_name,
               COUNT(DISTINCT product_id||store) as count,
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

    # ── Dispersión por subcategoría + moneda (+ precio unitario cuando aplica) ─
    spread_rows = db.execute(
        """
        SELECT line, line_name, currency, category, name, brand, price, store, store_name
        FROM price_snapshots WHERE price > 0 AND price < 999999
        """
    ).fetchall()
    spread_analytics = build_spread_analytics([dict(r) for r in spread_rows])
    dispersion = spread_analytics["dispersion"]
    canasta_spreads = spread_analytics["canasta_spreads"]
    marketing_spreads = spread_analytics["marketing_spreads"]
    for d in dispersion:
        d["avg_price_usd"] = price_to_usd(d.get("avg_price", 0), d.get("currency", ""))

    by_line_currency = db.execute(
        """
        SELECT line, line_name, currency,
               COUNT(DISTINCT product_id||store) as count,
               ROUND(AVG(price)::numeric, 2) as avg_price,
               ROUND(MIN(price)::numeric, 2) as min_price,
               ROUND(MAX(price)::numeric, 2) as max_price
        FROM price_snapshots WHERE price > 0 AND price < 999999
        GROUP BY line, line_name, currency ORDER BY line, currency
        """
    ).fetchall()

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
    stores_24h = active_stores_24h

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
    failing_stores = [r for r in failing_stores if r["store"] in DEFAULT_STORES]

    # ── Freshness ────────────────────────────────────────────────────────────
    freshness = db.execute(
        """SELECT store, store_name, MAX(queried_at) as last_seen
           FROM price_snapshots WHERE price > 0
           GROUP BY store, store_name ORDER BY last_seen DESC LIMIT 20"""
    ).fetchall()

    # ── Operacional: store health scores (active catalog only) ───────────────
    store_health_all = db.execute(
        """SELECT store, total_requests, total_successes,
                  CASE WHEN total_requests>0 THEN ROUND((total_successes*100.0/total_requests)::numeric,1) ELSE 0 END as success_pct,
                  consecutive_failures, last_success, last_error
           FROM store_health ORDER BY success_pct ASC, consecutive_failures DESC"""
    ).fetchall()
    store_health = [{k: r[k] for k in r.keys()} for r in store_health_all if r["store"] in DEFAULT_STORES]
    healthy_count = sum(1 for h in store_health if float(h.get("success_pct") or 0) >= 80)

    # ── Moat summary (agent-facing, rolling windows) ─────────────────────────
    cutoff_7d = (now - timedelta(days=7)).isoformat()
    stores_fresh_24h_rows = db.execute(
        """SELECT store, MAX(queried_at) as last_seen, COUNT(*) as n
           FROM price_snapshots WHERE price > 0 AND queried_at >= """
        + cutoff_24h_sql
        + " GROUP BY store"
    ).fetchall()
    stores_fresh_24h = {r["store"] for r in stores_fresh_24h_rows if r["store"] in DEFAULT_STORES}
    stores_active_7d_rows = db.execute(
        """SELECT store, COUNT(*) as n FROM price_snapshots
           WHERE price > 0 AND queried_at >= ? GROUP BY store""",
        (cutoff_7d,),
    ).fetchall()
    stores_active_7d = {r["store"] for r in stores_active_7d_rows if r["store"] in DEFAULT_STORES}
    coverage_7d_pct = round(len(stores_active_7d) / len(DEFAULT_STORES) * 100, 1) if DEFAULT_STORES else 0
    fresh_24h_pct = round(len(stores_fresh_24h) / len(DEFAULT_STORES) * 100, 1) if DEFAULT_STORES else 0
    moat_stale = sorted(
        s for s in DEFAULT_STORES
        if s not in stores_fresh_24h
    )[:10]

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

    # ── Weak signal: outliers (>3× avg within spread group) ─────────────────
    outliers = []
    for row in dispersion:
        if row["count"] < 5:
            continue
        threshold = float(row["avg_price"] or 0) * 3
        if threshold <= 0:
            continue
        sub = row.get("subcategory")
        params: list = [row["line_key"], row["currency"], threshold]
        sub_sql = ""
        if sub and sub != "otros" and not str(sub).startswith("cat:"):
            sub_sql = " AND name LIKE ?"
            params.insert(2, f"%{sub}%")
        anoms = db.execute(
            f"""SELECT name, store_name, price, currency, line_name
               FROM price_snapshots
               WHERE line=? AND currency=?{sub_sql} AND price>0 AND price>?
               ORDER BY price DESC LIMIT 5""",
            tuple(params),
        ).fetchall()
        for a in anoms:
            item = dict(a)
            item["price_usd"] = price_to_usd(item.get("price", 0), item.get("currency", ""))
            outliers.append(item)
    outliers = outliers[:10]

    # ── Inflation 7d: per line + currency (nominal + USD-normalized) ────────
    inflation = []
    for row in by_line_currency:
        recent_avg = db.execute(
            """SELECT ROUND(AVG(price)::numeric,2) as avg_price
               FROM price_snapshots
               WHERE line=? AND currency=? AND price>0 AND price<999999 AND queried_at >= ?""",
            (row["line"], row["currency"], now7),
        ).fetchone()
        older_avg = db.execute(
            """SELECT ROUND(AVG(price)::numeric,2) as avg_price
               FROM price_snapshots
               WHERE line=? AND currency=? AND price>0 AND price<999999
                 AND queried_at >= ? AND queried_at < ?""",
            (row["line"], row["currency"], now14, now7),
        ).fetchone()
        r_avg = float(recent_avg["avg_price"] or 0) if recent_avg else 0.0
        o_avg = float(older_avg["avg_price"] or 0) if older_avg else 0.0
        delta = round((r_avg - o_avg) / o_avg * 100, 1) if o_avg > 0 else 0
        cur = row["currency"] or ""
        inflation.append({
            "line": row["line_name"] or row["line"],
            "line_key": row["line"],
            "currency": cur,
            "avg_now": r_avg,
            "avg_before": o_avg,
            "delta_pct": delta,
            "avg_now_usd": price_to_usd(r_avg, cur),
            "avg_before_usd": price_to_usd(o_avg, cur),
        })

    # ── Canasta basica: fixed 10 products compared across top stores ─────────
    canasta_products = ["leche", "arroz", "aceite", "azucar", "huevos", "pan", "cafe", "pollo", "queso", "jabon"]
    canasta: dict[str, dict] = {}
    for prod in canasta_products:
        rows = db.execute(
            """SELECT store_name, store, MIN(price) as best_price, currency
               FROM price_snapshots WHERE price>0 AND price<999999 AND name LIKE ?
               GROUP BY store_name, store, currency ORDER BY best_price ASC""",
            (f"%{prod}%",)
        ).fetchall()
        for r in rows:
            s = r["store_name"]
            canasta.setdefault(s, {"store_name": s, "items": 0, "total": 0, "currency": r["currency"]})
            canasta[s]["items"] += 1
            canasta[s]["total"] = round(canasta[s]["total"] + r["best_price"], 2)
    canasta_basica = sorted([v for v in canasta.values() if v["items"] >= 3],
                            key=lambda x: x["total"])[:10]

    db.close()

    moat_guide = _build_moat_guide(
        total_indexed=total_indexed,
        unique_products=unique_products,
        stores_indexed=stores_indexed,
        snapshots_24h=snapshots_24h,
        stores_fresh_24h=len(stores_fresh_24h),
        coverage_7d_pct=coverage_7d_pct,
        fresh_24h_pct=fresh_24h_pct,
        moat_age_h=moat_age_h,
        collector_status=collector_status,
        collector_age_h=collector_age_h,
        last_collected_at=last_collected_at,
        last_run=last_run,
        catalog_stores=len(DEFAULT_STORES),
        marketing_gate_pass=coverage_7d_pct >= 80,
        stale_stores=moat_stale,
    )

    return {
        "generated_at": now.isoformat(),
        "kpis": {
            "total_indexed": total_indexed,
            "unique_products": unique_products,
            "stores_indexed": stores_indexed,
            "total_snapshots": snapshots_24h,
            "snapshots_24h": snapshots_24h,
            "active_stores": active_stores_24h,
            "active_stores_24h": active_stores_24h,
            "total_stores": len(DEFAULT_STORES),
            "catalog_stores": len(STORES),
            "healthy_stores": healthy_count,
            "store_success_pct": round(healthy_count / len(DEFAULT_STORES) * 100, 1) if DEFAULT_STORES else 0,
            "coverage_7d_pct": coverage_7d_pct,
            "stores_fresh_24h": len(stores_fresh_24h),
            "fresh_24h_pct": fresh_24h_pct,
            "total_runs": total_runs,
            "stores_24h": stores_24h,
            "last_collected_at": str(last_collected_at) if last_collected_at else None,
            "moat_age_hours": round(moat_age_h, 1) if moat_age_h is not None else None,
        },
        "moat_summary": {
            "purpose": "Verified cross-retailer prices for agent compare, basket, and inflation signals.",
            "refresh_hours": 8,
            "total_indexed": total_indexed,
            "unique_products": unique_products,
            "stores_indexed": stores_indexed,
            "snapshots_24h": snapshots_24h,
            "last_collected_at": str(last_collected_at) if last_collected_at else None,
            "moat_age_hours": round(moat_age_h, 1) if moat_age_h is not None else None,
            "collector_stale": moat_age_h is not None and moat_age_h >= 24,
            "stores_active_catalog": len(DEFAULT_STORES),
            "stores_fresh_24h": len(stores_fresh_24h),
            "stores_active_7d": len(stores_active_7d),
            "coverage_7d_pct": coverage_7d_pct,
            "fresh_24h_pct": fresh_24h_pct,
            "marketing_gate_pct": 80,
            "marketing_gate_pass": coverage_7d_pct >= 80,
            "stale_stores": moat_stale,
            "agent_surfaces": ["market compare", "market basket", "/v1/intel/inflation", "MCP market_stats"],
        },
        "moat_guide": moat_guide,
        "metric_glossary": build_metric_glossary(),
        "by_line": [dict(r) for r in by_line],
        "by_country": by_country,
        "dispersion": dispersion,
        "canasta_spreads": canasta_spreads,
        "marketing_spreads": marketing_spreads,
        "analytics_meta": {
            "fx_reference": "USD",
            "fx_source": "static_pen_table",
            "dispersion_grouping": "line+currency+subcategory",
            "dispersion_crit_count": spread_analytics["dispersion_crit_count"],
            "marketing_crit_count": spread_analytics["marketing_crit_count"],
            "marketing_canasta_min_spread": spread_analytics.get("marketing_canasta_min_spread"),
        },
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
        # ── Analytics ────────────────────────────────────────────────────────
        "inflation": inflation,
        "canasta_basica": canasta_basica,
    }


def _static_dashboard() -> str:
    """Server-rendered fallback dashboard — no JavaScript required."""
    try:
        data = _dashboard_data()
    except Exception as e:
        import traceback
        return f"<pre>ERROR: {e}\n{traceback.format_exc()}</pre>"
    if "error" in data:
        return f"<html><body style='background:#0a0a0a;color:#ff4444;font:12px monospace;padding:20px'><pre>{data['error']}\n{data.get('trace','')}</pre></body></html>"

    def sec(section_id: str, title: str | None = None) -> str:
        t = title or section_title(section_id, section_id)
        summary = section_summary(section_id)
        intro = f'<p class="section-intro">{summary}</p>' if summary else ""
        return f'<div class="section">[ {t.upper()} ]</div>{intro}'

    def metric_cell(layer_id: str, key: str) -> str:
        label = metric_label(layer_id, key, key)
        desc = metric_description(layer_id, key)
        if desc:
            return f'<span class="metric-label">{label}</span><br><span class="metric-desc">{desc}</span>'
        return f'<span class="metric-label">{label}</span>'

    glossary = data.get("metric_glossary", {})
    status_legend = glossary.get("status_legend", {})
    legend_html = "".join(
        f"<li><b>{k}</b> — {v}</li>" for k, v in status_legend.items()
    )
    
    k = data["kpis"]
    m = data.get("moat_summary", {})
    g = data.get("moat_guide", {})
    indexed = k.get("total_indexed", k.get("total_snapshots", 0))
    snap_24 = k.get("snapshots_24h", k.get("total_snapshots", 0))
    stores_with_data = k.get("stores_indexed", k.get("active_stores", 0))
    cov_pct = round(stores_with_data / max(k["total_stores"], 1) * 100)
    cov_bar = "█" * (cov_pct // 5) + "░" * (20 - cov_pct // 5)
    stale_note = ""
    if m.get("collector_stale"):
        stale_note = f" · ⚠️ moat sin refresh reciente ({k.get('moat_age_hours', '?')}h)"
    elif snap_24 == 0 and indexed > 0:
        stale_note = " · ⚠️ inventario histórico — refresh 24h en cero"

    guide_html = ""
    for layer in g.get("layers", []):
        layer_id = layer.get("id", "")
        metrics = layer.get("metrics") or {}
        mrows = "".join(
            f"<tr><td>{metric_cell(layer_id, mk)}</td><td style='color:#3cffd0'>{mv}</td></tr>"
            for mk, mv in metrics.items()
        )
        surfaces = layer.get("surfaces") or []
        srows = "".join(
            f"<tr><td><code>{s['cmd']}</code></td><td>{s['use']}</td></tr>" for s in surfaces
        )
        guide_html += f"""<div class="section">{layer.get('title', layer.get('id', ''))}</div>
<p class="layer-q">{layer.get('question', '')}</p>
{f"<table><tr><th>Métrica</th><th>Valor</th></tr>{mrows}</table>" if mrows else ""}
{f"<table><tr><th>Comando / API</th><th>Para qué sirve</th></tr>{srows}</table>" if srows else ""}
<p class="layer-note">{layer.get('note', '')}</p>"""

    mental = "".join(f"<li>{x}</li>" for x in g.get("mental_model", []))
    header_intro = section_summary("header")
    
    lines_html = "".join(f"<tr><td>{r['line_name']}</td><td style='color:#3cffd0'>{r['count']:,}</td><td>{(r['avg_price'] or 0):.2f}</td><td>{(r['min_price'] or 0):.2f}</td><td>{(r['max_price'] or 0):.2f}</td></tr>" for r in data["by_line"])
    disc_html = "".join(f"<tr><td>{r['name'][:40]}</td><td>{r['store_name']}</td><td style='color:#3cffd0'>-{r.get('discount_pct',0) or 0}%</td></tr>" for r in data["top_discounts"])
    cheap_html = "".join(f"<tr><td>{r['line_name']}</td><td>{r['store_name']}</td><td style='color:#3cffd0'>{(r['avg_price'] or 0):.2f}</td></tr>" for r in data["cheapest_by_line"])
    out_html = "".join(f"<tr><td>{r['name'][:35]}</td><td>{r['store_name']}</td><td style='color:#ff4444'>{(r['price'] or 0):.2f}</td></tr>" for r in data["outliers"])
    fresh_html = "".join(f"<tr><td>{r['store_name']}</td><td>{str(r['last_seen'])[:19]}</td></tr>" for r in data["freshness"][:10])

    # ── New analytics HTML ──────────────────────────────────────────────────
    infl_html = "".join(
        f"<tr><td>{r['line']}</td><td>{r.get('currency','')}</td>"
        f"<td style='color:var(--green)'>{(r['avg_now'] or 0):.2f}</td>"
        f"<td>{(r['avg_before'] or 0):.2f}</td>"
        f"<td style='color:{'#ff4444' if r['delta_pct']>0 else '#3cffd0'}'>"
        f"{'+' if r['delta_pct']>0 else ''}{r['delta_pct']}%</td></tr>"
        for r in data["inflation"])

    disp_html = "".join(
        f"<tr><td>{r['line']}</td><td>{r.get('subcategory') or '—'}</td><td>{r.get('currency','')}</td>"
        f"<td>{r.get('price_basis','nominal')}</td>"
        f"<td>{(r['avg_price'] or 0):.2f}</td>"
        f"<td style='color:{'#ff4444' if r.get('status')=='crit' else ('#ffbd2e' if r.get('status')=='warn' else '#3cffd0')}'>"
        f"{(r['spread_ratio'] or 0):.1f}x"
        f"{' CRIT' if r.get('status')=='crit' else ''}</td></tr>"
        for r in data["dispersion"][:25])

    canasta_spread_html = "".join(
        f"<tr><td>{r['item']}</td><td>{r.get('currency','')}</td><td>{r.get('stores',0)}</td>"
        f"<td>{(r['spread_ratio'] or 0):.1f}x</td><td>{r.get('sample_name','')[:40]}</td></tr>"
        for r in data.get("canasta_spreads", [])[:15])

    mkt_html = "".join(
        f"<tr><td>{r['seed']}</td><td>{r.get('currency','')}</td><td>{r.get('price_basis','')}</td>"
        f"<td>{(r['spread_ratio'] or 0):.1f}x</td><td>{r.get('stores',0)} tiendas</td>"
        f"<td>{r.get('sample_name','')[:40]}</td></tr>"
        for r in data.get("marketing_spreads", [])[:10])
    
    riser_html = "".join(
        f"<tr><td>{r['product_id'][:25]}</td><td>{(r['price_before'] or 0):.2f}</td><td>{(r['price_now'] or 0):.2f}</td><td style='color:#ff4444'>+{r['delta_pct']}%</td></tr>"
        for r in data["top_risers"][:5])
    faller_html = "".join(
        f"<tr><td>{r['product_id'][:25]}</td><td>{(r['price_before'] or 0):.2f}</td><td>{(r['price_now'] or 0):.2f}</td><td style='color:#3cffd0'>{r['delta_pct']}%</td></tr>"
        for r in data["top_fallers"][:5])
    
    health_html = "".join(
        f"<tr><td>{r['store']}</td><td style='color:{'#3cffd0' if r['success_pct']>=90 else ('#ffbd2e' if r['success_pct']>=50 else '#ff4444')}'>{r['success_pct']}%</td><td>{r['consecutive_failures']}</td></tr>"
        for r in data["store_health"][:10])
    
    matrix_html = ""
    gaps = []
    if data["line_country_matrix"]:
        lines = list(dict.fromkeys(r["line"] for r in data["line_country_matrix"]))
        countries = sorted(set(r["country"] for r in data["line_country_matrix"]))
        lookup = {f"{r['line']}|{r['country']}": r["stores"] for r in data["line_country_matrix"]}
        matrix_html = "<table><tr><th></th>" + "".join(f"<th>{c}</th>" for c in countries) + "</tr>"
        for l in lines:
            matrix_html += f"<tr><td>{l}</td>"
            for c in countries:
                v = lookup.get(f"{l}|{c}", 0)
                if v == 0:
                    gaps.append(f"{l}x{c}")
                matrix_html += f"<td style='color:{'#3cffd0' if v>0 else '#333'}'>{v or '·'}</td>"
            matrix_html += "</tr>"
        matrix_html += "</table>"
    gaps_html = f"<p class='metric-desc'>Sin cobertura aún: {', '.join(gaps[:15])}</p>" if gaps else ""
    
    canasta_html = "".join(
        f"<tr><td>{r['store_name']}</td><td>{r['items']}/10</td><td style='color:#3cffd0'>{r['currency']} {r['total']:.2f}</td></tr>"
        for r in data["canasta_basica"])

    am = data.get("analytics_meta", {})
    meta_html = f"""<div class="help-box">
<b>Resumen analítico:</b> {am.get('dispersion_crit_count', 0)} grupos con brecha crítica (&gt;10x) ·
{am.get('marketing_crit_count', 0)} listos para copy (canasta ≥{am.get('marketing_canasta_min_spread', '?')}x) ·
agrupación: {am.get('dispersion_grouping', '—')}
</div>"""
    
    html = f"""<!DOCTYPE html>
<html><head><meta charset="UTF-8"><title>CLI Market // Data Moat</title>
<style>
body{{background:#0a0a0a;color:#b0b0b0;font:12px 'JetBrains Mono',monospace;padding:12px 16px}}
h1{{color:#3cffd0;font-size:14px;margin:0 0 4px}}
.sub{{color:#444;font-size:10px;margin:0 0 16px}}
table{{border-collapse:collapse;width:100%;max-width:800px;margin-bottom:16px}}
th{{text-align:left;color:#444;font-size:10px;text-transform:uppercase;padding:4px 8px;border-bottom:1px solid #1a1a1a}}
td{{padding:3px 8px;border-bottom:1px solid #111;font-size:11px;vertical-align:top}}
td.num{{text-align:right}}
.section{{color:#3cffd0;font-size:11px;margin:16px 0 6px;text-transform:uppercase;letter-spacing:2px}}
.section-intro{{color:#777;font-size:11px;line-height:1.55;margin:0 0 10px;max-width:720px}}
.layer-q{{color:#888;font-size:11px;margin:0 0 8px}}
.layer-note{{color:#555;font-size:10px;margin:0 0 12px;font-style:italic;max-width:720px;line-height:1.45}}
.metric-label{{color:#ccc;font-size:11px}}
.metric-desc{{color:#555;font-size:10px;line-height:1.4}}
.help-box{{background:#111;border:1px solid #1a1a1a;border-radius:4px;padding:10px 12px;margin:0 0 14px;max-width:720px;font-size:10px;color:#666;line-height:1.5}}
.coverage{{font:10px monospace;margin:8px 0;color:#555}}
.footer{{color:#333;font-size:9px;margin-top:20px;border-top:1px solid #1a1a1a;padding-top:8px}}
ul.glossary{{color:#666;font-size:10px;line-height:1.55;margin:0 0 16px 18px;max-width:720px}}
</style></head><body>
<h1>CLI Market · Data Moat</h1>
<p class="sub">{g.get('headline', 'Monitor de precios')} · <b>{indexed:,}</b> {metric_label('inventory', 'total_indexed', 'indexados')} · <b>{snap_24:,}</b> refresh 24h · {stores_with_data}/{k['total_stores']} tiendas{stale_note} · {data['generated_at'][:10]} {data['generated_at'][11:16]} UTC</p>
<p class="section-intro">{header_intro}</p>
<p class="coverage">Cobertura catálogo: {cov_pct}% {cov_bar}</p>

{sec('mental_model', 'Qué es el data moat')}
<ul style="color:#888;font-size:11px;line-height:1.6;margin:0 0 16px 18px;max-width:720px">{mental or '<li>Moat = precios verificados de muchas tiendas en un solo lugar</li>'}</ul>

<div class="section">[ GUÍA POR CAPAS ]</div>
<p class="section-intro">Cinco capas para entender el moat sin jerga financiera. Cada fila explica qué significa el número.</p>
{guide_html}

<div class="section">[ LEYENDA DE ESTADOS ]</div>
<ul class="glossary">{legend_html}</ul>

<div class="section">[ DETALLE ANALÍTICO ]</div>
<p class="section-intro">Exploración de precios por categoría, ofertas, cambios semanales y diferencias entre tiendas. Complementa — no reemplaza — inventario y frescura.</p>
{meta_html}

{sec('store_health')}
<table><tr><th>Tienda</th><th>{metric_label('store_health', 'success_pct', 'Éxito')}</th><th>{metric_label('store_health', 'consecutive_failures', 'Fallos')}</th><th>Estado</th></tr>{"".join(f"<tr><td>{h['store']}</td><td style='color:{'#3cffd0' if (h.get('success_pct',0) or 0)>=90 else ('#ffbd2e' if (h.get('success_pct',0) or 0)>=30 else '#ff4444')}'>{(h.get('success_pct',0) or 0):.0f}%</td><td>{h.get('consecutive_failures',0) or 0}</td><td style='color:{'#3cffd0' if (h.get('success_pct',0) or 0)>=90 else ('#ffbd2e' if (h.get('success_pct',0) or 0)>=30 else '#ff4444')}'>{'OK' if (h.get('success_pct',0) or 0)>=90 else ('WARN' if (h.get('success_pct',0) or 0)>=30 else 'DEAD')}</td></tr>" for h in data.get("store_health",[])[:15]) or '<tr><td colspan=4>sin datos</td></tr>'}</table>

{sec('by_line')}
<table><tr><th>Categoría</th><th>{metric_label('by_line', 'count', 'Precios')}</th><th>{metric_label('by_line', 'avg_price', 'Promedio')}</th><th>{metric_label('by_line', 'min_price', 'Mín')}</th><th>{metric_label('by_line', 'max_price', 'Máx')}</th></tr>{lines_html}</table>

{sec('cheapest_by_line')}
<table><tr><th>Categoría</th><th>Tienda más barata</th><th>Precio promedio</th></tr>{cheap_html}</table>

{sec('top_discounts')}
<table><tr><th>Producto</th><th>Tienda</th><th>{metric_label('top_discounts', 'discount_pct', 'Descuento')}</th></tr>{disc_html}</table>

{sec('outliers')}
<table><tr><th>Producto</th><th>Tienda</th><th>Precio</th></tr>{out_html}</table>

{sec('inflation')}
<table><tr><th>Categoría</th><th>Moneda</th><th>{metric_label('inflation', 'avg_now', 'Hoy')}</th><th>{metric_label('inflation', 'avg_before', 'Hace 7d')}</th><th>{metric_label('inflation', 'delta_pct', 'Cambio')}</th></tr>{infl_html or '<tr><td colspan=5>Sin historial de 7 días aún — se activará cuando tengamos lecturas en fechas distintas.</td></tr>'}</table>

{sec('dispersion')}
<table><tr><th>Categoría</th><th>{metric_label('dispersion', 'subcategory', 'Subcat')}</th><th>Moneda</th><th>{metric_label('dispersion', 'price_basis', 'Base')}</th><th>Promedio</th><th>{metric_label('dispersion', 'spread_ratio', 'Brecha')}</th></tr>{disp_html or '<tr><td colspan=6>sin datos</td></tr>'}</table>

{sec('canasta_spreads')}
<table><tr><th>Ítem</th><th>Moneda</th><th>Tiendas</th><th>Brecha</th><th>Ejemplo</th></tr>{canasta_spread_html or '<tr><td colspan=5>sin datos</td></tr>'}</table>

{sec('marketing_spreads')}
<table><tr><th>Ítem</th><th>Moneda</th><th>Base</th><th>{metric_label('marketing_spreads', 'spread_ratio', 'Brecha')}</th><th>{metric_label('marketing_spreads', 'stores', 'Tiendas')}</th><th>Ejemplo</th></tr>{mkt_html or '<tr><td colspan=6>Ninguna brecha supera el umbral verificado todavía</td></tr>'}</table>

{sec('canasta_basica', 'Canasta básica — completitud')}
<table><tr><th>Tienda</th><th>{metric_label('canasta_basica', 'items', 'Encontrados')}</th><th>%</th><th>{metric_label('canasta_basica', 'total', 'Total')}</th></tr>{"".join(f"<tr><td>{c['store_name']}</td><td style='color:{'#3cffd0' if c['items']>=7 else ('#ffbd2e' if c['items']>=4 else '#ff4444')}'>{'█'*(c['items'])+'░'*(10-c['items'])}</td><td>{c['items']*10}%</td><td>{c['currency']} {c['total']:.2f}</td></tr>" for c in data.get("canasta_basica",[])) or '<tr><td colspan=4>sin datos</td></tr>'}</table>

<div class="section">[ ALERTAS DE CALIDAD ]</div>
<p class="section-intro">Descuentos de 90 % o más suelen ser errores al leer la web (precio tachado mal interpretado), no ofertas reales.</p>
{"".join(f"<p style='color:#ff4444;font-size:10px'>⚠ {d['name'][:40]} ({d['store_name']}) -{abs(d.get('discount_pct',0) or 0)}%</p>" for d in data.get("top_discounts",[]) if abs(d.get("discount_pct",0) or 0)>=90) or '<p class="metric-desc">sin descuentos sospechosos</p>'}

<div class="section">[ CONFIABILIDAD DEL RECOLECTOR ]</div>
<p class="section-intro">Historial de éxito al leer cada tienda (distinto del estado operativo de arriba — aquí miramos más intentos).</p>
<table><tr><th>Tienda</th><th>Éxito</th><th>Fallos seguidos</th></tr>{health_html or '<tr><td colspan=3>sin datos</td></tr>'}</table>

{sec('line_country_matrix')}
{matrix_html or '<p class="metric-desc">sin datos</p>'}
{gaps_html}

{sec('canasta_basica')}
<table><tr><th>Tienda</th><th>Productos / 10</th><th>Total estimado</th></tr>{canasta_html or '<tr><td colspan=3>sin datos</td></tr>'}</table>

{sec('price_movers')}
<table><tr><th colspan=4 style="color:#ff4444">▲ SUBIERON</th></tr>{riser_html or '<tr><td colspan=4>Sin datos — se necesitan dos capturas en días distintos.</td></tr>'}</table>
<table><tr><th colspan=4 style="color:#3cffd0">▼ BAJARON</th></tr>{faller_html or '<tr><td colspan=4></td></tr>'}</table>

{sec('freshness_table', 'Frescura por tienda')}
<table><tr><th>Tienda</th><th>Último precio guardado</th></tr>{fresh_html}</table>

<p class="footer">Ultima actualizacion: {data['generated_at'][:10]} a las {data['generated_at'][11:16]} UTC · Glosario completo en GET /dashboard/data → metric_glossary · CLI Market · cli-market.dev</p>
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
