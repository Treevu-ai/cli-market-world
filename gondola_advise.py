"""Gondola Digital v0 — assortment/price advice on the formal online shelf.

Not Nielsen space: no facings, planogram, linear space, or POS share.

World-native copy so Fly can serve POST /v1/intel/gondola-advise on the
current PyPI pin (cli-market-core==1.12.48). routers/intel.py prefers
market_core.market_gondola when that module exists (1.12.49+). Keep this
file in lockstep with cli-market-core/market_core/market_gondola.py until
the pin bump, then delete the vendor.
"""
from __future__ import annotations

import re
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from market_core import store_credentials
from market_core.market_units import price_per_base_unit

DENYLIST = frozenset({
    "facing",
    "facings",
    "planogram",
    "planograma",
    "share of shelf",
    "espacio lineal",
})
NOT_INCLUDED = (
    "physical_space",
    "facings",
    "planogram",
    "pos_share",
    "market_share",
)
FRESH_HOURS = 24
MAX_ACTIONS = 7
PRICE_HIGH = 1.05
PRICE_LOW = 0.85
_TOKEN_RE = re.compile(r"[a-z0-9áéíóúñ]+")
_DENY_RE = re.compile("|".join(re.escape(w) for w in sorted(DENYLIST, key=len, reverse=True)), re.I)


class GondolaAdviceError(ValueError):
    pass


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _aware(dt: datetime) -> datetime:
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


def _parse_time(raw: Any) -> datetime | None:
    if raw is None:
        return None
    if isinstance(raw, datetime):
        return _aware(raw)
    text = str(raw).replace("Z", "+00:00")
    try:
        return _aware(datetime.fromisoformat(text))
    except ValueError:
        return None


def _tokens(text: str) -> set[str]:
    return {t for t in _TOKEN_RE.findall((text or "").lower()) if t}


def _num(val: Any) -> float | None:
    try:
        if val is None or val == "":
            return None
        return float(val)
    except (TypeError, ValueError):
        return None


def _is_fresh(row: dict[str, Any], now: datetime) -> bool:
    ts = _parse_time(row.get("queried_at"))
    if ts is None:
        return False
    return (now - ts) <= timedelta(hours=FRESH_HOURS)


def _query_hits(query: str, row: dict[str, Any]) -> bool:
    needed = _tokens(query)
    if not needed:
        return False
    blob = f"{row.get('name') or ''} {row.get('brand') or ''}"
    return needed <= _tokens(blob)


def _item_hits(item: dict[str, Any], row: dict[str, Any]) -> bool:
    pid = str(item.get("product_id") or "").strip()
    if pid and str(row.get("product_id") or "") == pid:
        return True
    query = str(item.get("query") or item.get("name") or "").strip()
    return _query_hits(query, row) if query else False


def _item_label(item: dict[str, Any]) -> str:
    return str(item.get("query") or item.get("name") or item.get("product_id") or "").strip()


def _category_hits(category: str, row: dict[str, Any]) -> bool:
    skip = {"de", "y", "la", "el", "los", "las"}
    needed = {t for t in _tokens(category) if t not in skip}
    if not needed:
        return True
    blob = f"{row.get('name') or ''} {row.get('brand') or ''} {row.get('line') or ''}"
    return bool(needed & _tokens(blob))


def _has_discount(row: dict[str, Any]) -> bool:
    d = _num(row.get("discount"))
    if d is not None and d > 0:
        return True
    list_price = _num(row.get("list_price"))
    price = _num(row.get("price"))
    return list_price is not None and price is not None and list_price > price * 1.02


def _confidence(row: dict[str, Any] | None) -> str:
    raw = (row or {}).get("confidence")
    if raw in ("ok", "low", "stale"):
        return str(raw)
    return "ok" if row else "low"


def _load_rows(db) -> list[dict[str, Any]]:
    cur = db.execute(
        """SELECT product_id, store, store_name, name, brand, price, list_price,
                  discount, line, currency, queried_at, confidence
           FROM price_snapshots"""
    )
    cols = [d[0] for d in cur.description]
    return [dict(zip(cols, r)) for r in cur.fetchall()]


def _candidate_stores(country: str, line: str | None) -> list[str]:
    catalog = store_credentials.get_all_stores() or {}
    cc = (country or "").strip().upper()
    out: list[str] = []
    if not isinstance(catalog, dict):
        return out
    for store_id, meta in catalog.items():
        meta = meta or {}
        raw_cc = str(meta.get("country") or "").upper()
        if cc and cc not in raw_cc:
            continue
        if line and str(meta.get("line") or "") != line:
            continue
        out.append(store_id)
    return out


