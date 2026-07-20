#!/usr/bin/env python3
"""
Price Volatility Report — P4: análisis de elasticidad y volatilidad de precios.

Identifica qué productos y categorías tienen mayor spread de precios entre retailers,
detecta outliers de precio, y rankea retailers por consistencia de datos.
Alimenta el Price Pulse newsletter y prioriza qué integraciones de retailer mejorar.

Métricas por producto:
  CV (coeficiente de variación) = std / mean — volatilidad relativa entre retailers
  Spread pct = (max - min) / min * 100 — diferencia máx/mín en %
  Outlier flag — si algún retailer está > 2 std del promedio del producto

Métricas por retailer:
  Data consistency score — % de productos sin precio outlier extremo
  Coverage rank — cuántos productos únicos indexa vs total del moat

Uso:
  python ops/price_volatility_report.py              # reporte consola
  python ops/price_volatility_report.py --slack      # resumen Slack
  python ops/price_volatility_report.py --json       # JSON puro
  python ops/price_volatility_report.py --top 20     # top N productos más volátiles
  python ops/price_volatility_report.py --country PE # filtrar por país
"""
from __future__ import annotations

import argparse
import json
import math
import os
import sys
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "ops"))

try:
    from load_env import load_repo_env
    load_repo_env()
except Exception:
    pass

try:
    import httpx
    _HAS_HTTPX = True
except ImportError:
    _HAS_HTTPX = False

API_BASE = os.getenv("MARKET_API_URL", "https://cli-market-api.fly.dev")


# ---------------------------------------------------------------------------
# Fetch helpers
# ---------------------------------------------------------------------------

def _fetch_json(
    url: str,
    *,
    method: str = "GET",
    body: dict | None = None,
    params: dict | None = None,
    timeout: int = 45,
) -> dict | list | None:
    token = os.getenv("MARKET_API_TOKEN", "").strip()
    headers = {"Authorization": f"Bearer {token}"} if token else {}
    headers["Content-Type"] = "application/json"
    try:
        if _HAS_HTTPX:
            if method == "POST":
                r = httpx.post(url, headers=headers, json=body or {}, timeout=timeout)
            else:
                r = httpx.get(url, headers=headers, params=params, timeout=timeout)
            r.raise_for_status()
            return r.json()
        import urllib.parse as _urlparse
        import urllib.request as _urllib
        full_url = f"{url}?{_urlparse.urlencode(params)}" if params else url
        data = json.dumps(body or {}).encode() if method == "POST" else None
        req = _urllib.Request(full_url, headers=headers, data=data, method=method)
        with _urllib.urlopen(req, timeout=timeout) as resp:
            return json.loads(resp.read())
    except Exception as e:
        print(f"[volatility] fetch error {url}: {e}", file=sys.stderr)
        return None


def _fetch_trending(country: str = "PE", limit: int = 50) -> list[dict]:
    # country/limit passed via params (not f-string interpolation) so caller-supplied
    # values (e.g. from the public /v1/intel/price-volatility endpoint) can't inject
    # extra query parameters into this internal request.
    result = _fetch_json(f"{API_BASE}/analytics/trending", params={"country": country, "limit": limit})
    if isinstance(result, list):
        return result
    if isinstance(result, dict):
        return result.get("trending", result.get("products", result.get("items", [])))
    return []


def _fetch_basket(item_names: list[str], country: str = "PE") -> dict | None:
    """POST /v1/basket/compare expects {"items": [{"name": ...}]}, not product ids —
    build_basket_compare() resolves items by name against price_snapshots."""
    if not item_names:
        return None
    return _fetch_json(
        f"{API_BASE}/v1/basket/compare",
        method="POST",
        body={"items": [{"name": name} for name in item_names[:30]], "country": country},
    )


def _fetch_dashboard() -> dict:
    return _fetch_json(f"{API_BASE}/dashboard/data") or {}


# ---------------------------------------------------------------------------
# Statistics helpers (no numpy dependency)
# ---------------------------------------------------------------------------

def _mean(values: list[float]) -> float | None:
    return sum(values) / len(values) if values else None


