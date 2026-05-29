#!/usr/bin/env python3
"""Shared renderers for LinkedIn Day 01–30 assets (Pillow)."""

from __future__ import annotations

import re
import shutil
from pathlib import Path
from typing import Any

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
ASSETS_ROOT = ROOT / "docs" / "linkedin" / "assets"
LINKEDIN_DIR = ROOT / "docs" / "linkedin"
METRICS_DIR = ROOT / "docs" / "metrics"

PE_STORES = frozenset(
    {"wong", "metro", "plazavea", "promart", "vivanda", "tottus", "plaza_vea"}
)

BG = "#0d1117"
PANEL = "#161b22"
ACCENT = "#58a6ff"
GREEN = "#7ee787"
MUTED = "#8b949e"
TEXT = "#e6edf3"
ORANGE = "#ffa657"


def load_font(size: int, bold: bool = False) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSansMono-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf" if bold else "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    ]
    for p in paths:
        if Path(p).is_file():
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def parse_day_md(day: int) -> dict[str, Any]:
    path = LINKEDIN_DIR / f"Day-{day:02d}.md"
    raw = path.read_text(encoding="utf-8")
    fm: dict[str, str] = {}
    body = raw
    if raw.startswith("---"):
        parts = raw.split("---", 2)
        if len(parts) >= 3:
            for line in parts[1].strip().splitlines():
                if ":" in line:
                    k, v = line.split(":", 1)
                    fm[k.strip()] = v.strip()
            body = parts[2]
    title_m = re.search(rf"^# Day {day} — (.+)$", body, re.MULTILINE)
    title = title_m.group(1).strip() if title_m else f"Día {day}"

    def section(name: str) -> str:
        pat = rf"(?m)^## {re.escape(name)}\s*\n(.*?)(?=^## |\Z)"
        m = re.search(pat, body, re.DOTALL)
        return m.group(1).strip() if m else ""

    hooks = section("Hooks (elegir 1)")
    hook_line = ""
    for line in hooks.splitlines():
        line = line.strip()
        if re.match(r"^\d+\.", line):
            hook_line = re.sub(r"^\d+\.\s*", "", line)
            hook_line = re.sub(r"\*\*([^*]+)\*\*:\s*", "", hook_line)
            hook_line = hook_line.replace("**", "").strip()
            break

    post = section("Post (copiar a LinkedIn — sin link en cuerpo)")
    if not post:
        post = section("Post (copiar a LinkedIn — sin link en cuerpo; adjuntar carousel)")
    first_post_line = ""
    for line in post.splitlines():
        t = line.strip()
        if t and not t.startswith("**Slide") and not t.startswith("|"):
            first_post_line = t.replace("**", "")
            break

    return {
        "day": day,
        "title": title,
        "hook": hook_line or first_post_line or title,
        "pillar": fm.get("pillar", ""),
        "hooks_raw": hooks,
        "post": post,
    }


def _header(draw: ImageDraw.ImageDraw, w: int, day: int, subtitle: str = "") -> int:
    font_lg = load_font(26, bold=True)
    font_sm = load_font(18)
    draw.rectangle((0, 0, w, 72), fill=PANEL)
    draw.text((40, 20), "CLI Market", fill=ACCENT, font=font_lg)
    draw.text((240, 24), f"Día {day:02d}/30", fill=MUTED, font=font_sm)
    if subtitle:
        draw.text((400, 24), subtitle[:55], fill=MUTED, font=font_sm)
    return 88


def _footer(draw: ImageDraw.ImageDraw, w: int, h: int) -> None:
    font_sm = load_font(17)
    draw.rectangle((0, h - 52, w, h), fill=PANEL)
    draw.text((40, h - 38), "cli-market.dev  ·  pip install cli-market  ·  MIT", fill=MUTED, font=font_sm)


def _wrap(draw: ImageDraw.ImageDraw, text: str, font, max_width: int) -> list[str]:
    words = text.split()
    lines: list[str] = []
    cur: list[str] = []
    for word in words:
        test = " ".join(cur + [word])
        if draw.textlength(test, font=font) <= max_width:
            cur.append(word)
        else:
            if cur:
                lines.append(" ".join(cur))
            cur = [word]
    if cur:
        lines.append(" ".join(cur))
    return lines or [text[:80]]