def _percentile(sorted_vals: list[float], p: float) -> float:
    if not sorted_vals:
        return 0.0
    if len(sorted_vals) == 1:
        return round(sorted_vals[0], 4)
    idx = (p / 100.0) * (len(sorted_vals) - 1)
    lo = int(idx)
    hi = min(lo + 1, len(sorted_vals) - 1)
    frac = idx - lo
    return round(sorted_vals[lo] * (1.0 - frac) + sorted_vals[hi] * frac, 4)


def _landscape(category: str, rows: list[dict[str, Any]], now: datetime) -> dict[str, Any]:
    priced: list[tuple[float, str]] = []
    for row in rows:
        if not _is_fresh(row, now) or not _category_hits(category, row):
            continue
        price = _num(row.get("price"))
        if price is None or price <= 0:
            continue
        parsed = price_per_base_unit(price, row.get("name") or "")
        if not parsed or parsed.get("price_per") is None:
            continue
        basis = parsed.get("basis")
        currency = (row.get("currency") or "PEN").upper()
        if basis == "L":
            unit = f"{currency}_per_L"
        elif basis == "kg":
            unit = f"{currency}_per_kg"
        else:
            unit = f"{currency}_per_unit"
        priced.append((float(parsed["price_per"]), unit))
    if len(priced) < 3:
        return {
            "status": "insufficient_data",
            "sample": len(priced),
            "unit": "PEN_per_L",
            "p20": None,
            "p50": None,
            "p80": None,
        }
    units = [u for _, u in priced]
    unit = max(set(units), key=units.count)
    vals = sorted(p for p, u in priced if u == unit)
    if len(vals) < 3:
        vals = sorted(p for p, _ in priced)
    return {
        "status": "ok",
        "sample": len(vals),
        "unit": unit,
        "p20": _percentile(vals, 20),
        "p50": _percentile(vals, 50),
        "p80": _percentile(vals, 80),
    }


def _store_freshness(stores: list[str], rows: list[dict[str, Any]], now: datetime) -> dict[str, str]:
    by_store: dict[str, list[dict[str, Any]]] = {s: [] for s in stores}
    for row in rows:
        sid = row.get("store")
        if sid in by_store:
            by_store[sid].append(row)
    out: dict[str, str] = {}
    for sid, store_rows in by_store.items():
        if not store_rows:
            out[sid] = "empty"
        elif any(_is_fresh(r, now) for r in store_rows):
            out[sid] = "fresh"
        else:
            out[sid] = "stale"
    return out


def _coverage(portfolio, stores, rows, now) -> list[dict[str, Any]]:
    freshness = _store_freshness(stores, rows, now)
    cells: list[dict[str, Any]] = []
    for item in portfolio:
        label = _item_label(item)
        hits = [r for r in rows if _item_hits(item, r)]
        for sid in stores:
            at_store = [r for r in hits if r.get("store") == sid]
            if any(_is_fresh(r, now) for r in at_store):
                status = "listed"
            elif freshness.get(sid) == "stale":
                status = "stale"
            elif freshness.get(sid) == "empty":
                status = "insufficient_data"
            else:
                status = "missing"
            cells.append({"sku": label, "store": sid, "status": status})
    return cells


def _mk_action(kind, *, priority, confidence, evidence, rationale, sku=""):
    return {
        "id": uuid.uuid4().hex[:10],
        "type": kind,
        "priority": priority,
        "confidence": confidence,
        "evidence": evidence,
        "rationale": rationale,
        "sku": sku,
    }


def _list_actions(cells, rows, now):
    actions = []
    for cell in cells:
        if cell["status"] != "missing":
            continue
        sid = cell["store"]
        peer = next((r for r in rows if r.get("store") == sid and _is_fresh(r, now)), None)
        if peer is None:
            continue
        actions.append(
            _mk_action(
                "LIST",
                priority=1,
                confidence=_confidence(peer),
                evidence=[{
                    "store": sid,
                    "own_status": "missing",
                    "peer_name": peer.get("name"),
                    "peer_price": _num(peer.get("price")),
                }],
                rationale=(
                    f"El SKU no aparece en la gondola digital formal de {sid} "
                    "y el retailer si tiene oferta viva reciente en el mismo canal online."
                ),
                sku=cell["sku"],
            )
        )
    return actions