def _std(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    m = sum(values) / len(values)
    variance = sum((v - m) ** 2 for v in values) / (len(values) - 1)
    return math.sqrt(variance)


def _cv(values: list[float]) -> float | None:
    m = _mean(values)
    s = _std(values)
    if m is None or s is None or m == 0:
        return None
    return round(s / m * 100, 1)


def _spread_pct(values: list[float]) -> float | None:
    if len(values) < 2:
        return None
    return round((max(values) - min(values)) / min(values) * 100, 1)


def _outlier_retailers(prices_by_store: dict[str, float]) -> list[str]:
    """Retailers whose price is > 2 std from the group mean."""
    vals = list(prices_by_store.values())
    m = _mean(vals)
    s = _std(vals)
    if m is None or s is None or s == 0:
        return []
    return [store for store, p in prices_by_store.items() if abs(p - m) > 2 * s]


# ---------------------------------------------------------------------------
# Analysis
# ---------------------------------------------------------------------------

def _extract_prices_from_basket(basket: dict) -> list[dict]:
    """Extract per-item cross-store price lists from a basket/compare response.

    build_basket_compare() groups its response by STORE
    (stores: [{store_name, breakdown: [{item, unit_price, ...}]}]), not by item —
    this inverts that into per-item prices_by_store dicts for volatility analysis.
    breakdown entries don't carry category/line, so category is always "unknown"
    here (honest limitation, not a bug — no category data exists at this layer)."""
    by_item: dict[str, dict[str, float]] = defaultdict(dict)
    product_id_by_item: dict[str, str | None] = {}

    for store_row in basket.get("stores", []):
        store_name = store_row.get("store_name") or store_row.get("store")
        if not store_name:
            continue
        for entry in store_row.get("breakdown") or []:
            item_name = entry.get("item")
            price = entry.get("unit_price")
            if not item_name or not price or float(price) <= 0:
                continue
            by_item[item_name][str(store_name)] = float(price)
            if entry.get("product_id"):
                product_id_by_item[item_name] = entry["product_id"]

    products_out = []
    for name, prices_by_store in by_item.items():
        if len(prices_by_store) < 2:
            continue

        vals = list(prices_by_store.values())
        products_out.append({
            "product_id": product_id_by_item.get(name),
            "name": name,
            "category": "unknown",
            "prices_by_store": prices_by_store,
            "n_stores": len(prices_by_store),
            "mean_price": round(_mean(vals), 2),
            "min_price": round(min(vals), 2),
            "max_price": round(max(vals), 2),
            "cv_pct": _cv(vals),
            "spread_pct": _spread_pct(vals),
            "outlier_retailers": _outlier_retailers(prices_by_store),
        })
    return products_out


def _retailer_stats(products: list[dict]) -> dict[str, dict]:
    stats: dict[str, dict] = defaultdict(lambda: {"products": 0, "outlier_count": 0, "prices": []})
    for p in products:
        for store, price in p["prices_by_store"].items():
            stats[store]["products"] += 1
            stats[store]["prices"].append(price)
            if store in p["outlier_retailers"]:
                stats[store]["outlier_count"] += 1

    result = {}
    for store, s in stats.items():
        n = s["products"]
        result[store] = {
            "products_indexed": n,
            "outlier_prices": s["outlier_count"],
            "outlier_rate_pct": round(s["outlier_count"] / n * 100, 1) if n > 0 else 0,
            "consistency_score": round((1 - s["outlier_count"] / n) * 100, 1) if n > 0 else 100,
            "mean_price": round(_mean(s["prices"]), 2) if s["prices"] else None,
        }
    return dict(sorted(result.items(), key=lambda x: -x[1]["consistency_score"]))


def build_report(*, country: str = "PE", top_n: int = 20) -> dict[str, Any]:
    now = datetime.now(timezone.utc)

    # Fetch trending products for the country
    trending = _fetch_trending(country=country, limit=50)
    item_names = [p.get("name") for p in trending if p.get("name")]

    # Fetch basket comparison to get multi-retailer prices
    basket = _fetch_basket(item_names, country=country) if item_names else None

    products: list[dict] = []
    if basket:
        products = _extract_prices_from_basket(basket)

    # Fallback: use dashboard moat data to estimate coverage
    dashboard = _fetch_dashboard()
    moat = dashboard.get("moat_summary", {})
    total_prices = moat.get("total_prices") or moat.get("total_products") or 0
    store_count = moat.get("total_stores") or moat.get("store_count") or 0

    # Sort products by CV descending (most volatile first)
    products_sorted = sorted(products, key=lambda x: (x.get("cv_pct") or 0), reverse=True)

    # Category volatility summary
    cat_cv: dict[str, list[float]] = defaultdict(list)
    cat_spread: dict[str, list[float]] = defaultdict(list)
    for p in products:
        cat = p["category"]
        if p.get("cv_pct") is not None:
            cat_cv[cat].append(p["cv_pct"])
        if p.get("spread_pct") is not None:
            cat_spread[cat].append(p["spread_pct"])

    category_summary = {}
    for cat in set(list(cat_cv.keys()) + list(cat_spread.keys())):
        category_summary[cat] = {
            "products": len(cat_cv.get(cat, [])),
            "avg_cv_pct": round(_mean(cat_cv[cat]), 1) if cat_cv.get(cat) else None,
            "avg_spread_pct": round(_mean(cat_spread[cat]), 1) if cat_spread.get(cat) else None,
        }
    category_summary = dict(
        sorted(category_summary.items(), key=lambda x: -(x[1].get("avg_cv_pct") or 0))
    )

    retailer_stats = _retailer_stats(products)

    # High-value insights
    high_spread = [p for p in products_sorted if (p.get("spread_pct") or 0) >= 20]
    with_outliers = [p for p in products_sorted if p.get("outlier_retailers")]

    return {
        "generated_at": now.isoformat(),
        "country": country,
        "moat": {
            "total_prices": total_prices,
            "store_count": store_count,
        },
        "analysis": {
            "products_with_multi_store_prices": len(products),
            "products_high_spread_20pct_plus": len(high_spread),
            "products_with_outlier_retailers": len(with_outliers),
            "avg_cv_pct": round(_mean([p["cv_pct"] for p in products if p.get("cv_pct") is not None]), 1) if products else None,
            "avg_spread_pct": round(_mean([p["spread_pct"] for p in products if p.get("spread_pct") is not None]), 1) if products else None,
        },
        "top_volatile": products_sorted[:top_n],
        "category_volatility": category_summary,
        "retailer_stats": retailer_stats,
        "data_available": bool(products),
    }


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def _fmt_console(report: dict) -> str:
    lines: list[str] = []
    ts = report["generated_at"][:16].replace("T", " ")
    a = report["analysis"]
    moat = report["moat"]

    lines.append(f"\n{'='*65}")
    lines.append(f"  PRICE VOLATILITY REPORT  [{ts} UTC]  país: {report['country']}")
    lines.append(f"{'='*65}")

    if not report["data_available"]:
        lines.append("\n  [Sin datos de precios multi-retailer disponibles]")
        lines.append("  Verificar MARKET_API_TOKEN y que el endpoint /v1/basket/compare esté activo.")
        lines.append(f"\n{'='*65}\n")
        return "\n".join(lines)

    lines.append(f"\n  MOAT: {moat['total_prices']:,} precios · {moat['store_count']} stores")
    lines.append("\n  RESUMEN DE VOLATILIDAD")
    lines.append(f"  {'Productos con precio multi-retailer':<38} {a['products_with_multi_store_prices']:>5}")
    lines.append(f"  {'Spread >= 20% (candidatos a alerta)':<38} {a['products_high_spread_20pct_plus']:>5}")
    lines.append(f"  {'Productos con retailer outlier (>2σ)':<38} {a['products_with_outlier_retailers']:>5}")
    lines.append(f"  {'CV promedio':<38} {a['avg_cv_pct'] or '—':>5}%")
    lines.append(f"  {'Spread promedio (max-min/min)':<38} {a['avg_spread_pct'] or '—':>5}%")

    lines.append(f"\n{'─'*65}")
    lines.append("  TOP PRODUCTOS MÁS VOLÁTILES (CV)")
    lines.append(f"{'─'*65}")
    lines.append(f"  {'Producto':<35} {'CV%':>5}  {'Spread%':>8}  {'Stores':>6}")
    for p in report["top_volatile"][:15]:
        name = str(p.get("name") or p.get("product_id") or "?")[:34]
        cv = f"{p['cv_pct']:.1f}" if p.get("cv_pct") is not None else "?"
        sp = f"{p['spread_pct']:.1f}" if p.get("spread_pct") is not None else "?"
        lines.append(f"  {name:<35} {cv:>5}  {sp:>8}  {p['n_stores']:>6}")

    if report.get("category_volatility"):
        lines.append(f"\n{'─'*65}")
        lines.append("  VOLATILIDAD POR CATEGORÍA")
        lines.append(f"{'─'*65}")
        for cat, stats in list(report["category_volatility"].items())[:8]:
            cv = f"{stats['avg_cv_pct']:.1f}%" if stats.get("avg_cv_pct") is not None else "?"
            sp = f"{stats['avg_spread_pct']:.1f}%" if stats.get("avg_spread_pct") is not None else "?"
            lines.append(f"  {cat:<30} CV: {cv:<8} Spread: {sp} ({stats['products']} productos)")

    if report.get("retailer_stats"):
        lines.append(f"\n{'─'*65}")
        lines.append("  CONSISTENCIA POR RETAILER")
        lines.append(f"{'─'*65}")
        lines.append(f"  {'Retailer':<25} {'Score':>6}  {'Outliers':>8}  {'Productos':>9}")
        for store, s in list(report["retailer_stats"].items())[:10]:
            lines.append(
                f"  {store:<25} {s['consistency_score']:>5}%  {s['outlier_prices']:>8}  {s['products_indexed']:>9}"
            )

    lines.append(f"\n{'='*65}\n")
    return "\n".join(lines)


def _fmt_slack(report: dict) -> str:
    ts = report["generated_at"][:16].replace("T", " ")
    a = report["analysis"]

    if not report["data_available"]:
        return f"📊 *Price Volatility* [{ts} UTC] — sin datos de precios multi-retailer disponibles."

    top5 = report["top_volatile"][:5]
    top_lines = "\n".join(
        f"  • `{p.get('name') or p.get('product_id')}` — CV {p.get('cv_pct') or '?'}% · spread {p.get('spread_pct') or '?'}%"
        for p in top5
    )

    return "\n".join([
        f"📊 *Price Volatility Report* [{ts} UTC] · país: {report['country']}",
        "",
        f"*{a['products_with_multi_store_prices']}* productos analizados · "
        f"*{a['products_high_spread_20pct_plus']}* con spread ≥20% · "
        f"CV promedio: *{a.get('avg_cv_pct') or '—'}%*",
        "",
        "*Top 5 más volátiles:*",
        top_lines,
    ])


def _post_slack(message: str) -> bool:
    token = os.getenv("SLACK_BOT_TOKEN", "").strip()
    channel = os.getenv("SLACK_BITACORA_CHANNEL", os.getenv("SLACK_CHANNEL", "")).strip()
    if not token or not channel:
        print("[volatility] Slack no configurado", file=sys.stderr)
        return False
    try:
        if _HAS_HTTPX:
            r = httpx.post(
                "https://slack.com/api/chat.postMessage",
                headers={"Authorization": f"Bearer {token}"},
                json={"channel": channel, "text": message},
                timeout=15,
            )
            return r.json().get("ok", False)
    except Exception as e:
        print(f"[volatility] Slack error: {e}", file=sys.stderr)
    return False


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(description="Price Volatility Report — P4")
    parser.add_argument("--country", default="PE", help="País ISO2 (PE, CL, CO, MX…)")
    parser.add_argument("--top", type=int, default=20, help="Top N productos volátiles")
    parser.add_argument("--slack", action="store_true", help="Postear resumen a Slack")
    parser.add_argument("--json", dest="json_out", action="store_true", help="Salida JSON")
    args = parser.parse_args()

    report = build_report(country=args.country, top_n=args.top)

    if args.json_out:
        print(json.dumps(report, indent=2, default=str))
    else:
        print(_fmt_console(report))

    if args.slack:
        _post_slack(_fmt_slack(report))

    return 1 if report["analysis"]["products_high_spread_20pct_plus"] > 0 else 0


if __name__ == "__main__":
    raise SystemExit(main())
