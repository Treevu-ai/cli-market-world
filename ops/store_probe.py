#!/usr/bin/env python3
"""Probe active stores — run after changing market_stores.py.

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

QUERIES = {
    "supermercados": "leche",
    "farmacias": "vitamina",
    "electro": "televisor",
    "moda": "camisa",
    "hogar": "silla",
    "departamentales": "televisor",
}


async def probe_store(store: str) -> dict:
    cfg = STORES[store]
    term = QUERIES.get(cfg.get("line", ""), "producto")
    try:
        rows = await fetch_store(store, term, limit=3)
        return {
            "store": store,
            "platform": cfg.get("platform"),
            "country": cfg.get("country"),
            "ok": len(rows) > 0,
            "count": len(rows),
            "query": term,
        }
    except Exception as e:
        return {
            "store": store,
            "platform": cfg.get("platform"),
            "country": cfg.get("country"),
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

    if args.json:
        print(json.dumps({"ok": len(ok), "bad": len(bad), "results": results}, indent=2))
    else:
        print(f"Active catalog: {len(DEFAULT_STORES)} stores")
        print(f"OK: {len(ok)}  FAIL/empty: {len(bad)}")
        if bad:
            print("\nNeeds attention:")
            for r in sorted(bad, key=lambda x: x["store"]):
                err = r.get("error", "0 results")
                print(f"  {r['store']:16} {r['platform']:8} {err}")

    return 0 if len(ok) >= len(DEFAULT_STORES) * 0.7 else 1


if __name__ == "__main__":
    raise SystemExit(asyncio.run(main()))
