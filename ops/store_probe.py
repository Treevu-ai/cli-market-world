#!/usr/bin/env python3
"""Probe active stores — run after changing market_stores.py.

Uses brand-aware probe terms so electro/moda stores are not tested with
generic queries that do not match their catalog (e.g. Motorola ≠ televisor).

Usage:
  python3 ops/store_probe.py
  python3 ops/store_probe.py --json
"""

from __future__ import annotations

import argparse
import asyncio
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from market_core import fetch_store, STORES, DEFAULT_STORES

LINE_DEFAULTS = {
    "supermercados": "leche",
    "farmacias": "paracetamol",
    "electro": "celular",
    "moda": "camiseta",
    "hogar": "silla",
    "departamentales": "televisor",
}

# Brand / locale overrides — probe what the store actually sells
STORE_PROBE: dict[str, str] = {
    "motorola_ar": "motorola",
    "motorola_br": "celular motorola",
    "motorola_mx": "motorola",
    "motorola_cl": "motorola",
    "electrolux_ar": "heladera",
    "electrolux_cl": "refrigerador",
    "whirlpool_ar": "lavarropas",
    "whirlpool_it": "lavatrice",
    "whirlpool_fr": "lave-linge",
    "mambo_br": "leite",
    "pacheco_br": "dipirona",
    "globo_br": "dipirona",
    "farmatodo_mx": "paracetamol",
    "cea_br": "camiseta",
    "hering_br": "camiseta",
    "aramis_br": "camisa",
    "miess_br": "perfume",
    "decathlon_br": "tenis",
    "oster_br": "liquidificador",
    "rihappy_br": "boneca",
    "easy_ar": "taladro",
    "promart_pe": "taladro",
    "coppell_ar": "televisor",
}


def probe_term(store: str) -> str:
    if store in STORE_PROBE:
        return STORE_PROBE[store]
    line = STORES[store].get("line", "")
    return LINE_DEFAULTS.get(line, "producto")


async def probe_store(store: str) -> dict:
    cfg = STORES[store]
    term = probe_term(store)
    try:
        rows = await fetch_store(store, term, limit=3)
        return {
            "store": store,
            "platform": cfg.get("platform"),
            "country": cfg.get("country"),
            "line": cfg.get("line"),
            "ok": len(rows) > 0,
            "count": len(rows),
            "query": term,
        }
    except Exception as e:
        return {
            "store": store,
            "platform": cfg.get("platform"),
            "country": cfg.get("country"),
            "line": cfg.get("line"),
            "ok": False,
            "count": 0,
            "query": term,
            "error": str(e)[:120],
        }


async def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()

    results = await asyncio.gather(*[probe_store(s) for s in DEFAULT_STORES])
    ok = [r for r in results if r["ok"]]
    bad = [r for r in results if not r["ok"]]
    pct = round(len(ok) / len(DEFAULT_STORES) * 100, 1) if DEFAULT_STORES else 0

    if args.json:
        print(json.dumps({"ok": len(ok), "bad": len(bad), "pct": pct, "results": results}, indent=2))
    else:
        print(f"Active catalog: {len(DEFAULT_STORES)} stores")
        print(f"OK: {len(ok)}  FAIL/empty: {len(bad)}  ({pct}%)")
        if bad:
            print("\nNeeds attention:")
            for r in sorted(bad, key=lambda x: x["store"]):
                err = r.get("error", "0 results")
                print(f"  {r['store']:16} {r.get('line','?'):14} q={r['query']!r:20} {err}")

    return 0 if pct >= 70 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
