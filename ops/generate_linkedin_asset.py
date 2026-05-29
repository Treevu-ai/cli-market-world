#!/usr/bin/env python3
"""Generate LinkedIn image assets from production compare JSON.

Usage:
  python3 ops/generate_linkedin_asset.py --day 1
  python3 ops/generate_linkedin_asset.py --day 1 --json docs/metrics/query-leche-pe.json
"""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
PE_STORES = frozenset(
    {"wong", "metro", "plazavea", "promart", "vivanda", "tottus", "plaza_vea"}
)

DAY_CONFIG = {
    1: {
        "query": "leche",
        "country": "PE",
        "json": ROOT / "docs/metrics/query-leche-pe.json",
        "command": 'market compare "leche" --country PE',
        "elapsed": "0.8s",
        "out_dir": ROOT / "docs/linkedin/assets/day-01",
    },
}


def _load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/liberation/LiberationMono-Regular.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for path in candidates:
        if Path(path).is_file():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()


def _pe_rows(data: dict, limit: int = 4) -> list[dict]:
    rows: list[dict] = []
    for item in data.get("comparison", []):
        name = item.get("name", "")
        if "leche" not in name.lower():
            continue
        prices = {
            k: v
            for k, v in (item.get("prices") or {}).items()
            if k in PE_STORES and isinstance(v, (int, float)) and v < 200
        }
        if len(prices) < 1:
            continue
        short = name if len(name) <= 42 else name[:39] + "..."
        rows.append(
            {
                "name": short,
                "prices": prices,
                "best_store": item.get("best_store"),
                "best_price": item.get("best_price"),
            }
        )
        if len(rows) >= limit:
            break
    if len(rows) < limit:
        for item in data.get("comparison", []):
            if any(r["name"] == item.get("name") for r in rows):
                continue
            prices = {
                k: v
                for k, v in (item.get("prices") or {}).items()
                if k in PE_STORES and isinstance(v, (int, float)) and v < 200
            }
            if not prices:
                continue
            name = item.get("name", "")
            short = name if len(name) <= 42 else name[:39] + "..."
            rows.append({"name": short, "prices": prices, "best_store": item.get("best_store"), "best_price": item.get("best_price")})
            if len(rows) >= limit:
                break
    return rows


def _json_excerpt(data: dict, rows: list[dict]) -> str:
    excerpt = {
        "query": data.get("query", "leche"),
        "stores_compared": data.get("stores_compared", 36),
        "comparison": [
            {
                "name": r["name"],
                "prices": r["prices"],
                "best_store": r["best_store"],
                "best_price": r["best_price"],
            }
            for r in rows
        ],
    }
    return json.dumps(excerpt, indent=2, ensure_ascii=False)


def render_day01(
    data: dict,
    cfg: dict,
    out_dir: Path,
) -> list[Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = _pe_rows(data, 4)
    stores_compared = data.get("stores_compared", 36)
    command = cfg["command"]
    elapsed = cfg["elapsed"]

    w, h = 1200, 1500
    img = Image.new("RGB", (w, h), "#0d1117")
    draw = ImageDraw.Draw(img)

    font_title = _load_font(28, bold=True)
    font_mono = _load_font(22)
    font_mono_sm = _load_font(18)
    font_label = _load_font(20, bold=True)

    # Header bar
    draw.rectangle((0, 0, w, 72), fill="#161b22")
    draw.text((40, 22), "CLI Market", fill="#58a6ff", font=font_title)
    draw.text((280, 26), "comercio para agentes de IA", fill="#8b949e", font=font_mono_sm)

    y = 100
    draw.text((40, y), "$ " + command, fill="#7ee787", font=font_mono)
    y += 44
    badge = f"  {elapsed}  ·  {stores_compared} retailers  ·  PE  "
    draw.rounded_rectangle((40, y, 40 + len(badge) * 11, y + 36), radius=8, fill="#238636")
    draw.text((52, y + 6), badge.strip(), fill="#ffffff", font=font_mono_sm)
    y += 56

    # Results table
    draw.text((40, y), "Comparación multi-tienda (precios de góndola)", fill="#c9d1d9", font=font_label)
    y += 36
    for i, row in enumerate(rows):
        draw.rectangle((40, y, w - 40, y + 88), fill="#161b22" if i % 2 == 0 else "#0d1117")
        draw.text((52, y + 8), row["name"], fill="#e6edf3", font=font_mono_sm)
        price_line = "  ".join(f"{s}: S/ {p:.2f}" for s, p in sorted(row["prices"].items()))
        draw.text((52, y + 36), price_line, fill="#79c0ff", font=font_mono_sm)
        best = f"mejor: {row['best_store']} S/ {row['best_price']:.2f}"
        draw.text((52, y + 60), best, fill="#ffa657", font=font_mono_sm)
        y += 92

    y += 20
    draw.text((40, y), "JSON (respuesta API — recorte)", fill="#c9d1d9", font=font_label)
    y += 32

    json_text = _json_excerpt(data, rows)
    for line in json_text.splitlines():
        color = "#a5d6ff" if '"' in line else "#8b949e"
        if line.strip().startswith('"best'):
            color = "#ffa657"
        draw.text((48, y), line[:95], fill=color, font=font_mono_sm)
        y += 24
        if y > h - 80:
            draw.text((48, y), "  …", fill="#8b949e", font=font_mono_sm)
            break

    draw.rectangle((0, h - 56, w, h), fill="#161b22")
    draw.text(
        (40, h - 40),
        "pip install cli-market  ·  cli-market.dev  ·  datos en vivo",
        fill="#8b949e",
        font=font_mono_sm,
    )

    main_path = out_dir / "day-01-linkedin.png"
    img.save(main_path, "PNG", optimize=True)

    # Terminal-only crop (top section) for optional stories
    terminal = img.crop((0, 0, w, min(720, h)))
    term_path = out_dir / "day-01-terminal.png"
    terminal.save(term_path, "PNG", optimize=True)

    # JSON panel
    jw, jh = 1200, 900
    jimg = Image.new("RGB", (jw, jh), "#1e1e1e")
    jdraw = ImageDraw.Draw(jimg)
    jdraw.text((32, 24), "POST /products/compare", fill="#d4d4d4", font=font_label)
    jy = 64
    for line in json_text.splitlines():
        jdraw.text((32, jy), line[:100], fill="#9cdcfe", font=font_mono_sm)
        jy += 26
        if jy > jh - 40:
            break
    json_path = out_dir / "day-01-compare-json.png"
    jimg.save(json_path, "PNG", optimize=True)

    # Simple GIF: terminal reveal (3 frames)
    gif_path = out_dir / "day-01-terminal.gif"
    frames = [
        terminal.crop((0, 0, w, 400)),
        terminal.crop((0, 0, w, 560)),
        terminal,
    ]
    frames[0].save(
        gif_path,
        save_all=frames[1:],
        append_images=frames[1:],
        duration=700,
        loop=0,
        optimize=True,
    )

    return [main_path, term_path, json_path, gif_path]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--day", type=int, default=1)
    parser.add_argument("--json", type=Path, help="Override compare JSON path")
    args = parser.parse_args()

    cfg = DAY_CONFIG.get(args.day)
    if not cfg:
        print(f"No asset config for day {args.day}", flush=True)
        return 1

    json_path = args.json or cfg["json"]
    if not json_path.is_file():
        print(f"Missing {json_path} — run compare fetch first", flush=True)
        return 1

    data = json.loads(json_path.read_text(encoding="utf-8"))
    paths = render_day01(data, cfg, cfg["out_dir"])
    for p in paths:
        print(p.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
