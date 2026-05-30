#!/usr/bin/env python3
"""Generate LinkedIn image assets for all 30 campaign days.

Usage:
  python3 ops/generate_all_linkedin_assets.py           # all days
  python3 ops/generate_all_linkedin_assets.py --day 7   # single day
  python3 ops/generate_all_linkedin_assets.py --patch    # update Day-*.md Assets sections

Output: docs/linkedin/assets/day-NN/day-NN-linkedin.png (attach on LinkedIn)
Carousel days also: day-NN-slide-01.png …
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import re
import sys
from pathlib import Path

import httpx

sys.path.insert(0, str(Path(__file__).resolve().parent))

from content_paths import assets_root, content_root, linkedin_dir, metrics_dir, display_path, rel_to_content
from linkedin_asset_lib import (
    CAROUSEL_CFG,
    DAY_TEMPLATE,
    DIAGRAM_DAYS,
    METRICS_DAYS,
    TERMINAL_CFG,
    parse_day_md,
    render_carousel,
    render_diagram,
    render_metrics,
    render_quote,
    render_terminal,
)

COMPARE_URL = "https://cli-market-production.up.railway.app/products/compare"


def _load_monday():
    path = Path(__file__).parent / "monday.py"
    spec = importlib.util.spec_from_file_location("monday_ops", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def fetch_compare(query: str, country: str) -> dict:
    cache = metrics_dir() / f"query-{query}-{country.lower()}.json"
    if cache.is_file():
        return json.loads(cache.read_text(encoding="utf-8"))
    print(f"  Fetching compare {query} {country}…", flush=True)
    r = httpx.post(
        COMPARE_URL,
        json={"query": query, "country": country, "limit": 12},
        timeout=90.0,
    )
    r.raise_for_status()
    data = r.json()
    metrics_dir().mkdir(parents=True, exist_ok=True)
    cache.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    return data


def template_for(day: int) -> str:
    if day in DAY_TEMPLATE:
        return DAY_TEMPLATE[day]
    if day in METRICS_DAYS:
        return "metrics"
    if day in DIAGRAM_DAYS:
        return "diagram"
    if day in CAROUSEL_CFG:
        return "carousel"
    if day in TERMINAL_CFG:
        return "terminal"
    return "quote"


def generate_day(day: int, kpis: dict) -> Path | None:
    meta = parse_day_md(day)
    out_dir = assets_root() / f"day-{day:02d}"
    tpl = template_for(day)

    if tpl == "metrics":
        return render_metrics(day, meta, kpis, out_dir)
    if tpl == "diagram":
        return render_diagram(day, meta, out_dir)
    if tpl == "carousel":
        slides = CAROUSEL_CFG[day]
        return render_carousel(day, meta, slides, out_dir)
    if tpl == "terminal":
        cfg = TERMINAL_CFG[day]
        data = fetch_compare(cfg["query"], cfg["country"])
        return render_terminal(day, meta, cfg["command"], data, out_dir)
    return render_quote(day, meta, out_dir)


def patch_day_assets_section(day: int, tpl: str) -> None:
    path = linkedin_dir() / f"Day-{day:02d}.md"
    if not path.is_file():
        return
    text = path.read_text(encoding="utf-8")
    rel = rel_to_content(assets_root() / f"day-{day:02d}" / f"day-{day:02d}-linkedin.png")
    extra = ""
    if tpl == "carousel":
        n = len(CAROUSEL_CFG.get(day, []))
        extra = (
            f"\n**Carousel ({n} imágenes):** subir en orden `day-{day:02d}-slide-01.png` … "
            f"`{n:02d}.png` en la misma carpeta.\n"
        )
    new_section = f"""## Assets

**Adjuntar en LinkedIn:** `{rel}`{extra}
Regenerar: `python3 ops/generate_all_linkedin_assets.py --day {day}` · todos: `python3 ops/generate_all_linkedin_assets.py`
"""
    patched, n = re.subn(
        r"(?ms)^## Assets\s*\n.*?(?=^## |\Z)",
        new_section,
        text,
        count=1,
    )
    if n == 0:
        patched = text.rstrip() + "\n\n" + new_section
    path.write_text(patched, encoding="utf-8")


def write_index() -> None:
    lines = [
        "# LinkedIn assets — 30 días",
        "",
        "Flujo de publicación: abrir `Day-NN.md` → copiar **Post** → adjuntar **`day-NN-linkedin.png`**.",
        "",
        "| Día | Imagen principal |",
        "|-----|------------------|",
    ]
    for d in range(1, 31):
        p = assets_root() / f"day-{d:02d}" / f"day-{d:02d}-linkedin.png"
        flag = "✅" if p.is_file() else "—"
        lines.append(f"| {d} | {flag} `assets/day-{d:02d}/day-{d:02d}-linkedin.png` |")
    lines += [
        "",
        "## Regenerar todo",
        "",
        "```bash",
        "python3 ops/sync_linkedin_metrics.py   # opcional: KPIs en copy",
        "python3 ops/generate_all_linkedin_assets.py --patch",
        "```",
        "",
        "Requisitos: `pip install pillow httpx`",
        "",
    ]
    (assets_root() / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate all LinkedIn day assets")
    parser.add_argument("--day", type=int, help="Single day 1-30")
    parser.add_argument("--patch", action="store_true", help="Update Day-*.md Assets sections")
    parser.add_argument("--skip-fetch", action="store_true", help="Use cached compare JSON only")
    args = parser.parse_args()

    if args.skip_fetch:
        global fetch_compare  # noqa: PLW0603

        def _cached_only(query: str, country: str) -> dict:
            cache = metrics_dir() / f"query-{query}-{country.lower()}.json"
            if not cache.is_file():
                raise FileNotFoundError(cache)
            return json.loads(cache.read_text(encoding="utf-8"))

        fetch_compare = _cached_only  # type: ignore[assignment]

    days = [args.day] if args.day else list(range(1, 31))
    if args.day and not 1 <= args.day <= 30:
        print("Day must be 1-30", file=sys.stderr)
        return 1

    print(f"Content root: {content_root()}", flush=True)
    print("Loading dashboard KPIs…", flush=True)
    monday = _load_monday()
    data = monday.fetch_data()
    kpis = data.get("kpis", {})

    ok = 0
    for day in days:
        try:
            tpl = template_for(day)
            path = generate_day(day, kpis)
            print(f"Day {day:02d} ({tpl}): {display_path(path)}")
            if args.patch:
                patch_day_assets_section(day, tpl)
            ok += 1
        except Exception as e:
            print(f"Day {day:02d} FAILED: {e}", file=sys.stderr)

    if not args.day:
        write_index()
        cr = content_root()
        print(f"\nDone: {ok}/{len(days)} assets → {assets_root().relative_to(cr)}/ (content: {cr})")

    return 0 if ok == len(days) else 1


if __name__ == "__main__":
    raise SystemExit(main())
