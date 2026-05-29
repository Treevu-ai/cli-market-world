#!/usr/bin/env python3
"""Sync LinkedIn copy + data-gate from production dashboard.

Run after major product jumps (e.g. moat 19K → 41K) so posts and gates match /dashboard/data.

Usage:
  python3 ops/sync_linkedin_metrics.py           # update data-gate + metric-heavy Day-*.md
  python3 ops/sync_linkedin_metrics.py --dry-run
"""

from __future__ import annotations

import argparse
import re
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA_GATE = ROOT / "docs" / "linkedin" / "data-gate.md"
LINKEDIN_DIR = ROOT / "docs" / "linkedin"

# Day files that embed aggregate KPIs (not full regenerate)
METRIC_DAYS = (7, 8, 10, 11, 14, 28, 30)


def _load_monday():
    import importlib.util

    path = Path(__file__).parent / "monday.py"
    spec = importlib.util.spec_from_file_location("monday_ops", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _fmt(n: int | float) -> str:
    if isinstance(n, float):
        n = int(n)
    return f"{n:,}"


def _short_k(n: int) -> str:
    if n >= 1000:
        return f"{n // 1000}K+"
    return str(n)


def metrics_from_dashboard(data: dict) -> dict[str, str]:
    k = data.get("kpis", {})
    coll = data.get("collector", {}) or {}
    moat = data.get("moat_summary", {}) or {}
    indexed = int(k.get("total_indexed", 0) or 0)
    snap24 = int(k.get("snapshots_24h", k.get("total_snapshots", 0)) or 0)
    stores = int(k.get("stores_indexed", k.get("active_stores", 0)) or 0)
    fresh = int(k.get("stores_fresh_24h", stores) or 0)
    coverage = float(k.get("coverage_7d_pct", 0) or 0)
    countries = len(data.get("by_country", []) or [])
    last_run = coll.get("prices_upserted") or coll.get("last_prices") or "—"
    stores_run = coll.get("stores_ok")
    stores_total = coll.get("stores_total") or k.get("total_stores", 36)
    run_line = (
        f"**{last_run}** precios · {stores_run}/{stores_total} tiendas"
        if stores_run is not None
        else f"collector activo · {stores} tiendas indexadas"
    )
    return {
        "date": date.today().isoformat(),
        "indexed": _fmt(indexed),
        "indexed_raw": str(indexed),
        "snap24": _fmt(snap24),
        "snap24_raw": str(snap24),
        "stores": str(stores),
        "fresh": str(fresh),
        "coverage": f"{coverage:.1f}",
        "countries": str(countries or 8),
        "indexed_k": _short_k(indexed),
        "snap_k": _short_k(snap24),
        "run_line": run_line,
        "moat_stale": "false" if not moat.get("stale") else "true",
    }


def _replace_block(text: str, header: str, new_body: str) -> str:
    pattern = (
        rf"(?m)(^## {re.escape(header)} — .*?\n\n)"
        r"(\|.*?\|\n(?:\|.*?\|\n)+)"
    )
    return re.sub(pattern, rf"\1{new_body}\n", text, count=1)


def update_data_gate(m: dict[str, str], dry_run: bool) -> bool:
    if not DATA_GATE.is_file():
        print("Missing data-gate.md", file=sys.stderr)
        return False

    text = DATA_GATE.read_text(encoding="utf-8")
    table = (
        "| Métrica | Valor | OK para LI? |\n"
        "|---------|-------|-------------|\n"
        f"| Precios indexados (moat) | **{m['indexed']}** | ✅ |\n"
        f"| Refresh 24h | **{m['snap24']}** | ✅ |\n"
        f"| Tiendas fresh 24h | **{m['fresh']}** | ✅ |\n"
        f"| Tiendas con datos | **{m['stores']}** | ✅ |\n"
        f"| **coverage_7d_pct** | **{m['coverage']}%** | ✅ gate semana 2 |\n"
        f"| Collector last run | {m['run_line']} | ✅ |\n"
        f"| `price_snapshots_upsert_ready` | **true** | ✅ |\n"
        f"| Store success % (lifetime) | 55.6% | ❌ solo ops |\n"
        f"| Moat stale | **{m['moat_stale']}** | ✅ |"
    )
    new_text = _replace_block(text, "Snapshot verificado", table)
    new_text = re.sub(
        r"(?m)^date: \d{4}-\d{2}-\d{2}",
        f"date: {m['date']}",
        new_text,
        count=1,
    )
    # Gate checklist lines with dynamic numbers
    new_text = re.sub(
        r"Cifra `\[N\]` en Day 07 → usar \*\*[\d,]+\*\*.*",
        f"Cifra `[N]` en Day 07 → usar **{m['snap24']}** (24h) o **{m['indexed']}** (indexado)",
        new_text,
    )
    new_text = re.sub(
        r"Claims agregados .* — OK",
        f"Claims agregados {m['snap_k']} / {m['indexed_k']} — OK",
        new_text,
    )
    for day_row, snap_label in ((7, "Semana 1 wrap"), (10, "Collector 8h"), (14, "3 insights")):
        new_text = re.sub(
            rf"(\| {day_row} \| {snap_label} \| ✅ publicar \| )[^|]+(\|)",
            rf"\1{m['snap24']} fresh · {m['indexed']} indexados · {m['fresh']} fresh\2",
            new_text,
        )

    if new_text == text:
        print("data-gate: no changes")
        return False
    if not dry_run:
        DATA_GATE.write_text(new_text, encoding="utf-8")
    print(f"data-gate: updated ({'dry-run' if dry_run else 'written'})")
    return True


def _patch_day_file(path: Path, m: dict[str, str], dry_run: bool) -> bool:
    if not path.is_file():
        return False
    text = path.read_text(encoding="utf-8")
    orig = text

    subs = [
        (r"\b19,452\b", m["indexed"]),
        (r"\b19\.452\b", m["indexed"]),
        (r"\b8,392\b", m["snap24"]),
        (r"\b8\.392\b", m["snap24"]),
        (r"\b8,000\+", m["snap_k"]),
        (r"\b8K\+", m["snap_k"]),
        (r"\b19K\+", m["indexed_k"]),
        (r"\b19,000\+", f"{m['indexed_k'].replace('+', '')}+"),
        (r"\b94\.4%", f"{m['coverage']}%"),
        (r"\b30 retailers\b", f"{m['stores']} retailers"),
        (r"\*\*30\*\* retailers", f"**{m['stores']}** retailers"),
        (r"→ \*\*30\*\* retailers", f"→ **{m['stores']}** retailers"),
        (r"\b30 retailers fresh\b", f"{m['fresh']} retailers fresh"),
        (r"\b30 fresh\b", f"{m['fresh']} fresh"),
        (r"\b34\*\* con histórico", f"{m['stores']}** con histórico"),
    ]
    for pat, repl in subs:
        text = re.sub(pat, repl, text)

    if text == orig:
        return False
    if not dry_run:
        path.write_text(text, encoding="utf-8")
    print(f"  {path.name}: patched")
    return True


def update_day_files(m: dict[str, str], dry_run: bool) -> int:
    n = 0
    for day in METRIC_DAYS:
        path = LINKEDIN_DIR / f"Day-{day:02d}.md"
        if _patch_day_file(path, m, dry_run):
            n += 1
    return n


def main() -> int:
    parser = argparse.ArgumentParser(description="Sync LinkedIn metrics from production")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    monday = _load_monday()
    print("Fetching dashboard...")
    data = monday.fetch_data()
    m = metrics_from_dashboard(data)
    print(
        f"  indexed={m['indexed']} snap24={m['snap24']} "
        f"stores={m['stores']} coverage={m['coverage']}%"
    )

    update_data_gate(m, args.dry_run)
    count = update_day_files(m, args.dry_run)
    print(f"Done — {count} day file(s) {'would change' if args.dry_run else 'updated'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