def render_quote(day: int, meta: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    w, h = 1200, 1200
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    y = _header(draw, w, day, meta.get("pillar", ""))

    font_huge = load_font(42, bold=True)
    font_body = load_font(28)
    font_title = load_font(22, bold=True)

    draw.text((40, y + 20), meta["title"][:70], fill=MUTED, font=font_title)
    y += 70

    for line in _wrap(draw, meta["hook"], font_huge, w - 100)[:5]:
        draw.text((40, y), line, fill=TEXT, font=font_huge)
        y += 52

    y = max(y + 40, 520)
    excerpt = meta.get("post", "").splitlines()
    shown = 0
    for line in excerpt:
        t = line.strip()
        if not t or t.startswith("|") or t.startswith("**Slide"):
            continue
        t = t.replace("**", "")
        for wl in _wrap(draw, t, font_body, w - 100)[:2]:
            draw.text((40, y), wl, fill=MUTED, font=font_body)
            y += 36
            shown += 1
            if shown >= 4:
                break
        if shown >= 4:
            break

    _footer(draw, w, h)
    path = out_dir / f"day-{day:02d}-linkedin.png"
    img.save(path, "PNG", optimize=True)
    return path


def render_metrics(day: int, meta: dict[str, Any], kpis: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    w, h = 1200, 1200
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    y = _header(draw, w, day, "datos en vivo")

    font_title = load_font(32, bold=True)
    font_kpi = load_font(48, bold=True)
    font_lbl = load_font(20)

    draw.text((40, y + 10), meta["title"], fill=TEXT, font=font_title)
    y += 60

    indexed = int(kpis.get("total_indexed", 0) or 0)
    snap = int(kpis.get("snapshots_24h", 0) or 0)
    stores = int(kpis.get("stores_indexed", 0) or 0)
    cov = float(kpis.get("coverage_7d_pct", 0) or 0)

    cards = [
        ("Indexados", f"{indexed:,}"),
        ("Refresh 24h", f"{snap:,}"),
        ("Retailers", str(stores)),
        ("Cobertura 7d", f"{cov:.1f}%"),
    ]
    for i, (label, value) in enumerate(cards):
        col = i % 2
        row = i // 2
        x0 = 40 + col * 560
        y0 = y + row * 200
        draw.rounded_rectangle((x0, y0, x0 + 520, y0 + 170), radius=12, fill=PANEL)
        draw.text((x0 + 24, y0 + 20), label, fill=MUTED, font=font_lbl)
        draw.text((x0 + 24, y0 + 60), value, fill=GREEN, font=font_kpi)

    y += 420
    draw.text((40, y), meta["hook"][:90], fill=TEXT, font=font_lbl)
    _footer(draw, w, h)
    path = out_dir / f"day-{day:02d}-linkedin.png"
    img.save(path, "PNG", optimize=True)
    return path


def _compare_rows(data: dict, query_hint: str, limit: int = 4) -> list[dict]:
    rows: list[dict] = []
    hint = query_hint.lower()

    def add_item(item: dict) -> bool:
        prices = {
            k: v
            for k, v in (item.get("prices") or {}).items()
            if k in PE_STORES and isinstance(v, (int, float)) and 0 < v < 500
        }
        if not prices:
            return False
        name = item.get("name", "")
        short = name if len(name) <= 44 else name[:41] + "..."
        rows.append(
            {
                "name": short,
                "prices": prices,
                "best_store": item.get("best_store"),
                "best_price": item.get("best_price"),
            }
        )
        return True

    for item in data.get("comparison", []):
        if hint in item.get("name", "").lower() and add_item(item) and len(rows) >= limit:
            return rows
    for item in data.get("comparison", []):
        if add_item(item) and len(rows) >= limit:
            return rows
    return rows


def render_terminal(
    day: int,
    meta: dict[str, Any],
    command: str,
    data: dict,
    out_dir: Path,
    elapsed: str = "0.8s",
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    rows = _compare_rows(data, data.get("query", "producto"))
    stores = data.get("stores_compared", 36)

    w, h = 1200, 1350
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    y = _header(draw, w, day, "terminal")

    font_mono = load_font(20)
    font_sm = load_font(17)
    font_lbl = load_font(19, bold=True)

    draw.text((40, y), "$ " + command, fill=GREEN, font=font_mono)
    y += 40
    badge = f"{elapsed} · {stores} retailers"
    draw.rounded_rectangle((40, y, 40 + len(badge) * 10 + 20, y + 32), radius=8, fill="#238636")
    draw.text((52, y + 6), badge, fill="#fff", font=font_sm)
    y += 48

    draw.text((40, y), "Comparación multi-tienda", fill=TEXT, font=font_lbl)
    y += 32
    for i, row in enumerate(rows):
        draw.rectangle((40, y, w - 40, y + 78), fill=PANEL if i % 2 == 0 else BG)
        draw.text((52, y + 6), row["name"], fill=TEXT, font=font_sm)
        pl = "  ".join(f"{s}: S/ {p:.2f}" for s, p in sorted(row["prices"].items())[:3])
        draw.text((52, y + 30), pl, fill=ACCENT, font=font_sm)
        draw.text((52, y + 52), f"→ {row['best_store']} S/ {row['best_price']:.2f}", fill=ORANGE, font=font_sm)
        y += 82

    _footer(draw, w, h)
    path = out_dir / f"day-{day:02d}-linkedin.png"
    img.save(path, "PNG", optimize=True)
    return path


def render_diagram(day: int, meta: dict[str, Any], out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    w, h = 1200, 1000
    img = Image.new("RGB", (w, h), BG)
    draw = ImageDraw.Draw(img)
    _header(draw, w, day)
    font = load_font(24, bold=True)
    font_sm = load_font(18)

    boxes = [
        (80, 280, "Agente IA", "Razona · planifica · tools"),
        (420, 280, "CLI Market", "API · MCP · checkout"),
        (760, 280, "30+ retailers", "VTEX · Magento · 8 países"),
    ]
    for x, yy, title, sub in boxes:
        draw.rounded_rectangle((x, yy, x + 280, yy + 140), radius=14, fill=PANEL, outline=ACCENT, width=2)
        draw.text((x + 20, yy + 30), title, fill=GREEN, font=font)
        for i, sl in enumerate(_wrap(draw, sub, font_sm, 240)):
            draw.text((x + 20, yy + 70 + i * 24), sl, fill=MUTED, font=font_sm)
    draw.line((360, 350, 420, 350), fill=ACCENT, width=4)
    draw.line((700, 350, 760, 350), fill=ACCENT, width=4)
    draw.polygon([(410, 340), (420, 350), (410, 360)], fill=ACCENT)
    draw.polygon([(750, 340), (760, 350), (750, 360)], fill=ACCENT)

    draw.text((40, 500), meta["hook"][:100], fill=TEXT, font=font_sm)
    _footer(draw, w, h)
    path = out_dir / f"day-{day:02d}-linkedin.png"
    img.save(path, "PNG", optimize=True)
    return path


def render_carousel(
    day: int,
    meta: dict[str, Any],
    slides: list[tuple[str, str]],
    out_dir: Path,
) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    paths: list[Path] = []
    for i, (title, body) in enumerate(slides, start=1):
        size = 1080
        img = Image.new("RGB", (size, size), BG)
        draw = ImageDraw.Draw(img)
        font_t = load_font(40, bold=True)
        font_b = load_font(26)
        font_n = load_font(22)
        draw.text((60, 50), f"{i}/{len(slides)}", fill=MUTED, font=font_n)
        draw.text((60, 100), title, fill=GREEN, font=font_t)
        y = 200
        for line in _wrap(draw, body, font_b, size - 120)[:8]:
            draw.text((60, y), line, fill=TEXT, font=font_b)
            y += 38
        draw.text((60, size - 70), "CLI Market", fill=ACCENT, font=font_n)
        p = out_dir / f"day-{day:02d}-slide-{i:02d}.png"
        img.save(p, "PNG", optimize=True)
        paths.append(p)

    main = out_dir / f"day-{day:02d}-linkedin.png"
    shutil.copy2(paths[0], main)
    return main


# template per day: quote | metrics | terminal | diagram | carousel
DAY_TEMPLATE: dict[int, str] = {
    1: "terminal",
    2: "diagram",
    4: "terminal",
    5: "carousel",
    6: "diagram",
    7: "metrics",
    8: "terminal",
    10: "metrics",
    11: "metrics",
    12: "carousel",
    14: "metrics",
    25: "terminal",
    28: "metrics",
    30: "metrics",
}

TERMINAL_CFG: dict[int, dict[str, str]] = {
    1: {"query": "leche", "country": "PE", "command": 'market compare "leche" --country PE'},
    4: {"query": "leche", "country": "PE", "command": 'market compare "leche" --country PE'},
    8: {"query": "arroz", "country": "PE", "command": 'market compare "arroz" --country PE'},
    25: {"query": "leche", "country": "PE", "command": 'market search "leche" --country PE'},
}

CAROUSEL_CFG: dict[int, list[tuple[str, str]]] = {
    5: [
        ("Instala", "pip install cli-market\nCLI + API + 36 herramientas MCP"),
        ("Autentica", "market login\nFree tier · token listo"),
        ("Busca y compara", 'market compare "arroz" --country PE\n30 retailers · 8 países'),
        ("Checkout", "market checkout --payment yape\nPayPal · QR · el agente cierra la compra"),
    ],
    12: [
        ("¿Qué compra un agente?", "Top búsquedas en CLI Market esta semana"),
        ("#1 Leche", "PE · AR · BR — comparación multi-tienda"),
        ("#2 Arroz", "Mayor variación entre cadenas en Lima"),
        ("#3 Aceite", "Señal de góndola cada 8h"),
        ("#4 Farmacia", "Spread alto entre retailers"),
        ("#5 Electro", "Miles de SKUs indexados"),
        ("Insight", "Supermercados dominan · farmacias = mayor spread"),
        ("CTA", "pip install cli-market\ncli-market.dev/tools"),
    ],
}

METRICS_DAYS = {7, 10, 11, 14, 28, 30}
DIAGRAM_DAYS = {2, 6}
