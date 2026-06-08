#!/usr/bin/env python3
"""Render landing demo.gif (terminalizer-style) from live market_stats."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CORE = ROOT.parent / "cli-market-core"
for p in (ROOT, CORE):
    if str(p) not in sys.path:
        sys.path.insert(0, str(p))

from market_core import market_stats as stats  # noqa: E402
from market_core.market_mcp_registry import public_tool_count  # noqa: E402

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError as exc:  # pragma: no cover
    raise SystemExit("pip install pillow") from exc

# Theme aligned with ops/terminalizer.yml + landing globals.css
BG = (10, 10, 10)
FG = (176, 176, 176)
MINT = (60, 255, 208)
DIM = (120, 130, 125)
BORDER = (60, 255, 208)
TITLE_BG = (28, 28, 30)
DOT_RED = (255, 95, 87)
DOT_YELLOW = (255, 189, 46)
DOT_GREEN = (40, 200, 64)

WIDTH, HEIGHT = 920, 520
PAD = 28
TITLE_H = 44
FONT_SIZE = 15
LINE_H = 22
CURSOR_BLINK = 6  # frames

OUT_PATHS = [
    ROOT / "landing" / "public" / "demo.gif",
    ROOT / "ops" / "demo.gif",
]


def _font(size: int = FONT_SIZE) -> ImageFont.FreeTypeFont | ImageFont.ImageFont:
    candidates = [
        Path(r"C:\Users\acuba\AppData\Local\Microsoft\Windows\Fonts\JetBrainsMono-Regular.ttf"),
        Path("/usr/share/fonts/truetype/jetbrains-mono/JetBrainsMono-Regular.ttf"),
        Path("/System/Library/Fonts/Supplemental/Andale Mono.ttf"),
        Path("C:/Windows/Fonts/consola.ttf"),
    ]
    for path in candidates:
        if path.is_file():
            return ImageFont.truetype(str(path), size)
    return ImageFont.load_default()


def _script() -> list[tuple[str, str, int]]:
    """Lines: kind (prompt|out|dim|head), text, hold_frames after reveal."""
    pkg = stats.PYPI_PACKAGE_NAME
    ver = stats.PACKAGE_VERSION
    rv = stats.RETAILERS_VERIFIED
    rd = stats.RETAILERS_DEFINED
    countries = stats.COUNTRIES
    mcp = stats.MCP_TOOLS
    mcp_legacy = public_tool_count("legacy")
    return [
        ("dim", '🤖 AGENT: "Compara arroz en Perú y arma una canasta."', 10),
        ("dim", "", 2),
        ("prompt", "pip install cli-market-world", 8),
        ("out", f"✓ {pkg} {ver}", 8),
        ("dim", "", 2),
        ("prompt", "market init", 6),
        ("out", f"✓ {rd} retailers · {rv} verificados · {mcp} MCP · {countries} países", 12),
        ("dim", "", 2),
        ("prompt", 'market compare "arroz" --country PE', 8),
        ("dim", "", 2),
        ("out", "Metro S/2.90 · Wong S/3.10 · Plaza Vea S/2.95 · normalizado/kg", 10),
        ("dim", "", 2),
        ("prompt", 'market basket "arroz:1 leche:1" --country PE', 8),
        ("dim", "", 2),
        ("out", "Mejor: Metro S/12.40 · ahorro S/1.20 vs promedio", 10),
        ("dim", "", 2),
        ("prompt", "market tools", 6),
        ("out", f"Shop · Intel · Account · {mcp} tools ({mcp_legacy} legacy)", 8),
        ("dim", "", 4),
        ("head", "─────────────────────────────────────────", 2),
        ("head", "🧾  AGENT RECEIPT", 4),
        ("head", "─────────────────", 2),
        ("out", f"Comparado:  {rv} retailers verificados · PE", 4),
        ("out", "Canasta:    Metro · S/12.40", 4),
        ("out", f"MCP:        {mcp} curated ({mcp_legacy} legacy)", 4),
        ("out", "Tiempo:     <15 segundos", 4),
        ("head", "─────────────────", 2),
        ("dim", "cli-market.dev  ·  MIT  ·  pip install cli-market-world", 22),
    ]


def _draw_frame(visible: list[tuple[str, str]], cursor_on: bool, tick: int) -> Image.Image:
    img = Image.new("RGB", (WIDTH, HEIGHT), BG)
    draw = ImageDraw.Draw(img)
    font = _font()

    # Outer glow
    draw.rounded_rectangle((12, 12, WIDTH - 12, HEIGHT - 12), radius=14, outline=BORDER, width=2)
    draw.rounded_rectangle((14, 14, WIDTH - 14, HEIGHT - 14), radius=12, outline=(30, 90, 75), width=1)

    # Title bar
    draw.rounded_rectangle((PAD, PAD, WIDTH - PAD, PAD + TITLE_H), radius=10, fill=TITLE_BG)
    draw.rectangle((PAD + 8, PAD + TITLE_H - 2, WIDTH - PAD - 8, PAD + TITLE_H), fill=TITLE_BG)
    for i, color in enumerate((DOT_RED, DOT_YELLOW, DOT_GREEN)):
        x = PAD + 16 + i * 18
        draw.ellipse((x, PAD + 16, x + 10, PAD + 26), fill=color)
    draw.text((PAD + 72, PAD + 12), "CLI Market — Agent Receipt", font=font, fill=MINT)

    y = PAD + TITLE_H + 18
    x0 = PAD + 16
    max_y = HEIGHT - PAD - 12

    for kind, text in visible:
        if y > max_y:
            break
        if kind == "prompt":
            draw.text((x0, y), "$ ", font=font, fill=MINT)
            draw.text((x0 + draw.textlength("$ ", font=font), y), text, font=font, fill=MINT)
        elif kind == "head":
            draw.text((x0, y), text, font=font, fill=MINT)
        elif kind == "dim":
            draw.text((x0, y), text, font=font, fill=DIM)
        else:
            draw.text((x0 + 8, y), text, font=font, fill=FG)
        y += LINE_H

    if cursor_on and y <= max_y:
        cx = x0
        if visible and visible[-1][0] == "prompt":
            cx = x0 + draw.textlength("$ " + visible[-1][1], font=font)
        elif visible and visible[-1][0] in ("out", "head", "dim"):
            cx = x0 + 8 + draw.textlength(visible[-1][1], font=font)
        if tick % CURSOR_BLINK < CURSOR_BLINK // 2:
            draw.rectangle((cx, y - 2, cx + 9, y + FONT_SIZE), fill=MINT)

    return img


def _build_frames() -> list[Image.Image]:
    script = _script()
    frames: list[Image.Image] = []
    visible: list[tuple[str, str]] = []
    tick = 0

    for kind, text, hold in script:
        if kind == "prompt":
            for n in range(1, len(text) + 1):
                partial = ("prompt", text[:n])
                if visible and visible[-1][0] == "prompt":
                    visible[-1] = partial
                else:
                    visible.append(partial)
                for _ in range(2):
                    frames.append(_draw_frame(visible, cursor_on=True, tick=tick))
                    tick += 1
            for _ in range(hold):
                frames.append(_draw_frame(visible, cursor_on=False, tick=tick))
                tick += 1
        else:
            visible.append((kind, text))
            for _ in range(hold):
                frames.append(_draw_frame(visible, cursor_on=False, tick=tick))
                tick += 1

    # Loop tail: hold final frame before repeat
    for _ in range(14):
        frames.append(_draw_frame(visible, cursor_on=False, tick=tick))
        tick += 1
    return frames


def main() -> int:
    frames = _build_frames()
    duration_ms = 72
    first, *rest = frames

    def quantize(im: Image.Image) -> Image.Image:
        return im.convert("P", palette=Image.Palette.ADAPTIVE, colors=48)

    out = OUT_PATHS[0]
    out.parent.mkdir(parents=True, exist_ok=True)
    quantize(first).save(
        out,
        save_all=True,
        append_images=[quantize(f) for f in rest],
        duration=duration_ms,
        loop=0,
        optimize=True,
        disposal=2,
    )
    for dest in OUT_PATHS[1:]:
        shutil.copy2(out, dest)
    print(f"Wrote {out} ({len(frames)} frames, {len(frames) * duration_ms / 1000:.1f}s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())