def _price_actions(portfolio, rows, now):
    actions = []
    for item in portfolio:
        target = _num(item.get("pvp"))
        if target is None or target <= 0:
            continue
        query = _item_label(item)
        for row in rows:
            if not _item_hits(item, row) or not _is_fresh(row, now):
                continue
            price = _num(row.get("price"))
            if price is None:
                continue
            if price > target * PRICE_HIGH or price < target * PRICE_LOW:
                gap = round(100.0 * (price - target) / target, 1)
                actions.append(
                    _mk_action(
                        "PRICE",
                        priority=2,
                        confidence=_confidence(row),
                        evidence=[{
                            "store": row.get("store"),
                            "own_price": price,
                            "pvp": target,
                            "gap_pct": gap,
                        }],
                        rationale=(
                            f"El precio online en {row.get('store')} ({price}) "
                            f"se desvia del PVP de referencia ({target})."
                        ),
                        sku=query,
                    )
                )
    return actions


def _promo_actions(portfolio, rows, now, competitors):
    if not competitors:
        return []
    names = {c.lower() for c in competitors}
    actions = []
    for item in portfolio:
        query = _item_label(item)
        own_fresh = [r for r in rows if _item_hits(item, r) and _is_fresh(r, now)]
        for own in own_fresh:
            if _has_discount(own):
                continue
            sid = own.get("store")
            rival = next(
                (
                    r
                    for r in rows
                    if r.get("store") == sid
                    and _is_fresh(r, now)
                    and not _item_hits(item, r)
                    and _has_discount(r)
                    and (
                        (r.get("brand") or "").lower() in names
                        or any(c in (r.get("name") or "").lower() for c in names)
                    )
                ),
                None,
            )
            if rival is None:
                continue
            conf = "ok" if _confidence(rival) == "ok" else "low"
            actions.append(
                _mk_action(
                    "PROMO",
                    priority=3,
                    confidence=conf,
                    evidence=[{
                        "store": sid,
                        "own_discount": False,
                        "competitor": rival.get("brand") or rival.get("name"),
                        "competitor_discount": rival.get("discount"),
                        "competitor_price": _num(rival.get("price")),
                    }],
                    rationale=(
                        f"Hay descuento vivo de un competidor en {sid} "
                        "y el SKU propio no esta en promocion en gondola digital."
                    ),
                    sku=query,
                )
            )
    return actions


def validate_advice(payload: dict[str, Any]) -> None:
    for action in payload.get("actions") or []:
        kind = action.get("type")
        if kind in ("LIST", "PRICE", "PROMO") and not action.get("evidence"):
            raise GondolaAdviceError(f"{kind} requires evidence")
        if _DENY_RE.search(str(action.get("rationale") or "")):
            raise GondolaAdviceError("denylist term in rationale")


def advise_gondola(
    db,
    *,
    country: str,
    category: str,
    portfolio: list[dict[str, Any]] | None = None,
    line: str | None = None,
    competitors: list[str] | None = None,
    now: datetime | None = None,
) -> dict[str, Any]:
    if not (country or "").strip():
        raise GondolaAdviceError("country is required")
    if not (category or "").strip():
        raise GondolaAdviceError("category is required")
    items = list(portfolio or [])
    if not items:
        raise GondolaAdviceError("portfolio is required")
    clock = now or _now()
    stores = _candidate_stores(country, line)
    rows = _load_rows(db)
    if line:
        rows = [r for r in rows if not r.get("line") or r.get("line") == line]
    cells = _coverage(items, stores, rows, clock)
    landscape = _landscape(category, rows, clock)
    listed = any(c["status"] == "listed" for c in cells)
    if landscape["status"] == "insufficient_data" and not listed:
        actions = [
            _mk_action(
                "HOLD",
                priority=4,
                confidence="insufficient_data",
                evidence=[{"reason": "insufficient_data"}],
                rationale=(
                    "No hay suficientes observaciones frescas en gondola digital "
                    "formal para recomendar listado o precio."
                ),
                sku=_item_label(items[0]),
            )
        ]
    else:
        actions = _list_actions(cells, rows, clock)
        actions.extend(_price_actions(items, rows, clock))
        actions.extend(_promo_actions(items, rows, clock, competitors or []))
        actions.sort(key=lambda a: (a["priority"], a["type"]))
        actions = actions[:MAX_ACTIONS]
    payload = {
        "run_id": uuid.uuid4().hex,
        "schema_version": "gondola-advise.v0",
        "scope": "digital_shelf_formal",
        "country": country.strip().upper(),
        "category": category,
        "not_included": list(NOT_INCLUDED),
        "coverage": {
            "rows": sorted({c["sku"] for c in cells}),
            "cols": stores,
            "cells": cells,
        },
        "landscape": landscape,
        "actions": actions,
        "generated_at": clock.isoformat(),
    }
    validate_advice(payload)
    return payload
